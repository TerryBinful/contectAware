"""Synthetic score sequences from the execution specification §24."""
import numpy as np

STABLE_AUTH = np.array([0.90, 0.91, 0.89, 0.92, 0.90])
STABLE_IMPOSTOR = np.array([0.10, 0.12, 0.09, 0.11, 0.08])
ALTERNATING = np.array([0.90, 0.10, 0.91, 0.09, 0.92, 0.08])
BOUNDARY = np.array([0.50, 0.49, 0.51, 0.50, 0.49])
TRANSITION = np.array([0.92, 0.91, 0.90, 0.40, 0.32, 0.21])
RECOVERY = np.array([0.20, 0.30, 0.48, 0.72, 0.86, 0.91])

ALL = {"stable_auth": STABLE_AUTH, "stable_impostor": STABLE_IMPOSTOR, "alternating": ALTERNATING,
       "boundary": BOUNDARY, "transition": TRANSITION, "recovery": RECOVERY}


def dyadic_streams(n_streams=12, max_len=60, seed=0):
    """Random streams whose values are multiples of 1/256, so windowed sums are exact in float64."""
    rng = np.random.default_rng(seed)
    out = []
    for i in range(n_streams):
        L = int(rng.integers(1, max_len))
        regime = rng.random() < 0.5
        base = rng.integers(0, 257, size=L) / 256.0
        if regime:  # add structure: a genuine-ish run then an impostor-ish block
            cut = int(rng.integers(0, L + 1))
            base[:cut] = np.clip(base[:cut] * 0.3 + 0.7, 0, 1)
            base = np.round(base * 256) / 256
        out.append(base)
    return out
