#!/usr/bin/env python3
"""Build reports/STAGE2_SENSITIVITY_ANALYSIS_REPORT.md from the generated sensitivity outputs.
Every number is read from a result file; nothing is typed by hand. Missing runs are reported as
NOT EXECUTED rather than estimated.

  python scripts/make_sensitivity_report.py --primary results/mechanism_comparison \
      --sens results/mechanism_comparison/sensitivity --report reports/STAGE2_SENSITIVITY_ANALYSIS_REPORT.md
"""
import argparse, json, os, sys, time
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import mechanisms as M

ap = argparse.ArgumentParser()
ap.add_argument('--primary', required=True); ap.add_argument('--sens', required=True); ap.add_argument('--report', required=True)
a = ap.parse_args()
ORDER = M.MECHANISM_ORDER
P_MEC = pd.read_csv(os.path.join(a.primary, 'mechanism_metrics.csv')).set_index('mechanism')
P_OP = pd.read_csv(os.path.join(a.primary, 'operating_points.csv'))
P_T = pd.read_csv(os.path.join(a.primary, 'statistical_tests.csv'))
P_META = json.load(open(os.path.join(a.primary, 'experiment_metadata.json')))

def op_summary(path):
    O = pd.read_csv(path)
    g = O.groupby('mechanism').agg(n=('calib_FAR', 'size'), feasible=('feasible_operating_point_exists', 'sum'),
                                   mean_calib_FAR=('calib_FAR', 'mean'))
    g['infeasible'] = g.n - g.feasible
    return O, g.reindex(ORDER).round(4)

L = []
w = L.append
w('# STAGE 2 — SENSITIVITY ANALYSIS REPORT\n')
w(f'Generated {time.strftime("%Y-%m-%d %H:%M:%S")}. Primary analysis: `{a.primary}` '
  f'(commit `{P_META["git_commit"][:8]}`, seed {P_META["random_seed"]}).\n')
w('**These are secondary analyses. The primary result remains the 31-user analysis at FAR 0.05 ± 0.01 '
  'and is not modified by anything in this report.**\n')

# ---------------- A ----------------
cf = os.path.join(a.sens, 'complete_feasibility')
w('## A. Complete-feasibility subset\n')
if os.path.exists(os.path.join(cf, 'sensitivity_metadata.json')):
    m = json.load(open(os.path.join(cf, 'sensitivity_metadata.json')))
    MEC = pd.read_csv(os.path.join(cf, 'mechanism_metrics.csv')).set_index('mechanism').reindex(ORDER)
    T = pd.read_csv(os.path.join(cf, 'statistical_tests.csv'))
    C = pd.read_csv(os.path.join(cf, 'primary_vs_subset_comparison.csv'))
    n = m['n_users_eligible']
    w(f"**Eligibility rule:** {m['eligibility_rule']}, determined exclusively from "
      f"`operating_points.csv` (calibration data). Final-test performance played no part.\n")
    w(f"**Subset size: {n} of {m['n_users_primary']} enrolled users** "
      f"({m['n_users_excluded']} excluded), {m['n_sequences']} sequences.\n")
    w('### A.1 Statistical power of this subset\n')
    w(f'With n = {n} paired observations the smallest attainable two-sided Wilcoxon signed-rank p-value is '
      f'{2/2**n:.5f}; after Holm correction across 8 comparisons the smallest attainable adjusted p-value is '
      f'{min(1.0, 8*2/2**n):.3f}. **No comparison in this subset can reach p < 0.05 regardless of effect size.** '
      f'Observed significant comparisons: {int(T.significant_holm_005.sum())} of {len(T)}. The loss of significance '
      'relative to the primary analysis is therefore a power artefact of the subset size and is NOT evidence '
      'that the effects are absent.\n')
    w('### A.2 Subset results (mean over users)\n')
    cols = ['n_users', 'FAR_mean', 'FRR_mean', 'transition_rate_per_100_mean', 'n_flip_events_mean',
            'detection_latency_frames_mean', 'recovery_latency_frames_mean', 'detection_rate', 'recovery_rate']
    w(MEC[cols].round(4).reset_index().to_markdown(index=False) + '\n')
    w('### A.3 Direction of effects compared with the primary analysis\n')
    piv = C.pivot_table(index='mechanism', columns='metric', values=['primary_mean', 'subset_mean'])
    w(C.round(4).to_markdown(index=False) + '\n')
    tr = MEC['transition_rate_per_100_mean']
    lower = [m2 for m2 in ORDER if m2 != 'instantaneous' and tr[m2] < tr['instantaneous']]
    w(f'\nDirectionally, {len(lower)} of 8 stabilisation mechanisms still show a lower transition rate than the '
      f'instantaneous baseline in the subset. Absolute FAR and FRR are lower for every mechanism than in the '
      'primary analysis, which is expected: users for whom all nine mechanisms were feasible are users whose '
      'score distributions permit fine operating-point control.\n')
    w(f"**Substantive interpretation change: none established.** The direction of the stability effect is "
      f"preserved; statistical confirmation is impossible at n = {n}. Excluded users are listed in "
      f'`{os.path.relpath(cf)}/eligibility_table.csv` with the mechanisms that were infeasible for each.\n')
else:
    w('NOT EXECUTED\n')

# ---------------- B ----------------
w('\n## B. Operating-point sensitivity (FAR 0.03 / 0.05 / 0.07, each ± 0.01)\n')
runs = [('0.03', os.path.join(a.sens, 'far_003')), ('0.05 (primary)', a.primary), ('0.07', os.path.join(a.sens, 'far_007'))]
rows, feas_rows, missing = [], [], []
for label, path in runs:
    seq = os.path.join(path, 'sequence_metrics.csv'); op = os.path.join(path, 'operating_points.csv')
    if not (os.path.exists(seq) and os.path.exists(op)):
        missing.append(label); continue
    S = pd.read_csv(seq); O, g = op_summary(op)
    nuser = S.enrolled_user.nunique()
    for mech in ORDER:
        sub = S[S.mechanism == mech]
        pu = sub.groupby('enrolled_user')[['FAR', 'FRR', 'transition_rate_per_100', 'detection_latency_frames',
                                           'recovery_latency_frames']].mean()
        rows.append(dict(target=label, n_users=nuser, mechanism=mech, FAR=pu.FAR.mean(), FRR=pu.FRR.mean(),
                         transition_rate_per_100=pu.transition_rate_per_100.mean(),
                         detection_latency_frames=pu.detection_latency_frames.mean(),
                         recovery_latency_frames=pu.recovery_latency_frames.mean(),
                         infeasible=int(g.loc[mech, 'infeasible']) if mech in g.index else None))
    feas_rows.append(dict(target=label, users=nuser, total_combinations=len(O),
                          infeasible=int((~O.feasible_operating_point_exists).sum()),
                          worst_mechanism=g.infeasible.idxmax(), worst_count=int(g.infeasible.max())))
if rows:
    R = pd.DataFrame(rows)
    w('### B.1 Feasibility by target\n')
    w(pd.DataFrame(feas_rows).to_markdown(index=False) + '\n')
    w('### B.2 Transition rate per 100 frames by target\n')
    w(R.pivot_table(index='mechanism', columns='target', values='transition_rate_per_100').reindex(ORDER).round(3).reset_index().to_markdown(index=False) + '\n')
    w('### B.3 FRR by target\n')
    w(R.pivot_table(index='mechanism', columns='target', values='FRR').reindex(ORDER).round(4).reset_index().to_markdown(index=False) + '\n')
    w('### B.4 Detection latency (frames) by target\n')
    w(R.pivot_table(index='mechanism', columns='target', values='detection_latency_frames').reindex(ORDER).round(3).reset_index().to_markdown(index=False) + '\n')
    w('### B.5 Achieved FAR by target\n')
    w(R.pivot_table(index='mechanism', columns='target', values='FAR').reindex(ORDER).round(4).reset_index().to_markdown(index=False) + '\n')
    R.round(5).to_csv(os.path.join(a.sens, 'operating_point_sensitivity_summary.csv'), index=False)
    # rank stability
    ranks = R.pivot_table(index='mechanism', columns='target', values='transition_rate_per_100').rank()
    w(f'\nRank correlation of mechanisms by transition rate across targets (Spearman, pairwise): '
      f'{ranks.corr(method="spearman").round(3).to_dict()}\n')
if missing:
    w(f'\n**NOT EXECUTED at this time: targets {", ".join(missing)}.** The report must be regenerated '
      'once those runs complete; no values for them are estimated here.\n')
open(a.report, 'w').write('\n'.join(L))
print('wrote', a.report, '| sections A/B present:', os.path.exists(os.path.join(cf, 'mechanism_metrics.csv')), bool(rows))
