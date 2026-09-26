"""Figure 5 (optional): one real test sequence under three decision policies.

Top: the normalised score trace of a single 180-frame test sequence (60 genuine |
60 impostor | 60 genuine), with the three policies' accept and reject thresholds.
Below: the authentication state under instantaneous, dwell k = 2, and margin 0.05 with
dwell 2. Inset: the 3GPP Event A3 analogue -- a dead band of width 2*Hys around the
neighbour-minus-serving difference, plus a time-to-trigger the condition must hold for.

The decision rule is NOT reimplemented here. This script imports the frozen module
`experiment_Files/Stage2/src/decision_v2.py` and calls `sim_margin_dwell`, so the states
drawn are produced by exactly the code that produced the results tables.

Sources (read only):
  f3/scores/<user>.parquet                      -> the score trace
  analysis/factorial/operating_points.csv       -> each policy's theta for that participant
The chosen sequence is reported on stdout and recorded in _fig5_checks.json.
"""
import os, sys, json, importlib.util
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _style import apply_style, save, despine, ANALYSIS, OI, INK, INK2, INK3, GRID, HERE

apply_style()
RESULTS = os.path.normpath(os.path.join(ANALYSIS, '..'))
REPO = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
SRC = os.path.join(REPO, 'experiment_Files', 'Stage2', 'src')

# import the frozen rule module standalone (its package does a relative import of metrics)
sys.path.insert(0, os.path.join(REPO, 'experiment_Files', 'Stage2'))
import src.decision_v2 as D                                      # noqa: E402

TARGET = 0.05
POLICIES = [('m0_k1', 0.0, 1, 'Instantaneous'),
            ('m0_k2', 0.0, 2, 'Dwell $k=2$'),
            ('m0.05_k2', 0.05, 2, 'Margin $m=0.05$ + dwell $k=2$')]

OPS = pd.read_csv(os.path.join(ANALYSIS, 'factorial', 'operating_points.csv'))
OPS = OPS[(OPS.target == TARGET) & (OPS.feasible == True)]          # noqa: E712
theta_of = {(r.enrolled_user, r.cell): json.loads(r.chosen_params)['theta']
            for r in OPS.itertuples()}

# participants for whom all three policies are feasible at FAR 0.05
cells = {c for c, _, _, _ in POLICIES}
users = sorted({u for (u, c) in theta_of if c in cells})
users = [u for u in users if all((u, c) in theta_of for c in cells)]


def states_for(user, S):
    th = np.array([theta_of[(user, c)] for c, _, _, _ in POLICIES])
    m = np.array([mm for _, mm, _, _ in POLICIES])
    k = np.array([kk for _, _, kk, _ in POLICIES])
    return D.sim_margin_dwell(S, th, m, k)          # (3, n_seq, T), 1 = authenticated


def transitions(v):
    return int(np.sum(v[1:] != v[:-1]))


# ---- choose a sequence where the three policies visibly differ --------------------
best = None
for user in users:
    f = os.path.join(RESULTS, 'f3', 'scores', user.split('-')[0] + '.parquet')
    if not os.path.exists(f):
        continue
    df = pd.read_parquet(f)
    df = df[df.split == 'test']
    if df.empty:
        continue
    seqs = list(dict.fromkeys(df.sequence_id.tolist()))
    S = np.stack([df[df.sequence_id == s].sort_values('frame').score.to_numpy()
                  for s in seqs])
    if S.shape[1] != 180:
        continue
    B = states_for(user, S)                                     # (3, n_seq, 180)
    for j, sq in enumerate(seqs):
        inst, dw, hy = B[0, j], B[1, j], B[2, j]
        n_i, n_d, n_h = transitions(inst), transitions(dw), transitions(hy)
        # want: instantaneous visibly unstable, dwell better, margin+dwell best,
        # and all three still detecting the impostor at some point
        detects = all(v[60:120].min() == 0 for v in (inst, dw, hy))
        if not (detects and n_i > n_d > n_h >= 2):
            continue
        score = (n_i - n_d) + (n_d - n_h) + 0.01 * n_i
        if best is None or score > best[0]:
            best = (score, user, sq, S[j], B[:, j], (n_i, n_d, n_h))

if best is None:
    raise SystemExit('No sequence satisfies the "three policies visibly differ" criterion.')
_, USER, SEQ, s, states, ntr = best
print(f'  chosen sequence {SEQ} (participant {USER}); '
      f'transitions instantaneous/dwell/margin+dwell = {ntr[0]}/{ntr[1]}/{ntr[2]}')

T = len(s)
t = np.arange(T)
th = {c: theta_of[(USER, c)] for c, _, _, _ in POLICIES}

# ---- draw ------------------------------------------------------------------------
fig = plt.figure(figsize=(3.45, 4.5))
gs = fig.add_gridspec(4, 1, height_ratios=[3.0, 1, 1, 1], hspace=0.34,
                      left=0.165, right=0.968, top=0.99, bottom=0.095)
ax = fig.add_subplot(gs[0, 0])

# impostor window
ax.add_patch(Rectangle((60, -0.02), 60, 1.06, color=OI['vermillion'], alpha=0.07,
                       lw=0, zorder=0))
ax.text(90, 1.035, 'impostor', ha='center', va='top', fontsize=6.4,
        color=OI['vermillion'])
for x in (60, 120):
    ax.axvline(x, color=INK3, lw=0.6, ls=(0, (3, 2)), zorder=1)

ax.plot(t, s, '-', color=INK2, lw=0.8, zorder=3)

c, m, k, _ = POLICIES[2]
hi_thr, lo_thr = th[c] + m / 2, th[c] - m / 2
ax.axhspan(lo_thr, hi_thr, color=OI['blue'], alpha=0.13, lw=0, zorder=2)
ax.axhline(hi_thr, color=OI['blue'], lw=0.9, zorder=4)
ax.axhline(lo_thr, color=OI['blue'], lw=0.9, zorder=4)
ax.axhline(th['m0_k1'], color=INK, lw=0.9, ls=(0, (4, 2)), zorder=4)
ax.text(178, hi_thr + 0.015, r'$\theta+m/2$', ha='right', va='bottom',
        fontsize=6.0, color=OI['blue'])
ax.text(178, lo_thr - 0.015, r'$\theta-m/2$', ha='right', va='top',
        fontsize=6.0, color=OI['blue'])
ax.text(2, lo_thr - 0.035, r'$\theta$ (instantaneous, dashed)', ha='left', va='top',
        fontsize=6.0, color=INK)

ax.set_ylabel('Normalised score\n(ECDF units)', fontsize=7.4)
ax.set_ylim(-0.02, 1.06)
ax.set_xlim(0, T)
ax.tick_params(axis='x', length=0, labelbottom=False)
ax.grid(True, axis='y', lw=0.5, alpha=0.7)
ax.set_axisbelow(True)
despine(ax, keep=('left',))

# ---- state lanes -----------------------------------------------------------------
for i, (cell, mm, kk, lab) in enumerate(POLICIES):
    a = fig.add_subplot(gs[i + 1, 0], sharex=ax)
    v = states[i]
    a.add_patch(Rectangle((60, -0.35), 60, 1.45, color=OI['vermillion'], alpha=0.07,
                          lw=0, zorder=0))
    a.step(t, v, where='post', color=OI['blue'], lw=1.3, zorder=3)
    a.fill_between(t, 0, v, step='post', color=OI['blue'], alpha=0.16, lw=0, zorder=2)
    for x in (60, 120):
        a.axvline(x, color=INK3, lw=0.6, ls=(0, (3, 2)), zorder=1)
    a.set_ylim(-0.35, 1.95)
    a.set_yticks([0, 1]); a.set_yticklabels(['reject', 'accept'], fontsize=6.2)
    a.text(1.5, 1.88, f'{lab} - {transitions(v)} transitions', fontsize=6.5,
           color=INK, ha='left', va='top')
    despine(a, keep=('left',))
    a.tick_params(axis='y', length=0)
    if i < len(POLICIES) - 1:
        a.tick_params(axis='x', length=0, labelbottom=False)
    else:
        a.set_xlabel('Frame index (1 frame $\\approx$ 1 minute)', fontsize=7.8)
        a.set_xticks([0, 60, 120, 180])

# ---- 3GPP Event A3 inset ---------------------------------------------------------
ins = ax.inset_axes([0.605, 0.055, 0.375, 0.40])
tt = np.linspace(0, 10, 400)
d = -0.75 + 1.5 / (1 + np.exp(-(tt - 4.4) * 1.5)) + 0.07 * np.sin(tt * 3.1)
ins.axhspan(-0.35, 0.35, color=OI['blue'], alpha=0.16, lw=0)
ins.axhline(0.35, color=OI['blue'], lw=0.6); ins.axhline(-0.35, color=OI['blue'], lw=0.6)
ins.plot(tt, d, color=INK2, lw=0.8)
enter = tt[np.argmax(d > 0.35)]
ins.axvspan(enter, enter + 1.5, color=OI['orange'], alpha=0.22, lw=0)
ins.annotate('', xy=(enter, -0.92), xytext=(enter + 1.5, -0.92),
             arrowprops=dict(arrowstyle='<->', lw=0.6, color=INK2))
ins.text(enter + 0.75, -0.80, 'TTT', ha='center', va='bottom', fontsize=5.4, color=INK2)
ins.text(9.7, -0.30, r'$2\cdot$Hys', ha='right', va='bottom', fontsize=5.4,
         color=OI['blue'])
ins.text(0.2, 1.00, '3GPP Event A3', ha='left', va='top', fontsize=5.6, color=INK)
ins.text(0.2, 0.70, 'neighbour $-$ serving', ha='left', va='top', fontsize=5.0,
         color=INK2)
ins.set_xlim(0, 10); ins.set_ylim(-1.05, 1.05)
ins.set_xticks([]); ins.set_yticks([])
for sp in ins.spines.values():
    sp.set_color(INK3); sp.set_linewidth(0.5)
ins.set_facecolor('white')
ins.patch.set_alpha(0.94)

save(fig, 'fig5_sequence_schematic')

# ---- numeric checks --------------------------------------------------------------
checks = [
    ('fig5 sequence drawn', SEQ, f'participant {USER}, split=test, {T} frames'),
    ('fig5 sequence layout', '60 genuine | 60 impostor | 60 genuine',
     'transition_idx=60, recovery_idx=120 in the score dump'),
    ('fig5 transitions instantaneous / dwell k=2 / margin 0.05 + dwell 2',
     f'{ntr[0]} / {ntr[1]} / {ntr[2]}', 'minimum possible for this sequence is 2'),
    ('fig5 thresholds used',
     '; '.join(f"{c} theta={th[c]:.6f}" for c, _, _, _ in POLICIES),
     'from factorial/operating_points.csv at target FAR 0.05 for this participant'),
    ('fig5 margin band', f'[{lo_thr:.6f}, {hi_thr:.6f}]',
     'theta -/+ m/2 with m = 0.05, as in src/decision_v2.sim_margin_dwell'),
    ('fig5 states come from the frozen module', 'src.decision_v2.sim_margin_dwell',
     'not reimplemented in this script'),
    ('fig5 candidate participants (all three cells feasible at FAR 0.05)',
     str(len(users)), 'from operating_points.csv'),
]
json.dump([dict(check=c, value=v, note=n) for c, v, n in checks],
          open(os.path.join(HERE, '_fig5_checks.json'), 'w'), indent=2)
for c, v, n in checks:
    print(f'  CHECK {c}: {v}  ({n})')
