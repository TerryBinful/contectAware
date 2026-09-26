"""Histogram score densities for the SPRT and HMM arms (fitted on VALIDATION data only)."""
from __future__ import annotations

import numpy as np


class ScoreDensity:
    """Genuine (f1) and impostor (f0) score densities on [0, 1] as Laplace-smoothed histograms.

    Only the RATIO f1/f0 per bin matters to SPRT/HMM, so bin probabilities are stored.
    """

    def __init__(self, f1_counts, f0_counts):
        f1_counts = np.asarray(f1_counts, dtype=float)
        f0_counts = np.asarray(f0_counts, dtype=float)
        self.nb = len(f1_counts)
        self.f1 = (f1_counts + 1.0) / (f1_counts.sum() + self.nb)
        self.f0 = (f0_counts + 1.0) / (f0_counts.sum() + self.nb)
        self.llr_bins = np.log(self.f1) - np.log(self.f0)

    @classmethod
    def fit(cls, genuine_scores, impostor_scores, n_bins: int = 20):
        edges = np.linspace(0, 1, n_bins + 1)
        c1 = np.histogram(np.clip(genuine_scores, 0, 1), bins=edges)[0]
        c0 = np.histogram(np.clip(impostor_scores, 0, 1), bins=edges)[0]
        return cls(c1, c0)

    def bin(self, p):
        p = np.asarray(p, dtype=float)
        return np.clip(np.floor(p * self.nb).astype(int), 0, self.nb - 1)

    def llr(self, p):
        return self.llr_bins[self.bin(p)]

    def probs(self, p):
        b = self.bin(p)
        return self.f1[b], self.f0[b]

    def to_dict(self):
        return {"n_bins": self.nb, "f1": self.f1.tolist(), "f0": self.f0.tolist(), "llr_bins": self.llr_bins.tolist()}

    @classmethod
    def from_dict(cls, d):
        obj = cls.__new__(cls)
        obj.nb = int(d["n_bins"])
        obj.f1 = np.asarray(d["f1"])
        obj.f0 = np.asarray(d["f0"])
        obj.llr_bins = np.asarray(d["llr_bins"])
        return obj
