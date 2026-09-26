"""Stage 2 v2 decision layer, implementing docs/Stage2/PREREGISTRATION_v2.md (frozen 2026-09-26).

This module operates ONLY on dumped score streams (C7). It never fits or refits a model.

Contents
  * Batch (vectorised) simulators for every mechanism: one call evaluates many parameter
    candidates on many sequences at once. Semantics are identical to the reference classes in
    src/mechanisms.py (verified frame-by-frame in tests/test_decision_v2.py).
  * The fixed-level factorial mechanism `margin_dwell(theta, m, k)` for the primary analysis (§3).
  * Candidate grids for the tuned-family comparison (§4.1), including the continuous SPRT grid (C4)
    and the single-threshold trust variant (C6).
  * Reachability filter (C2) and the one-sided minimum-FRR selection rule (C1).
  * v2 sequence metrics (C5).

Implementation decisions that the preregistration does not spell out are listed in
docs/Stage2/V2_ANALYSIS_IMPLEMENTATION_NOTES.md. They were fixed before any v2 score existed.
"""
import numpy as np
from . import metrics as MET

S_MAX = 1.0          # the ECDF normaliser caps normalised scores at 1.0 (PREREGISTRATION_v2 C2)

# --------------------------------------------------------------------------------------------
# Batch simulators. S: float array (n_seq, T). Parameter arrays have length n_cand.
# Return int8 states of shape (n_cand, n_seq, T); 1 = AUTHENTICATED. Initial state AUTHENTICATED.
# --------------------------------------------------------------------------------------------
def _col(x):
    return np.asarray(x, float)[:, None]

def sim_instantaneous(S, theta):
    return (S[None, :, :] >= np.asarray(theta, float)[:, None, None]).astype(np.int8)

def _moving_mean(S, w):
    c = np.cumsum(np.pad(S, ((0, 0), (1, 0))), axis=1)
    T = S.shape[1]; t = np.arange(T)
    lo = np.maximum(t + 1 - w, 0)
    return (c[:, t + 1] - c[:, lo]) / (t + 1 - lo)

def sim_moving_average(S, theta, w):
    theta, w = np.asarray(theta, float), np.asarray(w, int)
    out = np.empty((len(theta),) + S.shape, np.int8)
    for ww in np.unique(w):
        i = np.flatnonzero(w == ww); F = _moving_mean(S, int(ww))
        out[i] = F[None] >= theta[i][:, None, None]
    return out

def sim_ewma(S, theta, alpha):
    theta, alpha = np.asarray(theta, float), np.asarray(alpha, float)
    out = np.empty((len(theta),) + S.shape, np.int8)
    for a in np.unique(alpha):
        i = np.flatnonzero(alpha == a)
        F = np.empty_like(S); F[:, 0] = S[:, 0]
        for t in range(1, S.shape[1]):
            F[:, t] = a * S[:, t] + (1 - a) * F[:, t - 1]
        out[i] = F[None] >= theta[i][:, None, None]
    return out

def sim_majority_vote(S, theta, w, k):
    theta, w, k = np.asarray(theta, float), np.asarray(w, int), np.asarray(k, int)
    raw = (S[None] >= theta[:, None, None]).astype(np.int32)
    c = np.cumsum(np.pad(raw, ((0, 0), (0, 0), (1, 0))), axis=2)
    T = S.shape[1]; t = np.arange(T)
    out = np.empty(raw.shape, np.int8)
    for ww, kk in set(zip(w.tolist(), k.tolist())):
        i = np.flatnonzero((w == ww) & (k == kk))
        lo = np.maximum(t + 1 - ww, 0); n = t + 1 - lo
        need = np.ceil(kk * n / ww).astype(int)
        out[i] = (c[i][:, :, t + 1] - c[i][:, :, lo]) >= need[None, None, :]
    return out

def _dwell_loop(S, acc_thr, rej_test, dwell):
    """Generic latch: in REJECTED a frame qualifies if s >= acc_thr; in AUTHENTICATED a frame
    qualifies if rej_test(s) is True. `dwell` consecutive qualifying frames flip the state; any
    non-qualifying frame resets the counter. Covers debounce, v1 hysteresis and margin_dwell."""
    nc = len(acc_thr); ns, T = S.shape
    state = np.ones((nc, ns), np.int8); cnt = np.zeros((nc, ns), np.int32)
    out = np.empty((nc, ns, T), np.int8)
    A = acc_thr[:, None]; D = dwell[:, None]
    for t in range(T):
        s = S[None, :, t]
        q = np.where(state == 1, rej_test(s), s >= A)
        cnt = np.where(q, cnt + 1, 0)
        flip = cnt >= D
        state = np.where(flip, 1 - state, state).astype(np.int8)
        cnt = np.where(flip, 0, cnt)
        out[:, :, t] = state
    return out

def sim_debounce(S, theta, n):
    th = np.asarray(theta, float)
    return _dwell_loop(S, th, lambda s: s < th[:, None], np.asarray(n, int))

def sim_hysteresis_v1(S, theta, margin, ttt):
    """v1 Hysteresis semantics (src/mechanisms.Hysteresis): reject-qualifying is s <= theta - m/2."""
    th, m = np.asarray(theta, float), np.asarray(margin, float)
    lo = th - m / 2
    return _dwell_loop(S, th + m / 2, lambda s: s <= lo[:, None], np.asarray(ttt, int))

def sim_margin_v1(S, theta, margin):
    """v1 MarginDualThreshold semantics: no dwell; reject-qualifying is s <= theta - m/2."""
    return sim_hysteresis_v1(S, theta, margin, np.ones(len(np.atleast_1d(theta)), int))

def sim_margin_dwell(S, theta, m, k):
    """PRIMARY factorial mechanism (PREREGISTRATION_v2 §3). Accept-qualifying s >= theta + m/2,
    reject-qualifying s < theta - m/2, k consecutive qualifying frames to change state.
    (m=0, k=1) is exactly `instantaneous`; (m=0, k>1) is exactly `debounce(n=k)`;
    (m>0, k=1) is a pure dual threshold; (m>0, k>1) is hysteresis."""
    th, mm = np.asarray(theta, float), np.asarray(m, float)
    lo = th - mm / 2
    return _dwell_loop(S, th + mm / 2, lambda s: s < lo[:, None], np.asarray(k, int))

def sim_trust(S, theta, gain, decay, tau_lo, tau_hi):
    th, g, d = (np.asarray(x, float)[:, None] for x in (theta, gain, decay))
    lo, hi = (np.asarray(x, float)[:, None] for x in (tau_lo, tau_hi))
    nc = th.shape[0]; ns, T = S.shape
    trust = np.ones((nc, ns)); state = np.ones((nc, ns), np.int8)
    out = np.empty((nc, ns, T), np.int8)
    for t in range(T):
        trust = np.clip(trust + g * (S[None, :, t] - th) - d * (trust - 0.5), 0.0, 1.0)
        state = np.where(state == 1, np.where(trust < lo, 0, 1), np.where(trust >= hi, 1, 0)).astype(np.int8)
        out[:, :, t] = state
    return out

def sprt_increment(s, sm):
    mg, sg, mi, si = sm['mu_gen'], sm['sd_gen'], sm['mu_imp'], sm['sd_imp']
    lg = -0.5 * ((s - mg) / sg) ** 2 - np.log(sg)
    li = -0.5 * ((s - mi) / si) ** 2 - np.log(si)
    return lg - li

def sim_sprt(S, A, B, delta, sm):
    A, B, dl = (np.asarray(x, float)[:, None] for x in (A, B, delta))
    inc = sprt_increment(S, sm)
    nc = A.shape[0]; ns, T = S.shape
    llr = np.zeros((nc, ns)); state = np.ones((nc, ns), np.int8)
    out = np.empty((nc, ns, T), np.int8)
    for t in range(T):
        llr = np.clip(llr + inc[None, :, t] + dl, -B, A)
        up, dn = llr >= A, llr <= -B
        state = np.where(up, 1, np.where(dn, 0, state)).astype(np.int8)
        llr = np.where(up | dn, 0.0, llr)
        out[:, :, t] = state
    return out

# --------------------------------------------------------------------------------------------
# Candidate grids
# --------------------------------------------------------------------------------------------
FACTORIAL_MARGINS = (0.0, 0.05, 0.1, 0.2)          # PREREGISTRATION_v2 §3
FACTORIAL_DWELLS = (1, 2, 3, 5, 10)
SPRT_A = tuple(np.geomspace(0.5, 64, 15).tolist())  # C4: log-spaced over [0.5, 64], 15 values
SPRT_B = SPRT_A
SPRT_DELTA = tuple(np.linspace(-2, 2, 21).tolist())  # C4: 21 values over [-2, 2]

FAMILY_ORDER = ['instantaneous', 'moving_average', 'ewma', 'majority_vote', 'debounce',
                'margin_dual_threshold', 'hysteresis', 'trust_model', 'trust_model_single', 'sprt']

def cell_name(m, k):
    return f'm{m:g}_k{k}'

def cell_class(m, k):
    if m == 0 and k == 1: return 'instantaneous'
    if m == 0: return 'dwell_only'
    if k == 1: return 'margin_only'
    return 'hysteresis'

def family_grid(name, thetas):
    """Tuned-family grids (§4.1). Unchanged from v1 except SPRT (C4) and trust_model_single (C6)."""
    T = list(thetas)
    if name == 'instantaneous':
        return [dict(theta=t) for t in T]
    if name == 'moving_average':
        return [dict(theta=t, w=w) for t in T for w in (3, 5, 10, 20)]
    if name == 'ewma':
        return [dict(theta=t, alpha=a) for t in T for a in (0.1, 0.2, 0.3, 0.5)]
    if name == 'majority_vote':
        return [dict(theta=t, w=w, k=k) for t in T for w, k in ((3, 2), (5, 3), (5, 4), (10, 6), (10, 8))]
    if name == 'debounce':
        return [dict(theta=t, n=n) for t in T for n in (2, 3, 5, 10)]
    if name == 'margin_dual_threshold':
        return [dict(theta=t, margin=m) for t in T for m in (0.05, 0.1, 0.2, 0.4)]
    if name == 'hysteresis':
        return [dict(theta=t, margin=m, ttt_frames=k) for t in T for m in (0.05, 0.1, 0.2) for k in (2, 3, 5, 10)]
    if name == 'trust_model':
        return [dict(theta=t, gain=g, decay=d, tau_lo=0.4, tau_hi=0.6)
                for t in T for g in (0.1, 0.3, 0.6) for d in (0.0, 0.05, 0.2)]
    if name == 'trust_model_single':
        return [dict(theta=t, gain=g, decay=d, tau_lo=0.5, tau_hi=0.5)
                for t in T for g in (0.1, 0.3, 0.6) for d in (0.0, 0.05, 0.2)]
    if name == 'sprt':
        return [dict(A=a, B=b, delta=dl) for a in SPRT_A for b in SPRT_B for dl in SPRT_DELTA]
    raise KeyError(name)

def factorial_grid(thetas, m, k):
    return [dict(theta=t, m=m, k=k) for t in thetas]

def simulate(name, grid, S, sm=None):
    P = lambda key: np.array([g[key] for g in grid])
    if name == 'instantaneous':        return sim_instantaneous(S, P('theta'))
    if name == 'moving_average':       return sim_moving_average(S, P('theta'), P('w'))
    if name == 'ewma':                 return sim_ewma(S, P('theta'), P('alpha'))
    if name == 'majority_vote':        return sim_majority_vote(S, P('theta'), P('w'), P('k'))
    if name == 'debounce':             return sim_debounce(S, P('theta'), P('n'))
    if name == 'margin_dual_threshold':return sim_margin_v1(S, P('theta'), P('margin'))
    if name == 'hysteresis':           return sim_hysteresis_v1(S, P('theta'), P('margin'), P('ttt_frames'))
    if name in ('trust_model', 'trust_model_single'):
        return sim_trust(S, P('theta'), P('gain'), P('decay'), P('tau_lo'), P('tau_hi'))
    if name == 'sprt':                 return sim_sprt(S, P('A'), P('B'), P('delta'), sm)
    if name == 'margin_dwell':         return sim_margin_dwell(S, P('theta'), P('m'), P('k'))
    raise KeyError(name)

# --------------------------------------------------------------------------------------------
# C2 reachability: can the mechanism return to AUTHENTICATED at the maximum normalised score?
# --------------------------------------------------------------------------------------------
def reachable(name, p, sm=None, s_max=S_MAX):
    """Returns (reachable: bool, reason: str). Structural check only; uses no outcome data."""
    if name in ('instantaneous', 'moving_average', 'ewma', 'majority_vote', 'debounce'):
        thr = p['theta']
    elif name in ('margin_dual_threshold', 'hysteresis'):
        thr = p['theta'] + p['margin'] / 2
    elif name == 'margin_dwell':
        thr = p['theta'] + p['m'] / 2
    elif name in ('trust_model', 'trust_model_single'):
        drive = p['gain'] * (s_max - p['theta'])
        if drive <= 0:
            return False, 'trust cannot increase at the maximum score'
        t_star = np.inf if p['decay'] == 0 else 0.5 + drive / p['decay']
        return (bool(t_star > p['tau_hi']),
                'ok' if t_star > p['tau_hi'] else f'steady-state trust {t_star:.3f} <= tau_hi {p["tau_hi"]}')
    elif name == 'sprt':
        inc = float(sprt_increment(np.array(s_max), sm)) + p['delta']
        return (inc > 0, 'ok' if inc > 0 else f'LLR increment at max score {inc:.3f} <= 0')
    else:
        raise KeyError(name)
    return (bool(thr <= s_max), 'ok' if thr <= s_max else f'accept threshold {thr:.4f} > {s_max}')

# --------------------------------------------------------------------------------------------
# Calibration aggregate and C1 selection
# --------------------------------------------------------------------------------------------
def pooled_far_frr(states, truth):
    """states (n_cand, n_seq, T), truth (n_seq, T) -> pooled frame-level FAR, FRR per candidate."""
    imp, gen = truth == 0, truth == 1
    far = (states * imp[None]).sum((1, 2)) / max(imp.sum(), 1)
    frr = ((1 - states) * gen[None]).sum((1, 2)) / max(gen.sum(), 1)
    return far.astype(float), frr.astype(float)

def complexity(p):
    """Same definition as v1 (src/calibrate._complexity), extended with the factorial dwell."""
    base = p.get('w', 0) + p.get('n', 0) + p.get('ttt_frames', 0) + p.get('A', 0) + p.get('B', 0)
    if 'm' in p:                       # margin_dwell only; majority_vote's `k` is excluded, as in v1
        base += p['k'] + p['m']
    return base

def select_one_sided(grid, far, frr, reach, target, tol):
    """C1: eligible iff reachable (C2) and target - tol <= FAR <= target. Among eligible: minimum
    calibration FRR, then minimum complexity, then lower calibration FAR, then grid order.
    No substitution: returns (None, record) if nothing is eligible."""
    lo, hi = target - tol, target
    band = (far >= lo - 1e-12) & (far <= hi + 1e-12)
    elig = np.flatnonzero(band & reach)
    rec = dict(target_FAR=target, tolerance=tol, eligible_interval=[lo, hi], n_candidates=len(grid),
               n_rejected_unreachable=int((~reach).sum()), n_in_band=int(band.sum()),
               n_in_band_rejected_unreachable=int((band & ~reach).sum()), n_eligible=int(len(elig)),
               achievable_min_FAR=float(far.min()), achievable_max_FAR=float(far.max()),
               achievable_min_FAR_reachable=float(far[reach].min()) if reach.any() else np.nan,
               achievable_max_FAR_reachable=float(far[reach].max()) if reach.any() else np.nan)
    if len(elig) == 0:
        rec.update(feasible=False, chosen_index=None, chosen_params=None, calib_FAR=np.nan, calib_FRR=np.nan)
        return None, rec
    key = sorted(elig, key=lambda i: (frr[i], complexity(grid[i]), far[i], i))
    i = int(key[0])
    rec.update(feasible=True, chosen_index=i, chosen_params=grid[i], calib_FAR=float(far[i]), calib_FRR=float(frr[i]))
    return i, rec

# --------------------------------------------------------------------------------------------
# Theta grid (unchanged rule from v1, calibration data only)
# --------------------------------------------------------------------------------------------
def theta_grid(cal_scores, cal_truth, cfg, target):
    pooled = cal_scores.ravel(); imp = cal_scores[cal_truth == 0]
    tol = cfg['far_tolerance']
    q_far = 1.0 - np.linspace(max(target - 3 * tol, 1e-4), target + 3 * tol, cfg['n_far_grid'])
    return sorted(set(np.quantile(pooled, cfg['theta_quantiles']).tolist()
                      + np.quantile(imp, np.clip(q_far, 0, 1)).tolist()))

def estimate_score_models(cal_scores, cal_truth):
    """Gaussian score models for SPRT, calibration only (same as src/calibrate.estimate_score_models)."""
    g, i = cal_scores[cal_truth == 1], cal_scores[cal_truth == 0]
    f = lambda x: (float(np.mean(x)), float(max(np.std(x), 1e-3)))
    mg, sg = f(g); mi, si = f(i)
    return dict(mu_gen=mg, sd_gen=sg, mu_imp=mi, sd_imp=si)

# --------------------------------------------------------------------------------------------
# C5 sequence metrics
# --------------------------------------------------------------------------------------------
def sequence_metrics_v2(state, truth, transition_idx, recovery_idx, flip_window=3, stable=3):
    r = MET.evaluate_sequence(state, truth, transition_idx, recovery_idx, flip_window, stable)
    n = r['n_transitions']
    det_cap = recovery_idx - transition_idx           # impostor block length (60 frames)
    rec_cap = len(state) - recovery_idx               # recovery block length (60 frames)
    det, rec = r['detection_latency_frames'], r['recovery_latency_frames']
    r.update(excess_transitions=max(n - 2, 0), fewer_than_2_transitions=int(n < 2),
             detection_failure=int(np.isnan(det)), recovery_failure=int(np.isnan(rec)),
             detection_latency_censored=float(det_cap if np.isnan(det) else det),
             recovery_latency_censored=float(rec_cap if np.isnan(rec) else rec),
             detection_censored_flag=int(np.isnan(det)), recovery_censored_flag=int(np.isnan(rec)),
             detection_censor_cap=int(det_cap), recovery_censor_cap=int(rec_cap))
    return r

# --------------------------------------------------------------------------------------------
# Statistics helpers (no sklearn dependency)
# --------------------------------------------------------------------------------------------
def auc(y, s):
    from scipy.stats import rankdata
    y = np.asarray(y); s = np.asarray(s, float)
    n1, n0 = int((y == 1).sum()), int((y == 0).sum())
    if n1 == 0 or n0 == 0:
        return np.nan
    r = rankdata(s)
    return float((r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))

def bootstrap_mean_ci(v, n_boot=2000, seed=0, alpha=0.05):
    v = np.asarray([x for x in v if np.isfinite(x)], float)
    if len(v) < 2:
        return dict(mean=float(v.mean()) if len(v) else np.nan, lo=np.nan, hi=np.nan, n=int(len(v)))
    rng = np.random.default_rng(seed)
    m = rng.choice(v, size=(n_boot, len(v)), replace=True).mean(1)
    return dict(mean=float(v.mean()), median=float(np.median(v)), lo=float(np.quantile(m, alpha / 2)),
                hi=float(np.quantile(m, 1 - alpha / 2)), n=int(len(v)))

def holm(pvals):
    p = np.asarray(pvals, float); out = np.full(len(p), np.nan)
    ok = np.flatnonzero(np.isfinite(p))
    if len(ok) == 0:
        return out
    order = ok[np.argsort(p[ok])]; m = len(ok); run = 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (m - r) * p[i])); out[i] = run
    return out

def wilcoxon_paired(x, y):
    """Two-sided paired Wilcoxon signed-rank, zero_method='zsplit' (as v1). NaN if degenerate."""
    from scipy import stats
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 5 or np.allclose(x, y):
        return np.nan, np.nan
    w = stats.wilcoxon(x, y, zero_method='zsplit')
    return float(w.statistic), float(w.pvalue)
