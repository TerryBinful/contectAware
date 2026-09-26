"""Figure 4: score validity collapses when the context shortcut is removed (F3 vs F7).

Paired slope chart, one line per participant, from the F3 feature set (which retains
location and device-state features) to F7 (which removes them). Participant means are
marked and joined by a heavy line; a dashed rule at AUC 0.5 marks chance.

Sources (read only):
  secondary/score_validity_f3_f7.csv       -> enrolled_user, AUC_F3, AUC_F7
  secondary/score_validity_summary.json    -> means and the paired-difference CI
"""
import os, sys, json
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _style import write_checks, apply_style, save, despine, ANALYSIS, OI, INK, INK2, INK3

apply_style()
SEC = os.path.join(ANALYSIS, 'secondary')
D = pd.read_csv(os.path.join(SEC, 'score_validity_f3_f7.csv'))
J = json.load(open(os.path.join(SEC, 'score_validity_summary.json')))

n = len(D)
m3, m7 = D.AUC_F3.mean(), D.AUC_F7.mean()
diff = J['diff']

fig, ax = plt.subplots(figsize=(3.3, 3.2))
fig.subplots_adjust(left=0.165, right=0.955, top=0.945, bottom=0.165)

x3, x7 = 0.0, 1.0
# Every participant falls, so direction carries no information. The accent hue is
# reserved for the participant whose scores end BELOW chance, which a mean hides.
for _, r in D.iterrows():
    sub = r.AUC_F7 < 0.5
    ax.plot([x3, x7], [r.AUC_F3, r.AUC_F7], '-',
            color=OI['vermillion'] if sub else INK3,
            lw=1.5 if sub else 0.7, alpha=0.95 if sub else 0.55, zorder=2 + int(sub))
    ax.plot([x3, x7], [r.AUC_F3, r.AUC_F7], 'o', ms=2.4, mfc='white',
            mec=OI['vermillion'] if sub else INK3, mew=0.6, zorder=3 + int(sub))

ax.plot([x3, x7], [m3, m7], '-', color=OI['blue'], lw=2.4,
        solid_capstyle='round', zorder=6)
ax.plot([x3, x7], [m3, m7], 'o', ms=6.5, mfc=OI['blue'], mec='white', mew=1.1, zorder=7)
ax.annotate(f'mean {m3:.3f}', (x3, m3), textcoords='offset points', xytext=(-6, 6),
            ha='left', va='bottom', fontsize=7.0, color=OI['blue'])
ax.annotate(f'mean {m7:.3f}', (x7, m7), textcoords='offset points', xytext=(-9, -5),
            ha='right', va='top', fontsize=7.0, color=OI['blue'])

ax.axhline(0.5, ls=(0, (4, 3)), lw=0.9, color=INK2, zorder=1)
ax.text(1.30, 0.505, 'chance', fontsize=6.8, color=INK2, ha='right', va='bottom')
ax.annotate('1 participant falls below chance', xy=(x7, float(D.AUC_F7.min())),
            xytext=(0.40, 0.452), fontsize=6.6, color=OI['vermillion'],
            ha='center', va='center',
            arrowprops=dict(arrowstyle='->', lw=0.7, color=OI['vermillion'],
                            shrinkA=2, shrinkB=3))

ax.text(0.5, 0.245,
        f'paired difference {diff["mean"]:.3f}\n'
        f'95% CI [{diff["lo"]:.3f}, {diff["hi"]:.3f}]\n'
        f'n = {diff["n"]} participants, fully paired',
        ha='center', va='bottom', fontsize=6.8, color=INK, linespacing=1.5)

ax.set_xlim(-0.30, 1.32)
ax.set_ylim(0.23, 1.045)
ax.set_xticks([x3, x7])
ax.set_xticklabels(['F3\n(with location and\ndevice-state features)',
                    'F7\n(those features\nremoved)'], linespacing=1.45)
ax.tick_params(axis='x', pad=3)
ax.set_yticks([0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
ax.set_ylabel('AUC (area under the ROC curve)')
ax.grid(True, axis='y', lw=0.5, alpha=0.8)
ax.set_axisbelow(True)
despine(ax, keep=('left',))

save(fig, 'fig4_score_validity_f3_f7')

# ---- numeric checks --------------------------------------------------------------
n_down = int((D.AUC_F7 < D.AUC_F3).sum())
n_up = int((D.AUC_F7 > D.AUC_F3).sum())
n_below_chance = int((D.AUC_F7 < 0.5).sum())
checks = [
    ('fig4 participants plotted', str(n), f"summary json says n_users={J['n_users']}"),
    ('fig4 mean AUC F3', f'{m3:.6f}', f"summary json {J['mean_AUC_F3']:.6f}; "
     f"match={np.isclose(m3, J['mean_AUC_F3'])}"),
    ('fig4 mean AUC F7', f'{m7:.6f}', f"summary json {J['mean_AUC_F7']:.6f}; "
     f"match={np.isclose(m7, J['mean_AUC_F7'])}"),
    ('fig4 annotated means (3 dp)', f'{m3:.3f} -> {m7:.3f}', 'paper text: 0.990 -> 0.758'),
    ('fig4 paired diff and CI', f"{diff['mean']:.3f} [{diff['lo']:.3f}, {diff['hi']:.3f}]",
     'paper text: 0.232 [0.191, 0.273]'),
    ('fig4 mean of per-participant diffs equals summary mean',
     f"{D.diff_F3_minus_F7.mean():.6f}", f"summary {diff['mean']:.6f}; "
     f"match={np.isclose(D.diff_F3_minus_F7.mean(), diff['mean'])}"),
    ('fig4 AUC falls / rises / unchanged', f'{n_down} / {n_up} / {n - n_down - n_up}', ''),
    ('fig4 participants at or below chance under F7', str(n_below_chance),
     f'min AUC_F7 = {D.AUC_F7.min():.4f}'),
    ('fig4 pairing', 'complete', 'every participant has both an F3 and an F7 AUC'),
]
write_checks('fig4_score_validity_f3_f7', checks)
