"""Mechanism registry: families, parameter grids and the swept parameter for each mechanism.

Each mechanism is evaluated as a set of COMBOS (fixed parameters) x a SWEEP vector (the
parameter that moves the operating point, normally the score threshold theta). The operating
point procedure (operating_point.py) picks one (combo, sweep value) per mechanism.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field

import numpy as np

from ..config import theta_grid
from .batch import BATCH
from .reference import REFERENCE

FAMILY = {
    "threshold": "memoryless baseline",
    "moving_average": "score smoothing (window)",
    "ewma": "score smoothing (exponential)",
    "majority_vote": "decision smoothing (window vote)",
    "debounce": "decision persistence (dwell / TTT only)",
    "margin": "state-dependent thresholds (margin only)",
    "hysteresis": "margin + dwell (handover-style hysteresis)",
    "trust": "bounded evidence accumulation (trust model)",
    "sprt": "sequential test (Wald SPRT with restart)",
    "hmm": "Bayesian filter (2-state HMM) — supplementary",
}
LABEL = {"threshold": "Threshold", "moving_average": "Moving avg", "ewma": "EWMA", "majority_vote": "Majority vote",
         "debounce": "Debounce", "margin": "Margin", "hysteresis": "Hysteresis", "trust": "Trust",
         "sprt": "SPRT", "hmm": "HMM (supp.)"}
ORDER = ["threshold", "moving_average", "ewma", "majority_vote", "debounce", "margin", "hysteresis", "trust", "sprt", "hmm"]


@dataclass
class MechanismSpec:
    name: str
    sweep_name: str
    sweep_values: np.ndarray
    combos: list = field(default_factory=list)       # list of dicts of fixed params
    needs_density: bool = False

    @property
    def batch(self):
        return BATCH[self.name]

    @property
    def reference(self):
        return REFERENCE[self.name]

    @property
    def family(self):
        return FAMILY[self.name]

    @property
    def label(self):
        return LABEL[self.name]

    def n_cells(self):
        return len(self.combos) * len(self.sweep_values)


def _product(grid: dict) -> list[dict]:
    if not grid:
        return [{}]
    keys = list(grid)
    return [dict(zip(keys, vals)) for vals in itertools.product(*(grid[k] for k in keys))]


def build_specs(cfg: dict, names=None) -> dict[str, MechanismSpec]:
    th = theta_grid(cfg)
    g = cfg["mechanisms"]["grids"]
    names = names or (cfg["mechanisms"]["primary_set"] + cfg["mechanisms"].get("supplementary_set", []))
    specs = {}
    for nm in names:
        if nm == "threshold":
            specs[nm] = MechanismSpec(nm, "theta", th, [{}])
        elif nm in ("moving_average", "ewma", "majority_vote", "debounce", "margin", "hysteresis", "trust"):
            specs[nm] = MechanismSpec(nm, "theta", th, _product(g[nm]))
        elif nm == "sprt":
            b = g["sprt"]["beta"]
            betas = np.logspace(b["log10_min"], b["log10_max"], int(b["n"]))
            specs[nm] = MechanismSpec(nm, "beta", betas, _product({"alpha": g["sprt"]["alpha"]}), needs_density=True)
        elif nm == "hmm":
            specs[nm] = MechanismSpec(nm, "theta", th, _product(g["hmm"]), needs_density=True)
        else:
            raise ValueError(f"unknown mechanism {nm}")
    return specs


def params_string(name: str, combo: dict, sweep_name: str, value: float) -> str:
    parts = [f"{k}={v:g}" if isinstance(v, (int, float)) else f"{k}={v}" for k, v in combo.items()]
    parts.append(f"{sweep_name}={value:.4g}")
    return ", ".join(parts)
