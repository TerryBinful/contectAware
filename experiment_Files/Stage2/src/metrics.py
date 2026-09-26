"""Evaluation layer for the mechanism comparison: security, stability, responsiveness.

Definitions are fixed here and unit-tested in tests/test_mechanisms.py. The legacy
"oscillation episode" definition (overlapping 4-frame windows, Stage 1 finding) is NOT used.

Notation: state s_t in {0,1} (1 = authenticated), ground-truth identity y_t in {0,1}
(1 = enrolled user present), frames indexed 0..T-1, 1 frame ~ 1 minute.
"""
import numpy as np

# ---------- security ----------
def security(state, truth):
    imp, gen = truth == 0, truth == 1
    fa = int(np.sum(state[imp] == 1)); fr = int(np.sum(state[gen] == 0))
    return dict(FAR=float(fa / imp.sum()) if imp.any() else np.nan,
                FRR=float(fr / gen.sum()) if gen.any() else np.nan,
                false_accept_frames=fa, false_reject_frames=fr,
                n_impostor_frames=int(imp.sum()), n_genuine_frames=int(gen.sum()))

# ---------- stability ----------
def n_transitions(state):
    """Number of committed state changes: |{t : s_t != s_{t-1}}|."""
    return int(np.sum(np.abs(np.diff(state))))

def transition_rate(state, per=100):
    return float(n_transitions(state) * per / max(len(state) - 1, 1))

def n_flip_events(state, window=3):
    """A flip event is a state change that is followed or preceded by another state change
    within `window` frames: |{i in C : exists j in C, j != i, |t_j - t_i| <= window}| where C is
    the set of change indices. This replaces the legacy overlapping-window 'episode' count."""
    c = np.flatnonzero(np.abs(np.diff(state)) == 1)
    if len(c) < 2:
        return 0
    d = np.abs(c[:, None] - c[None, :]); np.fill_diagonal(d, 10 ** 9)
    return int(np.sum(d.min(1) <= window))

def mean_state_run_length(state):
    if len(state) == 0:
        return np.nan
    ch = np.flatnonzero(np.diff(state)) + 1
    runs = np.diff(np.concatenate([[0], ch, [len(state)]]))
    return float(np.mean(runs))

def stability(state, window=3):
    return dict(n_transitions=n_transitions(state), transition_rate_per_100=transition_rate(state),
                n_flip_events=n_flip_events(state, window), mean_run_length_frames=mean_state_run_length(state),
                median_run_length_frames=float(np.median(np.diff(np.concatenate(
                    [[0], np.flatnonzero(np.diff(state)) + 1, [len(state)]])))) if len(state) else np.nan,
                frac_frames_authenticated=float(np.mean(state)))

# ---------- responsiveness ----------
def detection_latency(state, transition_idx, stable=3, block_end=None):
    """Frames from the genuine->impostor transition until the state reaches a STABLE rejected
    state *inside the impostor block*.

    The detection event and the whole `stable`-frame confirmation window must lie within
    [transition_idx, block_end); block_end is the first frame of the genuine recovery block.
    A stable rejection that only occurs during the recovery block is NOT a detection: the system
    would be rejecting the legitimate user, not the impostor. Returns NaN when stable rejection is
    never achieved inside the impostor block (the sequence is then a detection FAILURE and is
    reported as such, never silently converted to 0).
    """
    end = len(state) if block_end is None else int(block_end)
    s = state[transition_idx:end]
    for i in range(len(s) - stable + 1):
        if np.all(s[i:i + stable] == 0):
            return float(i)
    return float('nan')

def recovery_latency(state, recovery_idx, stable=3):
    """Frames from the return of the enrolled user until the state becomes 1 for `stable`
    consecutive frames. NaN if it never recovers."""
    s = state[recovery_idx:]
    for i in range(len(s) - stable + 1):
        if np.all(s[i:i + stable] == 1):
            return float(i)
    return float('nan')

def responsiveness(state, truth, transition_idx, recovery_idx, stable=3):
    gen = truth == 1
    out = dict(detection_latency_frames=detection_latency(state, transition_idx, stable,
                                                          block_end=recovery_idx),
               lockout_frames_during_genuine=int(np.sum(state[gen] == 0)),
               lockout_fraction_during_genuine=float(np.mean(state[gen] == 0)) if gen.any() else np.nan)
    out['recovery_latency_frames'] = (recovery_latency(state, recovery_idx, stable)
                                      if recovery_idx is not None else np.nan)
    return out

def evaluate_sequence(state, truth, transition_idx, recovery_idx, flip_window=3, stable=3):
    return dict(**security(state, truth), **stability(state, flip_window),
                **responsiveness(state, truth, transition_idx, recovery_idx, stable))
