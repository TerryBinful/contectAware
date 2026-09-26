#!/usr/bin/env python3
"""Reproducibility check: re-run a configuration from scratch (fresh work dir, new results label)
and require EXACT equality of every scientific output with the original run.

    python scripts/check_reproducibility.py --config configs/pilot.yaml

Timing fields (fit_seconds, wall_s, *_utc) and logs/figures are excluded from the comparison.
Writes results/<label>/reproducibility_check.json. Exit code 1 on any difference (REPRODUCIBILITY).
"""
import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ca_stability.config import load_config, resolve_paths  # noqa: E402
from ca_stability.pipeline import run_pipeline  # noqa: E402
from ca_stability.provenance import utcnow, write_json  # noqa: E402

VOLATILE = ("fit_seconds", "wall_s", "utc", "generated", "finished")
COMPARE = ["participant_split.json", "dataset_audit/eligibility.csv", "dataset_audit/feature_inventory.csv",
           "baseline/exp1_per_user_classifier_metrics.csv", "baseline/exp1_summary.json", "baseline/exp1_reliability_test.csv",
           "benchmark/manifest.csv", "benchmark/genuine_streams.csv", "benchmark/coverage.json", "benchmark/leakage_checks.json",
           "benchmark/densities.json", "benchmark/sanity_checks.json", "benchmark/genuine_stream_scores.parquet",
           "benchmark/sequence_scores.parquet", "sweeps/sweep_val.csv", "sweeps/sweep_test.csv", "operating_points.csv",
           "participant_metrics.csv", "sequence_metrics.csv", "transition_metrics.csv", "mechanism_metrics.csv",
           "statistical_tests.csv", "friedman_ranks.csv"]


def _strip(o):
    if isinstance(o, dict):
        return {k: _strip(v) for k, v in o.items() if not any(t in k for t in VOLATILE)}
    if isinstance(o, list):
        return [_strip(v) for v in o]
    return o


def same(a: Path, b: Path) -> tuple[bool, str]:
    if not a.exists() or not b.exists():
        return False, f"missing ({a.exists()}, {b.exists()})"
    if a.suffix == ".json":
        return (_strip(json.loads(a.read_text())) == _strip(json.loads(b.read_text()))), ""
    da = pd.read_csv(a) if a.suffix == ".csv" else pd.read_parquet(a)
    db = pd.read_csv(b) if b.suffix == ".csv" else pd.read_parquet(b)
    drop = [c for c in da.columns if any(t in c for t in VOLATILE)]
    try:
        pd.testing.assert_frame_equal(da.drop(columns=drop), db.drop(columns=drop, errors="ignore"), check_exact=True)
        return True, ""
    except AssertionError as e:
        return False, str(e).splitlines()[0][:200]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--keep", action="store_true", help="keep the re-run's results directory")
    a = ap.parse_args()
    cfg = load_config(a.config)
    orig = resolve_paths(cfg)["results"]
    label = cfg["experiment"]["label"] + "_repro"
    tmp_work = Path(tempfile.mkdtemp(prefix="ca_repro_work_"))
    cfg2 = load_config(a.config, {"experiment": {"label": label}, "paths": {"work_root": str(tmp_work)}})
    r = run_pipeline(cfg2)
    rows, ok = [], True
    for rel in COMPARE:
        if not (orig / rel).exists():
            continue
        eq, why = same(orig / rel, r.res / rel)
        ok &= eq
        rows.append({"file": rel, "identical": eq, "detail": why})
    out = {"checked_utc": utcnow(), "config": a.config, "original": str(orig), "rerun_label": label,
           "all_identical": bool(ok), "files": rows,
           "excluded": "timing fields, logs, figures, experiment_metadata.json, stage markers"}
    write_json(out, orig / "reproducibility_check.json")
    shutil.rmtree(tmp_work, ignore_errors=True)
    if not a.keep:
        shutil.rmtree(r.res, ignore_errors=True)
    print(json.dumps({k: v for k, v in out.items() if k != "files"}, indent=2))
    for x in rows:
        if not x["identical"]:
            print("DIFFERS:", x)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
