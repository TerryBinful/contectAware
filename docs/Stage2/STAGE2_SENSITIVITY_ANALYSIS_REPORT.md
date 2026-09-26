# STAGE 2 — SENSITIVITY ANALYSIS REPORT

> **SUPERSEDED — Stage 2 v1.** This document describes the **v1** rules (symmetric FAR band,
> v1 SPRT grid, v1 stability framing) and is retained as exploratory provenance. It is superseded by
> `docs/Stage2/V2_RESULTS.md` and `docs/Stage2/V2_FORENSIC_AUDIT_AND_PLAN.md`. In particular its claim
> that SPRT is structurally infeasible (23/31 users) does **not** hold under v2, where SPRT is feasible
> for 31/31. Do not cite figures from this document as final results.


Generated 2026-09-26 05:30:47. Primary analysis: `results/mechanism_comparison` (commit `a0e36cb4`, seed 20260918).

**These are secondary analyses. The primary result remains the 31-user analysis at FAR 0.05 ± 0.01 and is not modified by anything in this report.**

## A. Complete-feasibility subset

**Eligibility rule:** all 9 mechanisms feasible at the calibration operating point, determined exclusively from `operating_points.csv` (calibration data). Final-test performance played no part.

**Subset size: 6 of 31 enrolled users** (25 excluded), 35 sequences.

### A.1 Statistical power of this subset

With n = 6 paired observations the smallest attainable two-sided Wilcoxon signed-rank p-value is 0.03125; after Holm correction across 8 comparisons the smallest attainable adjusted p-value is 0.250. **No comparison in this subset can reach p < 0.05 regardless of effect size.** Observed significant comparisons: 0 of 72. The loss of significance relative to the primary analysis is therefore a power artefact of the subset size and is NOT evidence that the effects are absent.

### A.2 Subset results (mean over users)

| mechanism             |   n_users |   FAR_mean |   FRR_mean |   transition_rate_per_100_mean |   n_flip_events_mean |   detection_latency_frames_mean |   recovery_latency_frames_mean |   detection_rate |   recovery_rate |
|:----------------------|----------:|-----------:|-----------:|-------------------------------:|---------------------:|--------------------------------:|-------------------------------:|-----------------:|----------------:|
| instantaneous         |         6 |     0.0019 |     0.0042 |                         1.4742 |               0.5833 |                          0      |                         0.0833 |           1      |          1      |
| moving_average        |         6 |     0.0206 |     0.0479 |                         1.1639 |               0.0556 |                          1.2056 |                         5.4944 |           1      |          1      |
| ewma                  |         6 |     0.0128 |     0.0471 |                         1.3191 |               0.3889 |                          0.6833 |                         5.3722 |           1      |          1      |
| majority_vote         |         6 |     0.0213 |     0.0153 |                         1.1949 |               0.0556 |                          1.2778 |                         1.4167 |           1      |          1      |
| debounce              |         6 |     0.0199 |     0.1211 |                         1.1173 |               0.0556 |                          1.1944 |                         6.8333 |           1      |          0.8889 |
| margin_dual_threshold |         6 |     0.0028 |     0.0028 |                         1.3346 |               0.3611 |                          0      |                         0.0833 |           1      |          1      |
| hysteresis            |         6 |     0.0745 |     0.2409 |                         0.9466 |               0.0556 |                          2.8333 |                         7.7125 |           0.9722 |          0.6111 |
| trust_model           |         6 |     0.0461 |     0.1115 |                         1.0801 |               0      |                          2.7667 |                        11.3611 |           1      |          0.9333 |
| sprt                  |         6 |     0.0038 |     0.018  |                         1.2104 |               0.1667 |                          0.1444 |                         1.9667 |           1      |          1      |

### A.3 Direction of effects compared with the primary analysis

| mechanism             | metric                   |   primary_mean |   subset_mean |   primary_significant |   subset_significant | significance_changed   |
|:----------------------|:-------------------------|---------------:|--------------:|----------------------:|---------------------:|:-----------------------|
| instantaneous         | FAR                      |         0.053  |        0.0019 |                   nan |                  nan | False                  |
| instantaneous         | FRR                      |         0.0471 |        0.0042 |                   nan |                  nan | False                  |
| instantaneous         | transition_rate_per_100  |         2.6834 |        1.4742 |                   nan |                  nan | False                  |
| instantaneous         | detection_latency_frames |         1.0317 |        0      |                   nan |                  nan | False                  |
| moving_average        | FAR                      |         0.0578 |        0.0206 |                     1 |                    0 | True                   |
| moving_average        | FRR                      |         0.0888 |        0.0479 |                     1 |                    0 | True                   |
| moving_average        | transition_rate_per_100  |         1.539  |        1.1639 |                     1 |                    0 | True                   |
| moving_average        | detection_latency_frames |         1.9199 |        1.2056 |                     1 |                    0 | True                   |
| ewma                  | FAR                      |         0.062  |        0.0128 |                     0 |                    0 | False                  |
| ewma                  | FRR                      |         0.0908 |        0.0471 |                     1 |                    0 | True                   |
| ewma                  | transition_rate_per_100  |         1.53   |        1.3191 |                     1 |                    0 | True                   |
| ewma                  | detection_latency_frames |         1.728  |        0.6833 |                     1 |                    0 | True                   |
| majority_vote         | FAR                      |         0.0705 |        0.0213 |                     1 |                    0 | True                   |
| majority_vote         | FRR                      |         0.0583 |        0.0153 |                     1 |                    0 | True                   |
| majority_vote         | transition_rate_per_100  |         1.5829 |        1.1949 |                     1 |                    0 | True                   |
| majority_vote         | detection_latency_frames |         2.1403 |        1.2778 |                     1 |                    0 | True                   |
| debounce              | FAR                      |         0.0663 |        0.0199 |                     1 |                    0 | True                   |
| debounce              | FRR                      |         0.1899 |        0.1211 |                     1 |                    0 | True                   |
| debounce              | transition_rate_per_100  |         1.3411 |        1.1173 |                     1 |                    0 | True                   |
| debounce              | detection_latency_frames |         2.4296 |        1.1944 |                     1 |                    0 | True                   |
| margin_dual_threshold | FAR                      |         0.0587 |        0.0028 |                     0 |                    0 | False                  |
| margin_dual_threshold | FRR                      |         0.116  |        0.0028 |                     0 |                    0 | False                  |
| margin_dual_threshold | transition_rate_per_100  |         1.4717 |        1.3346 |                     1 |                    0 | True                   |
| margin_dual_threshold | detection_latency_frames |         1.6704 |        0      |                     0 |                    0 | False                  |
| hysteresis            | FAR                      |         0.0677 |        0.0745 |                     0 |                    0 | False                  |
| hysteresis            | FRR                      |         0.3546 |        0.2409 |                     1 |                    0 | True                   |
| hysteresis            | transition_rate_per_100  |         0.9041 |        0.9466 |                     1 |                    0 | True                   |
| hysteresis            | detection_latency_frames |         2.993  |        2.8333 |                     1 |                    0 | True                   |
| trust_model           | FAR                      |         0.058  |        0.0461 |                     0 |                    0 | False                  |
| trust_model           | FRR                      |         0.2583 |        0.1115 |                     1 |                    0 | True                   |
| trust_model           | transition_rate_per_100  |         0.9864 |        1.0801 |                     1 |                    0 | True                   |
| trust_model           | detection_latency_frames |         3.2274 |        2.7667 |                     1 |                    0 | True                   |
| sprt                  | FAR                      |         0.0563 |        0.0038 |                     0 |                    0 | False                  |
| sprt                  | FRR                      |         0.0744 |        0.018  |                     0 |                    0 | False                  |
| sprt                  | transition_rate_per_100  |         1.3177 |        1.2104 |                     1 |                    0 | True                   |
| sprt                  | detection_latency_frames |         1.628  |        0.1444 |                     0 |                    0 | False                  |


Directionally, 8 of 8 stabilisation mechanisms still show a lower transition rate than the instantaneous baseline in the subset. Absolute FAR and FRR are lower for every mechanism than in the primary analysis, which is expected: users for whom all nine mechanisms were feasible are users whose score distributions permit fine operating-point control.

**Substantive interpretation change: none established.** The direction of the stability effect is preserved; statistical confirmation is impossible at n = 6. Excluded users are listed in `results/mechanism_comparison/sensitivity/complete_feasibility/eligibility_table.csv` with the mechanisms that were infeasible for each.


## B. Operating-point sensitivity (FAR 0.03 / 0.05 / 0.07, each ± 0.01)

### B.1 Feasibility by target

| target         |   users |   total_combinations |   infeasible | worst_mechanism   |   worst_count |
|:---------------|--------:|---------------------:|-------------:|:------------------|--------------:|
| 0.03           |      31 |                  279 |           26 | sprt              |            22 |
| 0.05 (primary) |      31 |                  279 |           32 | sprt              |            23 |
| 0.07           |      31 |                  279 |           35 | sprt              |            25 |

### B.2 Transition rate per 100 frames by target

| mechanism             |   0.03 |   0.05 (primary) |   0.07 |
|:----------------------|-------:|-----------------:|-------:|
| instantaneous         |  2.566 |            2.683 |  2.554 |
| moving_average        |  1.584 |            1.539 |  1.488 |
| ewma                  |  1.524 |            1.53  |  1.575 |
| majority_vote         |  1.653 |            1.583 |  1.583 |
| debounce              |  1.592 |            1.341 |  1.469 |
| margin_dual_threshold |  1.292 |            1.472 |  1.687 |
| hysteresis            |  1.083 |            0.904 |  1.063 |
| trust_model           |  0.993 |            0.986 |  1.021 |
| sprt                  |  1.318 |            1.318 |  1.324 |

### B.3 FRR by target

| mechanism             |   0.03 |   0.05 (primary) |   0.07 |
|:----------------------|-------:|-----------------:|-------:|
| instantaneous         | 0.0563 |           0.0471 | 0.0406 |
| moving_average        | 0.0752 |           0.0888 | 0.0781 |
| ewma                  | 0.0912 |           0.0908 | 0.0721 |
| majority_vote         | 0.1091 |           0.0583 | 0.05   |
| debounce              | 0.1445 |           0.1899 | 0.1404 |
| margin_dual_threshold | 0.148  |           0.116  | 0.1273 |
| hysteresis            | 0.309  |           0.3546 | 0.1853 |
| trust_model           | 0.2906 |           0.2583 | 0.22   |
| sprt                  | 0.0753 |           0.0744 | 0.0713 |

### B.4 Detection latency (frames) by target

| mechanism             |   0.03 |   0.05 (primary) |   0.07 |
|:----------------------|-------:|-----------------:|-------:|
| instantaneous         |  0.709 |            1.032 |  1.397 |
| moving_average        |  1.146 |            1.92  |  2.184 |
| ewma                  |  1.537 |            1.728 |  1.909 |
| majority_vote         |  1.656 |            2.14  |  2.313 |
| debounce              |  1.744 |            2.43  |  2.39  |
| margin_dual_threshold |  1.508 |            1.67  |  1.535 |
| hysteresis            |  3.033 |            2.993 |  3.326 |
| trust_model           |  2.149 |            3.227 |  3.849 |
| sprt                  |  1.617 |            1.628 |  1.605 |

### B.5 Achieved FAR by target

| mechanism             |   0.03 |   0.05 (primary) |   0.07 |
|:----------------------|-------:|-----------------:|-------:|
| instantaneous         | 0.0424 |           0.053  | 0.066  |
| moving_average        | 0.0535 |           0.0578 | 0.0764 |
| ewma                  | 0.051  |           0.062  | 0.0733 |
| majority_vote         | 0.052  |           0.0705 | 0.076  |
| debounce              | 0.0528 |           0.0663 | 0.0736 |
| margin_dual_threshold | 0.0546 |           0.0587 | 0.0616 |
| hysteresis            | 0.0621 |           0.0677 | 0.092  |
| trust_model           | 0.0488 |           0.058  | 0.0821 |
| sprt                  | 0.056  |           0.0563 | 0.0559 |


Rank correlation of mechanisms by transition rate across targets (Spearman, pairwise): {'0.03': {'0.03': 1.0, '0.05 (primary)': 0.85, '0.07': 0.683}, '0.05 (primary)': {'0.03': 0.85, '0.05 (primary)': 1.0, '0.07': 0.867}, '0.07': {'0.03': 0.683, '0.05 (primary)': 0.867, '0.07': 1.0}}
