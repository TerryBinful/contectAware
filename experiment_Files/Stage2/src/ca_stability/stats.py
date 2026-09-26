"""Stage H — participant-level statistics (unit of analysis = genuine user; frames are never
treated as independent). Pre-registered families:

  omnibus   : Friedman test across the primary mechanisms for each outcome (+ Kendall's W; Nemenyi
              critical difference on average ranks, reported whether or not Friedman is significant,
              but interpreted only if it is).
  vs_threshold : Wilcoxon signed-rank, each mechanism vs the instantaneous threshold, Holm within outcome.
  primary   : hysteresis vs the best smoother (chosen on VALIDATION, recorded in operating_points.csv)
              on the primary outcome; alpha = 0.05, single test. Other outcomes Holm-adjusted.
  H3        : hysteresis vs margin-only and vs debounce-only on the primary outcome (Holm over 2).
  H4        : condition M vs condition X ANIA, per mechanism (Holm over mechanisms).
Effect sizes: median paired difference with user-level bootstrap 95% CI; matched-pairs rank-biserial r.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats as st

from .splits import user_seed

# (key, column template, family, label, lower_is_better)
OUTCOMES = [
    ("ania", "{c}_ania_median", "responsiveness", "Sustained detection delay (frames, median per user)", True),
    ("first_lock", "{c}_first_lock_median", "responsiveness", "First-lock delay (frames)", True),
    ("recovery", "{c}_recovery_median", "responsiveness", "Recovery latency after return (frames)", True),
    ("miss_rate", "{c}_miss_rate", "security", "Missed impostor blocks (fraction)", True),
    ("far_frame", "{c}_far_frame", "security", "FAR_frame: impostor frames accepted (fraction)", True),
    ("frr_time", "frr_time", "security", "FRR_time: genuine frames locked (fraction)", True),
    ("false_locks_per_hour", "false_locks_per_hour", "stability", "False locks per genuine hour", True),
    ("transitions_per_hour", "transitions_per_hour", "stability", "State transitions per genuine hour", True),
    ("pingpong_per_hour", "pingpong_per_hour", "stability", "Ping-pong events per genuine hour", True),
    ("lockout_mean_frames", "lockout_mean_frames", "responsiveness", "Mean false-lock duration (frames)", True),
]


def outcome_column(key: str, cond: str) -> str:
    for k, tmpl, *_ in OUTCOMES:
        if k == key:
            return tmpl.format(c=cond)
    raise KeyError(key)


def holm(p: np.ndarray) -> np.ndarray:
    p = np.asarray(p, dtype=float)
    out = np.full(len(p), np.nan)
    ok = ~np.isnan(p)
    q = p[ok]
    m = len(q)
    if m == 0:
        return out
    order = np.argsort(q)
    adj = np.empty(m)
    run = 0.0
    for i, j in enumerate(order):
        run = max(run, min(1.0, (m - i) * q[j]))
        adj[j] = run
    out[ok] = adj
    return out


def rank_biserial(d: np.ndarray) -> float:
    d = d[d != 0]
    if len(d) == 0:
        return 0.0
    r = st.rankdata(np.abs(d))
    wp, wm = r[d > 0].sum(), r[d < 0].sum()
    return float((wp - wm) / (wp + wm))


def bootstrap_median_ci(x: np.ndarray, reps: int, seed: int, alpha: float = 0.05):
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    if len(x) == 0:
        return np.nan, np.nan
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(x), size=(reps, len(x)))
    meds = np.median(x[idx], axis=1)
    return float(np.quantile(meds, alpha / 2)), float(np.quantile(meds, 1 - alpha / 2))


def paired_test(a: np.ndarray, b: np.ndarray, reps: int, seed: int) -> dict:
    ok = ~np.isnan(a) & ~np.isnan(b)
    a, b = a[ok], b[ok]
    d = a - b
    res = {"n_users": int(len(d)), "median_a": float(np.median(a)) if len(a) else np.nan,
           "median_b": float(np.median(b)) if len(b) else np.nan,
           "median_diff": float(np.median(d)) if len(d) else np.nan,
           "n_a_lower": int((d < 0).sum()), "n_b_lower": int((d > 0).sum()), "n_ties": int((d == 0).sum())}
    res["ci_lo"], res["ci_hi"] = bootstrap_median_ci(d, reps, seed)
    res["rank_biserial"] = rank_biserial(d) if len(d) else np.nan
    if len(d) < 5 or np.all(d == 0):
        res["statistic"], res["p_value"] = np.nan, (1.0 if len(d) and np.all(d == 0) else np.nan)
    else:
        w = st.wilcoxon(a, b, zero_method="wilcox", alternative="two-sided")
        res["statistic"], res["p_value"] = float(w.statistic), float(w.pvalue)
    return res


def nemenyi_cd(k: int, n: int, alpha: float = 0.05) -> float:
    q = st.studentized_range.ppf(1 - alpha, k, 1e6) / np.sqrt(2)
    return float(q * np.sqrt(k * (k + 1) / (6.0 * n)))


def wide(pu: pd.DataFrame, col: str, mechs: list) -> pd.DataFrame:
    return pu.pivot(index="genuine_uuid", columns="mechanism", values=col).reindex(columns=mechs)


def run_stats(cfg, pu: pd.DataFrame, ops: pd.DataFrame, sel_cond: str, conditions: list):
    """pu: participant metrics for ONE target on the TEST partition. Returns (tests df, ranks df)."""
    alpha = float(cfg["stats"]["alpha"])
    reps = int(cfg["stats"]["bootstrap_reps"])
    seed = int(cfg["experiment"]["seed"])
    mechs = [m for m in cfg["mechanisms"]["primary_set"] if m in set(pu.mechanism)]
    best_sm = ops.best_smoother.iloc[0]
    rows, rank_rows = [], []
    for key, tmpl, fam, label, _ in OUTCOMES:
        col = tmpl.format(c=sel_cond)
        Wd = wide(pu, col, mechs)
        comp = Wd.dropna()
        # --- omnibus
        if len(comp) >= 3 and comp.shape[1] >= 3 and not np.allclose(comp.values, comp.values[:, :1]):
            fr = st.friedmanchisquare(*[comp[m].values for m in mechs])
            chi2, p = float(fr.statistic), float(fr.pvalue)
            kw = chi2 / (len(comp) * (len(mechs) - 1))
        else:
            chi2, p, kw = np.nan, np.nan, np.nan
        ranks = comp.rank(axis=1, method="average").mean() if len(comp) else pd.Series(np.nan, index=mechs)
        cd = nemenyi_cd(len(mechs), len(comp), alpha) if len(comp) else np.nan
        rows.append({"family": "omnibus", "outcome": key, "outcome_family": fam, "condition": sel_cond if "{c}" in tmpl else "",
                     "comparison": f"Friedman across {len(mechs)} mechanisms", "mech_a": "", "mech_b": "",
                     "n_users": int(len(comp)), "statistic": chi2, "p_value": p, "kendalls_w": kw,
                     "nemenyi_cd": cd, "significant": bool(p < alpha) if not np.isnan(p) else False})
        for m in mechs:
            rank_rows.append({"outcome": key, "mechanism": m, "avg_rank": float(ranks.get(m, np.nan)),
                              "n_users": int(len(comp)), "nemenyi_cd": cd, "friedman_p": p})
        # --- each vs threshold
        fam_rows = []
        for i, m in enumerate(mechs):
            if m == "threshold":
                continue
            r = paired_test(Wd[m].values, Wd["threshold"].values, reps, seed + 17 * i + len(rows))
            fam_rows.append({"family": "vs_threshold", "outcome": key, "outcome_family": fam,
                             "condition": sel_cond if "{c}" in tmpl else "", "comparison": f"{m} - threshold",
                             "mech_a": m, "mech_b": "threshold", **r})
        ph = holm(np.array([r["p_value"] for r in fam_rows]))
        for r, q in zip(fam_rows, ph):
            r["p_holm"] = q
            r["significant"] = bool(q < alpha) if not np.isnan(q) else False
        rows.extend(fam_rows)
        # --- primary: hysteresis vs best smoother (all outcomes; primary outcome is the confirmatory one)
        if "hysteresis" in mechs and best_sm in mechs:
            r = paired_test(Wd["hysteresis"].values, Wd[best_sm].values, reps, seed + 1000 + len(rows))
            rows.append({"family": "primary" if key == "ania" else "primary_secondary_outcomes", "outcome": key,
                         "outcome_family": fam, "condition": sel_cond if "{c}" in tmpl else "",
                         "comparison": f"hysteresis - {best_sm} (best smoother on validation)",
                         "mech_a": "hysteresis", "mech_b": best_sm, **r})
    # Holm across the secondary outcomes of the primary contrast
    sec = [i for i, r in enumerate(rows) if r["family"] == "primary_secondary_outcomes"]
    for i, q in zip(sec, holm(np.array([rows[i]["p_value"] for i in sec]))):
        rows[i]["p_holm"] = q
        rows[i]["significant"] = bool(q < alpha) if not np.isnan(q) else False
    for i, r in enumerate(rows):
        if r["family"] == "primary":
            r["p_holm"] = r["p_value"]
            r["significant"] = bool(r["p_value"] < alpha) if not np.isnan(r["p_value"]) else False
    # --- H3 component ablation on the primary outcome
    col = outcome_column("ania", sel_cond)
    Wd = wide(pu, col, mechs)
    h3 = []
    for other in ("margin", "debounce"):
        if "hysteresis" in mechs and other in mechs:
            r = paired_test(Wd["hysteresis"].values, Wd[other].values, reps, seed + 2000 + len(h3))
            h3.append({"family": "H3_component_ablation", "outcome": "ania", "outcome_family": "responsiveness",
                       "condition": sel_cond, "comparison": f"hysteresis - {other}", "mech_a": "hysteresis",
                       "mech_b": other, **r})
    for r, q in zip(h3, holm(np.array([r["p_value"] for r in h3]))):
        r["p_holm"] = q
        r["significant"] = bool(q < alpha) if not np.isnan(q) else False
    rows.extend(h3)
    # --- H4 condition effect
    if set(conditions) >= {"M", "X"}:
        h4 = []
        for i, m in enumerate(mechs):
            d = pu[pu.mechanism == m].set_index("genuine_uuid")
            r = paired_test(d["M_ania_median"].values, d["X_ania_median"].values, reps, seed + 3000 + i)
            h4.append({"family": "H4_context_matching", "outcome": "ania", "outcome_family": "responsiveness",
                       "condition": "M vs X", "comparison": f"{m}: M - X", "mech_a": m, "mech_b": m, **r})
        for r, q in zip(h4, holm(np.array([r["p_value"] for r in h4]))):
            r["p_holm"] = q
            r["significant"] = bool(q < alpha) if not np.isnan(q) else False
        rows.extend(h4)
    tests = pd.DataFrame(rows)
    cols = ["family", "outcome", "outcome_family", "condition", "comparison", "mech_a", "mech_b", "n_users",
            "median_a", "median_b", "median_diff", "ci_lo", "ci_hi", "n_a_lower", "n_b_lower", "n_ties",
            "statistic", "p_value", "p_holm", "significant", "rank_biserial", "kendalls_w", "nemenyi_cd"]
    return tests.reindex(columns=cols), pd.DataFrame(rank_rows)


def mechanism_summary(cfg, pu: pd.DataFrame, conditions: list) -> pd.DataFrame:
    """Median across users (+ bootstrap CI) of each participant-level outcome, per mechanism."""
    reps = int(cfg["stats"]["bootstrap_reps"])
    seed = int(cfg["experiment"]["seed"])
    rows = []
    for (tname, part, m), d in pu.groupby(["target_name", "partition", "mechanism"], sort=False):
        row = {"target_name": tname, "partition": part, "mechanism": m, "params_str": d.params_str.iloc[0],
               "n_users": int(d.genuine_uuid.nunique())}
        # pooled counts (security)
        row["genuine_hours"] = float(d.genuine_hours.sum())
        row["false_locks"] = int(d.locks.sum())
        row["false_locks_per_hour_pooled"] = float(d.locks.sum() / d.genuine_hours.sum())
        row["fr_frames"] = int(d.locked_frames.sum())
        row["frr_time_pooled"] = float(d.locked_frames.sum() / d.frames.sum())
        for c in conditions:
            row[f"{c}_fa_frames"] = int(d[f"{c}_fa_frames"].sum())
            row[f"{c}_impostor_frames"] = int(d[f"{c}_impostor_frames"].sum())
            row[f"{c}_far_frame_pooled"] = float(d[f"{c}_fa_frames"].sum() / d[f"{c}_impostor_frames"].sum())
        for key, tmpl, *_ in OUTCOMES:
            for c in (conditions if "{c}" in tmpl else [None]):
                col = tmpl.format(c=c) if c else tmpl
                x = d[col].values.astype(float)
                lo, hi = bootstrap_median_ci(x, reps, user_seed(seed, "boot", tname, part, m, col))
                row[f"{col}__median"] = float(np.nanmedian(x)) if np.any(~np.isnan(x)) else np.nan
                row[f"{col}__ci_lo"], row[f"{col}__ci_hi"] = lo, hi
                row[f"{col}__mean"] = float(np.nanmean(x)) if np.any(~np.isnan(x)) else np.nan
        rows.append(row)
    return pd.DataFrame(rows)
