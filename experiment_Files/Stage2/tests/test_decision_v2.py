"""Tests for the v2 offline decision layer (src/decision_v2.py, scripts/decision_layer_offline.py).
Synthetic data only. Run:  python -m pytest tests -q   (or: python tests/test_decision_v2.py)
"""
import json, os, subprocess, sys, tempfile
import numpy as np, pandas as pd
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src import mechanisms as M
from src import decision_v2 as D

RNG = np.random.default_rng(7)
S = np.clip(RNG.beta(2, 2, size=(6, 90)) + 0.15 * np.sin(np.arange(90) / 4.0), 0, 1)
S[:, 30:45] = RNG.uniform(0, 0.3, size=(6, 15))        # an impostor-like dip
S[0, :5] = [0.5, 0.5, 0.5, 0.5, 0.5]                     # exact-threshold ties
THETAS = [0.3, 0.45, 0.5, 0.62, 0.8]
SM = dict(mu_gen=0.7, sd_gen=0.15, mu_imp=0.3, sd_imp=0.2)

def reference(name, p, seq):
    q = dict(p)
    if name == 'trust_model_single':
        name = 'trust_model'
    if name == 'sprt':
        q.pop('delta', None); q.update(SM)
    return M.build(name, q).run(seq)

def test_batch_simulators_match_reference_classes():
    for name in M.MECHANISM_ORDER + ['trust_model_single']:
        grid = D.family_grid(name, THETAS)
        if name == 'sprt':
            grid = [g for g in grid if g['delta'] == 0.0][::7]
        st = D.simulate(name, grid, S, SM)
        for c, p in enumerate(grid):
            for j in range(S.shape[0]):
                ref = reference(name, p, S[j])
                assert np.array_equal(st[c, j], ref), (name, p, j)

def test_sprt_delta_shifts_increment():
    p = dict(A=4.0, B=4.0, delta=-1.0)
    st = D.sim_sprt(S, [p['A']], [p['B']], [p['delta']], SM)[0]
    # reference: SPRT on a stream whose LLR increment is shifted by delta
    llr, state, out = 0.0, 1, []
    for s in S[1]:
        llr = float(np.clip(llr + D.sprt_increment(s, SM) + p['delta'], -p['B'], p['A']))
        if llr >= p['A']: state, llr = 1, 0.0
        elif llr <= -p['B']: state, llr = 0, 0.0
        out.append(state)
    assert np.array_equal(st[1], out)

def test_factorial_corners_are_exact():
    th = np.array(THETAS)
    one = np.ones(len(th), int)
    assert np.array_equal(D.sim_margin_dwell(S, th, 0 * th, one), D.sim_instantaneous(S, th))
    for k in D.FACTORIAL_DWELLS[1:]:
        assert np.array_equal(D.sim_margin_dwell(S, th, 0 * th, k * one), D.sim_debounce(S, th, k * one)), k

def test_margin_dwell_semantics():
    # reject-qualifying is strict: s == theta - m/2 does not count
    st = D.sim_margin_dwell(np.array([[0.4, 0.4, 0.39, 0.39, 0.61, 0.61]]), [0.5], [0.2], [2])[0, 0]
    assert st.tolist() == [1, 1, 1, 0, 0, 1]      # two frames >= 0.6 re-accept
    st = D.sim_margin_dwell(np.array([[0.39, 0.39, 0.6, 0.55, 0.6, 0.6]]), [0.5], [0.2], [2])[0, 0]
    assert st.tolist() == [1, 0, 0, 0, 0, 1]     # counter resets on the non-qualifying 0.55

def test_reachability():
    assert D.reachable('instantaneous', dict(theta=1.0))[0]
    assert not D.reachable('instantaneous', dict(theta=1.0001))[0]
    assert not D.reachable('hysteresis', dict(theta=0.95, margin=0.2, ttt_frames=3))[0]
    assert D.reachable('hysteresis', dict(theta=0.9, margin=0.2, ttt_frames=3))[0]
    assert not D.reachable('margin_dwell', dict(theta=0.97, m=0.1, k=2))[0]
    assert D.reachable('trust_model', dict(theta=0.5, gain=0.3, decay=0.0, tau_lo=0.4, tau_hi=0.6))[0]
    # fixed point 0.5 + 0.1*0.2/0.2 = 0.6, not > tau_hi 0.6
    assert not D.reachable('trust_model', dict(theta=0.8, gain=0.1, decay=0.2, tau_lo=0.4, tau_hi=0.6))[0]
    assert not D.reachable('trust_model', dict(theta=1.0, gain=0.3, decay=0.0, tau_lo=0.4, tau_hi=0.6))[0]
    inc1 = float(D.sprt_increment(np.array(1.0), SM))
    assert D.reachable('sprt', dict(A=2, B=2, delta=0.0), SM)[0] == (inc1 > 0)
    assert not D.reachable('sprt', dict(A=2, B=2, delta=-inc1 - 0.01), SM)[0]

def test_one_sided_selection():
    grid = [dict(theta=t) for t in (0.1, 0.2, 0.3, 0.4, 0.5)]
    far = np.array([0.060, 0.050, 0.045, 0.039, 0.045])
    frr = np.array([0.01, 0.10, 0.20, 0.05, 0.20])
    reach = np.array([True, True, True, True, True])
    i, r = D.select_one_sided(grid, far, frr, reach, 0.05, 0.01)
    assert i == 1 and r['n_eligible'] == 3              # 0.060 above band, 0.039 below band
    i, _ = D.select_one_sided(grid, far, frr, np.array([True, False, True, True, True]), 0.05, 0.01)
    assert i == 2                                        # tie on FRR/complexity -> lower FAR, then grid order
    i, r = D.select_one_sided(grid, far + 0.05, frr, reach, 0.05, 0.01)
    assert i is None and r['feasible'] is False          # no substitution

def test_v2_sequence_metrics():
    truth = np.r_[np.ones(60), np.zeros(60), np.ones(60)].astype(int)
    r = D.sequence_metrics_v2(truth.copy(), truth, 60, 120)
    assert r['excess_transitions'] == 0 and r['detection_failure'] == 0 and r['detection_latency_frames'] == 0
    never = np.ones(180, int)
    r = D.sequence_metrics_v2(never, truth, 60, 120)
    assert r['detection_failure'] == 1 and r['detection_latency_censored'] == 60 and r['fewer_than_2_transitions'] == 1
    stuck = np.r_[np.ones(60), np.zeros(120)].astype(int)
    r = D.sequence_metrics_v2(stuck, truth, 60, 120)
    assert r['recovery_failure'] == 1 and r['recovery_latency_censored'] == 60

def test_stats_helpers():
    y = np.r_[np.ones(50), np.zeros(50)]; s = np.r_[np.arange(50) + 50, np.arange(50)]
    assert D.auc(y, s) == 1.0 and abs(D.auc(y, np.zeros(100)) - 0.5) < 1e-12
    assert np.allclose(D.holm([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06])

def test_end_to_end_self_test():
    with tempfile.TemporaryDirectory() as d:
        subprocess.check_call([sys.executable, os.path.join(ROOT, 'scripts', 'decision_layer_offline.py'),
                               '--self-test', '--out', d, '--max-users', '5'], stdout=subprocess.DEVNULL)
        meta = json.load(open(os.path.join(d, 'experiment_metadata.json')))
        assert meta['self_test'] and not meta['confirmatory']
        ops = pd.read_csv(os.path.join(d, 'factorial', 'operating_points.csv'))
        assert set(ops.cell) == {D.cell_name(m, k) for m in D.FACTORIAL_MARGINS for k in D.FACTORIAL_DWELLS}
        feas = ops[ops.feasible.astype(bool)]
        assert ((feas.calib_FAR >= feas.target - 0.01 - 1e-9) & (feas.calib_FAR <= feas.target + 1e-9)).all()
        assert os.path.exists(os.path.join(d, 'primary', 'PRIMARY_DECISION.md'))
        mm = pd.read_csv(os.path.join(d, 'families', 'mechanism_metrics.csv'))
        assert list(mm.mechanism) == D.FAMILY_ORDER

def test_moving_average_matches_numpy_mean_on_exact_ties():
    """Deterministic regression test for the secondary-analysis moving_average defect.

    No RNG. The score streams use values with short binary expansions, and the candidate
    thresholds are set to the EXACT np.mean of the trailing windows, so a tie occurs at every
    frame. The previous cumsum window mean differed from np.mean by ~7e-16 and therefore
    flipped `>= theta` at those ties; random-float fixtures never expose this, which is why
    test_batch_simulators_match_reference_classes passed while the defect was live.

    Two assertions: (1) the internal window mean is bit-for-bit np.mean; (2) the batch
    simulator reproduces src/mechanisms.MovingAverage frame for frame at tied thresholds.
    """
    # Values chosen so that floating-point accumulation genuinely diverges: these are
    # non-terminating in binary, so a cumsum window sum differs from np.mean. (A fixture of
    # exactly-representable values such as k/8 would make both paths agree and the test
    # would pass against the defect -- verified, and rejected for that reason.)
    S = np.array([[(i % 7) / 7.0 for i in range(60)],
                  [((i % 9) + 1) / 10.0 for i in range(60)],
                  [1 / 3.0] * 60], float)
    for w in (3, 5, 10, 20):
        ref = np.array([[S[j, max(0, t + 1 - w):t + 1].mean() for t in range(S.shape[1])]
                        for j in range(S.shape[0])])
        # (1) bit-for-bit equality with np.mean, not merely allclose
        assert np.array_equal(D._moving_mean(S, w), ref), f'window mean != np.mean at w={w}'
        # (2) thresholds that are exactly attained window means -> ties at every frame
        thetas = sorted(set(ref.ravel().tolist()))
        grid = [dict(theta=t, w=w) for t in thetas]
        B = D.simulate('moving_average', grid, S)
        for i, p in enumerate(grid):
            for j in range(S.shape[0]):
                assert np.array_equal(M.build('moving_average', p).run(S[j]), B[i, j]), \
                    f'batch != reference class at w={w}, theta={p["theta"]!r}, seq={j}'


if __name__ == '__main__':
    fns = [v for k, v in dict(globals()).items() if k.startswith('test_')]
    for f in fns:
        f(); print('ok', f.__name__)
    print(f'{len(fns)}/{len(fns)} tests passed')
