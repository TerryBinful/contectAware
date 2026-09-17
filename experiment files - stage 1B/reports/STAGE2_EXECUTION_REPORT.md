# STAGE 2 EXECUTION REPORT (auto-generated)

Generated 2026-09-17 23:59:21 from `results/primary`. Every number below comes from an executed run; nothing is projected.

## Status

- Config: **Stage 2 PRIMARY - regular-cadence cohort, unseen impostors, feature-group ablation**
- Planned runs: **372**  (12 of 31 eligible users complete)
- **EXECUTED: 144 runs**, failed: 0
- Total compute recorded: 0.74 h
- Environment: 3.12.3, sklearn 1.6.1, commit 87bfed05
- Seed: 20260916

> **INCOMPLETE RUN.** 228 of 372 runs were not executed. Re-run with `--resume` or complete the grid in Colab; the summary below covers only the executed subset.

## Ablation summary (mean over enrolled users, bootstrap 95% CI)

| feature_set           | model               |   n_users |   AUC_mean |   AUC_lo |   AUC_hi |   EER_mean |   EER_lo |   EER_hi |   FAR_mean |   FRR_mean |
|:----------------------|:--------------------|----------:|-----------:|---------:|---------:|-----------:|---------:|---------:|-----------:|-----------:|
| F1_ALL                | gradient_boosting   |        12 |     0.9983 |   0.9955 |   0.9999 |     0.0107 |   0.0037 |   0.022  |     0.0155 |     0.0277 |
| F2_STAGE1_COMPARABLE  | gradient_boosting   |        12 |     0.9786 |   0.9501 |   0.9942 |     0.0586 |   0.0347 |   0.0974 |     0.0653 |     0.0764 |
| F3_NO_LOC_NO_DEVSTATE | gradient_boosting   |        12 |     0.997  |   0.9916 |   0.9998 |     0.0145 |   0.0042 |   0.0319 |     0.0154 |     0.0186 |
| F4_LOCATION_ONLY      | gradient_boosting   |        12 |     0.9276 |   0.8478 |   0.9739 |     0.1267 |   0.0827 |   0.195  |     0.1226 |     0.1594 |
| F5_DEVICE_STATE_ONLY  | gradient_boosting   |        12 |     0.7326 |   0.701  |   0.7649 |     0.3511 |   0.3229 |   0.3762 |     0.3157 |     0.4271 |
| F6_MISSINGNESS_ONLY   | gradient_boosting   |        12 |     0.8449 |   0.8065 |   0.8821 |     0.232  |   0.1792 |   0.2904 |     0.2074 |     0.2634 |
| F1_ALL                | logistic_regression |        12 |     0.9813 |   0.9714 |   0.9903 |     0.0455 |   0.0269 |   0.0648 |     0.0506 |     0.0618 |
| F2_STAGE1_COMPARABLE  | logistic_regression |        12 |     0.8924 |   0.8679 |   0.9164 |     0.1835 |   0.1502 |   0.2186 |     0.1629 |     0.2549 |
| F3_NO_LOC_NO_DEVSTATE | logistic_regression |        12 |     0.9701 |   0.9432 |   0.9902 |     0.0648 |   0.0293 |   0.1051 |     0.0696 |     0.0656 |
| F4_LOCATION_ONLY      | logistic_regression |        12 |     0.8083 |   0.7598 |   0.8518 |     0.2397 |   0.1952 |   0.283  |     0.27   |     0.232  |
| F5_DEVICE_STATE_ONLY  | logistic_regression |        12 |     0.7306 |   0.7054 |   0.7559 |     0.349  |   0.3217 |   0.3752 |     0.3305 |     0.3866 |
| F6_MISSINGNESS_ONLY   | logistic_regression |        12 |     0.8546 |   0.8126 |   0.8908 |     0.2194 |   0.1624 |   0.281  |     0.2115 |     0.2019 |

Operating point for FAR/FRR: threshold from the calibration EER point. `EER_mean` is the test-set oracle EER (reported for reference; never used to set an operating point).

## Feature-set definitions

- **F1_ALL** (225 features): all 225 features; location and device-state INCLUDED per Stage 2 decision
- **F2_STAGE1_COMPARABLE** (103 features): closest analogue of the Stage 1 pool (acc+gyro+location+discrete), for comparability
- **F3_NO_LOC_NO_DEVSTATE** (119 features): ablation: motion/ambient sensing only; no location, no device state, no watch
- **F4_LOCATION_ONLY** (17 features): diagnostic: identity information carried by location alone
- **F5_DEVICE_STATE_ONLY** (34 features): diagnostic: identity information carried by device/OS state alone
- **F6_MISSINGNESS_ONLY** (225 features): diagnostic: binary NaN indicators only; tests the Stage 1 data-availability shortcut

## Protocol sizes (median across executed runs)

| quantity                     |   median |
|:-----------------------------|---------:|
| n_genuine_train              |   3829.5 |
| n_genuine_calib              |   1277   |
| n_genuine_test               |   1277   |
| n_impostor_train             |  48000   |
| n_impostor_calib             |  23600   |
| n_impostor_test              |  47624   |
| n_test_impostor_participants |     23.5 |
| n_test_segments              |      3   |
| genuine_test_span_hours      |     29.2 |

## Leakage checks

| check                                            |   passed |   evaluated |
|:-------------------------------------------------|---------:|------------:|
| enrolled_user_not_in_own_impostor_sets           |      144 |         144 |
| genuine_calib_before_test                        |      144 |         144 |
| genuine_train_before_calib                       |      144 |         144 |
| impostor_pools_disjoint                          |      144 |         144 |
| no_duplicate_train_rows                          |      144 |         144 |
| no_row_reuse_train_test                          |      144 |         144 |
| preprocessing_fitted_on_training_rows_only       |      144 |         144 |
| test_impostor_rows_from_unseen_participants_only |      144 |         144 |
| test_impostors_unseen_in_fitting                 |      144 |         144 |

All checks abort the run on failure, so any run present in the results passed all of them.

## Failures

None.

## Per-user variability (executed users)

EER range across users, gradient boosting, F1_ALL: 0.0000 to 0.0688

## Files

`per_run_results.csv`, `ablation_summary.csv`, `run__*.json`, `per_impostor/`, `score_streams/`, `manifests/`, `experiment_metadata.json`, `logs/run.log`, figures in `figures/`.
