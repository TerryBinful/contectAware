"""Matched operating-point calibration.

Every mechanism is tuned on CALIBRATION sequences only (calibration partition of the enrolled
user + impostor participants from the calibration pool, all disjoint from the fitting pool and
from the final-test impostors). The identical rule is applied to every mechanism:

    A candidate is FEASIBLE only if   target - tolerance <= calibration FAR <= target + tolerance.
    (A one-sided "FAR <= upper" rule is NOT a valid reading of target +/- tolerance: it admits
    FAR = 0 candidates, which are not matched to the operating point at all.)

    Among feasible candidates:
      1. calibration FAR closest to the target;
      2. tie-break: lower calibration FRR;
      3. tie-break: simpler parameters (smaller windows/thresholds).

    If NO candidate is feasible, nothing is silently substituted: the nearest achievable candidate
    is used, and the record states that no feasible operating point existed, the nearest achievable
    FAR, and whether it lies above or below the interval. Infeasible cases are counted per mechanism
    in the final report. Final-test data are never used here.

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
    lower, upper = target_far - tolerance, target_far + tolerance
    feasible = [r for r in rows if lower <= r['FAR'] <= upper]
    if feasible:
        best = sorted(feasible, key=lambda r: (abs(r['FAR'] - target_far), r['FRR'], r['complexity']))[0]
        direction = 'within_interval'
    else:
        best = sorted(rows, key=lambda r: (abs(r['FAR'] - target_far), r['FRR'], r['complexity']))[0]
        direction = 'below_interval' if best['FAR'] < lower else 'above_interval'
    fars = [r['FAR'] for r in rows]
    return best['params'], dict(mechanism=name, chosen_params=best['params'], calib_FAR=float(best['FAR']),
                                calib_FRR=float(best['FRR']), target_FAR=target_far, tolerance=tolerance,
                                feasible_interval=[float(lower), float(upper)],
                                n_candidates=len(rows), n_feasible_candidates=len(feasible),
                                feasible_operating_point_exists=bool(feasible),
                                constraint_satisfied=bool(feasible), nearest_candidate_direction=direction,
                                achievable_min_FAR=float(min(fars)), achievable_max_FAR=float(max(fars)))

def estimate_score_models(streams):
    """Gaussian score models for SPRT, estimated on CALIBRATION streams only."""
    g = np.concatenate([s[t == 1] for s, t in streams]); i = np.concatenate([s[t == 0] for s, t in streams])
    f = lambda x: (float(np.mean(x)), float(max(np.std(x), 1e-3)))
    mg, sg = f(g); mi, si = f(i)
    return dict(mu_gen=mg, sd_gen=sg, mu_imp=mi, sd_imp=si)
