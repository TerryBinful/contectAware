"""Stage B — participant split.

For every genuine user g the other cohort members are partitioned into three DISJOINT roles:

    impostor_train(g) : their TRAIN-period frames are negatives when fitting g's model
    impostor_cal(g)   : their VAL-period frames provide unseen impostor blocks for calibration
    impostor_test(g)  : their TEST-period frames provide unseen impostor blocks for the final test

So (i) g's model never sees a calibration or test impostor, (ii) mechanism parameters are never
tuned on a test impostor of the same genuine user, and (iii) because every participant's own
timeline is also split chronologically, no frame is ever used in more than one of
{model training, calibration, test}.
"""
from __future__ import annotations

import hashlib

import numpy as np
import pandas as pd

from .provenance import LOG, write_json


def user_seed(master_seed: int, *parts) -> int:
    h = hashlib.sha256(("|".join([str(master_seed), *map(str, parts)])).encode()).hexdigest()
    return int(h[:8], 16)


def build_split(cfg: dict, eligibility: pd.DataFrame, out_path=None) -> dict:
    seed = int(cfg["experiment"]["seed"])
    elig = eligibility.copy()
    cohort = sorted(elig.loc[elig.eligible, "uuid"].tolist())
    excluded = elig.loc[~elig.eligible, ["uuid", "exclusion_reason"]].to_dict(orient="records")
    if len(cohort) < 8:
        raise RuntimeError(f"METHODOLOGY: only {len(cohort)} eligible participants; need >= 8")

    genuine = list(cohort)
    k = cfg["cohort"].get("max_genuine_users")
    if k:
        rng = np.random.default_rng(user_seed(seed, "pilot-genuine-subset"))
        genuine = sorted(rng.choice(cohort, size=min(int(k), len(cohort)), replace=False).tolist())

    fr = cfg["roles"]
    roles = {}
    for g in genuine:
        others = [u for u in cohort if u != g]
        rng = np.random.default_rng(user_seed(seed, "roles", g))
        perm = [others[i] for i in rng.permutation(len(others))]
        n = len(perm)
        n_tr = int(round(fr["impostor_train"] * n))
        n_cal = int(round(fr["impostor_cal"] * n))
        roles[g] = {
            "impostor_train": sorted(perm[:n_tr]),
            "impostor_cal": sorted(perm[n_tr:n_tr + n_cal]),
            "impostor_test": sorted(perm[n_tr + n_cal:]),
        }
        r = roles[g]
        assert not (set(r["impostor_train"]) & set(r["impostor_cal"]))
        assert not (set(r["impostor_train"]) & set(r["impostor_test"]))
        assert not (set(r["impostor_cal"]) & set(r["impostor_test"]))
        assert g not in set().union(*map(set, r.values()))
        assert min(len(v) for v in r.values()) >= 1, f"empty impostor role for {g}"

    split = {
        "protocol": "open-set: per genuine user, impostor roles are disjoint; chronological periods per participant",
        "master_seed": seed,
        "cohort_mode": cfg["cohort"]["mode"],
        "cohort": cohort,
        "genuine_users": genuine,
        "excluded": excluded,
        "periods": {"fractions": cfg["periods"]["fractions"], "embargo_minutes": cfg["periods"]["embargo_minutes"]},
        "role_fractions": fr,
        "roles": roles,
    }
    if out_path is not None:
        write_json(split, out_path)
    LOG.info("Split: cohort %d, genuine %d, excluded %d", len(cohort), len(genuine), len(excluded))
    return split


def role_table(split: dict) -> pd.DataFrame:
    rows = []
    for g, r in split["roles"].items():
        for role, users in r.items():
            for u in users:
                rows.append({"genuine_uuid": g, "role": role, "uuid": u})
    return pd.DataFrame(rows)
