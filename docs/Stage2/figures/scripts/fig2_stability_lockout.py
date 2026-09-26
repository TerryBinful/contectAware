"""Figure 2: the stability-lockout plane at matched operating points.

One marker per decision mechanism at target FAR 0.05, positioned by mean FRR (x) and
mean excess transitions per sequence (y), with 95% bootstrap CI bars on both axes.
Faint satellite markers give the same mechanism at target FAR 0.03 and 0.07, joined to
the 0.05 marker by a thin trail, so the reader can see whether a mechanism's position
is an artefact of the chosen operating point.

The y axis is BROKEN. `instantaneous` sits an order of magnitude above every other
mechanism, and on one continuous linear axis the remaining nine collapse into an
unreadable band across the bottom sixth of the panel. The break is marked on both
axes and both segments are linear with the same tick spacing, so no magnitude is
distorted -- only the empty interval 0.95 to 1.55 is removed.

Sources (read only):
  families/mechanism_metrics.csv                  -> FAR 0.05 (primary calibration target)
  secondary/far_0.03/mechanism_metrics.csv        -> FAR 0.03 sensitivity
  secondary/far_0.07/mechanism_metrics.csv        -> FAR 0.07 sensitivity
"""
import os, sys, json
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _style import (write_checks, apply_style, save, despine, ANALYSIS, DISPLAY,
                    OI, INK, INK2, INK3)

apply_style()

P05 = pd.read_csv(os.path.join(ANALYSIS, 'families', 'mechanism_metrics.csv'))
P03 = pd.read_csv(os.path.join(ANALYSIS, 'secondary', 'far_0.03', 'mechanism_metrics.csv'))
P07 = pd.read_csv(os.path.join(ANALYSIS, 'secondary', 'far_0.07', 'mechanism_metrics.csv'))
for name, d in [('0.05', P05), ('0.03', P03), ('0.07', P07)]:
    assert len(d) == 10, f'{name}: expected 10 mechanisms, got {len(d)}'

X, Y = 'FRR_mean', 'excess_transitions_mean'
ORDER = list(P05.mechanism)
idx05, idx03, idx07 = (d.set_index('mechanism') for d in (P05, P03, P07))

# Colour carries one bit: the mechanism under test vs the reference mechanisms.
ACCENT, BASE = OI['vermillion'], INK2
BREAK_LO, BREAK_HI = 0.95, 1.55          # the empty interval that is removed

fig, (hi, lo) = plt.subplots(2, 1, figsize=(3.6, 4.0), sharex=True,
                             gridspec_kw=dict(height_ratios=[1.0, 2.6], hspace=0.09))
fig.subplots_adjust(left=0.185, right=0.955, top=0.985, bottom=0.115)


def draw(ax):
    """All ten mechanisms are drawn on BOTH axes; each axis then clips to its range."""
    for m in ORDER:
        xs = [idx03.loc[m, X], idx05.loc[m, X], idx07.loc[m, X]]
        ys = [idx03.loc[m, Y], idx05.loc[m, Y], idx07.loc[m, Y]]
        ax.plot(xs, ys, '-', color=INK3, lw=0.6, alpha=0.55, zorder=1)
        ax.plot([xs[0], xs[2]], [ys[0], ys[2]], 'o', ms=2.6, mfc='white',
                mec=INK3, mew=0.6, alpha=0.95, zorder=2)
    for m in ORDER:
        r = idx05.loc[m]
        c = ACCENT if m == 'hysteresis' else BASE
        ax.errorbar(r[X], r[Y],
                    xerr=[[r[X] - r['FRR_lo']], [r['FRR_hi'] - r[X]]],
                    yerr=[[r[Y] - r['excess_transitions_lo']],
                          [r['excess_transitions_hi'] - r[Y]]],
                    fmt='none', ecolor=c, elinewidth=0.7, capsize=1.6,
                    capthick=0.7, alpha=0.45, zorder=3)
        ax.plot(r[X], r[Y], 'o', ms=5.0, mfc=c, mec='white', mew=0.9, zorder=4)


for ax in (hi, lo):
    draw(ax)
    ax.grid(True, lw=0.5, alpha=0.8)
    ax.set_axisbelow(True)

hi.set_ylim(BREAK_HI, 3.55)
lo.set_ylim(-0.085, BREAK_LO)
hi.set_yticks([2.0, 2.5, 3.0, 3.5])
lo.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8])
lo.set_xlim(0.0, 0.232)

despine(hi, keep=('left',))
despine(lo, keep=('left', 'bottom'))
hi.tick_params(bottom=False)

# break marks on both spines of the gap
kw = dict(marker=[(-1, -0.55), (1, 0.55)], markersize=5, linestyle='none',
          color=INK3, mec=INK3, mew=0.8, clip_on=False)
hi.plot([0], [0], transform=hi.transAxes, **kw)
lo.plot([0], [1], transform=lo.transAxes, **kw)

# --- direct labels ---------------------------------------------------------------
# Hand-placed offsets in points: ten labels do not auto-place legibly at 8.5 cm.
OFF = {
    'instantaneous':         (hi, 9, 0, 'left', 'center'),
    'moving_average':        (lo, 0, 9, 'center', 'bottom'),
    'ewma':                  (lo, 8, 1, 'left', 'bottom'),
    'majority_vote':         (lo, -8, 3, 'right', 'bottom'),
    'debounce':              (lo, 0, -9, 'center', 'top'),
    'margin_dual_threshold': (lo, 8, 3, 'left', 'bottom'),
    'hysteresis':            (lo, 0, 9, 'center', 'bottom'),
    'trust_model':           (lo, 4, 8, 'right', 'bottom'),
    'trust_model_single':    (lo, 8, -1, 'left', 'top'),
    'sprt':                  (lo, -9, -2, 'right', 'top'),
}
for m in ORDER:
    ax, dx, dy, ha, va = OFF[m]
    r = idx05.loc[m]
    ax.annotate(DISPLAY[m], (r[X], r[Y]), textcoords='offset points',
                xytext=(dx, dy), ha=ha, va=va, fontsize=6.6,
                color=ACCENT if m == 'hysteresis' else INK, zorder=6)

lo.set_xlabel('False rejection rate (fraction of frames)')
fig.text(0.016, 0.55, 'Excess transitions per 180-frame sequence\n'
                      '(count above the minimum of 2)',
         rotation=90, va='center', ha='left', fontsize=8.5, color=INK)

# "better" = fewer lockouts and fewer spurious flips
lo.annotate('better', xy=(0.006, -0.055), xytext=(0.047, 0.115),
            fontsize=6.8, color=INK2, ha='left', va='center',
            arrowprops=dict(arrowstyle='->', lw=0.7, color=INK2, shrinkA=2, shrinkB=1))
hi.text(0.230, 3.46,
        'open markers: target FAR 0.03 and 0.07\nbars: 95% bootstrap CI at FAR 0.05',
        fontsize=5.9, color=INK2, ha='right', va='top', linespacing=1.55)

save(fig, 'fig2_stability_lockout')

# ---- numeric checks --------------------------------------------------------------
checks = []
for m in ORDER:
    r = idx05.loc[m]
    checks.append((f'fig2 {DISPLAY[m]} at FAR 0.05 (FRR, excess)',
                   f'{r[X]:.4f}, {r[Y]:.4f}',
                   f"CI FRR [{r['FRR_lo']:.4f}, {r['FRR_hi']:.4f}]; "
                   f"CI excess [{r['excess_transitions_lo']:.4f}, {r['excess_transitions_hi']:.4f}]; "
                   f"n={int(r['n_users_feasible'])}"))
gap = [m for m in ORDER if BREAK_LO < idx05.loc[m, Y] < BREAK_HI
       or BREAK_LO < idx03.loc[m, Y] < BREAK_HI or BREAK_LO < idx07.loc[m, Y] < BREAK_HI]
checks.append(('fig2 points hidden inside the axis break',
               'none' if not gap else ','.join(gap),
               f'break spans excess {BREAK_LO}-{BREAK_HI}'))
feas = {m: (int(idx03.loc[m, 'n_users_feasible']), int(idx05.loc[m, 'n_users_feasible']),
            int(idx07.loc[m, 'n_users_feasible'])) for m in ORDER}
checks.append(('fig2 feasible participants per mechanism (0.03/0.05/0.07)',
               f"{min(min(v) for v in feas.values())}-{max(max(v) for v in feas.values())}",
               '; '.join(f'{DISPLAY[m]} {a}/{b}/{c}' for m, (a, b, c) in feas.items())))
write_checks('fig2_stability_lockout', checks)
