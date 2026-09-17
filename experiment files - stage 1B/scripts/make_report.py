#!/usr/bin/env python3
"""Build the ablation summary, figures and the execution report from whatever runs exist.
Works on partial results; it never invents a run that was not executed.
  python scripts/make_report.py --out results/primary --report reports/STAGE2_EXECUTION_REPORT.md
"""
import argparse, json, os, sys, glob, time
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import evaluate, features

ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--report', required=True)
ap.add_argument('--figdir', default='figures'); a = ap.parse_args()
R = pd.read_csv(os.path.join(a.out, 'per_run_results.csv'))
meta = json.load(open(os.path.join(a.out, 'experiment_metadata.json')))
cfg = meta['config']; planned = meta['planned_runs']
os.makedirs(a.figdir, exist_ok=True)

agg = []
for (f, m), g in R.groupby(['feature_set', 'model']):
    ci = {k: evaluate.bootstrap_ci(g[c], seed=cfg['seed']) for k, c in
          [('AUC', 'AUC'), ('EER', 'EER_test_oracle'), ('FAR', 'cal_EER_threshold_FAR'),
           ('FRR', 'cal_EER_threshold_FRR'), ('FAR1pct_FRR', 'cal_FAR0.01_FRR')]}
    agg.append(dict(feature_set=f, model=m, n_users=len(g),
                    **{f'{k}_{s}': ci[k][s] for k in ci for s in ('mean', 'lo', 'hi')},
                    runtime_median_s=float(g.total_seconds.median())))
A = pd.DataFrame(agg).sort_values(['model', 'feature_set'])
A.to_csv(os.path.join(a.out, 'ablation_summary.csv'), index=False)

for metric, col in [('AUC', 'AUC'), ('EER', 'EER_test_oracle')]:
    order = sorted(R.feature_set.unique()); models = sorted(R.model.unique())
    fig, ax = plt.subplots(figsize=(11, 4.5))
    data = [R.loc[(R.feature_set == f) & (R.model == m), col].dropna().values for f in order for m in models]
    ax.boxplot(data)
    ax.set_xticks(range(1, len(data) + 1))
    ax.set_xticklabels([f'{f}\n{m[:4]}' for f in order for m in models])
    ax.set_ylabel(metric); ax.set_title(f'Stage 2 {metric} per enrolled user (unseen impostors, n={R.enrolled_user.nunique()} users)')
    plt.xticks(rotation=45, ha='right', fontsize=7); plt.tight_layout()
    fig.savefig(os.path.join(a.figdir, f'{metric}_by_feature_set.png'), dpi=150); plt.close(fig)

checks = []
for p in glob.glob(os.path.join(a.out, 'run__*.json')):
    checks += json.load(open(p))['leakage_checks']
C = pd.DataFrame(checks).groupby('check')['passed'].agg(['sum', 'size']).reset_index() if checks else pd.DataFrame()
fails = json.load(open(os.path.join(a.out, 'failures.json'))) if os.path.exists(os.path.join(a.out, 'failures.json')) else []

def tbl(df, cols=None, r=4):
    d = df[cols] if cols else df
    return d.round(r).to_markdown(index=False)

with open(a.report, 'w') as fh:
    w = fh.write
    w(f"# STAGE 2 EXECUTION REPORT (auto-generated)\n\nGenerated {time.strftime('%Y-%m-%d %H:%M:%S')} from `{a.out}`. "
      "Every number below comes from an executed run; nothing is projected.\n\n")
    w(f"## Status\n\n- Config: **{cfg['name']}**\n- Planned runs: **{planned}**  ({R.enrolled_user.nunique()} of "
      f"{len(json.load(open(os.path.join(a.out,'manifests','participant_pools.json')))['enrolled_candidates'])} eligible users complete)\n"
      f"- **EXECUTED: {len(R)} runs**, failed: {len(fails)}\n"
      f"- Total compute recorded: {R.total_seconds.sum()/3600:.2f} h\n"
      f"- Environment: {meta['environment']['python']}, sklearn {meta['environment']['sklearn']}, commit {meta['environment']['git_commit'][:8]}\n"
      f"- Seed: {cfg['seed']}\n\n")
    if len(R) < planned:
        w(f"> **INCOMPLETE RUN.** {planned - len(R)} of {planned} runs were not executed. Re-run with `--resume` "
          "or complete the grid in Colab; the summary below covers only the executed subset.\n\n")
    w("## Ablation summary (mean over enrolled users, bootstrap 95% CI)\n\n")
    w(tbl(A, ['feature_set', 'model', 'n_users', 'AUC_mean', 'AUC_lo', 'AUC_hi', 'EER_mean', 'EER_lo', 'EER_hi',
              'FAR_mean', 'FRR_mean']) + "\n\n")
    w("Operating point for FAR/FRR: threshold from the calibration EER point. `EER_mean` is the test-set oracle EER "
      "(reported for reference; never used to set an operating point).\n\n")
    w("## Feature-set definitions\n\n")
    for k in cfg['feature_sets']:
        w(f"- **{k}** ({int(R.loc[R.feature_set==k,'n_features'].iloc[0]) if (R.feature_set==k).any() else '?'} features): {features.FEATURE_SETS[k]['note']}\n")
    w("\n## Protocol sizes (median across executed runs)\n\n")
    w(tbl(R[['n_genuine_train', 'n_genuine_calib', 'n_genuine_test', 'n_impostor_train', 'n_impostor_calib',
             'n_impostor_test', 'n_test_impostor_participants', 'n_test_segments', 'genuine_test_span_hours']]
          .median().to_frame('median').reset_index().rename(columns={'index': 'quantity'}), r=1) + "\n\n")
    w("## Leakage checks\n\n")
    if len(C):
        C.columns = ['check', 'passed', 'evaluated']
        w(tbl(C) + "\n\nAll checks abort the run on failure, so any run present in the results passed all of them.\n\n")
    w("## Failures\n\n" + (f"{len(fails)} run(s) failed; see `failures.json`.\n\n" if fails else "None.\n\n"))
    w("## Per-user variability (executed users)\n\n")
    piv = R.pivot_table(index='enrolled_user', columns=['model', 'feature_set'], values='EER_test_oracle')
    w(f"EER range across users, gradient boosting, F1_ALL: "
      f"{R.query('model==\"gradient_boosting\" and feature_set==\"F1_ALL\"').EER_test_oracle.min():.4f} to "
      f"{R.query('model==\"gradient_boosting\" and feature_set==\"F1_ALL\"').EER_test_oracle.max():.4f}\n\n")
    w("## Files\n\n`per_run_results.csv`, `ablation_summary.csv`, `run__*.json`, `per_impostor/`, `score_streams/`, "
      "`manifests/`, `experiment_metadata.json`, `logs/run.log`, figures in `figures/`.\n")
print('wrote', a.report, '| runs:', len(R), 'users:', R.enrolled_user.nunique())
