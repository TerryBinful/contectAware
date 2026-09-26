#!/usr/bin/env python3
"""Run the Stage 2 pipeline without installing the package:  python scripts/run_experiment.py --config configs/main.yaml"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ca_stability.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
