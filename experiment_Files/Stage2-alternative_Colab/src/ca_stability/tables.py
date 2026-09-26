"""Stage I — tables. Every number is read from a generated file; nothing is typed by hand.
Each table is written as CSV (machine-readable) and Markdown (for the report)."""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from .mdtable import df_to_markdown
from .mechanisms.registry import LABEL, ORDER


def fmt_ci(med, lo, hi, nd=3):
    if med is None or (isinstance(med, float) and np.isnan(med)):
        return "—"
    return f"{med:.{nd}f} [{lo:.{nd}f}, {hi:.{nd}f}]"


def _save(r, name, df, md_df=None):
    out = r.res / "tables"
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / f"{name}.csv", index=False)
    (out / f"{name}.md").write_text(df_to_markdown(md_df if md_df is not None else df) + "\n")
    return df


def _ordered(df, col="mechanism"):
    keys = ["_o"]
    df = df.assign(_o=df[col].map({m: i for i, m in enumerate(ORDER)}))
    if "target_name" in df:
        tord = {t: i for i, t in enumerate(dict.fromkeys(df.target_name))}
        df = df.assign(_t=df.target_name.map(tord))
        keys = ["_t", "_o"]
    return df.sort_values(keys, kind="mergesort").drop(columns=[k for k in keys])


def make_tables(r):
    res = r.res
    ds = json.loads((res / "dataset_audit" / "dataset_summary.json").read_text())
    split = r.split
    ops = pd.read_csv(res / "operating_points.csv")
    sel = ops.selection_condition.iloc[0]
    conds = r.cfg["benchmark"]["conditions"]
    other = [c for c in conds if c != sel]

    # T1 dataset
    t1 = pd.DataFrame([
        ("Participants in archive", ds["n_participants"]), ("Frames (all participants)", ds["n_frames"]),
        ("Feature columns / label columns", f"{ds['n_feature_columns']} / {ds['n_label_columns']}"),
        ("Pooled median inter-frame gap (s)", f"{ds['pooled_median_gap_s']:.1f}"),
        ("Regular-cadence participants (>=80% gaps in 59-61 s)", ds["n_regular_cadence"]),
        ("Fragmented-cadence participants", ds["n_fragmented_cadence"]),
        ("Eligible cohort (genuine and impostor pool)", len(split["cohort"])),
        ("Genuine users evaluated", len(split["genuine_users"])),
        ("Primary feature set", f"{ds['primary_feature_set']} ({ds['n_primary_features']} features)"),
        ("Run break (s)", f"{ds['run_break_gap_s']:.0f}"),
    ], columns=["Quantity", "Value"])
    _save(r, "T1_dataset", t1)

    # T2 split
    b = res / "benchmark"
    streams = pd.read_csv(b / "genuine_streams.csv")
    man = pd.read_csv(b / "manifest.csv")
    fp = r.cfg["_meta"]["frame_period_s"]
    rows = []
    for g in split["genuine_users"]:
        ro = split["roles"][g]
        s = streams[streams.genuine_uuid == g]
        rows.append({"genuine_uuid": g[:8], "impostor_train": len(ro["impostor_train"]), "impostor_cal": len(ro["impostor_cal"]),
                     "impostor_test": len(ro["impostor_test"]),
                     "val_hours": s[s.partition == "val"].length.sum() * fp / 3600,
                     "test_hours": s[s.partition == "test"].length.sum() * fp / 3600,
                     "val_sequences": int(((man.genuine_uuid == g) & (man.partition == "val")).sum()),
                     "test_sequences": int(((man.genuine_uuid == g) & (man.partition == "test")).sum())})
    _save(r, "T2_participant_split", pd.DataFrame(rows))

    # T3 Exp 1
    pu1 = pd.read_csv(res / "baseline" / "exp1_per_user_classifier_metrics.csv")
    cols = [("test_auc", "AUC"), ("test_eer", "EER"), ("test_far_at_0.5", "FAR@0.5"), ("test_frr_at_0.5", "FRR@0.5"),
            ("test_genuine_frac_band_0.4_0.6", "genuine mass in (0.4,0.6)"),
            ("test_impostor_frac_band_0.4_0.6", "impostor mass in (0.4,0.6)"),
            ("test_frac_within_90s_of_train", "test frames within 90 s of a train frame"),
            ("test_transitions_per_hour_at_0.5", "transitions/h at theta=0.5 (genuine test)")]
    t3 = pd.DataFrame([{"metric": lab, "median": pu1[c].median(), "q25": pu1[c].quantile(.25),
                        "q75": pu1[c].quantile(.75), "min": pu1[c].min(), "max": pu1[c].max()} for c, lab in cols])
    _save(r, "T3_exp1_classifier", t3)

    # T4 operating points
    t4 = _ordered(ops)[["target_name", "target_false_locks_per_hour", "mechanism", "params_str", "in_band",
                        "n_in_band_cells", "n_excluded_absorbing", "val_false_locks_per_hour", "val_lockout_mean_frames",
                        "val_ania_median", "val_far_frame", "val_miss_rate", "best_smoother"]]
    _save(r, "T4_operating_points", t4)

    mm = pd.read_csv(res / "mechanism_metrics.csv")
    for tname in ops.target_name.unique():
        m = _ordered(mm[(mm.partition == "test") & (mm.target_name == tname)])
        suffix = "" if tname == "primary" else f"_{tname}"

        def ci(col, nd=3):
            return [fmt_ci(a, b_, c, nd) for a, b_, c in zip(m[f"{col}__median"], m[f"{col}__ci_lo"], m[f"{col}__ci_hi"])]

        sec = pd.DataFrame({"Mechanism": m.mechanism.map(LABEL).values, "Parameters": m.params_str.values,
                            f"FAR_frame {sel} (median [95% CI])": ci(f"{sel}_far_frame"),
                            f"FA frames / impostor frames ({sel})": [f"{a}/{b_}" for a, b_ in zip(m[f"{sel}_fa_frames"], m[f"{sel}_impostor_frames"])],
                            f"Missed blocks {sel}": ci(f"{sel}_miss_rate"),
                            "FRR_time (median [95% CI])": ci("frr_time", 4),
                            "FR frames (pooled)": m.fr_frames.values})
        _save(r, f"T5_security{suffix}", sec)
        stab = pd.DataFrame({"Mechanism": m.mechanism.map(LABEL).values,
                             "False locks / h (median [95% CI])": ci("false_locks_per_hour"),
                             "False locks / h (pooled)": m.false_locks_per_hour_pooled.round(3).values,
                             "False locks (count)": m.false_locks.values,
                             "Transitions / h": ci("transitions_per_hour"),
                             "Ping-pong events / h": ci("pingpong_per_hour"),
                             "Mean false-lock duration (frames)": ci("lockout_mean_frames", 2)})
        _save(r, f"T6_stability{suffix}", stab)
        resp = {"Mechanism": m.mechanism.map(LABEL).values,
                f"Sustained detection {sel} (frames)": ci(f"{sel}_ania_median", 2),
                f"First lock {sel} (frames)": ci(f"{sel}_first_lock_median", 2),
                f"Recovery after return {sel} (frames)": ci(f"{sel}_recovery_median", 2)}
        for c in other:
            resp[f"Sustained detection {c} (frames)"] = ci(f"{c}_ania_median", 2)
            resp[f"Missed blocks {c}"] = ci(f"{c}_miss_rate")
        _save(r, f"T7_responsiveness{suffix}", pd.DataFrame(resp))

    # T8 statistics (primary target)
    st = pd.read_csv(res / "statistical_tests.csv")
    st = st[st.target_name == "primary"]
    om = st[st.family == "omnibus"][["outcome", "n_users", "statistic", "p_value", "kendalls_w", "nemenyi_cd"]]
    _save(r, "T8a_friedman", om)
    keep = st[st.family.isin(["primary", "primary_secondary_outcomes", "H3_component_ablation", "H4_context_matching"])]
    t8b = keep[["family", "outcome", "comparison", "n_users", "median_a", "median_b", "median_diff", "ci_lo", "ci_hi",
                "p_value", "p_holm", "rank_biserial", "significant"]]
    _save(r, "T8b_planned_contrasts", t8b)
    vs = st[st.family == "vs_threshold"][["outcome", "comparison", "n_users", "median_diff", "ci_lo", "ci_hi", "p_holm",
                                          "rank_biserial", "significant"]]
    _save(r, "T8c_vs_threshold", vs)

    # T9 operating-point transfer val -> test
    t9 = []
    for tname in ops.target_name.unique():
        for mech in ORDER:
            a = mm[(mm.target_name == tname) & (mm.mechanism == mech)]
            if a.empty:
                continue
            v, t = a[a.partition == "val"], a[a.partition == "test"]
            t9.append({"target_name": tname, "mechanism": mech,
                       "target": ops[(ops.target_name == tname)].target_false_locks_per_hour.iloc[0],
                       "val_false_locks_per_hour": float(v.false_locks_per_hour_pooled.iloc[0]),
                       "test_false_locks_per_hour": float(t.false_locks_per_hour_pooled.iloc[0]),
                       "test_over_target": float(t.false_locks_per_hour_pooled.iloc[0]) /
                       ops[(ops.target_name == tname)].target_false_locks_per_hour.iloc[0]})
    _save(r, "T9_operating_point_transfer", pd.DataFrame(t9))

    # T10 ANIA / miss by block length (test, primary, selection condition)
    tm = pd.read_csv(res / "transition_metrics.csv")
    tm = tm[(tm.partition == "test") & (tm.target_name == "primary")]
    t10 = (tm.groupby(["mechanism", "condition", "L_frames"])
           .agg(n=("seq_id", "size"), ania_median=("ania", "median"), miss_rate=("miss", "mean"),
                far_frame_mean=("far_frame", "mean"), recovery_median=("recovery", "median")).reset_index())
    _save(r, "T10_by_block_length", _ordered(t10))
