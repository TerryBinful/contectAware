# Paper tables — Stage 2

`tables.md` holds Tables 1–8 of the paper, generated from the frozen v2 analysis CSVs.
Regenerate from the Stage 2 root:

```bash
cd docs/Stage2 && ./build.sh tables      # or ./build.sh for figures and tables together
```

or directly, which is what `build.sh` does:

```bash
python3 tables/make_tables.py \
  ../../experiment_Files/Stage2/results/mechanism_comparison_v2/analysis > tables/tables.md
```

Requires `pandas` and `scipy` (the latter only for the Spearman ρ under Table 7). On
Windows PowerShell use `| Out-File -Encoding utf8 tables.md` rather than `>`, or the
`τ`, `ρ`, `θ` and `−` characters in the output get mangled.

`make_tables.py` is kept **byte-for-byte as delivered** — it writes markdown to stdout and
takes the analysis directory as its one argument. The redirect lives in `build.sh` rather
than in the script, so the script stays verbatim and auditable against what was reviewed.
Its docstring pins commit `a4a34a5`; nothing under `analysis/` has changed since, so it
still applies.

## What is in `tables.md`

| Table | Content | Source under `analysis/` |
|---|---|---|
| 1 | Primary confirmatory test at FAR 0.05, with the FAR 0.03 / 0.07 sensitivity as trailing prose | `primary/primary_tests.csv`, `secondary/factorial_far_*/primary_tests.csv` |
| 2 | Which factorial cell each participant's calibration selected | `primary/cell_selection.csv` |
| 3 | The full 20-cell factorial response surface | `factorial/response_surface.csv` |
| 4, 4a, 4b | Tuned stabiliser families at FAR 0.05, 0.03 and 0.07 | `families/mechanism_metrics.csv`, `secondary/far_0.0{3,7}/` |
| 5 | Paired tests against instantaneous thresholding | `families/statistical_tests.csv` |
| 6 | FAR drift, test minus calibration | `families/far_drift.csv` |
| 7 | Rank of families across the three operating points, with Spearman ρ between rankings | all three targets |
| 8 | Where instability sits, and what the score encodes | `families/sequence_metrics.csv`, `secondary/score_validity_*` |

Tables 4a and 4b are emitted **after** Table 7 rather than next to Table 4, because the
script builds them in the same loop that computes the rank comparison. Reorder them when
laying out the paper; the content is unaffected.

## Relationship to the figures

The tables and the figures in [`../figures/`](../figures/) were written independently
against the same CSVs, and they agree, which makes the overlap a useful cross-check
rather than duplication:

- **Table 3 is Figure 1's data**, plus three columns a heat map could not carry — test
  FAR, recovery failure and recovery latency.
- **Table 8's first four rows are Figure 3's gate numbers** (124/173 sequences with zero
  excess, 65.6% from the top five participants, 20/30 participants with any excess), and
  its last three rows are Figure 4's annotations (AUC 0.990 → 0.758, paired difference
  0.232 [0.191, 0.273]). All reproduce.
- **Table 7 has no figure equivalent.** It is the cleanest single answer to whether the
  ordering of mechanisms is an artefact of calibrating at FAR 0.05.

## One naming inconsistency to fix at layout time

Tables 4–7 apply the display names, so the composed cell reads **"Margin + dwell"**, in
line with the figures and for the reason given in `../figures/CAPTIONS.md`: in 3GPP Event
A3, hysteresis is the margin term alone and time-to-trigger is a separate dwell term.

Tables 1–3 print the raw identifiers straight from the CSVs, so they still show `cell_H`,
`cell_D`, `cell_M` and a `hysteresis` value in Table 3's `Class` column. That is faithful
to the stored artefacts and was left alone rather than patched in the reviewer's script.
Rename them in the paper, or add a line to the Table 3 note reading "`hysteresis` denotes
the margin + dwell class".
