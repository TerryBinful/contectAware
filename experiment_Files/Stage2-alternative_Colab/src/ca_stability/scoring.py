"""Stage C — Exp 1: the FIXED authentication-score generator.

One binary verification model per genuine user g (reusing the corrected protocol of
`experiment_Files/Stage1/exp4_feature_ablation.py`: HistGradientBoosting, class-balanced
weights, no SMOTE, no per-arm feature selection, imputer+scaler fitted on training rows only):

    positives : g's TRAIN-period frames
    negatives : TRAIN-period frames of impostor_train(g) (<= cap frames per impostor, seeded)
    score     : p_raw = P(frame belongs to g)
    calibration: per-user Platt scaling on the VALIDATION period
                 (g's val frames vs impostor_cal(g) val frames, class-balanced)

The calibrated score p_cal is the common evidence stream every decision mechanism consumes.
Nothing in this stage depends on any decision mechanism.
"""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.preprocessing import RobustScaler

from .provenance import LOG, write_json
from .splits import user_seed

EPS = 1e-6


# ----------------------------------------------------------------------------- metrics
def eer(y, s):
    if len(np.unique(y)) < 2:
        return float("nan"), float("nan")
    fpr, tpr, thr = roc_curve(y, s)
    fnr = 1 - tpr
    i = int(np.nanargmin(np.abs(fnr - fpr)))
    return float((fpr[i] + fnr[i]) / 2), float(thr[i])


def logit(p):
    p = np.clip(np.asarray(p, dtype=float), EPS, 1 - EPS)
    return np.log(p / (1 - p))


def verification_metrics(y, p, prefix=""):
    y = np.asarray(y)
    p = np.asarray(p)
    gen, imp = y == 1, y == 0
    e, _ = eer(y, p)
    out = {
        "eer": e,
        "auc": float(roc_auc_score(y, p)) if gen.any() and imp.any() else float("nan"),
        "far_at_0.5": float((p[imp] >= 0.5).mean()) if imp.any() else float("nan"),
        "frr_at_0.5": float((p[gen] < 0.5).mean()) if gen.any() else float("nan"),
        "brier_balanced": float(0.5 * np.mean((1 - p[gen]) ** 2) + 0.5 * np.mean(p[imp] ** 2)),
        "genuine_frac_p_le_0.4": float((p[gen] <= 0.4).mean()),
        "genuine_frac_band_0.4_0.6": float(((p[gen] > 0.4) & (p[gen] < 0.6)).mean()),
        "impostor_frac_p_ge_0.6": float((p[imp] >= 0.6).mean()),
        "impostor_frac_band_0.4_0.6": float(((p[imp] > 0.4) & (p[imp] < 0.6)).mean()),
        "genuine_median_p": float(np.median(p[gen])),
        "impostor_median_p": float(np.median(p[imp])),
        "n_genuine": int(gen.sum()),
        "n_impostor": int(imp.sum()),
    }
    return {f"{prefix}{k}": v for k, v in out.items()}


# ----------------------------------------------------------------------------- model
def build_classifier(cfg, seed):
    if cfg["classifier"]["type"] != "hgb":
        raise ValueError("only 'hgb' is implemented for the primary experiment")
    return HistGradientBoostingClassifier(random_state=seed, **cfg["classifier"]["params"])


def _impostor_train_rows(frames, users, cap, seed, g):
    idx = []
    for u in users:
        rows = np.flatnonzero(((frames.uuid == u) & (frames.period == "train")).values)
        if cap and len(rows) > cap:
            rng = np.random.default_rng(user_seed(seed, "imp-sample", g, u))
            rows = np.sort(rng.choice(rows, size=cap, replace=False))
        idx.append(rows)
    return np.concatenate(idx) if idx else np.array([], dtype=int)


def score_user(cfg, frames: pd.DataFrame, X_all: np.ndarray, g: str, roles: dict) -> tuple[pd.DataFrame, dict]:
    """Fit g's model and score the frames it is later evaluated on. X_all is the float32
    feature matrix aligned with `frames` rows."""
    seed = int(cfg["experiment"]["seed"])
    t0 = time.time()
    is_g = (frames.uuid == g).values
    per = frames.period.values
    g_tr = np.flatnonzero(is_g & (per == "train"))
    imp_tr = _impostor_train_rows(frames, roles["impostor_train"], cfg["classifier"]["max_impostor_frames_per_user"], seed, g)
    Xtr = X_all[np.concatenate([g_tr, imp_tr])]
    ytr = np.concatenate([np.ones(len(g_tr), int), np.zeros(len(imp_tr), int)])

    keep = ~np.all(np.isnan(Xtr), axis=0)                 # drop columns entirely NaN in training
    imputer = SimpleImputer(strategy="median").fit(Xtr[:, keep])
    scaler = RobustScaler().fit(imputer.transform(Xtr[:, keep]))

    def prep(rows):
        X = X_all[rows][:, keep]
        return scaler.transform(imputer.transform(X))

    model = build_classifier(cfg, user_seed(seed, "model", g)).fit(prep(np.concatenate([g_tr, imp_tr])), ytr)

    # rows to score: genuine val/test; impostor_cal val; impostor_test test
    sel = [("genuine", np.flatnonzero(is_g & np.isin(per, ["val", "test"])))]
    uu = frames.uuid.values
    sel.append(("imp_cal", np.flatnonzero(np.isin(uu, roles["impostor_cal"]) & (per == "val"))))
    sel.append(("imp_test", np.flatnonzero(np.isin(uu, roles["impostor_test"]) & (per == "test"))))
    rows = np.concatenate([r for _, r in sel])
    role = np.concatenate([[name] * len(r) for name, r in sel])
    p_raw = model.predict_proba(prep(rows))[:, 1]

    out = pd.DataFrame({
        "model_uuid": g, "row": rows, "uuid": uu[rows], "timestamp": frames.timestamp.values[rows],
        "period": per[rows], "run": frames.run.values[rows], "role": role, "p_raw": p_raw.astype(np.float64),
    })
    # --- per-user Platt calibration on the validation period only
    vmask = ((out.role == "genuine") & (out.period == "val")) | (out.role == "imp_cal")
    yv = (out.role[vmask] == "genuine").astype(int).values
    platt = LogisticRegression(C=1e4, class_weight="balanced", max_iter=1000).fit(logit(out.p_raw[vmask]).reshape(-1, 1), yv)
    out["p_cal"] = platt.predict_proba(logit(out.p_raw.values).reshape(-1, 1))[:, 1]

    # --- diagnostics
    info = {"genuine_uuid": g, "n_train_genuine": int(len(g_tr)), "n_train_impostor": int(len(imp_tr)),
            "n_train_impostor_users": len(roles["impostor_train"]), "n_features_used": int(keep.sum()),
            "platt_coef": float(platt.coef_[0, 0]), "platt_intercept": float(platt.intercept_[0])}
    for part, imp_role in (("val", "imp_cal"), ("test", "imp_test")):
        m = ((out.role == "genuine") & (out.period == part)) | (out.role == imp_role)
        y = (out.role[m] == "genuine").astype(int).values
        info.update(verification_metrics(y, out.p_cal[m].values, prefix=f"{part}_"))
        info[f"{part}_eer_raw"] = eer(y, out.p_raw[m].values)[0]
    # temporal adjacency (Stage 1 criterion C1): share of g's val/test frames with a g TRAIN frame within 90 s
    tr_ts = np.sort(frames.timestamp.values[g_tr])
    for part in ("val", "test"):
        ts = out.timestamp[(out.role == "genuine") & (out.period == part)].values
        pos = np.searchsorted(tr_ts, ts)
        prev = np.where(pos > 0, np.abs(ts - tr_ts[np.clip(pos - 1, 0, len(tr_ts) - 1)]), np.inf)
        nxt = np.where(pos < len(tr_ts), np.abs(tr_ts[np.clip(pos, 0, len(tr_ts) - 1)] - ts), np.inf)
        info[f"{part}_frac_within_90s_of_train"] = float(np.mean(np.minimum(prev, nxt) <= 90)) if len(ts) else float("nan")
    # instability of a plain 0.5 threshold on g's genuine test runs (for comparison with Stage 1's 2.69/h)
    gt = out[(out.role == "genuine") & (out.period == "test")].sort_values("timestamp")
    trans = 0
    for _, grp in gt.groupby("run"):
        s = grp.p_cal.values >= 0.5
        trans += int(np.sum(s[1:] != s[:-1])) + int(not s[0])
    info["test_transitions_at_0.5"] = trans
    info["test_transitions_per_hour_at_0.5"] = trans / (len(gt) / 60.0) if len(gt) else float("nan")
    info["fit_seconds"] = round(time.time() - t0, 2)
    # impostor disjointness assertions (fail loudly)
    assert not set(out.uuid[out.role == "imp_cal"]) & set(roles["impostor_train"])
    assert not set(out.uuid[out.role == "imp_test"]) & set(roles["impostor_train"])
    assert not set(out.uuid[out.role == "imp_test"]) & set(roles["impostor_cal"])
    return out, info


def run_scoring(cfg, frames, feat_cols, split, work_dir: Path, out_dir: Path):
    """Score every genuine user (checkpointed per user). Returns ({g: scores_df}, per-user metrics, summary)."""
    X_all = frames[feat_cols].to_numpy(dtype=np.float32)
    sdir = Path(work_dir) / "scores"
    sdir.mkdir(parents=True, exist_ok=True)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    scores, infos = {}, []
    genuine = split["genuine_users"]
    for i, g in enumerate(genuine, 1):
        fp, fi = sdir / f"{g}.pkl", sdir / f"{g}.info.json"
        if fp.exists() and fi.exists():
            scores[g] = pd.read_pickle(fp)
            infos.append(pd.read_json(fi, typ="series").to_dict())
            LOG.info("[%d/%d] %s: cached", i, len(genuine), g[:8])
            continue
        s, info = score_user(cfg, frames, X_all, g, split["roles"][g])
        s.to_pickle(fp)
        write_json(info, fi)
        scores[g] = s
        infos.append(info)
        LOG.info("[%d/%d] %s: test EER %.3f AUC %.3f (val EER %.3f) fit %.1fs", i, len(genuine), g[:8],
                 info["test_eer"], info["test_auc"], info["val_eer"], info["fit_seconds"])
    per_user = pd.DataFrame(infos).sort_values("genuine_uuid").reset_index(drop=True)
    per_user.to_csv(out_dir / "exp1_per_user_classifier_metrics.csv", index=False)

    gate = cfg["gate"]["min_median_test_auc"]
    summary = {
        "unit_of_analysis": "genuine participant",
        "n_genuine_users": int(len(per_user)),
        "feature_set": cfg["features"]["set"],
        "n_features": int(per_user.n_features_used.median()),
        "classifier": {"type": cfg["classifier"]["type"], **cfg["classifier"]["params"]},
        "calibration": cfg["classifier"]["calibration"],
    }
    for col in ["test_eer", "test_auc", "test_far_at_0.5", "test_frr_at_0.5", "test_brier_balanced",
                "test_genuine_frac_p_le_0.4", "test_genuine_frac_band_0.4_0.6", "test_impostor_frac_p_ge_0.6",
                "test_impostor_frac_band_0.4_0.6", "val_eer", "val_auc", "test_transitions_per_hour_at_0.5",
                "test_frac_within_90s_of_train", "val_frac_within_90s_of_train"]:
        v = per_user[col].astype(float)
        summary[col] = {"median": float(v.median()), "mean": float(v.mean()), "sd": float(v.std()),
                        "min": float(v.min()), "max": float(v.max())}
    summary["validity_checks"] = {
        "impostor_roles_disjoint": True,             # asserted per user inside score_user
        "preprocessing_fit_on_training_rows_only": True,
        "calibration_fit_on_validation_only": True,
        "smote_used": False,
        "max_frac_test_frames_within_90s_of_train": float(per_user.test_frac_within_90s_of_train.max()),
        "stage1_reference": {"closed_set_impostors": "59/59 seen", "frac_test_within_90s_of_train": 0.957,
                             "genuine_band_0.4_0.6": 0.0284, "transitions_per_hour": 597 / 222.32},
    }
    med_auc = summary["test_auc"]["median"]
    summary["gate"] = {"criterion": f"median per-user test AUC >= {gate}", "value": med_auc, "passed": bool(med_auc >= gate)}
    write_json(summary, out_dir / "exp1_summary.json")

    # pooled reliability (class-balanced within each user) on the TEST partition
    rel = []
    bins = np.linspace(0, 1, 11)
    for g, s in scores.items():
        m = ((s.role == "genuine") & (s.period == "test")) | (s.role == "imp_test")
        d = s[m]
        y = (d.role == "genuine").values
        w = np.where(y, 0.5 / max(y.sum(), 1), 0.5 / max((~y).sum(), 1))
        b = np.clip(np.digitize(d.p_cal.values, bins) - 1, 0, 9)
        for k in range(10):
            mk = b == k
            rel.append({"genuine_uuid": g, "bin": k, "w": w[mk].sum(), "w_genuine": w[mk & y].sum(),
                        "p_mean_w": float(np.sum(w[mk] * d.p_cal.values[mk]))})
    rel = pd.DataFrame(rel).groupby("bin")[["w", "w_genuine", "p_mean_w"]].sum().reset_index()
    rel["mean_predicted"] = rel.p_mean_w / rel.w.replace(0, np.nan)
    rel["observed_genuine_rate"] = rel.w_genuine / rel.w.replace(0, np.nan)
    rel.drop(columns=["p_mean_w"]).to_csv(out_dir / "exp1_reliability_test.csv", index=False)
    LOG.info("Exp1: median test EER %.3f, median test AUC %.3f; gate %s",
             summary["test_eer"]["median"], med_auc, "PASSED" if summary["gate"]["passed"] else "FAILED")
    return scores, per_user, summary
