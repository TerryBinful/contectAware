# V2 analysis — implementation notes (written before any v2 score existed)

Scope: `experiment_Files/Stage2/src/decision_v2.py`, `experiment_Files/Stage2/scripts/decision_layer_offline.py`,
`experiment_Files/Stage2/tests/test_decision_v2.py`. These implement `docs/Stage2/PREREGISTRATION_v2.md`
(frozen at commit 4802aa5).

## Status of data at the time of writing

No v2 score dump existed when this code was written. There was no `results/mechanism_comparison_v2`
directory, and no v2 score file had been produced or opened anywhere. The only data the code has
touched is synthetic: the fixtures in `tests/test_decision_v2.py` and the generator behind `--self-test`.
Every choice below was therefore made without sight of v2 outcomes. The commit that adds this file is
the analysis freeze point. `decision_layer_offline.py` records that commit, a dirty flag and the SHA-256
of each analysis file in `experiment_metadata.json`. It refuses to run a confirmatory analysis on
uncommitted code unless `--allow-dirty` is passed, and a run with that flag is labelled
`confirmatory: false`.

The v1 code and v1 results are not modified (PREREGISTRATION_v2 §6.3). The v1 class-based mechanisms
in `src/mechanisms.py` remain the reference semantics.

## Equivalence to the v1 reference implementation

The batch simulators are vectorised over candidates and sequences, and they must reproduce the v1
classes exactly. `test_batch_simulators_match_reference_classes` checks, frame by frame on random score
streams that include exact-threshold ties, that every candidate in every v1 family grid matches
`mechanisms.build(name, p).run()`. SPRT is checked at δ = 0, and `trust_model_single` against
`TrustModel` with τ_lo = τ_hi = 0.5. The δ offset is checked separately against a direct reference
loop.

## Interpretation choices the preregistration does not spell out

| # | Item | Choice | Reason |
|---|---|---|---|
| I1 | Factorial mechanism `margin_dwell(θ, m, k)` | A frame qualifies for acceptance if `s ≥ θ + m/2` and for rejection if `s < θ − m/2` (strict). `k` consecutive qualifying frames flip the state, and any non-qualifying frame resets the counter. Initial state is AUTHENTICATED. | With the strict inequality, `(0,1)` equals instantaneous and `(0,k)` equals debounce(n=k) exactly, which §3 requires. Both identities are tested. The v1 margin/hysteresis classes use `s ≤ θ − m/2`. That differs only on exact ties at the lower threshold, and the v1 families in the secondary comparison keep v1 semantics. |
| I2 | θ candidate grid | Same rule as v1: pooled calibration-score quantiles at `theta_quantiles`, plus impostor-calibration quantiles at `1 − linspace(max(target − 3·tol, 1e-4), target + 3·tol, n_far_grid)`. Recomputed for each FAR target. Calibration data only. | Unchanged from v1 (§2.1). Recomputing per target keeps the 0.03 and 0.07 analyses as well-resolved as the 0.05 one. |
| I3 | C1 tie-breaks | Minimum calibration FRR, then minimum complexity, then lower calibration FAR, then grid order. | The last two tie-breaks are not in the preregistration. They make selection deterministic and favour the more conservative operating point. |
| I4 | Complexity | Same as v1, `w + n + ttt + A + B`. For `margin_dwell`, `k + m` is added. The majority-vote `k` is excluded, as it was in v1. | Keeps v1 tie-breaking identical for the v1 families. Within a factorial cell only θ varies, so the complexity term is constant there. |
| I5 | Band edges | Eligibility uses `target − tol − 1e-12 ≤ FAR ≤ target + 1e-12`. | Floating-point guard only. |
| I6 | C2 for θ-based and margin mechanisms | The accept threshold must satisfy `≤ 1.0`. That is `θ` for instantaneous, MA, EWMA, MV and debounce, and `θ + m/2` for margin, hysteresis and `margin_dwell`. | Direct reading of C2. |
| I7 | C2 for the trust model (generalisation) | At `s = 1` the trust fixed point is `t* = 0.5 + gain·(1 − θ)/decay`, or unbounded if decay = 0 and θ < 1. Trust is clipped to 1. The candidate is reachable iff `gain·(1 − θ) > 0` and `t* > τ_hi`. | The trust model has no single accept threshold on the score. The fixed point at the maximum score is the structural analogue of C2. It uses no outcome data. |
| I8 | C2 for SPRT (generalisation) | Reachable iff the per-frame LLR increment at `s = 1`, plus δ, is `> 0`. | This is the structural condition for the statistic to be able to climb to +A. |
| I9 | C4 grids | `A = B = geomspace(0.5, 64, 15)` and `δ = linspace(−2, 2, 21)`, giving 4,725 candidates. δ is added to every per-frame LLR increment, before clipping to [−B, A]. | C4 fixes the ranges and counts but not the spacing of δ or where it enters. Adding it to the increment is the standard way to shift a sequential test's operating point. |
| I10 | SPRT score models | Gaussian genuine and impostor models, fitted on the calibration normalised scores. Same as v1 `calibrate.estimate_score_models`. | Unchanged. |
| I11 | Primary cell selection | `cell_X` is the feasible cell of class X with the lowest calibration FRR (at target 0.05). Ties go to the smaller `m + k`, then lower calibration FAR, then cell name. | Tie-break not in the preregistration. |
| I12 | Direction in criterion 1 | Two-sided paired Wilcoxon (`zero_method='zsplit'`, as in v1). Holm is applied across the two comparisons (H vs D, H vs M). The criterion counts only if Holm p < 0.05 and the mean paired difference (H − comparator) in excess transitions is < 0. | "Fewer" is directional. A significant result in the wrong direction must not count. |
| I13 | Non-inferiority CI | 2,000-sample user-level bootstrap percentile CI of the mean paired difference (H − comparator). Seeds are fixed: 1 for FRR, 2 for detection failure. | §3.1 and §5. |
| I14 | Missing pairs | A user with no feasible cell for either member of a pair is excluded from that pair. Exclusions are counted in `primary_tests.csv`. | No imputation (§5). |
| I15 | Failures and censoring | Detection must occur inside the impostor block, with 3 stable frames (v1 definition). Failure is a NaN latency. Censored latency replaces NaN with the block length (60), and a flag is kept. Conditional latencies use successes only. | C5. |
| I16 | "Matched" test FAR flag | The user-level bootstrap 95% CI of test FAR overlaps the eligibility band `[target − 0.01, target]`. | C5 names the flag but does not define it. |
| I17 | Tuned-family comparison | Ten rows: the nine v1 families plus `trust_model_single` (C6). Each is compared against instantaneous. Holm is applied per metric across the comparisons, as in v1. Metrics tested: excess transitions, FRR, FAR, detection failure, recovery failure, and censored detection and recovery latency. | §4.1 and §5. Unequal selection optimism is stated in the report. |
| I18 | No-SPRT subset | Users for whom every non-SPRT row (including `trust_model_single`) has a feasible calibration point at FAR 0.05. Decided from calibration only. | §4.3. |
| I19 | Score validity (F3 vs F7) | Per-user AUC on the pooled test-sequence frames, using `raw_score` and `truth`, computed by a rank formula (no sklearn). The script asserts that `sequence_id`, `impostor_user` and `truth` are identical between the two dumps, and flags any user where they differ. Reported as a descriptive mean difference with a bootstrap CI (seed 3). No decision layer is run on F7. | §4.4. |
| I20 | Unit of analysis | Sequence metrics are averaged within user before any test or CI. | §5. |

## What the self-test is and is not

`--self-test` writes synthetic dumps in the exact v2 schema and runs the whole pipeline. It exists
only to show that the code executes end to end and that outputs have the declared structure. Its
numbers, including the verdict it prints, say nothing about the research question and must never be
reported.

## Commands

```
cd experiment_Files/Stage2
python tests/test_decision_v2.py          # 9 tests, synthetic only
python scripts/decision_layer_offline.py --config configs/v2_scoredump_f3.json \
    --scores results/mechanism_comparison_v2/f3/scores \
    --f7-scores results/mechanism_comparison_v2/f7/scores \
    --out results/mechanism_comparison_v2/analysis
```

The `--scores` paths depend on where `run_mechanism_comparison.py` writes the dump
(`<out>/scores/<user[:8]>.parquet`, or `.csv.gz` when pyarrow is absent).
