"""Unit tests: mechanism behaviour against the synthetic fixtures, and leakage/metric definitions.
Run:  python -m pytest tests -q     (or: python tests/test_mechanisms.py)
"""
import os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import mechanisms as M
from src import metrics as MET

STABLE_AUTH = [0.90, 0.91, 0.89, 0.92, 0.90]
STABLE_IMP  = [0.10, 0.12, 0.09, 0.11, 0.08]
ALTERNATING = [0.90, 0.10, 0.91, 0.09, 0.92, 0.08]
BOUNDARY    = [0.50, 0.49, 0.51, 0.50, 0.49]
TRANSITION  = [0.92, 0.91, 0.90, 0.40, 0.32, 0.21]
RECOVERY    = [0.20, 0.30, 0.48, 0.72, 0.86, 0.91]

def run(name, params, seq):
    return M.build(name, params).run(np.array(seq, float)).tolist()

def test_instantaneous_matches_definition():
    assert run('instantaneous', dict(theta=0.5), STABLE_AUTH) == [1] * 5
    assert run('instantaneous', dict(theta=0.5), STABLE_IMP) == [0] * 5
    assert run('instantaneous', dict(theta=0.5), ALTERNATING) == [1, 0, 1, 0, 1, 0]
    assert run('instantaneous', dict(theta=0.5), BOUNDARY) == [1, 0, 1, 1, 0]   # >= is inclusive

def test_moving_average_smooths_alternating():
    out = run('moving_average', dict(theta=0.5, w=4), ALTERNATING)
    assert sum(np.abs(np.diff(out))) < sum(np.abs(np.diff(run('instantaneous', dict(theta=0.5), ALTERNATING))))

def test_ewma_update_rule():
    m = M.build('ewma', dict(theta=0.5, alpha=0.5)); m.reset()
    m.update(1.0); assert abs(m.diagnostics()['filtered'] - 1.0) < 1e-9      # initialised at first score
    m.update(0.0); assert abs(m.diagnostics()['filtered'] - 0.5) < 1e-9
    m.update(0.0); assert abs(m.diagnostics()['filtered'] - 0.25) < 1e-9

def test_majority_vote_window():
    assert run('majority_vote', dict(theta=0.5, w=3, k=2), [0.9, 0.9, 0.1, 0.1, 0.1]) == [1, 1, 1, 0, 0]

def test_debounce_requires_persistence():
    assert run('debounce', dict(theta=0.5, n=3), TRANSITION) == [1, 1, 1, 1, 1, 0]
    assert run('debounce', dict(theta=0.5, n=2), ALTERNATING) == [1] * 6      # never persists

def test_margin_dual_threshold_band():
    # band [0.4, 0.6]: scores inside the band never change the state
    assert run('margin_dual_threshold', dict(theta=0.5, margin=0.2), BOUNDARY) == [1] * 5
    assert run('margin_dual_threshold', dict(theta=0.5, margin=0.2), TRANSITION) == [1, 1, 1, 0, 0, 0]

def test_hysteresis_band_plus_persistence():
    out = run('hysteresis', dict(theta=0.5, margin=0.2, ttt_frames=2), TRANSITION)
    assert out == [1, 1, 1, 1, 0, 0]          # needs two consecutive frames <= 0.4
    assert run('hysteresis', dict(theta=0.5, margin=0.2, ttt_frames=3), ALTERNATING) == [1] * 6

def test_hysteresis_is_stricter_than_margin():
    a = run('margin_dual_threshold', dict(theta=0.5, margin=0.2), TRANSITION)
    b = run('hysteresis', dict(theta=0.5, margin=0.2, ttt_frames=2), TRANSITION)
    assert b.index(0) > a.index(0)            # persistence delays the transition

def test_trust_model_bounds_and_recovery():
    m = M.build('trust_model', dict(theta=0.5, gain=0.3, decay=0.05, tau_lo=0.4, tau_hi=0.6))
    out = m.run(np.array(STABLE_IMP + RECOVERY, float))
    assert 0.0 <= m.diagnostics()['trust'] <= 1.0
    assert out[len(STABLE_IMP) - 1] == 0                    # locks during the impostor block
    # trust must re-accumulate, so recovery is not instantaneous: six frames are not enough,
    # but sustained genuine scores do restore the authenticated state
    assert out[len(STABLE_IMP) + 5] == 0
    out2 = m.run(np.array(STABLE_IMP + RECOVERY + [0.92] * 10, float))
    assert out2[-1] == 1

def test_sprt_accumulates_and_commits():
    p = dict(mu_gen=0.9, sd_gen=0.15, mu_imp=0.1, sd_imp=0.15, A=4, B=4)
    assert run('sprt', p, STABLE_IMP)[-1] == 0
    assert run('sprt', p, STABLE_AUTH)[-1] == 1

def test_all_nine_registered_and_runnable():
    assert len(M.MECHANISM_ORDER) == 9 and set(M.MECHANISM_ORDER) == set(M.REGISTRY)
    for n in M.MECHANISM_ORDER:
        g = M.parameter_grid(n, [0.5])
        assert len(g) >= 1
        for params in g[:3]:
            out = M.build(n, params).run(np.array(TRANSITION + RECOVERY, float))
            assert set(np.unique(out)) <= {0, 1} and len(out) == 12

def test_reset_clears_state():
    m = M.build('debounce', dict(theta=0.5, n=2)); m.run(np.array(STABLE_IMP))
    m.reset(); assert m.state == M.AUTHENTICATED

# ---- metric definitions ----
def test_transition_and_flip_definitions():
    s = np.array([1, 1, 0, 1, 0, 1, 1, 1, 1, 1])
    assert MET.n_transitions(s) == 4
    assert MET.n_flip_events(s, window=3) == 4      # every change has another change within 3 frames
    assert MET.n_flip_events(np.array([1, 1, 1, 0, 0, 0, 0, 0, 0, 0]), window=3) == 0
    assert MET.n_transitions(np.ones(10, int)) == 0

def test_latency_definitions():
    truth = np.array([1, 1, 1, 0, 0, 0, 0, 0])      # impostor arrives at index 3
    state = np.array([1, 1, 1, 1, 1, 0, 0, 0])
    assert MET.detection_latency(state, 3, stable=2) == 2
    assert np.isnan(MET.detection_latency(np.ones(8, int), 3, stable=2))

def test_run_lengths():
    assert MET.mean_state_run_length(np.array([1, 1, 0, 0, 0, 1])) == 2.0

if __name__ == '__main__':
    fs = [(k, v) for k, v in sorted(globals().items()) if k.startswith('test_')]
    for k, f in fs:
        f(); print('PASS', k)
    print(f'\n{len(fs)}/{len(fs)} tests passed')
