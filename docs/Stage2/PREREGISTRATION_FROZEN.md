# Pre-registration (frozen) — Stage 2 decision-layer stabilisation comparison

Filled from `docs/planning/01_preregistration_template.md`. Frozen **2026-09-25**, before the primary
(`main`) run. Machine-readable twin: `experiment_Files/Stage2/configs/main.yaml` — if the two ever
disagree, the config file used by the run (hashed into `experiment_metadata.json`) is authoritative
and the disagreement is a documentation defect.

## 1. Research questions
- **RQ1.** At a matched genuine false-lock rate, do decision-layer stabilisation mechanisms differ in impostor-detection latency?
- **RQ2.** Does hysteresis (dual threshold + dwell, from cellular handover) differ from the best single-parameter smoother and from trust / sequential models on that trade-off?
- **RQ3.** Is any hysteresis effect attributable to margin **and** dwell jointly rather than either component alone?
- **RQ4.** Do findings differ between cross-context (X) and context-matched (M) impostors?

Working hypothesis: mechanisms exhibit **different trade-offs** at comparable operating points. No winner is assumed; a null result is a valid result.

## 2. Hypotheses
| | Hypothesis | Null |
|---|---|---|
| H1 | Mechanisms differ in detection delay at the matched false-lock rate | No difference (Friedman non-significant) |
| H2 | Hysteresis detection delay < best single-parameter smoother | No difference or hysteresis worse |
| H3 | Hysteresis beats **both** margin-only and dwell-only (debounce) | At least one component alone is not worse |
| H4 | Detection delay is longer in M than X, per mechanism | No difference |

## 3. Primary comparison (the only confirmatory test)
- A: hysteresis. B: best single-parameter smoother among {moving average, EWMA, majority vote, debounce, margin}, chosen on **validation** by the same statistic used for operating-point selection, and written to `operating_points.csv` (column `best_smoother`) **before** any test computation.
- Operating point: pooled genuine false-lock rate **0.125 / h** (1 per 8 genuine hours), ±15%.
- Condition: **M** if context-matched coverage ≥ 0.80 in both partitions, else X (decided by label availability only).
- Outcome: per-user median sustained-detection delay (frames; misses censored at L).
- Test: two-sided Wilcoxon signed-rank across genuine users, α = 0.05. Effect: median paired difference, user-level bootstrap 95% CI (5000), matched-pairs rank-biserial r.
- Everything else is secondary and Holm-corrected within its family (see `src/ca_stability/stats.py`).

## 4. Fixed design decisions
| Item | Decision | Why |
|---|---|---|
| Cohort | participants with ≥ 80% of gaps in 59–61 s, ≥ 300 val and test stream frames | frame-based parameters need a fixed time meaning; audit shows a clean bimodal split (34 vs 26) |
| Genuine / impostor pool | same cohort for both roles | reduces platform/cadence confounds between roles |
| Features (primary) | phone accelerometer + gyroscope (`raw_acc`, `proc_gyro`, 52) | excludes the Stage 1 location / device-state / missingness shortcuts |
| Time split | per participant 60/20/20 chronological, 30-min embargo | no temporal adjacency between train and evaluation (Stage 1 criterion C1) |
| Impostor roles | per genuine user: 50% train, 25% calibration, 25% test — disjoint | open-set; test impostors never seen by the model or by parameter selection |
| Classifier | HistGradientBoosting (200 it., lr 0.1, depth 6, leaf 50, L2 1, balanced); imputer/scaler fit on training rows; per-user Platt on validation | reuses the corrected protocol of `Stage1/exp4_feature_ablation.py`; no SMOTE, no selection |
| Exp 1 gate | median per-user test AUC ≥ 0.60, else STOP | hard gate (audit blueprint) |
| Sessions | a run ends at a gap > 120 s (2 × median period) or a period change; every run starts AUTH | gaps are not decisions |
| Benchmark | W = 5; L ∈ {3, 10, 30, 60} frames; 4 sequences per (user, condition, partition, L); burn-in ≤ 120, suffix ≤ 60 frames | `docs/planning/02_splice_benchmark_spec.md` |
| Grids | see `configs/main.yaml`; θ grid = sigmoid(linspace(−7, 7, 141)); SPRT β log-grid (60) | |
| Hysteresis dwell | T ∈ {2, 3, 5, 8} (T = 1 excluded) | T = 1 is exactly the margin arm; excluding it keeps arms non-nested for H3 |
| False-lock rate | pooled over validation users: Σ false locks / Σ genuine hours | per-user rates are mostly 0 at 1/8 h and cannot be matched individually |
| Selection | admissible = rate in band **and** mean false-lock duration ≤ 30 frames (A1); pick lowest validation median detection delay; ties → lower FAR_frame → closer rate → grid order; if none admissible → nearest rate (flagged) | identical rule for every mechanism |
| Sensitivity targets | 0.5 / h and 1 / 24 h | trade-off shape away from the primary point |
| Metrics | `docs/Stage2/METRIC_DEFINITIONS.md` (n_sustain = 3, W_pp = 5) | |

## 5. Falsification criteria
- **H2 falsified if** the primary Wilcoxon test is non-significant or the median paired difference ≥ 0 (with 1-minute frames, a difference < 1 frame is below the data's resolution).
- **Handover framing dropped if** H3's null holds, or trust / SPRT has lower-or-equal test median detection delay **and** FAR_frame than hysteresis at the matched primary point.
- **H1 rejected if** the Friedman test on detection delay is non-significant.

## 6. Reported regardless of outcome
Full validation and test sweep tables; per-user metrics; excluded participants and why; negative results; operating-point transfer (validation → test); all sensitivity analyses that were run.

## 7. Analyst degrees of freedom closed
No metric, mechanism, grid value or operating point changes after test results of the primary run are seen. Deviations are appended below with a date and reason.

## Amendments
- **A1 — 2026-09-25 — lockout admissibility (`operating_point.max_lockout_frames: 30`).** The pilot (8 genuine users) showed that, under the rate-only rule, margin, hysteresis, trust and HMM cells met 0.125 / h by *never unlocking* (e.g. θ + m/2 ≥ 1): up to 95% of genuine time locked. A false-lock count only measures genuine cost if locks are recoverable, so a cell is admissible only if its mean false-lock duration is ≤ 30 frames (≈ 30 min). This was decided on pilot **validation** sweeps, before the pilot's evaluate stage ran.
- **A2 — 2026-09-25 — disclosure.** The pilot's test-partition outputs (8 of 33 genuine users, a subset of the primary run) were produced as an end-to-end check before the primary run. After they were produced, only non-substantive code changes were made: an empty-suffix guard in the recovery metric (no effect when suffix ≥ W) and the `features.exclude_patterns` option, which the primary config leaves empty. No primary design value changed.
- **A3 — 2026-09-25 — added sensitivity configurations** (`sens_original_features`, `sens_motion_dynamics`, `sens_all_participants`). They are secondary robustness checks and cannot alter the primary result.
