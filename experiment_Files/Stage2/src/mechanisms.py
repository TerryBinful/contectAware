"""Post-pivot experiment: decision-layer stabilization mechanisms.

Every mechanism consumes the SAME authentication-score stream (produced by one fixed
per-user score generator) and returns an authentication state per frame through one interface:

    m.reset(); state = m.update(score, t)        # 1 = authenticated, 0 = rejected

Time base: frames. The ExtraSensory cadence is ~1 observation/minute (measured, see the dataset
audit), so all temporal parameters are expressed in FRAMES (1 frame ~ 1 minute). The legacy
"TTT = 3 seconds" formulation is not used anywhere.

Initial state: AUTHENTICATED. Benchmark sequences always start with a genuine block, so this
models a session that begins with the enrolled user present. It is recorded in every result file.
"""
import numpy as np

AUTHENTICATED, REJECTED = 1, 0

class DecisionMechanism:
    name = 'base'
    def __init__(self, **params):
        self.params = params
        self.reset()
    def reset(self):
        self.state = AUTHENTICATED
        self._diag = {}
    def update(self, score, t=None):
        raise NotImplementedError
    def diagnostics(self):
        return dict(self._diag)
    def run(self, scores, ts=None):
        self.reset()
        return np.array([self.update(s, None if ts is None else ts[i]) for i, s in enumerate(scores)], dtype=int)
    def __repr__(self):
        return f'{self.name}({self.params})'

class Instantaneous(DecisionMechanism):
    """state_t = 1 iff score_t >= theta. No memory. Baseline."""
    name = 'instantaneous'
    def update(self, score, t=None):
        self.state = AUTHENTICATED if score >= self.params['theta'] else REJECTED
        return self.state

class MovingAverage(DecisionMechanism):
    """Mean of the last w scores (partial window during startup) compared with theta."""
    name = 'moving_average'
    def reset(self):
        super().reset(); self.buf = []
    def update(self, score, t=None):
        self.buf.append(float(score))
        if len(self.buf) > self.params['w']:
            self.buf.pop(0)
        m = float(np.mean(self.buf))
        self._diag['filtered'] = m
        self.state = AUTHENTICATED if m >= self.params['theta'] else REJECTED
        return self.state

class EWMA(DecisionMechanism):
    """s_t = a*score_t + (1-a)*s_{t-1}, initialised at the first observed score."""
    name = 'ewma'
    def reset(self):
        super().reset(); self.s = None
    def update(self, score, t=None):
        a = self.params['alpha']
        self.s = float(score) if self.s is None else a * float(score) + (1 - a) * self.s
        self._diag['filtered'] = self.s
        self.state = AUTHENTICATED if self.s >= self.params['theta'] else REJECTED
        return self.state

class MajorityVote(DecisionMechanism):
    """Authenticated iff at least k of the last w raw decisions (score >= theta) are positive.
    Startup: partial window; k scaled to the frames seen so far (ceil(k*n/w)). Ties resolve to
    authenticated because the requirement is '>= k'."""
    name = 'majority_vote'
    def reset(self):
        super().reset(); self.buf = []
    def update(self, score, t=None):
        self.buf.append(1 if score >= self.params['theta'] else 0)
        w, k = self.params['w'], self.params['k']
        if len(self.buf) > w:
            self.buf.pop(0)
        need = int(np.ceil(k * len(self.buf) / w))
        self.state = AUTHENTICATED if sum(self.buf) >= need else REJECTED
        return self.state

class Debounce(DecisionMechanism):
    """A raw decision that disagrees with the committed state must persist n consecutive
    frames before the state changes. Symmetric in both directions."""
    name = 'debounce'
    def reset(self):
        super().reset(); self.count = 0
    def update(self, score, t=None):
        raw = AUTHENTICATED if score >= self.params['theta'] else REJECTED
        if raw == self.state:
            self.count = 0
        else:
            self.count += 1
            if self.count >= self.params['n']:
                self.state = raw; self.count = 0
        self._diag['pending'] = self.count
        return self.state

class MarginDualThreshold(DecisionMechanism):
    """Distinct entry/exit thresholds, no persistence requirement:
    rejected -> authenticated needs score >= theta_up; authenticated -> rejected needs
    score <= theta_down; theta_down = theta - margin/2, theta_up = theta + margin/2."""
    name = 'margin_dual_threshold'
    def _bounds(self):
        th, mg = self.params['theta'], self.params['margin']
        return th - mg / 2.0, th + mg / 2.0
    def update(self, score, t=None):
        lo, hi = self._bounds()
        if self.state == REJECTED and score >= hi:
            self.state = AUTHENTICATED
        elif self.state == AUTHENTICATED and score <= lo:
            self.state = REJECTED
        return self.state

class Hysteresis(MarginDualThreshold):
    """Dual thresholds AND a persistence requirement of ttt_frames consecutive qualifying
    frames (state-dependent thresholds + time-to-trigger, in frames)."""
    name = 'hysteresis'
    def reset(self):
        super().reset(); self.count = 0
    def update(self, score, t=None):
        lo, hi = self._bounds()
        qualifies = (score >= hi) if self.state == REJECTED else (score <= lo)
        if qualifies:
            self.count += 1
            if self.count >= self.params['ttt_frames']:
                self.state = AUTHENTICATED if self.state == REJECTED else REJECTED
                self.count = 0
        else:
            self.count = 0
        self._diag['pending'] = self.count
        return self.state

class TrustModel(DecisionMechanism):
    """Minimal bounded trust accumulator:
        trust <- clip( trust + gain*(score - theta) - decay*(trust - trust0), 0, 1 )
    Authenticated while trust >= tau_lo; a rejected state requires trust >= tau_hi to return.
    trust0 = 0.5, initial trust = 1.0 (session starts authenticated)."""
    name = 'trust_model'
    def reset(self):
        super().reset(); self.trust = 1.0
    def update(self, score, t=None):
        p = self.params
        self.trust = float(np.clip(self.trust + p['gain'] * (score - p['theta'])
                                   - p['decay'] * (self.trust - 0.5), 0.0, 1.0))
        self._diag['trust'] = self.trust
        if self.state == AUTHENTICATED:
            if self.trust < p['tau_lo']:
                self.state = REJECTED
        else:
            if self.trust >= p['tau_hi']:
                self.state = AUTHENTICATED
        return self.state

class SPRT(DecisionMechanism):
    """Sequential probability ratio test on the score stream.

    Per frame the log-likelihood ratio increment is taken from two Gaussian score models
    (genuine vs impostor) whose parameters are ESTIMATED ON CALIBRATION DATA ONLY and passed in.
    The cumulative statistic is clipped to [-B, A]; crossing +A commits AUTHENTICATED, crossing
    -B commits REJECTED, and the statistic resets to 0 after a decision. This is the sequential
    decision rule, not a re-classifier: it consumes the same scores as every other mechanism.
    """
    name = 'sprt'
    def reset(self):
        super().reset(); self.llr = 0.0
    def update(self, score, t=None):
        p = self.params
        mg, sg, mi, si = p['mu_gen'], p['sd_gen'], p['mu_imp'], p['sd_imp']
        lg = -0.5 * ((score - mg) / sg) ** 2 - np.log(sg)
        li = -0.5 * ((score - mi) / si) ** 2 - np.log(si)
        self.llr = float(np.clip(self.llr + (lg - li), -p['B'], p['A']))
        self._diag['llr'] = self.llr
        if self.llr >= p['A']:
            self.state = AUTHENTICATED; self.llr = 0.0
        elif self.llr <= -p['B']:
            self.state = REJECTED; self.llr = 0.0
        return self.state

REGISTRY = {m.name: m for m in [Instantaneous, MovingAverage, EWMA, MajorityVote, Debounce,
                                MarginDualThreshold, Hysteresis, TrustModel, SPRT]}
MECHANISM_ORDER = ['instantaneous', 'moving_average', 'ewma', 'majority_vote', 'debounce',
                   'margin_dual_threshold', 'hysteresis', 'trust_model', 'sprt']

def build(name, params):
    return REGISTRY[name](**params)

def parameter_grid(name, thetas, score_models=None):
    """Calibration search space. Temporal parameters are in FRAMES (~1 minute each)."""
    g = []
    if name == 'instantaneous':
        g = [dict(theta=t) for t in thetas]
    elif name == 'moving_average':
        g = [dict(theta=t, w=w) for t in thetas for w in (3, 5, 10, 20)]
    elif name == 'ewma':
        g = [dict(theta=t, alpha=a) for t in thetas for a in (0.1, 0.2, 0.3, 0.5)]
    elif name == 'majority_vote':
        g = [dict(theta=t, w=w, k=k) for t in thetas for w, k in ((3, 2), (5, 3), (5, 4), (10, 6), (10, 8))]
    elif name == 'debounce':
        g = [dict(theta=t, n=n) for t in thetas for n in (2, 3, 5, 10)]
    elif name == 'margin_dual_threshold':
        g = [dict(theta=t, margin=m) for t in thetas for m in (0.05, 0.1, 0.2, 0.4)]
    elif name == 'hysteresis':
        g = [dict(theta=t, margin=m, ttt_frames=k) for t in thetas for m in (0.05, 0.1, 0.2) for k in (2, 3, 5, 10)]
    elif name == 'trust_model':
        g = [dict(theta=t, gain=gn, decay=d, tau_lo=0.4, tau_hi=0.6)
             for t in thetas for gn in (0.1, 0.3, 0.6) for d in (0.0, 0.05, 0.2)]
    elif name == 'sprt':
        sm = score_models or dict(mu_gen=0.9, sd_gen=0.15, mu_imp=0.1, sd_imp=0.15)
        g = [dict(A=A, B=B, **sm) for A in (1, 2, 4, 8, 16) for B in (1, 2, 4, 8, 16)]
    else:
        raise KeyError(name)
    return g
