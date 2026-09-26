"""Command line entry point.

    python -m ca_stability.cli --config configs/main.yaml                # full run (resumable)
    python -m ca_stability.cli --config configs/pilot.yaml --until select
    python -m ca_stability.cli --config configs/main.yaml --force report # redo one stage
"""
from __future__ import annotations

import argparse
import sys

from .config import load_config
from .pipeline import STAGES, run_pipeline


def main(argv=None):
    ap = argparse.ArgumentParser(description="Stage 2 mechanism comparison (continuous authentication)")
    ap.add_argument("--config", required=True, help="YAML config (relative paths resolve against Stage2/)")
    ap.add_argument("--until", choices=STAGES, help="stop after this stage")
    ap.add_argument("--force", nargs="*", default=[], help=f"stages to recompute ('all' or any of {STAGES})")
    ap.add_argument("--label", help="override experiment.label (results/<label>/)")
    ap.add_argument("--data-dir", help="override data directory (else $CA_DATA_DIR or Stage2/data/raw)")
    a = ap.parse_args(argv)
    over = {}
    if a.label:
        over.setdefault("experiment", {})["label"] = a.label
    if a.data_dir:
        over.setdefault("data", {})["dir"] = a.data_dir
    cfg = load_config(a.config, over or None)
    try:
        run_pipeline(cfg, until=a.until, force=a.force)
    except Exception as exc:  # classified + logged to results/<label>/failures.json by the pipeline
        print(f"\nFAILED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
