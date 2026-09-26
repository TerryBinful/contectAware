"""Figure 1: factorial response surface at target FAR 0.05.

Two single-hue heat maps over margin m (rows) x dwell k (columns): excess transitions
per sequence, and FRR. Every cell annotated with its value (3 dp) and the number of
participants for whom that cell had a feasible calibration operating point. Cells with
no feasible operating point (absent from response_surface.csv) are greyed and labelled.

Source: analysis/factorial/response_surface.csv, rows with target == 0.05. Read only.
"""
import os, sys, json
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _style import (write_checks, apply_style, save, ANALYSIS, CMAP_EXCESS, CMAP_FRR,
                    INFEASIBLE, INK, INK2, OI, CELL_CLASS_DISPLAY)

apply_style()
R = pd.read_csv(os.path.join(ANALYSIS, 'factorial', 'response_surface.csv'))
d = R[R.target == 0.05].copy()

MARGINS = [0.0, 0.05, 0.1, 0.2]        # rows
DWELLS = [1, 2, 3, 5, 10]              # columns
checks = []

def grid_of(col):
    G = np.full((len(MARGINS), len(DWELLS)), np.nan)
    N = np.full((len(MARGINS), len(DWELLS)), np.nan)
    for i, m in enumerate(MARGINS):
        for j, k in enumerate(DWELLS):
            r = d[(np.isclose(d.margin, m)) & (d.dwell == k)]
            if len(r) == 1:
                G[i, j] = float(r[col].iloc[0]); N[i, j] = int(r.n_users_feasible.iloc[0])
            elif len(r) > 1:
                raise SystemExit(f'duplicate cell m={m} k={k}')
    return G, N

Ge, Ne = grid_of('excess_transitions')
Gf, Nf = grid_of('FRR')
assert np.array_equal(np.isnan(Ge), np.isnan(Gf)), 'feasibility differs between panels'
n_infeasible = int(np.isnan(Ge).sum())
checks.append(('fig1 cells present at FAR 0.05', f'{len(d)} of 20', ''))
checks.append(('fig1 infeasible (greyed) cells', f'{n_infeasible}', ''))
checks.append(('fig1 n_users_feasible range', f'{int(np.nanmin(Ne))}-{int(np.nanmax(Ne))}', ''))

# Stacked, not side by side: a 4x5 grid annotated with a value and an n per cell
# cannot be read at single-column width if two of them share the width.
fig, axes = plt.subplots(2, 1, figsize=(3.45, 5.5), sharex=True)
fig.subplots_adjust(hspace=0.10, left=0.215, right=0.815, top=0.985, bottom=0.145)
panels = [(axes[0], Ge, Ne, CMAP_EXCESS, 'Excess transitions\nper sequence (count)'),
          (axes[1], Gf, Nf, CMAP_FRR, 'False rejection rate\n(fraction of frames)')]

for pi, (ax, G, N, cmap, cblab) in enumerate(panels):
    masked = np.ma.masked_invalid(G)
    cmap = cmap.copy(); cmap.set_bad(INFEASIBLE)
    im = ax.imshow(masked, cmap=cmap, aspect='auto', origin='upper',
                   vmin=0, vmax=float(np.nanmax(G)))
    # Label each contiguous RUN of infeasible cells once. One label per cell makes
    # adjacent labels abut and read as a single word.
    for i in range(len(MARGINS)):
        j = 0
        while j < len(DWELLS):
            if np.isnan(G[i, j]):
                j2 = j
                while j2 + 1 < len(DWELLS) and np.isnan(G[i, j2 + 1]):
                    j2 += 1
                ax.text((j + j2) / 2, i, 'infeasible', ha='center', va='center',
                        fontsize=5.6, color=INK2, style='italic')
                j = j2 + 1
            else:
                j += 1
    for i in range(len(MARGINS)):
        for j in range(len(DWELLS)):
            if np.isnan(G[i, j]):
                continue
            # ink colour chosen by cell darkness so the label always reads
            freq = G[i, j] / max(float(np.nanmax(G)), 1e-12)
            col = 'white' if freq > 0.55 else INK
            ax.text(j, i - 0.15, f'{G[i, j]:.3f}', ha='center', va='center',
                    fontsize=6.8, color=col)
            ax.text(j, i + 0.22, f'n={int(N[i, j])}', ha='center', va='center',
                    fontsize=5.6, color=col, alpha=0.85)
    ax.set_xticks(range(len(DWELLS))); ax.set_xticklabels(DWELLS)
    ax.set_yticks(range(len(MARGINS))); ax.set_yticklabels([f'{m:g}' for m in MARGINS])
    ax.set_ylabel('Margin $m$ (score units)')
    ax.yaxis.set_label_coords(-0.235, 0.5)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0)
    cb = fig.colorbar(im, ax=ax, fraction=0.048, pad=0.035)
    cb.outline.set_visible(False); cb.ax.tick_params(labelsize=6.2, length=0)
    cb.set_label(cblab, fontsize=6.4, linespacing=1.4)
    # The four cell classes are the quadrants of (margin = 0 vs > 0) x (dwell = 1 vs > 1).
    # Outline them, then name the two factor levels in brackets OUTSIDE the axes, so the
    # four class names never collide with cell values.
    for (r0, c0, nr, nc) in [(0, 0, 1, 1), (0, 1, 1, 4), (1, 0, 3, 1), (1, 1, 3, 4)]:
        ax.add_patch(Rectangle((c0 - 0.5, r0 - 0.5), nc, nr, fill=False,
                               edgecolor=INK, lw=1.2, zorder=5))
    # margin factor-level bracket, drawn outside the axes
    for (y0, y1, lab) in [(-0.5, 0.5, 'no margin'), (0.5, 3.5, 'margin')]:
        ax.plot([-0.92, -0.92], [y0, y1], color=INK2, lw=0.8, clip_on=False)
        ax.text(-1.05, (y0 + y1) / 2, lab, ha='center', va='center', rotation=90,
                fontsize=6.2, color=INK2, clip_on=False)

# dwell factor-level bracket, once, under the shared x axis
ax = axes[1]
# x in data units, y in axes fractions, so the bracket clears the tick labels
tr = ax.get_xaxis_transform()
for (x0, x1, lab) in [(-0.5, 0.5, 'no dwell'), (0.5, 4.5, 'dwell')]:
    ax.plot([x0, x1], [-0.105, -0.105], transform=tr, color=INK2, lw=0.8, clip_on=False)
    ax.text((x0 + x1) / 2, -0.125, lab, transform=tr, ha='center', va='top',
            fontsize=6.2, color=INK2, clip_on=False)
ax.set_xlabel('Dwell $k$ (frames)')
ax.xaxis.set_label_coords(0.5, -0.235)

save(fig, 'fig1_factorial_surface')
write_checks('fig1_factorial_surface', checks)
