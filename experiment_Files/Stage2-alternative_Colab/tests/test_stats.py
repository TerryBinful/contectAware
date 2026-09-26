import numpy as np
import pandas as pd

from ca_stability.stats import bootstrap_median_ci, holm, paired_test, rank_biserial


def test_holm_matches_textbook():
    p = np.array([0.01, 0.04, 0.03, 0.005])
    assert np.allclose(holm(p), [0.03, 0.06, 0.06, 0.02])
    assert np.isnan(holm(np.array([np.nan, 0.01]))[0])


def test_rank_biserial_extremes():
    assert rank_biserial(np.array([1.0, 2.0, 3.0])) == 1.0
    assert rank_biserial(np.array([-1.0, -2.0])) == -1.0
    assert rank_biserial(np.array([0.0, 0.0])) == 0.0


def test_paired_identical_is_null():
    x = np.arange(10, dtype=float)
    r = paired_test(x, x.copy(), 200, 0)
    assert r["p_value"] == 1.0 and r["median_diff"] == 0.0 and r["n_ties"] == 10


def test_paired_detects_consistent_shift_and_drops_nan():
    rng = np.random.default_rng(0)
    a = rng.normal(size=30)
    b = a + 1.0 + rng.normal(scale=0.1, size=30)
    a[0] = np.nan
    r = paired_test(a, b, 500, 1)
    assert r["n_users"] == 29 and r["p_value"] < 1e-4 and r["rank_biserial"] == -1.0 and r["ci_hi"] < 0


def test_bootstrap_deterministic():
    x = np.random.default_rng(3).normal(size=40)
    assert bootstrap_median_ci(x, 300, 7) == bootstrap_median_ci(x, 300, 7)
