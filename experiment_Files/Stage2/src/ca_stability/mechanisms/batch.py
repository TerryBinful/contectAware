"""Vectorised mechanism engine used for the parameter sweeps.

A StreamBatch holds n score streams padded into an (n, T) array. `valid` marks real frames,
`reset` marks the first frame of each stream (session start). Every batch function evaluates
one fixed parameter combination for a vector of K values of the swept parameter and returns
states S with shape (K, n, T), True = AUTH. Values at invalid positions are meaningless and
must be masked by the caller.

Each function mirrors the per-frame class of the same name in `reference.py`, using the same
arithmetic expressions so that results are bit-identical (asserted in the test-suite).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class StreamBatch:
    P: np.ndarray        # (n, T) float64 calibrated scores, NaN where invalid
    valid: np.ndarray    # (n, T) bool
    reset: np.ndarray    # (n, T) bool, True at the first frame of each stream

    @property
    def n(self):
        return self.P.shape[0]

    @property
    def T(self):
        return self.P.shape[1]

    @classmethod
    def from_arrays(cls, arrays, starts=None, T=None):
        """Place stream i at columns [starts[i], starts[i] + len(arrays[i])) (default start 0)."""
        n = len(arrays)
        starts = np.zeros(n, dtype=int) if starts is None else np.asarray(starts, dtype=int)
        ends = starts + np.array([len(a) for a in arrays], dtype=int)
        T = int(max(ends.max() if n else 1, T or 0))
        P = np.full((n, T), np.nan)
        valid = np.zeros((n, T), dtype=bool)
        reset = np.zeros((n, T), dtype=bool)
        for i, a in enumerate(arrays):
            if len(a) == 0:
                continue
            P[i, starts[i]:ends[i]] = a
            valid[i, starts[i]:ends[i]] = True
            reset[i, starts[i]] = True
        return cls(P, valid, reset)

    def filled(self, value=0.5):
        return np.where(self.valid, self.P, value)


# ----------------------------------------------------------------------------- helpers
def positions(sb: StreamBatch) -> np.ndarray:
    """Index of each valid frame within its stream (0 at the reset frame); -1 if invalid."""
    c = np.cumsum(sb.valid, axis=1)
    base = np.maximum.accumulate(np.where(sb.reset, c - 1, 0), axis=1)
    return np.where(sb.valid, c - 1 - base, -1)


def window_sum(x: np.ndarray, pos: np.ndarray, k: int):
    """Sum of x over the last min(k, pos+1) frames of the same stream. x: (..., n, T)."""
    T = x.shape[-1]
    C = np.concatenate([np.zeros(x.shape[:-1] + (1,), dtype=np.float64), np.cumsum(x, axis=-1, dtype=np.float64)], axis=-1)
    w = np.minimum(k, pos + 1)                                  # 0 where invalid
    lo = np.clip(np.arange(T)[None, :] + 1 - w, 0, None)
    lo = np.broadcast_to(lo, x.shape)
    s = C[..., 1:] - np.take_along_axis(C, lo, axis=-1)
    return s, w


# ----------------------------------------------------------------------------- mechanisms
def threshold(sb: StreamBatch, fixed: dict, theta: np.ndarray, ctx=None):
    return sb.filled()[None] >= theta[:, None, None]


def ordered_window_sum(x: np.ndarray, pos: np.ndarray, k: int):
    """Window sum accumulated oldest-to-newest (the same float order as Python's sum over the
    reference deque), so moving averages are bit-identical to the reference implementation."""
    w = np.minimum(k, pos + 1)
    s = np.zeros(x.shape)
    for j in range(k - 1, -1, -1):                     # j = age of the frame being added
        if j >= x.shape[1]:
            continue
        shifted = np.zeros(x.shape)
        shifted[:, j:] = x[:, :x.shape[1] - j] if j else x
        s = s + np.where(j < w, shifted, 0.0)
    return s, w


def moving_average(sb, fixed, theta, ctx=None):
    pos = positions(sb)
    s, w = ordered_window_sum(sb.filled(0.0), pos, int(fixed["k"]))
    q = s / np.maximum(w, 1)
    return q[None] >= theta[:, None, None]


def ewma_values(sb, alpha):
    P, V, R = sb.filled(), sb.valid, sb.reset
    q = np.zeros(sb.n)
    out = np.empty(P.shape)
    for t in range(sb.T):
        p = P[:, t]
        new = np.where(R[:, t], p, alpha * p + (1 - alpha) * q)
        q = np.where(V[:, t], new, q)
        out[:, t] = q
    return out


def ewma(sb, fixed, theta, ctx=None):
    return ewma_values(sb, float(fixed["alpha"]))[None] >= theta[:, None, None]


def majority_vote(sb, fixed, theta, ctx=None):
    pos = positions(sb)
    votes = ((sb.filled()[None] >= theta[:, None, None]) & sb.valid[None]).astype(np.float64)
    cnt, w = window_sum(votes, pos, int(fixed["k"]))
    D = 2 * cnt - w[None]
    K = len(theta)
    S = np.empty((K, sb.n, sb.T), dtype=bool)
    s = np.ones((K, sb.n), dtype=bool)
    for t in range(sb.T):
        s = np.where(sb.reset[None, :, t], True, s)
        d = D[:, :, t]
        new = np.where(d > 0, True, np.where(d < 0, False, s))
        s = np.where(sb.valid[None, :, t], new, s)
        S[:, :, t] = s
    return S


def debounce(sb, fixed, theta, ctx=None):
    T_ = int(fixed["T"])
    P = sb.filled()
    K = len(theta)
    th = theta[:, None]
    S = np.empty((K, sb.n, sb.T), dtype=bool)
    s = np.ones((K, sb.n), dtype=bool)
    c = np.zeros((K, sb.n), dtype=np.int32)
    for t in range(sb.T):
        r = sb.reset[None, :, t]
        s = np.where(r, True, s)
        c = np.where(r, 0, c)
        raw = P[None, :, t] >= th
        cn = np.where(raw != s, c + 1, 0)
        flip = cn >= T_
        sn = np.where(flip, raw, s)
        cn = np.where(flip, 0, cn)
        v = sb.valid[None, :, t]
        s = np.where(v, sn, s)
        c = np.where(v, cn, c)
        S[:, :, t] = s
    return S


def margin(sb, fixed, theta, ctx=None):
    m = float(fixed["m"])
    lo, hi = (theta - m / 2)[:, None], (theta + m / 2)[:, None]
    P = sb.filled()
    K = len(theta)
    S = np.empty((K, sb.n, sb.T), dtype=bool)
    s = np.ones((K, sb.n), dtype=bool)
    for t in range(sb.T):
        s = np.where(sb.reset[None, :, t], True, s)
        p = P[None, :, t]
        sn = np.where(s, ~(p < lo), p >= hi)
        s = np.where(sb.valid[None, :, t], sn, s)
        S[:, :, t] = s
    return S


def hysteresis(sb, fixed, theta, ctx=None):
    m, T_ = float(fixed["m"]), int(fixed["T"])
    lo, hi = (theta - m / 2)[:, None], (theta + m / 2)[:, None]
    P = sb.filled()
    K = len(theta)
    S = np.empty((K, sb.n, sb.T), dtype=bool)
    s = np.ones((K, sb.n), dtype=bool)
    c = np.zeros((K, sb.n), dtype=np.int32)
    for t in range(sb.T):
        r = sb.reset[None, :, t]
        s = np.where(r, True, s)
        c = np.where(r, 0, c)
        p = P[None, :, t]
        cond = np.where(s, p < lo, p >= hi)
        cn = np.where(cond, c + 1, 0)
        flip = cn >= T_
        sn = np.where(flip, ~s, s)
        cn = np.where(flip, 0, cn)
        v = sb.valid[None, :, t]
        s = np.where(v, sn, s)
        c = np.where(v, cn, c)
        S[:, :, t] = s
    return S


def trust(sb, fixed, theta, ctx=None):
    r_, tau = float(fixed["r"]), float(fixed["tau"])
    th = theta[:, None]
    P = sb.filled()
    K = len(theta)
    S = np.empty((K, sb.n, sb.T), dtype=bool)
    tr = np.ones((K, sb.n))
    for t in range(sb.T):
        tr = np.where(sb.reset[None, :, t], 1.0, tr)
        tn = np.minimum(1.0, np.maximum(0.0, tr + r_ * (P[None, :, t] - th)))
        tr = np.where(sb.valid[None, :, t], tn, tr)
        S[:, :, t] = tr >= tau
    return S


def sprt(sb, fixed, beta, ctx=None):
    a = float(fixed["alpha"])
    A = np.log((1 - beta) / a)[:, None]
    B = np.log(beta / (1 - a))[:, None]
    llr = ctx["density"].llr(sb.filled())            # (n, T)
    K = len(beta)
    S = np.empty((K, sb.n, sb.T), dtype=bool)
    s = np.ones((K, sb.n), dtype=bool)
    L = np.zeros((K, sb.n))
    for t in range(sb.T):
        r = sb.reset[None, :, t]
        s = np.where(r, True, s)
        L = np.where(r, 0.0, L)
        Ln = L + llr[None, :, t]
        up, down = Ln >= A, Ln <= B
        sn = np.where(up, True, np.where(down, False, s))
        Ln = np.where(up | down, 0.0, Ln)
        v = sb.valid[None, :, t]
        s = np.where(v, sn, s)
        L = np.where(v, Ln, L)
        S[:, :, t] = s
    return S


def hmm_posterior(sb, rho, density, pi0=0.999):
    f1, f0 = density.probs(sb.filled())
    pi = np.full(sb.n, pi0)
    out = np.empty(sb.P.shape)
    for t in range(sb.T):
        pi = np.where(sb.reset[:, t], pi0, pi)
        prior = pi * (1 - rho) + (1 - pi) * rho
        num = prior * f1[:, t]
        new = num / (num + (1 - prior) * f0[:, t])
        pi = np.where(sb.valid[:, t], new, pi)
        out[:, t] = pi
    return out


def hmm(sb, fixed, theta, ctx=None):
    post = hmm_posterior(sb, float(fixed["rho"]), ctx["density"])
    return post[None] >= theta[:, None, None]


BATCH = {"threshold": threshold, "moving_average": moving_average, "ewma": ewma,
         "majority_vote": majority_vote, "debounce": debounce, "margin": margin,
         "hysteresis": hysteresis, "trust": trust, "sprt": sprt, "hmm": hmm}
