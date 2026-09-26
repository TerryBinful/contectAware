"""Stage A — dataset audit (outcome-blind). Uses the repository's own cadence checker
(`experiment_Files/05_cadence_check.py`) rather than a second implementation."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

from .config import REPO_ROOT
from .data import (all_columns, assign_periods, assign_runs, feature_columns, label_columns,
                   participant_id, select_feature_columns)
from .mdtable import df_to_markdown
from .provenance import LOG, write_json

CADENCE_SCRIPT = REPO_ROOT / "experiment_Files" / "05_cadence_check.py"
STAGE1_IMPORTANCE = REPO_ROOT / "experiment_Files" / "Stage1" / "results" / "repro_rf_feature_importance.csv"

GROUPS = [  # (prefix, category, behavioural?, note)
    ("raw_acc", "phone_motion", True, "phone accelerometer; 3d:mean_* also encode resting orientation/placement"),
    ("proc_gyro", "phone_motion", True, "phone gyroscope (absent on some phone models -> device cue)"),
    ("raw_magnet", "magnetometer", False, "orientation + ambient magnetic environment (place-dependent)"),
    ("watch_acceleration", "watch_motion", False, "wrist motion; missing whenever no watch was worn (37% of rows) -> device-availability cue"),
    ("watch_heading", "watch_heading", False, "compass heading; place/orientation"),
    ("location_quick_features", "location", False, "GPS-derived; Stage 1 shortcut group"),
    ("location", "location", False, "GPS-derived; altitude alone carried 26% of Stage 1 importance"),
    ("audio_naive", "audio_ambient", False, "ambient sound MFCC; environment"),
    ("audio_properties", "audio_ambient", False, "ambient sound level; environment"),
    ("discrete:time_of_day", "time_of_day", False, "clock time; routine/context cue, not identity evidence"),
    ("discrete", "device_state", False, "app/battery/ringer/wifi/call state and explicit *:missing flags"),
    ("lf_measurements", "environment_device", False, "light, pressure, humidity, temperature, battery level, screen"),
]


def load_cadence_module():
    spec = importlib.util.spec_from_file_location("cadence_check", CADENCE_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def classify_feature(col: str):
    for prefix, cat, beh, note in GROUPS:
        if col.startswith(prefix):
            return prefix.split(":")[0] if prefix != "discrete:time_of_day" else "discrete:time_of_day", cat, beh, note
    return "other", "other", False, ""


def run_dataset_audit(cfg: dict, files: list[Path], out_dir: Path) -> dict:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    cad = load_cadence_module()

    cols = all_columns(files)
    feats = feature_columns(cols)
    labs = label_columns(cols)
    assert not any(c.startswith("label") for c in feats), "a label column leaked into the feature list"

    # ---------------------------------------------------------------- per-file pass
    cadence_results, miss_rows, lab_rows, ts_frames = [], [], [], []
    col_missing = np.zeros(len(feats))
    per_user_col_missing = []
    n_total = 0
    group_prefixes = [g[0] for g in GROUPS]
    for f in files:
        uid = participant_id(f)
        d = pd.read_csv(f)
        n = len(d)
        n_total += n
        cadence_results.append(cad.analyse(timestamps=d["timestamp"].values, label=uid))
        na = d[feats].isna()
        col_missing += na.sum(axis=0).values
        per_user_col_missing.append(na.mean(axis=0).values)
        row = {"uuid": uid, "n_frames": n, "cell_missing_frac": float(na.values.mean())}
        for prefix in group_prefixes:
            gcols = [c for c in feats if c.startswith(prefix) and not
                     (prefix == "discrete" and c.startswith("discrete:time_of_day"))]
            if gcols:
                row[f"{prefix}__all_missing"] = float(na[gcols].all(axis=1).mean())
                row[f"{prefix}__any_missing"] = float(na[gcols].any(axis=1).mean())
        miss_rows.append(row)
        L = d[labs].fillna(0)
        lab_rows.append({"uuid": uid, "frac_frames_any_label": float((L.sum(axis=1) > 0).mean()),
                         **{c: float(L[c].mean()) for c in cfg["benchmark"]["context_labels"] if c in L}})
        ts_frames.append(pd.DataFrame({"uuid": uid, "timestamp": d["timestamp"].astype(np.int64).values}))

    # ---------------------------------------------------------------- cadence (05 script)
    summ = cad.summarise(cadence_results)
    write_json(summ, out_dir / "cadence_summary.json")
    cad_df = pd.DataFrame(summ["per_participant"])
    cad_df.to_csv(out_dir / "cadence_summary.csv", index=False)
    dt = float(summ["pooled_median_gap_s"])
    gap_break = cfg["cadence"]["gap_break_factor"] * dt
    lo, hi = cfg["cadence"]["regular_band_s"]

    # ---------------------------------------------------------------- feature inventory
    stage1 = pd.read_csv(STAGE1_IMPORTANCE) if STAGE1_IMPORTANCE.exists() else None
    if stage1 is not None:
        stage1 = stage1.sort_values("importance", ascending=False).reset_index(drop=True)
        cum = stage1["importance"].cumsum()
        n95 = int((cum >= 0.95).values.argmax() + 1)
        s1_valid = set(stage1.feature)
        s1_sel = set(stage1.feature.head(n95))
    else:
        s1_valid = s1_sel = set()
    primary_cols = set(select_feature_columns(cols, cfg))
    s1_pool_prefixes = cfg["features"]["sets"].get("original_pool", [])
    inv = []
    per_user_mat = np.vstack(per_user_col_missing)
    for j, c in enumerate(feats):
        grp, cat, beh, note = classify_feature(c)
        inv.append({
            "feature": c, "group": grp, "category": cat, "behavioural_candidate": beh,
            "explicit_missingness_flag": c.endswith(":missing"),
            "pooled_missing_frac": col_missing[j] / n_total,
            "median_participant_missing_frac": float(np.median(per_user_mat[:, j])),
            "n_participants_fully_missing": int((per_user_mat[:, j] >= 0.999).sum()),
            "in_stage1_pool": any(c.startswith(p) for p in s1_pool_prefixes),
            "in_stage1_valid_101": c in s1_valid,
            "in_stage1_selected": c in s1_sel,
            "in_primary_set": c in primary_cols,
            "note": note,
        })
    inv = pd.DataFrame(inv)
    inv.to_csv(out_dir / "feature_inventory.csv", index=False)
    grp_summary = (inv.groupby("category")
                   .agg(n_features=("feature", "size"),
                        pooled_missing_mean=("pooled_missing_frac", "mean"),
                        in_stage1_selected=("in_stage1_selected", "sum"),
                        in_primary=("in_primary_set", "sum")).reset_index())
    grp_summary.to_csv(out_dir / "feature_groups_summary.csv", index=False)

    miss = pd.DataFrame(miss_rows)
    miss.to_csv(out_dir / "missingness_by_group.csv", index=False)
    labels = pd.DataFrame(lab_rows)
    labels.to_csv(out_dir / "label_coverage.csv", index=False)

    # ---------------------------------------------------------------- eligibility
    ts = pd.concat(ts_frames, ignore_index=True).sort_values(["uuid", "timestamp"], kind="mergesort").reset_index(drop=True)
    ts["period"] = assign_periods(ts, cfg["periods"]["fractions"], cfg["periods"]["embargo_minutes"]).values
    ts["run"] = assign_runs(ts, gap_break).values
    runs = ts.groupby(["uuid", "period", "run"]).size().rename("length").reset_index()
    min_stream = cfg["benchmark"]["min_stream_frames"]
    elig = cad_df[["participant", "n_frames", "median_gap_s", "frac_gap_59_61", "n_runs",
                   "run_len_frames_median"]].rename(columns={"participant": "uuid"})
    elig["regular_cadence"] = elig["frac_gap_59_61"] >= cfg["cadence"]["regular_min_fraction"]
    for per in ("train", "val", "test", "embargo"):
        elig[f"frames_{per}"] = elig.uuid.map(ts[ts.period == per].groupby("uuid").size()).fillna(0).astype(int)
    for per in ("val", "test"):
        r = runs[(runs.period == per) & (runs.length >= min_stream)]
        elig[f"stream_frames_{per}"] = elig.uuid.map(r.groupby("uuid").length.sum()).fillna(0).astype(int)
        elig[f"n_streams_{per}"] = elig.uuid.map(r.groupby("uuid").size()).fillna(0).astype(int)
        elig[f"max_stream_{per}"] = elig.uuid.map(r.groupby("uuid").length.max()).fillna(0).astype(int)
    elig = elig.merge(miss[["uuid", "proc_gyro__all_missing", "raw_acc__all_missing"]], on="uuid", how="left")
    mpf = cfg["cohort"]["min_period_frames"]
    reasons = []
    for _, r in elig.iterrows():
        why = []
        if cfg["cohort"]["mode"] == "regular" and not r.regular_cadence:
            why.append(f"irregular cadence ({r.frac_gap_59_61:.2f} of gaps in {lo}-{hi}s)")
        if r.stream_frames_val < mpf:
            why.append(f"val stream frames {r.stream_frames_val} < {mpf}")
        if r.stream_frames_test < mpf:
            why.append(f"test stream frames {r.stream_frames_test} < {mpf}")
        if r.max_stream_val < 2 * cfg["benchmark"]["W"] + 1 or r.max_stream_test < 2 * cfg["benchmark"]["W"] + 1:
            why.append("no stream long enough to host a splice")
        reasons.append("; ".join(why))
    elig["exclusion_reason"] = reasons
    elig["eligible"] = elig["exclusion_reason"] == ""
    elig.to_csv(out_dir / "eligibility.csv", index=False)

    summary = {
        "n_participants": len(files),
        "n_frames": int(n_total),
        "n_feature_columns": len(feats),
        "n_label_columns": len(labs),
        "pooled_median_gap_s": dt,
        "pooled_mean_gap_s": summ["pooled_mean_gap_s"],
        "pooled_iqr_gap_s": summ["pooled_iqr_s"],
        "pooled_frac_gap_59_61": summ["pooled_frac_gap_59_61"],
        "frame_period_s_used": dt,
        "run_break_gap_s": gap_break,
        "n_regular_cadence": int(elig.regular_cadence.sum()),
        "n_fragmented_cadence": int((~elig.regular_cadence).sum()),
        "regular_fraction_gap_59_61_min": float(elig.loc[elig.regular_cadence, "frac_gap_59_61"].min()),
        "fragmented_fraction_gap_59_61_max": float(elig.loc[~elig.regular_cadence, "frac_gap_59_61"].max())
        if (~elig.regular_cadence).any() else None,
        "n_eligible": int(elig.eligible.sum()),
        "n_excluded": int((~elig.eligible).sum()),
        "cell_missing_mean_over_participants": float(miss.cell_missing_frac.mean()),
        "primary_feature_set": cfg["features"]["set"],
        "n_primary_features": int(inv.in_primary_set.sum()),
        "participants_without_gyroscope": miss.loc[miss["proc_gyro__all_missing"] > 0.99, "uuid"].tolist(),
    }
    write_json(summary, out_dir / "dataset_summary.json")
    _write_report(out_dir, summary, elig, grp_summary, cfg)
    LOG.info("Dataset audit: %d participants, median gap %.1fs, %d regular, %d eligible",
             len(files), dt, summary["n_regular_cadence"], summary["n_eligible"])
    return summary


def _write_report(out_dir: Path, s: dict, elig: pd.DataFrame, grp: pd.DataFrame, cfg: dict):
    lo, hi = cfg["cadence"]["regular_band_s"]
    lines = [
        "# Dataset audit report (auto-generated — do not edit by hand)",
        "",
        "## Observed facts (computed from the participant files in this run)",
        f"- Participants: {s['n_participants']}; frames: {s['n_frames']:,}; feature columns: {s['n_feature_columns']}; label columns: {s['n_label_columns']}.",
        f"- Pooled median inter-frame gap: {s['pooled_median_gap_s']:.1f} s (IQR {s['pooled_iqr_gap_s'][0]:.1f}-{s['pooled_iqr_gap_s'][1]:.1f} s; mean {s['pooled_mean_gap_s']:.1f} s).",
        f"- Share of gaps within {lo}-{hi} s: {s['pooled_frac_gap_59_61']:.3f}.",
        f"- Participants with >= {cfg['cadence']['regular_min_fraction']:.0%} of gaps in {lo}-{hi} s (regular): {s['n_regular_cadence']}; others (fragmented): {s['n_fragmented_cadence']}.",
        f"- Lowest regular-participant share: {s['regular_fraction_gap_59_61_min']:.3f}; highest fragmented-participant share: {s['fragmented_fraction_gap_59_61_max']}.",
        f"- Participants whose phone reports no gyroscope at all: {', '.join(p[:8] for p in s['participants_without_gyroscope']) or 'none'}.",
        f"- Mean (over participants) cell-level missingness over all features: {s['cell_missing_mean_over_participants']:.3f}.",
        "",
        "## Derived quantities",
        f"- Frame period used for all conversions: {s['frame_period_s_used']:.0f} s (1 frame = 1 decision ~ 1 minute).",
        f"- A contiguous run breaks where a gap exceeds {s['run_break_gap_s']:.0f} s (= {cfg['cadence']['gap_break_factor']} x frame period).",
        f"- Eligible genuine participants for the '{cfg['cohort']['mode']}' cohort: {s['n_eligible']}; excluded: {s['n_excluded']} (reasons in eligibility.csv).",
        "",
        "## Feature groups",
        "",
        df_to_markdown(grp),
        "",
        "## Assumptions",
        "- One ExtraSensory example (a 20-s recording, nominally once per minute) is one decision frame.",
        "- Frames inside a run are treated as consecutive decisions; temporal parameters are in frames.",
        "- Gaps above the run-break threshold end a session; every mechanism restarts in AUTH at a new run.",
        "",
        "## Limitations",
        "- Decision cadence is ~1/min; nothing here supports claims about sub-minute responsiveness.",
        "- Fragmented-cadence participants have frames that are not 60 s apart; they are excluded from the primary cohort.",
        "- Labels are self-reported and sparse; they are used only to align context-matched impostor blocks, never as features.",
    ]
    (out_dir / "DATASET_AUDIT_REPORT.md").write_text("\n".join(lines) + "\n")
