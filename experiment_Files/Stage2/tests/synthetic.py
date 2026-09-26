"""Synthetic ExtraSensory-shaped participant files for end-to-end tests (no real data needed).

Each participant has a distinct mean in the phone-motion features (identity signal) plus noise,
~60 s cadence with occasional long gaps (session breaks) and blocks of context labels."""
import gzip
import uuid as _uuid
from pathlib import Path

import numpy as np
import pandas as pd

CONTEXT = ["label:SITTING", "label:LYING_DOWN", "label:FIX_walking", "label:FIX_running", "label:OR_standing",
           "label:PHONE_IN_POCKET", "label:PHONE_IN_HAND", "label:PHONE_ON_TABLE", "label:IN_A_CAR",
           "label:LOC_home", "label:LOC_main_workplace"]
FEATS = [f"raw_acc:magnitude_stats:f{i}" for i in range(4)] + [f"proc_gyro:3d:f{i}" for i in range(3)] + \
        ["location:alt", "discrete:app_state:is_active", "discrete:time_of_day:between0and6"]


def make_dataset(out_dir: Path, n_users: int = 12, n_frames: int = 900, seed: int = 0, irregular: int = 1):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    ids = []
    for u in range(n_users):
        uid = str(_uuid.UUID(int=rng.integers(0, 2**63) << 64 | u)).upper()
        ids.append(uid)
        gaps = np.full(n_frames - 1, 60.0) + rng.integers(-1, 2, n_frames - 1)
        if u < irregular:                                   # fragmented-cadence participant
            gaps = rng.choice([20.0, 60.0, 300.0], size=n_frames - 1)
        br = rng.choice(np.arange(20, n_frames - 1), size=6, replace=False)
        gaps[br] = rng.integers(600, 7200, size=6)          # session breaks
        ts = 1_440_000_000 + np.concatenate([[0], np.cumsum(gaps)]).astype(np.int64)
        centre = rng.normal(scale=1.5, size=7)
        X = centre + rng.normal(scale=1.0, size=(n_frames, 7))
        df = pd.DataFrame(X, columns=FEATS[:7])
        df.insert(0, "timestamp", ts)
        df["location:alt"] = rng.normal(size=n_frames)
        df["discrete:app_state:is_active"] = rng.integers(0, 2, n_frames).astype(float)
        df["discrete:time_of_day:between0and6"] = 0.0
        df.loc[rng.random(n_frames) < 0.05, FEATS[4:7]] = np.nan
        ctx = np.repeat(rng.integers(0, len(CONTEXT), size=n_frames // 30 + 1), 30)[:n_frames]
        for j, c in enumerate(CONTEXT):
            v = (ctx == j).astype(float)
            v[rng.random(n_frames) < 0.2] = np.nan
            df[c] = v
        df["label_source"] = 2
        with gzip.open(out_dir / f"{uid}.features_labels.csv.gz", "wt") as f:
            df.to_csv(f, index=False)
    return ids


def synthetic_overrides(data_dir: Path, root: Path, n_users: int = 12) -> dict:
    return {
        "experiment": {"label": "synthetic", "status": "pilot"},
        "data": {"dir": str(data_dir), "expected_participants": n_users, "auto_download": False},
        "paths": {"results_root": str(root / "results"), "work_root": str(root / "work")},
        "cohort": {"min_period_frames": 60},
        "benchmark": {"L_frames": [3, 10], "sequences_per_L": 2, "prefix_cap": 30, "suffix_cap": 15},
        "classifier": {"params": {"max_iter": 30}},
        "mechanisms": {"theta_grid": {"n": 41},
                       "grids": {"moving_average": {"k": [2, 5]}, "ewma": {"alpha": [0.2, 0.5]},
                                 "majority_vote": {"k": [3, 5]}, "debounce": {"T": [2, 3]}, "margin": {"m": [0.1, 0.2]},
                                 "hysteresis": {"m": [0.1, 0.2], "T": [2, 3]}, "trust": {"r": [0.2, 0.5], "tau": [0.3]},
                                 "sprt": {"alpha": [0.01, 0.1], "beta": {"log10_min": -6, "log10_max": -0.31, "n": 20}},
                                 "hmm": {"rho": [0.01, 0.1]}}},
        "operating_point": {"primary_target": 1.0, "sensitivity_targets": [2.0]},
        "stats": {"bootstrap_reps": 100},
    }
