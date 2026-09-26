#!/usr/bin/env python3
"""SENSITIVITY ANALYSIS A — complete-feasibility subset.

Restricts the participant-level analysis to enrolled users for whom ALL nine mechanisms attained a
feasible calibration operating point. Eligibility is derived EXCLUSIVELY from
`operating_points.csv` (calibration data); final-test performance plays no part in it.

The primary 31-user analysis is not modified: this script only reads the primary outputs and writes
to a separate sensitivity directory.

  python scripts/sensitivity_complete_feasibility.py --primary results/mechanism_comparison \
      --out results/mechanism_comparison/sensitivity/complete_feasibility
"""
import argparse, json, os, sys, time
import numpy as np, pandas as pd
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import mechanisms as M, evaluate

ap = argparse.ArgumentParser()
ap.add_argument('--primary', required=True); ap.add_argument('--out', required=True)
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)

O = pd.read_csv(os.path.join(a.primary, 'operating_points.csv'))
S = pd.read_csv(os.path.join(a.primary, 'sequence_metrics.csv'))
meta = json.load(open(os.path.join(a.primary, 'experiment_metadata.json')))
n_mech = O.mechanism.nunique()

feas = O.groupby('enrolled_user').feasible_operating_point_exists.sum()
eligible = sorted(feas[feas == n_mech].index)
excluded = sorted(feas[feas < n_mech].index)
elig_tbl = (O.groupby('enrolled_user')
              .agg(n_mechanisms=('mechanism', 'nunique'),
                   n_feasible=('feasible_operating_point_exists', 'sum')).reset_index())
elig_tbl['eligible_complete_feasibility'] = elig_tbl.enrolled_user.isin(eligible)
infeas_by_user = (O[~O.feasible_operating_point_exists]
                  .groupby('enrolled_user').mechanism.apply(lambda s: ';'.join(sorted(s))).rename('infeasible_mechanisms'))
elig_tbl = elig_tbl.merge(infeas_by_user, on='enrolled_user', how='left')
elig_tbl.to_csv(os.path.join(a.out, 'eligibility_table.csv'), index=False)

METRICS = ['FAR', 'FRR', 'n_transitions', 'transition_rate_per_100', 'n_flip_events',
           'mean_run_length_frames', 'detection_latency_frames', 'recovery_latency_frames',
           'lockout_fraction_during_genuine']
ORDER = [m for m in M.MECHANISM_ORDER if m in set(S.mechanism)]
Ssub = S[S.enrolled_user.isin(eligible)].copy()
Ssub['detected'] = Ssub.detection_latency_frames.notna(); Ssub['recovered'] = Ssub.recovery_latency_frames.notna()
P = Ssub.groupby(['enrolled_user', 'mechanism'])[METRICS + ['detected', 'recovered']].mean().reset_index()
P.to_csv(os.path.join(a.out, 'participant_metrics.csv'), index=False)
Ssub.to_csv(os.path.join(a.out, 'sequence_metrics.csv'), index=False)

rows = []
for m in ORDER:
    g = P[P.mechanism == m]
    r = dict(mechanism=m, n_users=len(g), detection_rate=float(g.detected.mean()), recovery_rate=float(g.recovered.mean()),
             n_users_with_recovery_observed=int(g.recovery_latency_frames.notna().sum()))
    for k in METRICS:
        ci = evaluate.bootstrap_ci(g[k].dropna(), seed=meta['random_seed'])
        r[f'{k}_mean'], r[f'{k}_lo'], r[f'{k}_hi'] = ci['mean'], ci['lo'], ci['hi']
        r[f'{k}_n'] = int(g[k].notna().sum())
    rows.append(r)
MEC = pd.DataFrame(rows); MEC.to_csv(os.path.join(a.out, 'mechanism_metrics.csv'), index=False)

base = 'instantaneous'; tests = []
for k in METRICS:
    piv = P.pivot_table(index='enrolled_user', columns='mechanism', values=k)
    raw = []
    for m in ORDER:
        if m == base: continue
        d = piv[[base, m]].dropna()
        if len(d) < 5 or np.allclose(d[base], d[m]):
            raw.append((m, np.nan, np.nan, len(d), float((d[m] - d[base]).mean()) if len(d) else np.nan)); continue
        w = stats.wilcoxon(d[m], d[base], zero_method='zsplit')
        raw.append((m, float(w.statistic), float(w.pvalue), len(d), float((d[m] - d[base]).mean())))
    ps = [p for _, _, p, _, _ in raw]
    valid = len([q for q in ps if not np.isnan(q)])
    order = np.argsort([1e9 if np.isnan(p) else p for p in ps]); holm = [np.nan] * len(ps); running = 0
    for rank, i in enumerate(order):
        if np.isnan(ps[i]): continue
        running = max(running, min(1.0, ps[i] * (valid - rank))); holm[i] = running
    for (m, w, p, n, diff), hp in zip(raw, holm):
        tests.append(dict(metric=k, mechanism=m, baseline=base, n_users=n, mean_difference=diff,
                          wilcoxon_W=w, p_value=p, p_holm=hp,
                          significant_holm_005=bool(hp is not None and not np.isnan(hp) and hp < 0.05)))
T = pd.DataFrame(tests); T.to_csv(os.path.join(a.out, 'statistical_tests.csv'), index=False)

# comparison with the primary analysis (primary is NOT modified)
PM = pd.read_csv(os.path.join(a.primary, 'mechanism_metrics.csv')).set_index('mechanism')
PT = pd.read_csv(os.path.join(a.primary, 'statistical_tests.csv'))
cmp_rows = []
for m in ORDER:
    for k in ['FAR', 'FRR', 'transition_rate_per_100', 'detection_latency_frames']:
        pr = PT[(PT.metric == k) & (PT.mechanism == m)]
        sr = T[(T.metric == k) & (T.mechanism == m)]
        cmp_rows.append(dict(mechanism=m, metric=k,
                             primary_mean=float(PM.loc[m, f'{k}_mean']),
                             subset_mean=float(MEC.set_index('mechanism').loc[m, f'{k}_mean']),
                             primary_significant=bool(pr.significant_holm_005.iloc[0]) if len(pr) else None,
                             subset_significant=bool(sr.significant_holm_005.iloc[0]) if len(sr) else None))
C = pd.DataFrame(cmp_rows)
C['significance_changed'] = C.primary_significant.ne(C.subset_significant)
C.to_csv(os.path.join(a.out, 'primary_vs_subset_comparison.csv'), index=False)

json.dump(dict(analysis='complete-feasibility subset (SENSITIVITY, not primary)',
               generated=time.strftime('%Y-%m-%dT%H:%M:%S'), primary_dir=os.path.abspath(a.primary),
               eligibility_rule=f'all {n_mech} mechanisms feasible at the calibration operating point',
               eligibility_source='operating_points.csv (calibration only; no final-test information)',
               n_users_primary=int(S.enrolled_user.nunique()), n_users_eligible=len(eligible),
               n_users_excluded=len(excluded), excluded_users=excluded,
               n_sequences=int(Ssub.sequence_id.nunique()), seed=meta['random_seed'],
               git_commit=meta['git_commit'], target_far=meta['operating_point']['target_FAR'],
               tolerance=meta['operating_point']['tolerance'],
               significance_changes=int(C.significance_changed.sum())),
          open(os.path.join(a.out, 'sensitivity_metadata.json'), 'w'), indent=2)
print(f'eligible users: {len(eligible)}/{S.enrolled_user.nunique()}; excluded: {len(excluded)}')
print(MEC[['mechanism', 'n_users', 'FAR_mean', 'FRR_mean', 'transition_rate_per_100_mean',
           'detection_latency_frames_mean', 'recovery_rate']].round(4).to_string(index=False))
print('\nsignificance changes vs primary:', int(C.significance_changed.sum()))
print(C[C.significance_changed].to_string(index=False))
