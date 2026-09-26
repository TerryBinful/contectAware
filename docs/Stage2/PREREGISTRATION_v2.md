# PREREGISTRATION v2 — Stage 2 decision-layer comparison

Status: **re-registration after an exploratory run.** The v1 run (`results/mechanism_comparison/`,
commit `2847ae1`) has been seen by the researcher and by three reviews. It is hereby labelled
**exploratory**. This document fixes the analysis rules for the v2 run *before* the v2 scores exist.
It does not claim the innocence of a true pre-registration, and nothing here should be described as
pre-registered in the original sense.

Frozen at commit: recorded in `results/mechanism_comparison_v2/experiment_metadata.json`.
Date: 2026-09-26.

---

## 1. Question

Under a common authentication-score generator and matched operating conditions, how do temporal
decision-layer stabilisation mechanisms differ in security, temporal decision stability and
responsiveness during controlled identity transitions?

## 2. What is fixed before the run

### 2.1 Unchanged from v1 (leakage-verified; not to be modified)

Regular-cadence cohort (31 users); chronological 60/20/20 per-user split; participant-disjoint
impostor pools (fit 24 / calibration 12 / test 24) with unseen final-test impostors; training-only
imputation and scaling; one fixed per-user gradient-boosting score generator shared by all
mechanisms; log-odds raw scores with a monotone non-decreasing ECDF normaliser fitted on calibration
only; controlled identity-transition sequences `[genuine 60 | impostor 60 | recovery 60]` frames built
from contiguous real observations; frames as the temporal unit (~1 minute each); initial state
AUTHENTICATED; participant-level paired analysis.

### 2.2 Changed for v2, and why

| # | Change | Reason |
|---|---|---|
| C1 | **Selection rule: one-sided.** A candidate is eligible iff `target − tol ≤ calibration FAR ≤ target`. Among eligible candidates choose **minimum calibration FRR**, then minimum complexity. | v1 chose by `|FAR − target|`, which ignores FRR (D1) and yields FRR non-monotonicity in 23–71% of users for multi-parameter mechanisms. A symmetric band plus min-FRR would select the top of the band and inflate optimism; the one-sided band caps achieved FAR at the target (Neyman–Pearson). |
| C2 | **Reachability filter.** Reject any candidate whose accept threshold exceeds the maximum achievable normalised score (the ECDF caps at 1.0), before selection. Record rejections per user and mechanism. | v1 selected absorbing-latch configurations for 7/31 hysteresis and 3/31 margin users, which can never re-authenticate (D2). This is a structural constraint, not a performance criterion. **No recovery-rate floor is applied**: selecting on recovery would select on an outcome being measured. |
| C3 | **Calibration impostors round-robin** over all 12 calibration-pool participants; `calib_sequences_per_user = 24` (test stays 6). Record distinct calibration impostors per user. | v1 drew impostors at random with replacement from 6 sequences, so at most 6 of 12 were seen, and calibration-to-test FAR drift was +0.8 to +2.0 pp (D3). |
| C4 | **SPRT gets a continuous parameter**: log-spaced `A`, `B` over [0.5, 64] (15 × 15) plus an LLR offset `δ ∈ [−2, 2]` (21 values). | v1 offered 25 coarse points and no continuous parameter; the claim that SPRT's infeasibility is structural was an inference, not a finding (M3). |
| C5 | **Metrics added**: excess transitions `max(n − 2, 0)`; share of sequences with fewer than 2 transitions; detection- and recovery-failure rates; latencies reported both conditional on success and censored at 60 frames with a censoring flag; calibration-vs-test FAR drift per mechanism; test FAR with a 2,000-sample user-level bootstrap CI and a "matched" flag. | Each sequence contains two *required* transitions, so the v1 transition rate rewarded failure to respond: hysteresis (0.904/100) scored below the perfect-system floor (1.117/100) (M1). Conditional latency means excluded failures (M2). |
| C6 | **Trust model disclosure**, and a single-threshold variant `trust_model_single` (τ_lo = τ_hi = 0.5). | The v1 trust model uses τ_lo = 0.4, τ_hi = 0.6, which is itself a dual-threshold latch, so "hysteresis vs trust model" was not hysteresis vs a non-hysteretic alternative (M4). |
| C7 | **Score dump**: per-frame raw score, normalised score, truth, frame index, sequence id, impostor id and split, for every calibration and test sequence, plus each user's ECDF reference array. | Model fitting is ~92% of runtime (measured: 83.1 s fit vs 5.9 s calibration per user). Dumping scores makes every downstream rule change, metric and FAR target recomputable without refitting. |

## 3. Primary analysis — fixed-level factorial

Margin `m ∈ {0, 0.05, 0.1, 0.2}` × dwell `k ∈ {1, 2, 3, 5, 10}`, where `(0,1)` = instantaneous,
`(0,k>1)` = debounce, `(m>0,1)` = margin/dual-threshold and `(m>0,k>1)` = hysteresis. **In every cell
only θ is tuned**, by rule C1 with filter C2. Each cell therefore carries exactly one tuned parameter
and equal selection optimism. Margin and dwell main effects and their interaction are read from this
response surface.

Cells with no eligible candidate are reported as infeasible for that user; they are never replaced by
a nearest candidate in the primary analysis.

### 3.1 Decision rule: does hysteresis earn its place?

**Cell selection is performed on calibration data, per user, never on test.** For each user:

* `cell_H` = the eligible `(m > 0, k > 1)` cell with the lowest calibration FRR;
* `cell_D` = the eligible `(0, k > 1)` cell with the lowest calibration FRR;
* `cell_M` = the eligible `(m > 0, 1)` cell with the lowest calibration FRR.

Then, on **test** data, paired across users with Holm correction within this family, hysteresis earns
its place iff all three hold:

1. `cell_H` has fewer excess transitions than both `cell_D` and `cell_M` (paired Wilcoxon, Holm-adjusted p < 0.05 for both);
2. FRR non-inferiority: upper bound of the 95% bootstrap CI of the paired FRR difference (`cell_H` − comparator) is **< +0.02** against both;
3. detection-failure non-inferiority: same bound, **< +0.02** against both.

The ±0.02 margins are a judgement call, not a derived quantity. They are fixed here so they cannot be
chosen after seeing results, and the analysis will additionally report the full CI curve so a reader
can apply a different margin.

**If the criterion is not met, the reported conclusion is that hysteresis offers no measurable
advantage over its components on this benchmark.** That is a valid result and will be reported as the
headline finding, without softening, additional post-hoc comparisons, or a search for a subgroup in
which it succeeds.

## 4. Secondary analyses (declared in advance, reported as secondary)

1. **Tuned-family comparison** of all nine mechanisms under C1–C4, each family free to tune its own
   secondary parameters. Answers "best achievable per family"; carries unequal selection optimism by
   construction, which will be stated wherever it is reported.
2. **Operating-point sensitivity** at target FAR 0.03 / 0.05 / 0.07, each with tolerance 0.01,
   selection rule C1. Primary target is 0.05.
3. **No-SPRT subset**: users for whom every mechanism except SPRT has an eligible operating point
   (22 users at v1's rule). Replaces v1's complete-feasibility subset, which had 6 users and a
   Holm-adjusted p-floor of 0.25, making significance unattainable by construction.
4. **Score validity**: per-user AUC of `F3_NO_LOC_NO_DEVSTATE` versus `F7_F3_MISSINGNESS_ONLY`
   (missingness indicators of the F3 columns only), on identical splits and sequences. F7 is a
   construct-validity probe; **no decision layer is run on it**.

## 5. Statistical procedure

Unit of analysis: the enrolled user; sequence metrics are averaged within user before any test.
Paired Wilcoxon signed-rank tests; Holm correction **within each declared family** (factorial family
in §3.1; tuned-family comparisons against instantaneous; secondary analyses separately).
Uncertainty: 2,000-sample user-level bootstrap CIs. Missing detection or recovery events are reported
as failure rates with their sample sizes and are never imputed as zero.

Known dependence, not removed by this design: all users share one 24-participant test impostor pool;
frames may recur across sequences of the same user; sequences are averaged within user rather than
treated as subjects.

## 6. Commitments

1. A null result or a reversal of the v1 direction (for example, stabilisers showing FRR at or below
   instantaneous) will be reported as the finding.
2. No parameter, threshold, metric definition, cohort or criterion in this document will be changed
   after the v2 scores are inspected. Any change that nevertheless proves necessary will appear in a
   **DEVIATIONS** section of the v2 report, with its reason and its effect on the result.
3. v1 outputs are retained unmodified and labelled exploratory.
4. Anything not established by the v2 evidence will be written as NOT ESTABLISHED rather than
   inferred.

## 7. Out of scope for v2

Fragmented-cadence participants; feature sets other than F3 and the F7 probe; other score-generator
families; device-identity disentanglement (not possible in ExtraSensory: each participant used their
own phone, so an impostor block is also a device change — this remains a stated construct-validity
limitation, not an experiment).
