"""Figure 3: instability is concentrated in a minority of participants.

Lorenz-style cumulative share of excess transitions against the number of participants,
ranked from most to least unstable, for the instantaneous rule at target FAR 0.05.
The equality diagonal is the counterfactual in which every participant contributes the
same amount of instability.

Source (read only): families/sequence_metrics.csv, rows with target == 0.05 and
mechanism == 'instantaneous'. Per-participant value is the MEAN excess_transitions over
that participant's test sequences (participants contribute 5-6 sequences each).

The three annotated numbers are gates: if any fails to reproduce the script aborts.
"""
import os, sys, json
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _style import apply_style, save, despine, ANALYSIS, OI, INK, INK2, INK3, HERE

apply_style()
S = pd.read_csv(os.path.join(ANALYSIS, 'families', 'sequence_metrics.csv'))
d = S[(S.target == 0.05) & (S.mechanism == 'instantaneous')].copy()

per_user = d.groupby('enrolled_user').excess_transitions.mean().sort_values(ascending=False)
n_users, total = len(per_user), per_user.sum()
cum = np.concatenate([[0.0], np.cumsum(per_user.values) / total])
xs = np.arange(0, n_users + 1)

# ---- gates -----------------------------------------------------------------------
top5_share = per_user.head(5).sum() / total
n_zero_users = int((per_user == 0).sum())
n_zero_seq = int((d.excess_transitions == 0).sum())
n_seq = len(d)
gates = [
    ('top 5 of 30 share', f'{top5_share:.4f}', 0.656, round(top5_share, 3) == 0.656),
    ('participants with zero excess', f'{n_zero_users}/{n_users}', '10/30',
     (n_zero_users, n_users) == (10, 30)),
    ('sequences with zero excess', f'{n_zero_seq}/{n_seq}', '124/173',
     (n_zero_seq, n_seq) == (124, 173)),
]
for name, got, want, ok in gates:
    if not ok:
        raise SystemExit(f'GATE FAILED: {name} = {got}, expected {want}. Stopping.')

# ---- plot ------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(3.4, 3.0))
fig.subplots_adjust(left=0.175, right=0.97, top=0.965, bottom=0.165)

ax.plot([0, n_users], [0, 1], ls=(0, (4, 3)), lw=0.9, color=INK3, zorder=2)
ax.text(n_users * 0.72, 0.80, 'equal contribution', fontsize=6.4, color=INK2,
        rotation=32, rotation_mode='anchor', ha='center', va='bottom')

ax.fill_between(xs, cum, xs / n_users, color=OI['blue'], alpha=0.12,
                lw=0, zorder=1)
ax.plot(xs, cum, '-', color=OI['blue'], lw=2.0, solid_capstyle='round', zorder=3)
ax.plot(xs[1:], cum[1:], 'o', ms=2.8, mfc='white', mec=OI['blue'], mew=0.8, zorder=4)

# top-5 marker
ax.plot([5, 5], [0, cum[5]], ls=':', lw=0.9, color=INK2, zorder=2)
ax.plot([0, 5], [cum[5], cum[5]], ls=':', lw=0.9, color=INK2, zorder=2)
ax.plot(5, cum[5], 'o', ms=5.5, mfc=OI['vermillion'], mec='white', mew=0.9, zorder=5)
ax.annotate(f'top 5 of {n_users} participants\ncarry {top5_share*100:.1f}% of all\n'
            'excess transitions',
            xy=(5, cum[5]), xytext=(7.4, 0.455), fontsize=6.6, color=INK,
            ha='left', va='top', linespacing=1.45,
            arrowprops=dict(arrowstyle='->', lw=0.7, color=INK2, shrinkA=1, shrinkB=3))

# flat tail marker
first_zero = n_users - n_zero_users
ax.annotate(f'{n_zero_users}/{n_users} participants never flip spuriously\n'
            f'({n_zero_seq} of {n_seq} test sequences have zero excess)',
            xy=(first_zero, 1.0), xytext=(n_users - 0.6, 0.145),
            fontsize=6.6, color=INK, ha='right', va='bottom', linespacing=1.45,
            arrowprops=dict(arrowstyle='->', lw=0.7, color=INK2, shrinkA=1, shrinkB=2))

ax.set_xlim(0, n_users)
ax.set_ylim(0, 1.035)
ax.set_xticks([0, 5, 10, 15, 20, 25, 30])
ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
ax.set_yticklabels(['0', '25', '50', '75', '100'])
ax.set_xlabel('Participants, ranked by instability (count)')
ax.set_ylabel('Cumulative share of excess transitions (%)')
ax.grid(True, lw=0.5, alpha=0.8)
ax.set_axisbelow(True)
despine(ax)

save(fig, 'fig3_instability_concentration')

checks = [(f'fig3 gate: {n}', got, f'target {want}; PASS') for n, got, want, _ in gates]
checks.append(('fig3 participants plotted', str(n_users), 'one point per participant'))
checks.append(('fig3 sequences behind the means', str(n_seq),
               f'{n_seq/n_users:.2f} sequences per participant on average (5-6 each)'))
checks.append(('fig3 max per-participant mean excess',
               f'{per_user.max():.4f}', f'participant {per_user.index[0]}'))
json.dump([dict(check=c, value=v, note=n) for c, v, n in checks],
          open(os.path.join(HERE, '_fig3_checks.json'), 'w'), indent=2)
for c, v, n in checks:
    print(f'  CHECK {c}: {v}  ({n})')
