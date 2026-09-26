# Stage 2 results — provenance map

Read this before citing any number from `experiment_Files/Stage2/results/`.
Status as of the Stage 2 freeze, 2026-09-26.

## FINAL v2 CONFIRMATORY RECORD — cite these

| Path | Contents |
|---|---|
| `mechanism_comparison_v2/f3/scores/` | Frozen per-frame score dump, primary feature set `F3_NO_LOC_NO_DEVSTATE`. 31 users. Generated at commit `f42f55c`, seed 20260918, sklearn 1.6.1. **Immutable input** — never regenerated. |
| `mechanism_comparison_v2/f7/scores/` | Frozen score dump, `F7_F3_MISSINGNESS_ONLY` construct-validity probe. Identical splits and sequences. |
| `mechanism_comparison_v2/analysis/primary/` | **The preregistered primary result** (PREREGISTRATION_v2 §3.1, target FAR 0.05). Verified bit-for-bit identical before and after the moving-average fix. |
| `mechanism_comparison_v2/analysis/factorial/` | Fixed-level margin × dwell response surface. Also bit-for-bit unchanged by the fix. |
| `mechanism_comparison_v2/analysis/families/` | **Secondary** tuned-family comparison of ten mechanism families. Carries unequal selection optimism by construction. Post-fix. |
| `mechanism_comparison_v2/analysis/secondary/factorial_far_0.03/`, `factorial_far_0.07/` | **Declared secondary sensitivity** (§4.2): identical §3.1 criterion re-evaluated at the other two targets. Not the primary. |
| `mechanism_comparison_v2/analysis/secondary/far_0.03/`, `far_0.07/` | Tuned-family results at the sensitivity targets. Secondary. |
| `mechanism_comparison_v2/analysis/secondary/no_sprt_subset/` | Secondary subset analysis (§4.3). |
| `mechanism_comparison_v2/analysis/secondary/score_validity_f3_f7.*` | F3 vs F7 per-user AUC (§4.4). Descriptive probe; no decision layer is run on F7. |
| `dataset_audit/` | Cadence and eligibility audit. Establishes the ~1 observation/minute frame period and the 31-user regular-cadence cohort. Current. |

## NOT USED by the v2 analysis — do not cite as v2 results

| Path | Why it exists |
|---|---|
| `mechanism_comparison_v2/f3/unused_v1rule/` | `operating_points.csv` and `sequence_metrics.csv` written by the refit driver under the **v1 symmetric-band** selection rule during the score-dump run. They are not inputs to, or outputs of, the v2 offline analysis. Retained for provenance, renamed and quarantined so the distinction cannot be missed. |
| `archive/stage2_v2_scoredump_f3_results__duplicate_of_f3/` | Byte-identical duplicate of `mechanism_comparison_v2/f3` (verified with `diff -rq`, no differences). Produced by a Colab run that wrote to a second path. Archived rather than deleted. Nothing references it. |

## SUPERSEDED — exploratory evidence only

| Path | Status |
|---|---|
| `mechanism_comparison/` | Stage 2 **v1** corrected run, 31 users, symmetric FAR band. Superseded as primary by the v2 analysis. Valid exploratory evidence for how the design developed; its selection rule is the one v2 replaced (defect D1). |
| `mechanism_comparison/sensitivity/` | v1-rule sensitivity analyses, including the 6-user complete-feasibility subset whose Holm-adjusted p-floor of 0.25 made significance unattainable by construction. Superseded by §4.2 and §4.3 under v2 rules. |
| `stage2_exploratory_pre_calibration_fix/` | Pre-correction v1 run. Already carries its own `ARCHIVED_README.md`. Two known defects (one-sided FAR admission, unbounded detection latency). Do not cite. |
| `primary/`, `pilot/`, `pilot_mechanism/`, `costprobe/` | Stage 2 feature-ablation run and pilots. Supporting//development evidence. The ablation covered 13 of 31 users and does not license a general claim about excluding location and device-state features. |

## Superseded documents

`docs/Stage2/STAGE2_FINAL_CORRECTED_EXECUTION_REPORT.md`, `STAGE2_SENSITIVITY_ANALYSIS_REPORT.md` and
`FINAL_PROTOCOL_AUDIT.md` describe the **v1** rules. Each now carries a superseded banner. The most
consequential stale claim in them is that SPRT is "structurally infeasible" (23/31 under v1); under v2 SPRT
is feasible for **31/31** users. Use `docs/Stage2/V2_RESULTS.md` and
`docs/Stage2/V2_FORENSIC_AUDIT_AND_PLAN.md` as current.

## Reproduction

```bash
cd experiment_Files/Stage2
python scripts/decision_layer_offline.py \
    --config configs/v2_scoredump_f3.json \
    --scores results/mechanism_comparison_v2/f3/scores \
    --f7-scores results/mechanism_comparison_v2/f7/scores \
    --out    results/mechanism_comparison_v2/analysis
python tests/test_decision_v2.py && python tests/test_mechanisms.py
```

Runs in about 70 seconds on one CPU core and fits nothing. The score dumps are the frozen input; no step
of the v2 analysis requires the raw ExtraSensory data or a model refit.
