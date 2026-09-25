"""Matched operating-point calibration.

Every mechanism is tuned on CALIBRATION sequences only (calibration partition of the enrolled
user + impostor participants from the calibration pool, all disjoint from the fitting pool and
from the final-test impostors). The identical rule is applied to every mechanism:

    select the parameter set whose calibration frame-level FAR is closest to the common target
    FAR, subject to FAR <= target + tolerance;
    tie-break 1: lower calibration FRR;
    tie-break 2: fewer parameters / smaller temporal window (simpler mechanism);
    if no parameter set satisfies the constraint, take the lowest achievable FAR and flag it.

Test sequences are never used here.
"""
import numpy as np
from . import mechanisms as M, metrics

def _complexity(params):
    return (params.get('w', 0) + params.get('n', 0) + params.get('ttt_frames', 0)
            + params.get('A', 0) + params.get('B', 0))

def calibrate_mechanism(name, streams, target_far, tolerance, thetas, score_models=None):
    """streams: list of (scores, truth). Returns (best_params, record)."""
    rows = []
    for params in M.parameter_grid(name, thetas, score_models):
        m = M.build(name, params)
        fa = fr = ni = ng = 0
        for scores, truth in streams:
            st = m.run(scores)
            s = metrics.security(st, truth)
            fa += s['false_accept_frames']; fr += s['false_reject_frames']
            ni += s['n_impostor_frames']; ng += s['n_genuine_frames']
        rows.append(dict(params=params, FAR=fa / max(ni, 1), FRR=fr / max(ng, 1), complexity=_complexity(params)))
    feasible = [r for r in rows if r['FAR'] <= target_far + tolerance]
    flagged = not feasible
    pool = feasible if feasible else rows
    best = sorted(pool, key=lambda r: (abs(r['FAR'] - target_far), r['FRR'], r['complexity']))[0]
    return best['params'], dict(mechanism=name, chosen_params=best['params'], calib_FAR=float(best['FAR']),
                                calib_FRR=float(best['FRR']), target_FAR=target_far, tolerance=tolerance,
                                n_candidates=len(rows), constraint_satisfied=not flagged,
                                achievable_min_FAR=float(min(r['FAR'] for r in rows)))

def estimate_score_models(streams):
    """Gaussian score models for SPRT, estimated on CALIBRATION streams only."""
    g = np.concatenate([s[t == 1] for s, t in streams]); i = np.concatenate([s[t == 0] for s, t in streams])
    f = lambda x: (float(np.mean(x)), float(max(np.std(x), 1e-3)))
    mg, sg = f(g); mi, si = f(i)
    return dict(mu_gen=mg, sd_gen=sg, mu_imp=mi, sd_imp=si)
