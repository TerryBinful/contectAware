# Numbers checked

Every value drawn in a figure, checked against the source CSV or JSON it came from.
Each script writes its own record to `checks/<stem>_checks.json` when it runs; this file
collects them. Nothing under `experiment_Files/Stage2/results/mechanism_comparison_v2/analysis/`
was written to, and no experiment, model fit or score generation was rerun.

Reproduce everything with:

```bash
cd docs/Stage2/figures && ./build.sh
```

## Discrepancies found

**None in the figures.** Every value drawn matches its source file, and the three
Figure 3 gate numbers and the four Figure 4 annotations reproduce the values printed in
the paper exactly.

Two things are worth recording as findings rather than discrepancies:

1. **`bbox_inches='tight'` was silently truncating axis labels.** matplotlib's tight
   bounding box can only crop the canvas, never extend it, so an axis label wider than
   the figure is simply never rasterised — the saved PNG loses its closing bracket with
   no warning. `Figure.get_tightbbox` does not detect this either: it intersects with the
   canvas and reports such a figure as perfectly tight. `_style.check_overflow` therefore
   measures the artists themselves in display pixels and `_style.save` aborts if anything
   would be cut. It caught truncation in Figures 1, 2, 3 and 4 and in the first draft of
   Figure 5. Out-of-view tick labels are excluded, since matplotlib keeps them "visible"
   and they produce phantom failures.

2. **Figure 1 was redrawn stacked rather than side by side.** Two 4×5 heat maps annotated
   with a value and a participant count per cell cannot be read when they share 8.5 cm;
   the annotations fell to about 3 pt. Stacked, each panel gets the full column width.

## Figure 1 — factorial response surface

Source: `analysis/factorial/response_surface.csv`, `target == 0.05`.

| Check | Value | Note |
|---|---|---|
| cells present at FAR 0.05 | `17 of 20` | the other 3 have no feasible operating point and are greyed |
| infeasible (greyed) cells | `3` | *m*=0.1 *k*=10; *m*=0.2 *k*=5; *m*=0.2 *k*=10 |
| `n_users_feasible` range | `6–31` | cells are **not paired**; stated in the caption |

Every cell value printed in the figure is `response_surface.csv`'s `excess_transitions`
or `FRR` for that (margin, dwell) row, formatted to 3 dp, and every `n=` is that row's
`n_users_feasible`. The script raises if a (margin, dwell) pair appears more than once,
and asserts that the feasible-cell mask is identical in the two panels.

## Figure 2 — stability–lockout plane

Sources: `analysis/families/mechanism_metrics.csv` and the two
`analysis/secondary/far_0.0{3,7}/mechanism_metrics.csv`. Each file asserted to hold
exactly 10 mechanisms.

| Mechanism (FAR 0.05) | FRR, excess | 95% CI and n |
|---|---|---|
| Instantaneous | `0.0421, 2.0122` | FRR [0.0134, 0.0793]; excess [0.9676, 3.3078]; n=30 |
| Moving average | `0.0603, 0.5344` | FRR [0.0318, 0.0953]; excess [0.2602, 0.8656]; n=31 |
| EWMA | `0.0671, 0.5204` | FRR [0.0377, 0.1023]; excess [0.2258, 0.9109]; n=31 |
| Majority vote | `0.0482, 0.4258` | FRR [0.0214, 0.0838]; excess [0.2107, 0.6785]; n=31 |
| Debounce (dwell) | `0.0487, 0.3215` | FRR [0.0212, 0.0847]; excess [0.1236, 0.5560]; n=31 |
| Margin (dual threshold) | `0.0834, 0.4026` | FRR [0.0345, 0.1408]; excess [0.1396, 0.7372]; n=26 |
| Margin + dwell | `0.1244, 0.2028` | FRR [0.0731, 0.1776]; excess [0.1022, 0.3078]; n=30 |
| Trust model (dual τ) | `0.1717, 0.0376` | FRR [0.1301, 0.2168]; excess [0.0000, 0.0860]; n=31 |
| Trust model (single τ) | `0.0800, 0.1720` | FRR [0.0527, 0.1142]; excess [0.0753, 0.2914]; n=31 |
| SPRT | `0.0361, 0.3215` | FRR [0.0118, 0.0707]; excess [0.1473, 0.5495]; n=31 |

| Check | Value | Note |
|---|---|---|
| points hidden inside the axis break | `none` | break spans excess 0.95–1.55; verified against all three targets |
| feasible participants per mechanism | `18–31` | 0.03/0.05/0.07 — Instantaneous 30/30/29; Moving average 31/31/31; EWMA 31/31/29; Majority vote 31/31/31; Debounce 31/31/31; Margin (dual threshold) 18/26/23; Margin + dwell 30/30/31; Trust (dual τ) 31/31/31; Trust (single τ) 31/31/31; SPRT 31/31/29 |

Mechanisms are **not paired** with one another; the caption says so.

## Figure 3 — concentration of instability

Source: `analysis/families/sequence_metrics.csv`, `target == 0.05`,
`mechanism == 'instantaneous'`. The three annotated numbers are hard gates: the script
aborts rather than drawing if any fails.

| Check | Value | Result |
|---|---|---|
| top 5 of 30 share | `0.6560` | target 0.656 — **PASS** |
| participants with zero excess | `10/30` | target 10/30 — **PASS** |
| sequences with zero excess | `124/173` | target 124/173 — **PASS** |
| participants plotted | `30` | one point per participant |
| sequences behind the means | `173` | 5.77 per participant on average (5–6 each) |
| max per-participant mean excess | `16.0000` | participant `7CE37510-…` — the same participant drawn in Figure 5 |

## Figure 4 — score validity, F3 versus F7

Sources: `analysis/secondary/score_validity_f3_f7.csv`,
`analysis/secondary/score_validity_summary.json`.

| Check | Value | Against |
|---|---|---|
| participants plotted | `31` | summary JSON `n_users` = 31 ✓ |
| mean AUC F3 | `0.990121` | summary JSON `0.990121` ✓ |
| mean AUC F7 | `0.758470` | summary JSON `0.758470` ✓ |
| annotated means (3 dp) | `0.990 → 0.758` | paper text `0.990 → 0.758` ✓ |
| paired difference and CI | `0.232 [0.191, 0.273]` | paper text `0.232 [0.191, 0.273]` ✓ |
| mean of per-participant diffs | `0.231650` | summary JSON `diff.mean` `0.231650` ✓ |
| AUC falls / rises / unchanged | `30 / 0 / 1` | — |
| participants below chance under F7 | `1` | min `AUC_F7` = 0.3995 |
| pairing | `complete` | every participant has both an F3 and an F7 AUC |

## Figure 5 — one sequence under three policies

Sources: `f3/scores/7CE37510.parquet`, `analysis/factorial/operating_points.csv`.

| Check | Value | Note |
|---|---|---|
| sequence drawn | `7CE37510_tsts1` | participant `7CE37510-…`, `split == 'test'`, 180 frames |
| sequence layout | 60 genuine \| 60 impostor \| 60 genuine | `transition_idx` 60, `recovery_idx` 120 in the dump |
| transitions: instantaneous / dwell *k*=2 / margin 0.05 + dwell 2 | `43 / 13 / 5` | minimum possible for this sequence is 2 |
| thresholds used | `m0_k1 θ=0.879111`; `m0_k2 θ=0.891811`; `m0.05_k2 θ=0.883948` | from `operating_points.csv`, target FAR 0.05, this participant |
| margin band | `[0.858948, 0.908948]` | θ ∓ *m*/2 with *m* = 0.05 |
| decision states | `src.decision_v2.sim_margin_dwell` | the frozen module is imported, not reimplemented |
| candidate participants | `14` | all three cells feasible at FAR 0.05 |

Selection criterion, stated so the choice is auditable: among sequences where all three
policies detect the impostor at some point and transitions strictly decrease from
instantaneous to dwell to margin + dwell, the script takes the one with the largest total
separation. That criterion selects an extreme; the caption says so, and Figure 3 shows how
atypical this participant is.

## Post-hoc reproduction — POST HOC, NOT IN THE FROZEN PLAN

Script `scripts/posthoc_cellH_descriptives.py`; outputs `posthoc/posthoc_cellH_descriptives.csv`
and `posthoc/posthoc_cellH_vs_paper.csv`. Seed 20260918, 2,000 participant-level resamples, the
project's own `src.decision_v2.bootstrap_mean_ci`. See `posthoc/POSTHOC.md` for the tables.

All five point estimates for cell_H versus cell_D reproduce the values printed in
Section 5.1 to three decimal places. Confidence bounds move by at most 0.029 on the
proportion metrics and 0.199 frames on `recovery_latency_censored`, which is the expected
resampling variation at a different seed.
