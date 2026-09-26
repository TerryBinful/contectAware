"""The vectorised engine must reproduce the per-frame reference implementation exactly."""
import zlib

import numpy as np
import pytest

from ca_stability.mechanisms import BATCH, REFERENCE, ScoreDensity, StreamBatch
from fixtures import ALL, dyadic_streams

THETAS = np.array([0.1, 0.25, 0.375, 0.5, 0.625, 0.75, 0.9])
CASES = [
    ("threshold", {}),
    ("moving_average", {"k": 1}), ("moving_average", {"k": 3}), ("moving_average", {"k": 10}),
    ("ewma", {"alpha": 0.25}), ("ewma", {"alpha": 0.5}),
    ("majority_vote", {"k": 3}), ("majority_vote", {"k": 5}),
    ("debounce", {"T": 1}), ("debounce", {"T": 2}), ("debounce", {"T": 5}),
    ("margin", {"m": 0.125}), ("margin", {"m": 0.25}),
    ("hysteresis", {"m": 0.125, "T": 2}), ("hysteresis", {"m": 0.25, "T": 3}),
    ("trust", {"r": 0.25, "tau": 0.5}), ("trust", {"r": 0.5, "tau": 0.25}),
    ("hmm", {"rho": 0.01}), ("hmm", {"rho": 0.1}),
]
DENS = ScoreDensity.fit(np.r_[np.linspace(0.5, 1, 50)], np.r_[np.linspace(0, 0.6, 50)], 8)


def reference_states(name, combo, sweep_name, value, stream):
    kw = dict(combo, **{sweep_name: float(value)})
    cls = REFERENCE[name]
    m = cls(density=DENS, **kw) if name in ("sprt", "hmm") else cls(**kw)
    return m.run(stream)


@pytest.mark.parametrize("left_pad", [False, True])
@pytest.mark.parametrize("name,combo", CASES)
def test_equivalence(name, combo, left_pad):
    streams = dyadic_streams(14, 50, seed=zlib.crc32(f"{name}{combo}".encode()) % 1000) + list(ALL.values())
    starts = np.random.default_rng(1).integers(0, 7, len(streams)) if left_pad else None
    sb = StreamBatch.from_arrays(streams, starts=starts)
    S = BATCH[name](sb, combo, THETAS, {"density": DENS})
    for i, st in enumerate(streams):
        s0 = 0 if starts is None else starts[i]
        for k, th in enumerate(THETAS):
            ref = reference_states(name, combo, "theta", th, st)
            got = S[k, i, s0:s0 + len(st)]
            assert np.array_equal(ref, got), (name, combo, th, i)


@pytest.mark.parametrize("alpha", [0.01, 0.1])
def test_sprt_equivalence(alpha):
    betas = np.array([1e-6, 1e-3, 0.01, 0.1, 0.3])
    streams = dyadic_streams(14, 60, seed=3) + list(ALL.values())
    sb = StreamBatch.from_arrays(streams)
    S = BATCH["sprt"](sb, {"alpha": alpha}, betas, {"density": DENS})
    for i, st in enumerate(streams):
        for k, b in enumerate(betas):
            ref = reference_states("sprt", {"alpha": alpha}, "beta", b, st)
            assert np.array_equal(ref, S[k, i, :len(st)])


def test_streams_are_independent_and_reset():
    """Concatenating two streams in one row with a reset must equal running them separately."""
    a, b = ALL["transition"], ALL["recovery"]
    sb = StreamBatch.from_arrays([a, b])
    sb2 = StreamBatch(np.r_[a, b][None], np.ones((1, len(a) + len(b)), bool), np.zeros((1, len(a) + len(b)), bool))
    sb2.reset[0, 0] = sb2.reset[0, len(a)] = True
    for name, combo in CASES:
        S1 = BATCH[name](sb, combo, THETAS, {"density": DENS})
        S2 = BATCH[name](sb2, combo, THETAS, {"density": DENS})
        assert np.array_equal(np.concatenate([S1[:, 0, :len(a)], S1[:, 1, :len(b)]], axis=1), S2[:, 0, :]), name
