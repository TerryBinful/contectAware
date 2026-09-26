"""POST HOC, NOT IN THE FROZEN PLAN.

Reproduces the paired descriptives reported in Section 5.1 of the paper for the selected
hysteresis cell (cell_H) against the selected dwell-only cell (cell_D) and against the
selected margin-only cell (cell_M), at target FAR 0.05.

These quantities were computed during review. They are NOT part of the preregistered
confirmatory analysis (docs/Stage2/PREREGISTRATION_v2.md), which tests excess transitions
(C1) plus non-inferiority on FRR (C2) and detection failure (C3) only. Nothing here may
be read as a confirmatory test: no p-values, no Holm correction, no decision rule. The
CIs are descriptive bootstrap intervals over participants.

Method, matching the frozen pipeline exactly:
  * participants are paired -- a participant contributes only if BOTH cells were feasible;
  * the statistic is the mean of the per-participant paired difference (H minus comparator);
  * the interval is the project's own routine, src.decision_v2.bootstrap_mean_ci,
    with n_boot = 2000 and seed 20260918 (one seed for every metric and both
    comparisons, so the numbers are reproducible from this file alone).

Sources (read only):
  analysis/primary/cell_selection.csv        -> which cell each participant contributes
  analysis/factorial/participant_metrics.csv -> the values, rows with target == 0.05
"""
import os, sys, json
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _style import ANALYSIS, HERE

REPO = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'experiment_Files', 'Stage2'))
import src.decision_v2 as D                                       # noqa: E402

SEED, N_BOOT, TARGET = 20260918, 2000, 0.05
METRICS = ['recovery_failure', 'recovery_latency_censored',
           'lockout_fraction_during_genuine', 'FAR', 'detection_latency_censored']
# What Section 5.1 of the paper reports for cell_H vs cell_D, for comparison only.
PAPER_HD = {
    'recovery_failure': (0.103, 0.033, 0.189),
    'recovery_latency_censored': (7.99, 3.46, 13.37),
    'lockout_fraction_during_genuine': (0.074, 0.034, 0.119),
    'FAR': (0.002, -0.012, 0.016),
    'detection_latency_censored': (0.50, -0.29, 1.24),
}

SEL = pd.read_csv(os.path.join(ANALYSIS, 'primary', 'cell_selection.csv'))
PM = pd.read_csv(os.path.join(ANALYSIS, 'factorial', 'participant_metrics.csv'))
PM = PM[PM.target == TARGET].set_index(['enrolled_user', 'cell'])


def value(user, cell, metric):
    if not isinstance(cell, str) or (user, cell) not in PM.index:
        return np.nan
    return float(PM.loc[(user, cell), metric])


rows, prov = [], {}
for comp in ('D', 'M'):
    pair = SEL.dropna(subset=['cell_H', f'cell_{comp}'])
    users = pair.enrolled_user.tolist()
    prov[comp] = dict(
        n_users_paired=len(users),
        n_users_without_H=int(SEL.cell_H.isna().sum()),
        n_users_without_comparator=int(SEL[f'cell_{comp}'].isna().sum()),
        n_users_total=int(len(SEL)))
    for metric in METRICS:
        h = np.array([value(u, c, metric) for u, c in zip(users, pair.cell_H)])
        k = np.array([value(u, c, metric) for u, c in zip(users, pair[f'cell_{comp}'])])
        ok = np.isfinite(h) & np.isfinite(k)
        ci = D.bootstrap_mean_ci(h[ok] - k[ok], n_boot=N_BOOT, seed=SEED)
        rows.append(dict(comparison=f'cell_H vs cell_{comp}', metric=metric,
                         n_pairs=int(ok.sum()),
                         mean_H=float(np.mean(h[ok])), mean_comp=float(np.mean(k[ok])),
                         diff_mean=ci['mean'], diff_median=ci['median'],
                         ci_lo=ci['lo'], ci_hi=ci['hi'],
                         excludes_zero=bool(ci['lo'] > 0 or ci['hi'] < 0)))

R = pd.DataFrame(rows)
out_csv = os.path.join(HERE, 'posthoc_cellH_descriptives.csv')
R.to_csv(out_csv, index=False)

# ---- agreement with what the paper reports (cell_H vs cell_D only) ---------------
diffs = []
for metric, (pm_, plo, phi) in PAPER_HD.items():
    r = R[(R.comparison == 'cell_H vs cell_D') & (R.metric == metric)].iloc[0]
    dp = abs(r.diff_mean - pm_)
    diffs.append(dict(metric=metric,
                      reproduced=f'{r.diff_mean:+.3f} [{r.ci_lo:.3f}, {r.ci_hi:.3f}]',
                      paper=f'{pm_:+.3f} [{plo:.3f}, {phi:.3f}]',
                      point_estimate_abs_gap=round(float(dp), 6),
                      point_estimate_matches_to_3dp=bool(round(r.diff_mean, 3) == round(pm_, 3)),
                      ci_lo_gap=round(float(abs(r.ci_lo - plo)), 4),
                      ci_hi_gap=round(float(abs(r.ci_hi - phi)), 4)))
AG = pd.DataFrame(diffs)
AG.to_csv(os.path.join(HERE, 'posthoc_cellH_vs_paper.csv'), index=False)

json.dump(dict(label='POST HOC, NOT IN THE FROZEN PLAN', seed=SEED, n_boot=N_BOOT,
               target_FAR=TARGET, pairing=prov,
               routine='src.decision_v2.bootstrap_mean_ci (the project bootstrap)'),
          open(os.path.join(HERE, '_posthoc_provenance.json'), 'w'), indent=2)

pd.set_option('display.width', 200)
print('\nPOST HOC, NOT IN THE FROZEN PLAN  (target FAR %.2f, seed %d, %d resamples)\n'
      % (TARGET, SEED, N_BOOT))
for comp in ('D', 'M'):
    p = prov[comp]
    print(f"cell_H vs cell_{comp}: {p['n_users_paired']} paired participants of "
          f"{p['n_users_total']} "
          f"({p['n_users_without_H']} without an H cell, "
          f"{p['n_users_without_comparator']} without a {comp} cell)")
print()
print(R.to_string(index=False, float_format=lambda x: f'{x:.4f}'))
print('\nAgreement with the values printed in Section 5.1 (cell_H vs cell_D):\n')
print(AG.to_string(index=False))
print(f'\nwrote {os.path.basename(out_csv)} and posthoc_cellH_vs_paper.csv')
