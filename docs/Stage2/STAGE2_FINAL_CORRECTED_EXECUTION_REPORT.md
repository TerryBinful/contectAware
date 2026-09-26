# STAGE 2 — FINAL CORRECTED EXECUTION REPORT

Generated from `results/mechanism_comparison/`. Experiment id `postpivot_mechanism_comparison_v1_20260926T003304`, git commit
`a0e36cb4`, seed 20260918. Pre-correction results are archived separately in
`results/stage2_exploratory_pre_calibration_fix/` and are not mixed into anything below.

## Executive summary

The corrected experiment **completed successfully**: 31 of 31 eligible primary participants, 179
controlled identity-transition sequences, 9 mechanisms, 1611 sequence-level evaluations, **0 failures**.
All 18 unit tests and all 16 protocol/leakage checks pass against the final artefacts.

## Corrections applied

1. **Two-sided operating-point interval.** A candidate is feasible only if
   0.04 <= calibration FAR <=
   0.06. The previous one-sided rule
   admitted FAR near 0, which is not a matched operating point.
2. **Detection latency bounded to the impostor block.** Detection and its full confirmation window must precede
   the recovery transition; a stable rejection during the genuine recovery block is a detection FAILURE (NA),
   never a success and never silently 0.
3. **Calibration grid refined** using calibration impostor-score quantiles spanning FAR in
   [target-3*tol, target+3*tol]; calibration data only.
4. **Resume artefact bug (found during validation, not in the review).** Resuming a run previously overwrote
   `operating_points.csv`, the benchmark manifest and the score-generator manifest with only the resumed
   session's users. Fixed; the earlier corrected run was discarded and the experiment re-run end to end.
   `operating_points.csv` now holds 279 rows = 31 users x 9 mechanisms.

## Protocol

Regular-cadence cohort; chronological 60/20/20 per-user split; participant-disjoint impostor pools
(fit 24 / calibration 12 / test 24) with unseen final-test impostors; training-only preprocessing; one fixed
per-user gradient-boosting score generator shared by all mechanisms; log-odds scores normalised by an ECDF fitted
on calibration only; controlled identity-transition sequences [genuine 60 | impostor 60 | recovery 60 frames]
built from contiguous real observations; ~1 minute per frame. Full detail: `docs/Stage2/FINAL_PROTOCOL_AUDIT.md`.

## Participants

| | |
|---|---|
| Eligible primary participants | 31 |
| Completed | **31** |
| Excluded / failed | 0 |
| Sequences evaluated | 179 |

No participant was excluded after the fact.

## Operating-point calibration

Target FAR 0.05, tolerance 0.01,
feasible interval [0.04,
0.06].
**32 of 279** mechanism/user combinations had no feasible operating point
(16 above the interval,
16 below).

| mechanism             |   n |   feasible |   mean_calib_FAR |   median_calib_FAR |   infeasible |
|:----------------------|----:|-----------:|-----------------:|-------------------:|-------------:|
| instantaneous         |  31 |         30 |           0.0512 |             0.05   |            1 |
| moving_average        |  31 |         31 |           0.0499 |             0.05   |            0 |
| ewma                  |  31 |         31 |           0.0501 |             0.05   |            0 |
| majority_vote         |  31 |         31 |           0.0502 |             0.05   |            0 |
| debounce              |  31 |         31 |           0.05   |             0.05   |            0 |
| margin_dual_threshold |  31 |         23 |           0.0475 |             0.05   |            8 |
| hysteresis            |  31 |         31 |           0.0504 |             0.05   |            0 |
| trust_model           |  31 |         31 |           0.0503 |             0.05   |            0 |
| sprt                  |  31 |          8 |           0.0715 |             0.0556 |           23 |

Grid adequacy: for six of nine mechanisms every user was matched. The exceptions are **SPRT**
(23/31 infeasible) and **margin/dual-threshold** (8/31),
whose decision rules change FAR in coarse jumps (SPRT commits only when the log-likelihood ratio crosses a bound,
so its achievable FAR set is discrete). This is a structural property of those mechanisms, not a grid-resolution
artefact that a finer threshold grid would remove: the refined grid already targets the FAR region directly.
Their comparisons are correspondingly weaker and must be read with that caveat.

## Mechanisms evaluated

instantaneous, moving_average, ewma, majority_vote, debounce, margin_dual_threshold, hysteresis, trust_model, sprt — all nine, none removed.

## Data integrity

All 16 checks pass: pool disjointness; fitting never touched test impostors; enrolled user never their own
impostor; test impostors only from the unseen pool; genuine/recovery blocks disjoint; no duplicate genuine
timestamps; all blocks contiguous; identical sequence sets per mechanism; no duplicate rows; calibration recorded
for every user and mechanism; parameters fixed at calibration; matched FAR interval enforced where feasible;
infeasible cases explicitly recorded; seed and commit recorded. Re-runnable:
`python tests/test_leakage.py results/mechanism_comparison`.

## Results (mean over 31 users, bootstrap 95% CI)

| mechanism             |   FAR_mean |   FAR_lo |   FAR_hi |   FRR_mean |   FRR_lo |   FRR_hi |   transition_rate_per_100_mean |   n_flip_events_mean |   detection_latency_frames_mean |   recovery_latency_frames_mean |   detection_rate |   recovery_rate |   lockout_fraction_during_genuine_mean |
|:----------------------|-----------:|---------:|---------:|-----------:|---------:|---------:|-------------------------------:|---------------------:|--------------------------------:|-------------------------------:|-----------------:|----------------:|---------------------------------------:|
| instantaneous         |     0.053  |   0.0245 |   0.0854 |     0.0471 |   0.0089 |   0.1075 |                         2.6834 |               2.728  |                          1.0317 |                         0.4167 |           0.9892 |          0.9839 |                                 0.0471 |
| moving_average        |     0.0578 |   0.0318 |   0.0905 |     0.0888 |   0.0445 |   0.1479 |                         1.539  |               0.6392 |                          1.9199 |                         5.2038 |           0.9892 |          0.9731 |                                 0.0888 |
| ewma                  |     0.062  |   0.0317 |   0.0968 |     0.0908 |   0.0516 |   0.1409 |                         1.53   |               0.6371 |                          1.728  |                         6.2527 |           0.9839 |          0.9785 |                                 0.0908 |
| majority_vote         |     0.0705 |   0.043  |   0.1019 |     0.0583 |   0.0246 |   0.1084 |                         1.5829 |               0.5699 |                          2.1403 |                         1.8038 |           0.9892 |          0.9839 |                                 0.0583 |
| debounce              |     0.0663 |   0.0442 |   0.0934 |     0.1899 |   0.1169 |   0.2839 |                         1.3411 |               0.1237 |                          2.4296 |                         6.4139 |           0.9892 |          0.871  |                                 0.1899 |
| margin_dual_threshold |     0.0587 |   0.0282 |   0.0946 |     0.116  |   0.0515 |   0.1989 |                         1.4717 |               0.6559 |                          1.6704 |                         1.5172 |           0.9892 |          0.8602 |                                 0.116  |
| hysteresis            |     0.0677 |   0.0475 |   0.0926 |     0.3546 |   0.2541 |   0.4626 |                         0.9041 |               0.043  |                          2.993  |                         7.2373 |           0.9839 |          0.5269 |                                 0.3546 |
| trust_model           |     0.058  |   0.0374 |   0.0821 |     0.2583 |   0.1915 |   0.3326 |                         0.9864 |               0      |                          3.2274 |                        18.1309 |           1      |          0.7172 |                                 0.2583 |
| sprt                  |     0.0563 |   0.0243 |   0.1003 |     0.0744 |   0.0301 |   0.1448 |                         1.3177 |               0.2269 |                          1.628  |                         3.1078 |           0.9785 |          0.9624 |                                 0.0744 |

Latencies are in frames (~1 minute). Detection and recovery rates are the fractions of sequences in which a
stable rejected / authenticated state was reached within the relevant block; missing events are reported as
missing and excluded from the latency means rather than counted as zero.

## Statistical analysis

Unit of analysis is the enrolled user (sequence metrics averaged within user first). Paired Wilcoxon signed-rank
tests against the instantaneous baseline, Holm-corrected across the eight comparisons per metric.

| metric                   | mechanism             |   mean_difference |   p_holm | significant_holm_005   |
|:-------------------------|:----------------------|------------------:|---------:|:-----------------------|
| FAR                      | moving_average        |            0.0048 |   0.0167 | True                   |
| FAR                      | ewma                  |            0.009  |   0.2234 | False                  |
| FAR                      | majority_vote         |            0.0175 |   0.0002 | True                   |
| FAR                      | debounce              |            0.0133 |   0.0259 | True                   |
| FAR                      | margin_dual_threshold |            0.0057 |   0.5343 | False                  |
| FAR                      | hysteresis            |            0.0147 |   0.0982 | False                  |
| FAR                      | trust_model           |            0.005  |   0.2236 | False                  |
| FAR                      | sprt                  |            0.0033 |   0.7008 | False                  |
| FRR                      | moving_average        |            0.0417 |   0.0001 | True                   |
| FRR                      | ewma                  |            0.0437 |   0.0001 | True                   |
| FRR                      | majority_vote         |            0.0113 |   0.0004 | True                   |
| FRR                      | debounce              |            0.1429 |   0.0002 | True                   |
| FRR                      | margin_dual_threshold |            0.069  |   0.1065 | False                  |
| FRR                      | hysteresis            |            0.3076 |   0      | True                   |
| FRR                      | trust_model           |            0.2112 |   0      | True                   |
| FRR                      | sprt                  |            0.0273 |   0.0594 | False                  |
| transition_rate_per_100  | moving_average        |           -1.1444 |   0.0002 | True                   |
| transition_rate_per_100  | ewma                  |           -1.1534 |   0.0002 | True                   |
| transition_rate_per_100  | majority_vote         |           -1.1005 |   0.0002 | True                   |
| transition_rate_per_100  | debounce              |           -1.3423 |   0      | True                   |
| transition_rate_per_100  | margin_dual_threshold |           -1.2116 |   0.0001 | True                   |
| transition_rate_per_100  | hysteresis            |           -1.7793 |   0      | True                   |
| transition_rate_per_100  | trust_model           |           -1.697  |   0      | True                   |
| transition_rate_per_100  | sprt                  |           -1.3657 |   0.0002 | True                   |
| detection_latency_frames | moving_average        |            0.8882 |   0.0007 | True                   |
| detection_latency_frames | ewma                  |            0.6962 |   0.0015 | True                   |
| detection_latency_frames | majority_vote         |            1.1086 |   0.0001 | True                   |
| detection_latency_frames | debounce              |            1.3978 |   0.0021 | True                   |
| detection_latency_frames | margin_dual_threshold |            0.6387 |   0.1155 | False                  |
| detection_latency_frames | hysteresis            |            1.9613 |   0.0007 | True                   |
| detection_latency_frames | trust_model           |            2.1957 |   0.0001 | True                   |
| detection_latency_frames | sprt                  |            0.5962 |   0.1155 | False                  |

All eight stabilisation mechanisms reduce the transition rate relative to the instantaneous baseline
(all Holm-corrected p < 0.001). Six of eight increase FRR significantly; margin/dual-threshold and SPRT do not.
Six of eight increase detection latency significantly. FAR differences are significant for three mechanisms,
consistent with the operating-point matching constraining FAR by design.

## Limitations

1. ExtraSensory cadence is ~1 observation/minute, so nothing can be said about sub-minute responsiveness.
2. Identity transitions are **controlled sequences constructed from real participant observations**, not observed
   device handovers.
3. The primary feature set excludes location and device-state as a methodological control; the supporting
   ablation covered 13 of 31 users and does not prove the exclusion is universally harmless.
4. Cohort is 31 regular-cadence participants; fragmented participants are not represented.
5. Parameter grids are finite.
6. 32 mechanism/user pairs have no feasible operating point and are therefore not matched
   to the common operating condition; SPRT is most affected.
7. Frame-level metrics only; no user-perceived usability was measured.
8. A single score-generator family (gradient boosting) was used.

## Research interpretation

The experiment can establish, for this cohort and score generator, how the nine decision layers trade temporal
stability against security and responsiveness when their parameters are calibrated to a common target FAR on
held-out calibration data and evaluated on unseen-impostor test sequences. The measured pattern is that
stabilisation reduces state churn and, for most mechanisms, raises false rejection and detection latency; the
size of that trade differs markedly between mechanisms.

It cannot establish which mechanism is "best" (that depends on an operational cost function not specified here),
how these mechanisms behave at other operating points, on fragmented recordings, with other feature sets or score
generators, or in deployment with real handovers and real users. Mechanisms with many infeasible operating points
(SPRT, margin/dual-threshold) are not fully matched and their comparison is weaker than the rest.
