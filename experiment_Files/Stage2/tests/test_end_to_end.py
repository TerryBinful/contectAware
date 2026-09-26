"""Whole pipeline on a synthetic ExtraSensory-shaped dataset, plus leakage-detection tests that
must FAIL when leakage is injected."""
import json

import numpy as np
import pandas as pd
import pytest

from ca_stability.benchmark import leakage_checks
from ca_stability.config import load_config
from ca_stability.pipeline import run_pipeline
from synthetic import make_dataset, synthetic_overrides


@pytest.fixture(scope="module")
def run(tmp_path_factory):
    root = tmp_path_factory.mktemp("e2e")
    make_dataset(root / "data", n_users=12, n_frames=900, seed=5)
    cfg = load_config("configs/main.yaml", synthetic_overrides(root / "data", root))
    return run_pipeline(cfg)


def test_all_outputs_exist(run):
    for rel in ["experiment_metadata.json", "participant_split.json", "operating_points.csv", "operating_points.frozen.json",
                "mechanism_metrics.csv", "participant_metrics.csv", "sequence_metrics.csv", "transition_metrics.csv",
                "statistical_tests.csv", "RESULTS_REPORT.md", "dataset_audit/DATASET_AUDIT_REPORT.md",
                "benchmark/manifest.csv", "benchmark/leakage_checks.json", "sweeps/sweep_val.csv",
                "figures/fig04_outcomes_primary.png", "tables/T5_security.md"]:
        assert (run.res / rel).exists(), rel


def test_cohort_excludes_fragmented_participant(run):
    elig = pd.read_csv(run.res / "dataset_audit" / "eligibility.csv")
    assert (~elig.regular_cadence).sum() == 1
    assert len(run.split["cohort"]) == 11


def test_manifest_schema(run):
    man = pd.read_csv(run.res / "benchmark" / "manifest.csv")
    for c in ["seq_id", "genuine_uuid", "impostor_uuid", "condition", "L_min", "L_frames", "splice_idx", "return_idx",
              "dominant_label_g", "dominant_label_i", "seed", "partition"]:
        assert c in man.columns
    m = man[man.condition == "M"]
    assert (m.dominant_label_g == m.dominant_label_i).all()


def test_leakage_checks_pass_on_clean_run(run):
    assert json.loads((run.res / "benchmark" / "leakage_checks.json").read_text())["all_passed"]


def _inputs(run):
    streams, man, cov, gen_long, seq_long = run.bench_tables()
    return run.cfg, run.frames, run.split, streams, man, seq_long, gen_long


def test_leakage_detected_training_impostor(run):
    cfg, frames, split, streams, man, seq_long, gen_long = _inputs(run)
    man = man.copy()
    g = man.genuine_uuid.iloc[0]
    man.loc[0, "impostor_uuid"] = split["roles"][g]["impostor_train"][0]
    res = leakage_checks(cfg, frames, split, streams, man, seq_long, gen_long)
    assert not res["impostor_is_unseen_and_role_correct"]["passed"] and not res["all_passed"]


def test_leakage_detected_training_frame(run):
    cfg, frames, split, streams, man, seq_long, gen_long = _inputs(run)
    seq_long = seq_long.copy()
    g = man.genuine_uuid.iloc[0]
    train_row = int(np.flatnonzero((frames.uuid.values == g) & (frames.period.values == "train"))[-1])
    i = seq_long.index[seq_long.seq_id == man.seq_id.iloc[0]][0]
    seq_long.loc[i, "row"] = train_row
    res = leakage_checks(cfg, frames, split, streams, man, seq_long, gen_long)
    assert not res["no_training_frame_in_evaluation"]["passed"] and not res["period_purity"]["passed"]


def test_evaluate_refuses_modified_operating_points(run):
    from ca_stability.pipeline import stage_evaluate
    p = run.res / "operating_points.csv"
    original = p.read_text()
    try:
        p.write_text(original.replace("primary", "primary ", 1))
        run.force = {"evaluate"}
        with pytest.raises(RuntimeError, match="REPRODUCIBILITY"):
            stage_evaluate(run)
    finally:
        p.write_text(original)
        run.force = set()


def test_operating_points_selected_on_validation_only(run):
    ops = pd.read_csv(run.res / "operating_points.csv")
    cells = pd.read_csv(run.res / "sweeps" / "sweep_val.csv")
    assert set(ops.cell_id) <= set(cells.cell_id)
    assert ops.mechanism.nunique() == 10
