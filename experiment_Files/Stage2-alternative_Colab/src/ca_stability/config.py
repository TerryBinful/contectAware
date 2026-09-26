"""Configuration loading. YAML files may `extends:` another file; values are deep-merged."""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path

import yaml

STAGE2_ROOT = Path(__file__).resolve().parents[2]          # .../experiment_Files/Stage2
REPO_ROOT = STAGE2_ROOT.parents[1]                          # repository root


def _deep_merge(base: dict, over: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def load_config(path: str | os.PathLike, overrides: dict | None = None) -> dict:
    path = Path(path)
    if not path.is_absolute() and not path.exists():
        path = STAGE2_ROOT / path
    with open(path) as f:
        cfg = yaml.safe_load(f) or {}
    parent = cfg.pop("extends", None)
    if parent:
        base = load_config(path.parent / parent)
        cfg = _deep_merge(base, cfg)
    if overrides:
        cfg = _deep_merge(cfg, overrides)
    cfg.setdefault("_meta", {})["config_path"] = str(path)
    return cfg


def config_hash(cfg: dict) -> str:
    clean = {k: v for k, v in cfg.items() if not k.startswith("_")}
    return hashlib.sha256(json.dumps(clean, sort_keys=True, default=str).encode()).hexdigest()[:16]


def resolve_paths(cfg: dict) -> dict:
    """Absolute results/work/data directories for this run."""
    label = cfg["experiment"]["label"]
    res_root = Path(cfg["paths"]["results_root"])
    work_root = Path(cfg["paths"]["work_root"])
    if not res_root.is_absolute():
        res_root = STAGE2_ROOT / res_root
    if not work_root.is_absolute():
        work_root = Path(os.environ.get("CA_WORK_DIR", STAGE2_ROOT / work_root))
    data_dir = cfg["data"].get("dir") or os.environ.get("CA_DATA_DIR") or (STAGE2_ROOT / "data" / "raw")
    paths = {
        "results": res_root / label,
        "work": work_root / label,
        "data": Path(data_dir),
        "cache": work_root / "_shared_cache",
    }
    for key in ("results", "work", "cache"):
        paths[key].mkdir(parents=True, exist_ok=True)
    return paths


def theta_grid(cfg: dict):
    import numpy as np
    g = cfg["mechanisms"]["theta_grid"]
    z = np.linspace(g["logit_min"], g["logit_max"], int(g["n"]))
    return 1.0 / (1.0 + np.exp(-z))
