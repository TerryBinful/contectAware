#!/usr/bin/env python3
"""Download + MD5-verify + extract the public ExtraSensory per-participant feature/label archive.

    python scripts/download_data.py [--data-dir DIR]      (default: $CA_DATA_DIR or Stage2/data/raw)
Raw data is never committed (see .gitignore)."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ca_stability.config import load_config, resolve_paths  # noqa: E402
from ca_stability.data import dataset_fingerprint, ensure_dataset  # noqa: E402
from ca_stability.provenance import setup_logging  # noqa: E402

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir")
    ap.add_argument("--config", default="configs/main.yaml")
    a = ap.parse_args()
    setup_logging()
    cfg = load_config(a.config, {"data": {"dir": a.data_dir}} if a.data_dir else None)
    files = ensure_dataset(cfg, resolve_paths(cfg)["data"])
    print(dataset_fingerprint(files))
