# Experiment Plan — ordered, with inputs and outputs

| Step | Experiment | Priority | Inputs | Outputs | Blocks |
|---|---|---|---|---|---|
| 0 | Cadence check (`05_cadence_check.py`) | ESSENTIAL — first | One user CSV | Δt median/IQR; gap histogram | Everything |
| 1 | Freeze pre-registration | ESSENTIAL | Δt | Dated `01_preregistration_template.md` | Exp 2 |
| 2 | **Exp 1** — Per-user subject-disjoint verification baseline | ESSENTIAL | All 60 user CSVs | Per-user EER/FAR/FRR (mean ± sd); calibration; frozen GB per user; p-streams | Exp 2, 3, 4 |
| 3 | Build splice benchmark (`02_splice_benchmark_spec.md`) | ESSENTIAL | p-streams; label columns; impostor partition | manifest.csv; sequences; coverage report | Exp 2 |
| 4 | **Exp 2** — Mechanism bake-off at matched ANGA-time | ESSENTIAL | Sequences; `03_mechanism_reference.md` grids | Frontier plots (X, M); matched-point table; paired tests; Holm | Thesis core |
| 5 | **Exp 3** — Hysteresis component ablation & sensitivity | HIGH VALUE | Exp 2 grids | Heatmaps ANGA/ANIA over (m, T); margin-only vs dwell-only vs both | H3 |
| 6 | **Exp 4** — Feature-group ablation | OPTIONAL | Exp 1 pipeline | EER and Exp 2 top-3 at motion-only / +watch / +discrete,lf / +audio / all | Q11/Q12 defence |
| 7 | **Exp 5** — Cadence transfer (aggregate to 2Δt, 5Δt) | FUTURE WORK | Exp 2 top-3 | Frontier shift vs cadence | External validity |

## Exp 1 detail

- For each user g: positives = g's frames; negatives = frames from impostor-training users I_train(g). Test negatives = frames from I_test(g), disjoint from I_train(g). Choose the impostor split once (seeded) and reuse.
- Chronological 60/20/20 within g.
- Pipeline fitted inside training fold only: median imputation → RF Gini selection (top k) → SMOTE → GB → calibration on validation fold.
- Report: per-user EER, FAR@FRR-matched, Brier; table of excluded low-data users.
- Comparator: Kaur et al. 2026 (ExtraSensory, avg accuracy 98.7%, avg EER 2.07%).

## Exp 2 detail

- Primary comparison and operating point as pre-registered.
- Statistics: per-user median ANIA-time → paired Wilcoxon (hysteresis vs. each other mechanism); Holm over the secondary set; bootstrap 95% CIs on curve positions (resample users).
- Report both conditions. Report miss rates by L. Report recovery time.
- Figure 1: frontier, condition X. Figure 2: frontier, condition M. Table: matched point, all mechanisms, all metrics.

## Exp 3 detail

- Same sequences. Grid (m × T). Two heatmaps. One table: (4), (5), (6) at matched point.

## What each experiment lets you say

| After | Defensible phrase |
|---|---|
| Exp 1 | "user verification" |
| Exp 2 | "continuous authentication decision evaluation"; answer to RQ1/RQ2/RQ4 |
| Exp 3 | answer to RQ3; keep or drop the handover framing |
| Exp 4 | "behavioural" (or not) |

## Statistical minimums

- n = 60 users (minus exclusions) for paired tests.
- ≥10 sequences per user per condition.
- Report effect sizes (matched-pairs rank-biserial) alongside p-values.
- Every number in the thesis carries a CI or an sd.
