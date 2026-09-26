"""Reference, per-frame implementations of every decision mechanism.

Common interface (execution spec §16): every mechanism receives the SAME score stream p[t]
(calibrated P(genuine | frame t)) one frame at a time and returns a binary state:

    m.reset()                      start of a session (a contiguous run); state := AUTH
    m.update(score, timestamp)     consume one frame; returns the new state (True = AUTH)
    m.state()                      current state (True = AUTH, False = LOCKED)
    m.diagnostics()                internal variables, for inspection and tests

These classes are the readable definition of each mechanism. The vectorised engine in
`batch.py` is what the sweeps use; `tests/test_batch_equivalence.py` asserts the two produce
identical state sequences. All temporal parameters are in FRAMES (1 frame ~ 60 s here).
"""
from __future__ import annotations

from collections import deque

import numpy as np

AUTH, LOCKED = True, False


class DecisionMechanism:
    name = "base"

    def __init__(self, **params):
        self.params = params
        self.reset()

    def reset(self):
        self._state = AUTH
        self._t = 0

    def update(self, score: float, timestamp=None) -> bool:     # pragma: no cover - abstract
        raise NotImplementedError

    def state(self) -> bool:
        return self._state

    def diagnostics(self) -> dict:
        return {"t": self._t, "state": "AUTH" if self._state else "LOCKED"}

    def run(self, scores) -> np.ndarray:
        """Convenience: reset, then feed a whole session."""
        self.reset()
        return np.array([self.update(float(p)) for p in scores], dtype=bool)


# 1 ---------------------------------------------------------------- instantaneous threshold
class Threshold(DecisionMechanism):
    """AUTH iff p[t] >= theta. Memoryless baseline."""
    name = "threshold"

    def update(self, score, timestamp=None):
        self._t += 1
        self._state = score >= self.params["theta"]
        return self._state


# 2 ---------------------------------------------------------------- moving average
class MovingAverage(DecisionMechanism):
    """q[t] = mean of the last min(k, frames since reset) scores; AUTH iff q >= theta.
    Start-up: the window grows from 1 to k (no padding). No missing observations occur inside a
    session by construction (a gap ends the session)."""
    name = "moving_average"

    def reset(self):
        super().reset()
        self._buf = deque(maxlen=int(self.params["k"]))
        self._q = np.nan

    def update(self, score, timestamp=None):
        self._t += 1
        self._buf.append(score)
        self._q = sum(self._buf) / len(self._buf)
        self._state = self._q >= self.params["theta"]
        return self._state

    def diagnostics(self):
        return {**super().diagnostics(), "q": self._q, "window": len(self._buf)}


# 3 ---------------------------------------------------------------- EWMA
class EWMA(DecisionMechanism):
    """q[0] = p[0]; q[t] = alpha p[t] + (1 - alpha) q[t-1]; AUTH iff q >= theta."""
    name = "ewma"

    def reset(self):
        super().reset()
        self._q = None

    def update(self, score, timestamp=None):
        self._t += 1
        a = self.params["alpha"]
        self._q = score if self._q is None else a * score + (1 - a) * self._q
        self._state = self._q >= self.params["theta"]
        return self._state

    def diagnostics(self):
        return {**super().diagnostics(), "q": self._q}


# 4 ---------------------------------------------------------------- majority vote
class MajorityVote(DecisionMechanism):
    """Votes v = [p >= theta] over the last min(k, frames since reset) frames (k odd).
    AUTH if #AUTH votes > n/2, LOCKED if < n/2; a tie (only possible during start-up, when n is
    even) keeps the previous state."""
    name = "majority_vote"

    def reset(self):
        super().reset()
        self._buf = deque(maxlen=int(self.params["k"]))

    def update(self, score, timestamp=None):
        self._t += 1
        self._buf.append(score >= self.params["theta"])
        c, n = sum(self._buf), len(self._buf)
        if 2 * c > n:
            self._state = AUTH
        elif 2 * c < n:
            self._state = LOCKED
        return self._state

    def diagnostics(self):
        return {**super().diagnostics(), "votes_auth": int(sum(self._buf)), "window": len(self._buf)}


# 5 ---------------------------------------------------------------- debounce (dwell only)
class Debounce(DecisionMechanism):
    """raw = [p >= theta]. A state change is committed only after raw has disagreed with the
    current state for T consecutive frames (the Time-to-Trigger component alone)."""
    name = "debounce"

    def reset(self):
        super().reset()
        self._c = 0

    def update(self, score, timestamp=None):
        self._t += 1
        raw = score >= self.params["theta"]
        self._c = self._c + 1 if raw != self._state else 0
        if self._c >= self.params["T"]:
            self._state, self._c = raw, 0
        return self._state

    def diagnostics(self):
        return {**super().diagnostics(), "counter": self._c}


# 6 ---------------------------------------------------------------- margin (dual threshold)
class Margin(DecisionMechanism):
    """Schmitt trigger. theta_lock = theta - m/2 (exit AUTH), theta_unlock = theta + m/2 (enter
    AUTH). AUTH -> LOCKED when p < theta_lock; LOCKED -> AUTH when p >= theta_unlock. (The margin
    component alone.)"""
    name = "margin"

    def update(self, score, timestamp=None):
        self._t += 1
        th, m = self.params["theta"], self.params["m"]
        if self._state:
            self._state = not (score < th - m / 2)
        else:
            self._state = score >= th + m / 2
        return self._state


# 7 ---------------------------------------------------------------- hysteresis (margin + dwell)
class Hysteresis(DecisionMechanism):
    """Handover-style hysteresis: margin + Time-to-Trigger. The exit condition of the current
    state (AUTH: p < theta - m/2; LOCKED: p >= theta + m/2) must hold for T consecutive frames
    before the state flips; the counter resets whenever the condition fails."""
    name = "hysteresis"

    def reset(self):
        super().reset()
        self._c = 0

    def update(self, score, timestamp=None):
        self._t += 1
        th, m, T = self.params["theta"], self.params["m"], self.params["T"]
        cond = (score < th - m / 2) if self._state else (score >= th + m / 2)
        self._c = self._c + 1 if cond else 0
        if self._c >= T:
            self._state, self._c = not self._state, 0
        return self._state

    def diagnostics(self):
        return {**super().diagnostics(), "counter": self._c}


# 8 ---------------------------------------------------------------- trust model
class Trust(DecisionMechanism):
    """Bounded additive trust (Bours/Mondal-style): trust[0] = 1 at session start;
    trust[t] = clip(trust[t-1] + r (p[t] - theta), 0, 1); AUTH iff trust >= tau."""
    name = "trust"

    def reset(self):
        super().reset()
        self._trust = 1.0

    def update(self, score, timestamp=None):
        self._t += 1
        self._trust = min(1.0, max(0.0, self._trust + self.params["r"] * (score - self.params["theta"])))
        self._state = self._trust >= self.params["tau"]
        return self._state

    def diagnostics(self):
        return {**super().diagnostics(), "trust": self._trust}


# 9 ---------------------------------------------------------------- SPRT
class SPRT(DecisionMechanism):
    """Wald sequential probability ratio test, restarted after each decision.
    LLR += log f1(p) / f0(p) (f1: genuine score density, f0: impostor score density, both
    histogram estimates fitted on VALIDATION data). A = log((1 - beta)/alpha),
    B = log(beta/(1 - alpha)), alpha = tolerated P(decide genuine | impostor),
    beta = tolerated P(decide impostor | genuine). LLR >= A -> AUTH, LLR <= B -> LOCKED, LLR := 0
    after either decision; otherwise the previous state is held."""
    name = "sprt"

    def __init__(self, density=None, **params):
        self.density = density
        super().__init__(**params)

    def reset(self):
        super().reset()
        self._llr = 0.0

    def update(self, score, timestamp=None):
        self._t += 1
        a, b = self.params["alpha"], self.params["beta"]
        A, B = np.log((1 - b) / a), np.log(b / (1 - a))
        self._llr += float(self.density.llr(score))
        if self._llr >= A:
            self._state, self._llr = AUTH, 0.0
        elif self._llr <= B:
            self._state, self._llr = LOCKED, 0.0
        return self._state

    def diagnostics(self):
        return {**super().diagnostics(), "llr": self._llr}


# 9b --------------------------------------------------------------- two-state HMM filter
class HMMFilter(DecisionMechanism):
    """Two-state (genuine/impostor) HMM forward filter. Switch probability rho per frame,
    emissions = the same validation-fitted score densities as SPRT. pi[0-] = pi0 (0.999) at
    session start; predict pi- = pi (1 - rho) + (1 - pi) rho; update with f1(p), f0(p).
    AUTH iff posterior P(genuine) >= theta. Supplementary arm."""
    name = "hmm"
    PI0 = 0.999

    def __init__(self, density=None, **params):
        self.density = density
        super().__init__(**params)

    def reset(self):
        super().reset()
        self._pi = self.PI0

    def update(self, score, timestamp=None):
        self._t += 1
        rho = self.params["rho"]
        prior = self._pi * (1 - rho) + (1 - self._pi) * rho
        f1, f0 = self.density.probs(score)
        num = prior * f1
        self._pi = num / (num + (1 - prior) * f0)
        self._state = self._pi >= self.params["theta"]
        return self._state

    def diagnostics(self):
        return {**super().diagnostics(), "posterior_genuine": self._pi}


REFERENCE = {c.name: c for c in (Threshold, MovingAverage, EWMA, MajorityVote, Debounce, Margin,
                                  Hysteresis, Trust, SPRT, HMMFilter)}
