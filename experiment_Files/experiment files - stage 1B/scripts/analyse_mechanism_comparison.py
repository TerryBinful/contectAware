#!/usr/bin/env python3
"""Statistical analysis, figures and tables for the post-pivot mechanism comparison.

Unit of analysis = ENROLLED USER (sequence metrics are averaged within user first), so the
repeated-measures structure is preserved and frames are not treated as independent.
Comparisons are paired Wilcoxon signed-rank tests of each mechanism against the instantaneous
baseline, with Holm correction across the 8 comparisons per metric. Tests are fixed in advance
in this script, not chosen after inspecting results.

  python scripts/analyse_mechanism_comparison.py --out results/mechanism_comparison
"""
import argparse, json, os, sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import mechanisms as M, evaluate

ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); a = ap.parse_args()
OUT = a.out; FIG = os.path.join(OUT, 'figures'); TAB = os.path.join(OUT, 'tables')
os.makedirs(FIG, exist_ok=True); os.makedirs(TAB, exist_ok=True)
S = pd.read_csv(os.path.join(OUT, 'sequence_metrics.csv'))
METRICS = ['FAR', 'FRR', 'n_transitions', 'transition_rate_per_100', 'n_flip_events',
           'mean_run_length_frames', 'detection_latency_frames', 'recovery_latency_frames',
           'lockout_fraction_during_genuine']
ORDER = [m for m in M.MECHANISM_ORDER if m in set(S.mechanism)]

# per-user means (latencies: NaN = never detected/recovered; reported separately as a rate)
S['detected'] = S.detection_latency_frames.notna(); S['recovered'] = S.recovery_latency_frames.notna()
P = S.groupby(['enrolled_user', 'mechanism'])[METRICS + ['detected', 'recovered']].mean().reset_index()
P.to_csv(os.path.join(OUT, 'participant_metrics.csv'), index=False)

rows = []
for m in ORDER:
    g = P[P.mechanism == m]
    r = dict(mechanism=m, n_users=len(g), n_sequences=int((S.mechanism == m).sum()),
             detection_rate=float(g.detected.mean()), recovery_rate=float(g.recovered.mean()))
    for k in METRICS:
        ci = evaluate.bootstrap_ci(g[k].dropna(), seed=0)
        r[f'{k}_mean'], r[f'{k}_lo'], r[f'{k}_hi'] = ci['mean'], ci['lo'], ci['hi']
        r[f'{k}_median'] = float(g[k].median())
    rows.append(r)
MEC = pd.DataFrame(rows)
MEC.to_csv(os.path.join(OUT, 'mechanism_metrics.csv'), index=False)

# paired tests vs the instantaneous baseline
base = 'instantaneous'; tests = []
for k in METRICS:
    piv = P.pivot_table(index='enrolled_user', columns='mechanism', values=k)
    if base not in piv: continue
    raw = []
    for m in ORDER:
        if m == base or m not in piv: continue
        d = piv[[base, m]].dropna()
        if len(d) < 5 or np.allclose(d[base], d[m]):
            raw.append((m, np.nan, np.nan, len(d), float((d[m] - d[base]).mean()))); continue
        w = stats.wilcoxon(d[m], d[base], zero_method='zsplit')
        raw.append((m, float(w.statistic), float(w.pvalue), len(d), float((d[m] - d[base]).mean())))
    ps = [p for _, _, p, _, _ in raw]
    order = np.argsort([1e9 if np.isnan(p) else p for p in ps]); holm = [np.nan] * len(ps); running = 0
    for rank, i in enumerate(order):
        if np.isnan(ps[i]): continue
        running = max(running, min(1.0, ps[i] * (len([q for q in ps if not np.isnan(q)]) - rank)))
        holm[i] = running
    for (m, w, p, n, diff), hp in zip(raw, holm):
        d = piv[[base, m]].dropna()
        tests.append(dict(metric=k, mechanism=m, baseline=base, n_users=n, mean_difference=diff,
                          wilcoxon_W=w, p_value=p, p_holm=hp,
                          significant_holm_005=bool(hp is not None and not np.isnan(hp) and hp < 0.05)))
T = pd.DataFrame(tests); T.to_csv(os.path.join(OUT, 'statistical_tests.csv'), index=False)

# transition-level table
S.groupby('mechanism')[['detection_latency_frames', 'recovery_latency_frames', 'lockout_fraction_during_genuine']] \
 .describe().to_csv(os.path.join(OUT, 'transition_metrics.csv'))

def bar(metric, ylabel, fname, logy=False):
    g = MEC.set_index('mechanism').loc[ORDER]
    fig, ax = plt.subplots(figsize=(9, 4.2))
    y = g[f'{metric}_mean']; lo = y - g[f'{metric}_lo']; hi = g[f'{metric}_hi'] - y
    ax.bar(range(len(g)), y, yerr=[lo.clip(lower=0), hi.clip(lower=0)], capsize=3, color='#4C72B0')
    ax.set_xticks(range(len(g))); ax.set_xticklabels(ORDER, rotation=35, ha='right', fontsize=8)
    ax.set_ylabel(ylabel); ax.set_title(f'{ylabel} by mechanism (mean over {g.n_users.iloc[0]} users, 95% CI)')
    if logy: ax.set_yscale('log')
    plt.tight_layout(); fig.savefig(os.path.join(FIG, fname), dpi=150); plt.close(fig)

bar('FAR', 'False acceptance rate (frames)', 'fig1_mechanism_vs_FAR.png')
bar('FRR', 'False rejection rate (frames)', 'fig2_mechanism_vs_FRR.png')
bar('transition_rate_per_100', 'State transitions per 100 frames', 'fig3_mechanism_vs_transition_rate.png')
bar('detection_latency_frames', 'Detection latency (frames ~ minutes)', 'fig4_mechanism_vs_detection_latency.png')
bar('recovery_latency_frames', 'Recovery latency (frames ~ minutes)', 'fig5_mechanism_vs_recovery_latency.png')

# security-stability trade-off
fig, ax = plt.subplots(figsize=(6.5, 5))
g = MEC.set_index('mechanism').loc[ORDER]
ax.scatter(g.FAR_mean, g.transition_rate_per_100_mean, s=45, color='#C44E52')
for m in ORDER:
    ax.annotate(m, (g.loc[m, 'FAR_mean'], g.loc[m, 'transition_rate_per_100_mean']), fontsize=7,
                xytext=(4, 3), textcoords='offset points')
ax.set_xlabel('FAR (frames)'); ax.set_ylabel('transitions per 100 frames')
ax.set_title('Security-stability trade-off at the matched operating point')
plt.tight_layout(); fig.savefig(os.path.join(FIG, 'fig6_security_stability_tradeoff.png'), dpi=150); plt.close(fig)

# representative decision streams for one user/sequence
try:
    ex = S[S.sequence_id == sorted(S.sequence_id.unique())[0]]
    fig, ax = plt.subplots(figsize=(9, 3.4))
    ax.bar(range(len(ORDER)), [ex[ex.mechanism == m].n_transitions.mean() for m in ORDER], color='#55A868')
    ax.set_xticks(range(len(ORDER))); ax.set_xticklabels(ORDER, rotation=35, ha='right', fontsize=8)
    ax.set_ylabel('state transitions'); ax.set_title(f'Example sequence {ex.sequence_id.iloc[0]}')
    plt.tight_layout(); fig.savefig(os.path.join(FIG, 'fig7_example_sequence.png'), dpi=150); plt.close(fig)
except Exception as e:
    print('example figure skipped:', e)

# participant variability
fig, ax = plt.subplots(figsize=(9, 4.2))
ax.boxplot([P[P.mechanism == m].FRR.dropna().values for m in ORDER])
ax.set_xticks(range(1, len(ORDER) + 1)); ax.set_xticklabels(ORDER, rotation=35, ha='right', fontsize=8)
ax.set_ylabel('FRR per user'); ax.set_title('Participant-level variability in FRR')
plt.tight_layout(); fig.savefig(os.path.join(FIG, 'fig8_participant_variability.png'), dpi=150); plt.close(fig)

# tables
cols = ['mechanism', 'n_users', 'FAR_mean', 'FAR_lo', 'FAR_hi', 'FRR_mean', 'FRR_lo', 'FRR_hi',
        'transition_rate_per_100_mean', 'n_flip_events_mean', 'detection_latency_frames_mean',
        'recovery_latency_frames_mean', 'detection_rate', 'recovery_rate']
MEC[cols].round(4).to_csv(os.path.join(TAB, 'table_primary_results.csv'), index=False)
open(os.path.join(TAB, 'table_primary_results.md'), 'w').write(MEC[cols].round(4).to_markdown(index=False))
op = pd.read_csv(os.path.join(OUT, 'operating_points.csv'))
opg = op.groupby('mechanism')[['calib_FAR', 'calib_FRR', 'constraint_satisfied']].mean().round(4).reset_index()
opg.to_csv(os.path.join(TAB, 'table_operating_points.csv'), index=False)
open(os.path.join(TAB, 'table_statistical_tests.md'), 'w').write(
    T[T.metric.isin(['FAR', 'FRR', 'transition_rate_per_100', 'detection_latency_frames'])]
     .round(5).to_markdown(index=False))
print(MEC[cols[:9]].round(4).to_string(index=False))
print('\nusers:', P.enrolled_user.nunique(), '| sequences:', S.sequence_id.nunique(),
      '| figures:', len(os.listdir(FIG)), '| tables:', len(os.listdir(TAB)))
