# Stage 2 v2 results: confirmatory analysis under PREREGISTRATION_v2

## Provenance

| Item | Value |
|---|---|
| Score dumps | `results/mechanism_comparison_v2/f3` and `/f7`. Both were produced from commit `f42f55c` (the analysis freeze) with sklearn 1.6.1 and seed 20260918. |
| Users | 31 (regular-cadence cohort). 24 calibration and 6 test sequences each. 11 to 12 distinct calibration impostors per user (C3). |
| Analysis | `scripts/decision_layer_offline.py`, output in `results/mechanism_comparison_v2/analysis/`. |
| Analysis commit recorded | `f208f95`. The analysis code under `src/`, `scripts/` and `configs/` is byte-identical to the freeze `f42f55c`, checked with `git diff --quiet f42f55c f208f95`. The two commits in between (`9121634`, `e110618`) and `f208f95` itself only add result files. The dirty flag was false and the run is labelled `confirmatory: true`. |
| Deviations from the preregistration | None. No rule, grid, metric or criterion was changed after the scores existed. |
| Not used | `f3/operating_points.csv` and `f3/sequence_metrics.csv` were written by the refit driver using the v1 symmetric selection rule. They are not part of the v2 analysis. `stage2_v2_scoredump_f3_results/` is a byte-identical duplicate of `results/mechanism_comparison_v2/f3`. |

## Evidence

### Primary (§3.1): does hysteresis earn its place? Target FAR 0.05, band [0.04, 0.05]

Verdict, written mechanically: **Hysteresis offers no measurable advantage over its components on this benchmark.**

| Criterion | cell_H vs cell_D (dwell only), n = 30 | cell_H vs cell_M (margin only), n = 24 |
|---|---|---|
| 1. Fewer excess transitions (Holm p < 0.05) | Mean diff −0.13/seq, median 0. Of the 30 users, 20 tie, 6 favour H and 4 favour D. Holm p = 0.69. **Not met.** | Mean diff −0.20/seq, median 0. Of the 24 users, 13 tie, 7 favour H and 4 favour M. Holm p = 0.69. **Not met.** |
| 2. FRR non-inferiority (upper 95% CI < +0.02) | +0.074 [0.032, 0.119]. **Not met.** The CI excludes 0, so H is worse. | +0.030 [−0.008, 0.069]. **Not met.** |
| 3. Detection-failure non-inferiority | 0.000 [0.000, 0.000]. Met. | −0.007 [−0.021, 0.000]. Met. |

Other paired differences (H − comparator), descriptive:

- **Recovery failure:** +0.103 vs D and −0.004 vs M.
- **Censored detection latency:** +0.50 frames vs D and +1.08 frames vs M.

Selected cells:

- **cell_H:** m = 0.05 for 26 of 30 users, and m = 0.1 for 4.
- **cell_D:** k = 2 for 26 of 31 users.
- **cell_M:** feasible for 25 of 31 users.

Factorial response surface at FAR 0.05. Cell means over users feasible in that cell; the user sets differ across cells, so these are unpaired:

| Cell | Users feasible | Excess transitions / seq | FRR | Test FAR | Recovery failure |
|---|---|---|---|---|---|
| (0,1) instantaneous | 30 | 2.012 | 0.042 | 0.043 | 0.042 |
| (0,2) dwell | 29 | 0.466 | 0.052 | 0.049 | 0.044 |
| (0,3) dwell | 22 | 0.194 | 0.059 | 0.062 | 0.035 |
| (0.05,1) margin | 20 | 0.913 | 0.061 | 0.035 | 0.063 |
| (0.1,1) margin | 22 | 0.521 | 0.068 | 0.033 | 0.073 |
| (0.05,2) hysteresis | 14 | 0.288 | 0.079 | 0.053 | 0.055 |
| (0.05,3) hysteresis | 20 | 0.187 | 0.140 | 0.063 | 0.155 |
| (0.1,3) hysteresis | 17 | 0.059 | 0.210 | 0.062 | 0.320 |
| (0.2,2) hysteresis | 8 | 0.000 | 0.356 | 0.073 | 0.604 |

The full 20-cell surface and the CI curves at 80/90/95/99% are in `analysis/factorial/response_surface.csv` and `analysis/primary/frr_difference_curve.csv`.

### Secondary 1: tuned-family comparison at FAR 0.05

This comparison carries unequal selection optimism: families with more parameters had more chances to fit calibration.

| Mechanism | Users | Excess / seq [95% CI] | FRR | Test FAR | Recovery failure | Censored recovery latency (frames) |
|---|---|---|---|---|---|---|
| instantaneous | 30 | 2.01 [0.97, 3.31] | 0.042 | 0.043 | 0.042 | 2.7 |
| moving_average | 31 | 0.53 [0.26, 0.87] | 0.058 | 0.047 | 0.041 | 5.0 |
| ewma | 31 | 0.52 [0.23, 0.91] | 0.067 | 0.045 | 0.041 | 6.1 |
| majority_vote | 31 | 0.43 [0.21, 0.68] | 0.048 | 0.052 | 0.041 | 3.8 |
| debounce | 31 | 0.32 [0.12, 0.56] | 0.049 | 0.056 | 0.041 | 3.9 |
| margin_dual_threshold | 26 | 0.40 [0.14, 0.74] | 0.083 | 0.038 | 0.103 | 7.5 |
| hysteresis | 30 | 0.20 [0.10, 0.31] | 0.124 | 0.059 | 0.145 | 12.0 |
| trust_model (τ 0.4/0.6) | 31 | 0.04 [0.00, 0.09] | 0.172 | 0.059 | 0.138 | 19.1 |
| trust_model_single | 31 | 0.17 [0.08, 0.29] | 0.080 | 0.049 | 0.041 | 7.8 |
| sprt | 31 | 0.32 [0.15, 0.55] | 0.036 | 0.047 | 0.035 | 2.7 |

Against instantaneous, with Holm correction per metric across 9 comparisons:

- **Excess transitions:** every mechanism has fewer (all Holm p ≤ 0.0004).
- **FRR:** significantly higher for every mechanism except margin_dual_threshold and SPRT. SPRT's FRR differs from instantaneous by −0.005, Holm p = 0.86.
- **Test FAR:** significantly higher for majority vote, debounce, hysteresis, trust_model and trust_model_single, by +0.7 to +1.7 pp.
- **Recovery failure:** no difference is significant.

Reachability filter (C2), on the in-band candidates it removed at FAR 0.05:

- SPRT: 834
- margin: 240
- hysteresis: 236
- trust_model: 65

### Secondary 2: operating-point sensitivity (FAR 0.03 and 0.07)

The ordering of the families is unchanged at both targets. Hysteresis and trust_model keep the lowest excess transitions at the highest FRR and recovery failure, and SPRT keeps the lowest FRR:

- **FAR 0.03:** hysteresis 0.125 and trust 0.211, against instantaneous 0.050; SPRT 0.043.
- **FAR 0.07:** hysteresis 0.075 and trust 0.160, against instantaneous 0.030; SPRT 0.035.

The tables are in `analysis/secondary/far_0.03` and `analysis/secondary/far_0.07`.

### Secondary 3: no-SPRT subset

25 users, against 22 under the v1 rule. The pattern is the same as in the full cohort. The subset table has an empty SPRT row by construction.

### Secondary 4: score validity (F3 vs F7)

The F3 and F7 dumps have identical sequences for all 31 users. Frame-level test AUC:

- **F3:** mean 0.990, median 1.000, minimum 0.822.
- **F7 (missingness indicators only):** mean 0.758, minimum 0.400, maximum 1.000.
- **Difference:** +0.232 [0.191, 0.273].

## Interpretation (inference, labelled)

1. **The primary hypothesis is not supported, and hysteresis is FRR-inferior to dwell alone.** Against dwell-only, the stability gain from adding a margin is not detectable. Two thirds of users tie, because dwell-only already sits at about 0.3 excess transitions per sequence. Meanwhile FRR rises by about 7 pp and recovery failure by about 10 pp. On this benchmark the margin component costs usability and adds no measurable stability.
2. **Most of the stabilisation comes from temporal persistence, and the cheapest version is enough.** Going from (0,1) to (0,2) cuts excess transitions from 2.0 to 0.47 per sequence for about +1 pp FRR. This is unpaired and descriptive. It is consistent with the tuned debounce and majority-vote results.
3. **Stability and authentication performance trade off monotonically.** The mechanisms with the fewest transitions (trust_model, the larger hysteresis cells) get there by staying locked out: higher FRR, more recovery failures, and recovery latencies of 12 to 19 frames. A low transition count on its own is therefore not evidence of a better decision layer. This is exactly why C5 was added.
4. **Several stabilisers exceed their FAR on test.** Calibration capped FAR at 0.05, yet debounce, majority vote, hysteresis and trust ran 0.7 to 1.7 pp higher than instantaneous on test. Part of every stabiliser's advantage is paid for in security. The "matched" flag was true for every mechanism, but only because the user-level CIs are wide (about ±3 pp), so it cannot discriminate. The drift figures are more informative than the flag.
5. **SPRT is the notable secondary finding, and it reverses v1.** With a continuous parameter (C4) it was feasible for all 31 users. It gave the lowest FRR, the lowest recovery failure and no FAR penalty, while cutting excess transitions about sixfold. The v1 claim that SPRT's infeasibility was structural is refuted. This finding is secondary and was not confirmatory, and it carries the largest grid (4,725 candidates), so selection optimism is highest for SPRT.
6. **The instability being stabilised is concentrated and possibly artefactual.** Under instantaneous thresholding, 71.7% of test sequences have zero excess transitions, and 5 of 30 users contribute 65.6% of all excess transitions. Frame-level AUC is at the ceiling for most users. Missingness alone reaches 0.76, which suggests the score partly encodes device or logging identity rather than behaviour. The design cannot separate these (see §7 of the preregistration). The stability problem is real but small and uneven, which limits power for any mechanism comparison. This is an explanation for the tied results, not an excuse for them.

## Recommendation

1. **Essential:** report the preregistered headline without softening: "hysteresis offers no measurable advantage over its components on this benchmark". Add the FRR-inferiority against dwell-only. Do not search for a subgroup or target where it wins (§3.1).
2. **Essential:** reframe the contribution around the method and the trade-off, not a winning mechanism:
   - a matched-operating-point, preregistered comparison of stabilisation policies;
   - evidence that temporal persistence (dwell k = 2) captures most of the achievable stability;
   - evidence that stronger stabilisation buys stability with lockout and FAR drift;
   - the observation that the handover analogy's distinctive element, the margin, does not transfer usefully here.
3. **Essential:** keep SPRT's performance labelled secondary and exploratory. If you want it confirmatory, it needs its own preregistration and a fresh test set, which this dataset cannot provide without reuse.
4. **Essential:** state the construct-validity limitation prominently. F3 AUC is at the ceiling, and missingness alone reaches AUC 0.76.
5. **Optional:** delete the duplicate `stage2_v2_scoredump_f3_results/` folder, and label the v1-rule CSVs inside `f3/` as not part of v2.
