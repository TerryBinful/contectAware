"""Shared style for the Stage 2 paper figures.

Conventions (fixed here so every figure matches):
  * matplotlib only, no seaborn; 300 dpi PNG + vector PDF.
  * Okabe-Ito colour-blind-safe palette. The 3-hue categorical subset used in
    Figure 5 was validated with the dataviz palette validator (all six checks PASS,
    worst adjacent CVD dE 11.0 deuteranopia).
  * Sequential encodings are SINGLE-HUE, light -> dark. No rainbow/viridis: a
    multi-hue ramp implies category boundaries that the data does not have.
  * No titles inside the image. Captions live in CAPTIONS.md.
  * Axis labels always carry units.
  * Recessive grid and spines; text in ink colours, never in a series colour.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.text as mtext
from matplotlib.colors import LinearSegmentedColormap
import os

# ---- Okabe-Ito ----
OI = dict(black='#000000', orange='#E69F00', skyblue='#56B4E9', green='#009E73',
          yellow='#F0E442', blue='#0072B2', vermillion='#D55E00', purple='#CC79A7')
INK, INK2, INK3 = '#1a1a1a', '#4d4d4d', '#808080'
GRID = '#d9d9d9'
INFEASIBLE = '#e8e8e8'          # neutral grey for cells with no feasible operating point

def seq_cmap(hex_hi, name):
    """Single-hue sequential ramp, near-white -> the given hue."""
    return LinearSegmentedColormap.from_list(name, ['#f7f7f7', hex_hi], N=256)

CMAP_EXCESS = seq_cmap(OI['blue'], 'excess')       # stability magnitude
CMAP_FRR    = seq_cmap(OI['vermillion'], 'frr')    # lockout magnitude

# Display names. The `hysteresis` cell class is ALWAYS shown as "margin + dwell":
# in 3GPP, hysteresis is the margin term alone and time-to-trigger is the separate
# dwell term, so naming the composed cell "hysteresis" would misstate the analogue.
DISPLAY = {
    'instantaneous': 'Instantaneous', 'moving_average': 'Moving average', 'ewma': 'EWMA',
    'majority_vote': 'Majority vote', 'debounce': 'Debounce (dwell)',
    'margin_dual_threshold': 'Margin (dual threshold)', 'hysteresis': 'Margin + dwell',
    'trust_model': 'Transformer, dual τ', 'trust_model_single': 'Trust model (single τ)',
    'sprt': 'SPRT',
}
DISPLAY['trust_model'] = 'Trust model (dual τ)'
CELL_CLASS_DISPLAY = {'instantaneous': 'instantaneous', 'dwell_only': 'dwell only',
                      'margin_only': 'margin only', 'hysteresis': 'margin + dwell'}

def apply_style():
    plt.rcParams.update({
        'font.family': 'DejaVu Sans', 'font.size': 8,
        'axes.labelsize': 8.5, 'axes.titlesize': 8.5,
        'xtick.labelsize': 7.5, 'ytick.labelsize': 7.5, 'legend.fontsize': 7.5,
        'axes.edgecolor': INK3, 'axes.linewidth': 0.6,
        'xtick.color': INK2, 'ytick.color': INK2,
        'xtick.major.width': 0.6, 'ytick.major.width': 0.6,
        'axes.labelcolor': INK, 'text.color': INK,
        'grid.color': GRID, 'grid.linewidth': 0.5,
        'figure.dpi': 120, 'savefig.dpi': 300,
        'savefig.bbox': 'tight', 'savefig.pad_inches': 0.02,
        'pdf.fonttype': 42, 'ps.fonttype': 42,      # embed TrueType, not Type-3
    })

def despine(ax, keep=('left', 'bottom')):
    for s in ('top', 'right', 'left', 'bottom'):
        ax.spines[s].set_visible(s in keep)

# ---- where things live -----------------------------------------------------------
# docs/Stage2/figures/
#   scripts/   this file and the figure scripts   (HERE)
#   rendered/  the PNG and PDF pairs              (RENDERED)
#   checks/    one JSON of checked numbers each   (CHECKS)
#   posthoc/   the post-hoc tables and their note (POSTHOC)
# Every path is derived from __file__, so the scripts run from any working directory.
HERE = os.path.dirname(os.path.abspath(__file__))
FIG_ROOT = os.path.dirname(HERE)
REPO = os.path.normpath(os.path.join(FIG_ROOT, '..', '..', '..'))
RENDERED = os.path.join(FIG_ROOT, 'rendered')
CHECKS = os.path.join(FIG_ROOT, 'checks')
POSTHOC = os.path.join(FIG_ROOT, 'posthoc')
ANALYSIS = os.path.join(REPO, 'experiment_Files', 'Stage2', 'results',
                        'mechanism_comparison_v2', 'analysis')
STAGE2_SRC = os.path.join(REPO, 'experiment_Files', 'Stage2')
for _d in (RENDERED, CHECKS, POSTHOC):
    os.makedirs(_d, exist_ok=True)


def write_checks(stem, checks):
    """Write one figure's checked numbers to checks/<stem>_checks.json and echo them."""
    import json
    with open(os.path.join(CHECKS, f'{stem}_checks.json'), 'w') as fh:
        json.dump([dict(check=c, value=v, note=n) for c, v, n in checks], fh, indent=2)
    for c, v, n in checks:
        print(f'  CHECK {c}: {v}' + (f'  ({n})' if n else ''))

def check_overflow(fig, tol=0.004):
    """Return per-side overflow, in inches, of drawn content past the figure canvas.

    matplotlib's `bbox_inches='tight'` can only CROP; it cannot extend the canvas.
    Anything an artist draws outside the figure rectangle is never rasterised, so an
    axis label wider than the figure is silently truncated and the saved PNG simply
    has no closing bracket. That failure is invisible unless it is measured, so every
    figure here is measured before it is written.
    """
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    # NB: Figure.get_tightbbox is useless here -- it intersects with the canvas, so it
    # reports a figure whose xlabel is cut in half as perfectly tight. Measure the
    # artists themselves instead, in display pixels.
    # Ticks outside the view interval keep a live, "visible" label that is never
    # drawn. Counting those as overflow produces phantom failures, so drop them.
    skip = set()
    for ax in fig.axes:
        for axis in (ax.xaxis, ax.yaxis):
            v0, v1 = sorted(axis.get_view_interval())
            for tick in list(axis.get_major_ticks()) + list(axis.get_minor_ticks()):
                if not (v0 - 1e-12 <= tick.get_loc() <= v1 + 1e-12):
                    skip.add(id(tick.label1)); skip.add(id(tick.label2))
    boxes = [ax.get_tightbbox(r) for ax in fig.axes]
    for t in fig.findobj(mtext.Text):
        if id(t) not in skip and t.get_visible() and t.get_text().strip():
            try:
                boxes.append(t.get_window_extent(r))
            except Exception:
                pass
    boxes = [b for b in boxes if b is not None and b.width > 0 and b.height > 0]
    x0 = min(b.x0 for b in boxes); x1 = max(b.x1 for b in boxes)
    y0 = min(b.y0 for b in boxes); y1 = max(b.y1 for b in boxes)
    W, H = fig.get_size_inches() * fig.dpi
    d = fig.dpi
    over = dict(left=max(0.0, -x0) / d, bottom=max(0.0, -y0) / d,
                right=max(0.0, x1 - W) / d, top=max(0.0, y1 - H) / d)
    return {k: v for k, v in over.items() if v > tol}


def save(fig, stem, strict=True):
    over = check_overflow(fig)
    if over:
        msg = ', '.join(f'{k} by {v:.3f} in' for k, v in sorted(over.items()))
        if strict:
            raise SystemExit(f'LAYOUT ERROR in {stem}: content runs off the canvas '
                             f'({msg}) and would be truncated. Shorten the labels or '
                             f'widen the figure.')
        print(f'  WARNING {stem}: content off-canvas ({msg})')
    png = os.path.join(RENDERED, stem + '.png'); pdf = os.path.join(RENDERED, stem + '.pdf')
    fig.savefig(png)
    # CreationDate: None omits the timestamp the PDF backend would otherwise stamp in.
    # These PDFs are committed, so without this every rebuild shows as a modified file
    # even when the figure is identical, and the diff is pure noise.
    fig.savefig(pdf, metadata={'CreationDate': None})
    plt.close(fig)
    w, h = fig.get_size_inches()
    print(f'  wrote rendered/{os.path.basename(png)} and rendered/{os.path.basename(pdf)} '
          f'({w*2.54:.1f} x {h*2.54:.1f} cm, no off-canvas content)')
    return png, pdf
