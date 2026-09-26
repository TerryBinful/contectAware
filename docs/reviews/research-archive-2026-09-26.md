# Research Archive — Continuous Smartphone Authentication
**Date:** 2026-09-26  
**Status:** Stage 2 methodological audit and pre-freeze position

## 1. Research Context

The research investigates continuous/implicit smartphone authentication using contextual smartphone sensing, with particular attention to the instability that can arise when noisy high-frequency authentication scores are converted directly into binary authentication decisions.

The refined study is no longer framed as a general claim that hysteresis is missing from behavioural authentication. The literature audit identified prior work using related mechanisms, so the defensible research contribution is narrower and methodological: a controlled comparison of alternative temporal decision-layer stabilisation mechanisms under matched operating conditions and identity-transition evaluation.

The current conceptual architecture is:

> **Data → temporally valid enrolment/test → per-user authentication score → common score stream → temporal decision layer → authentication decision**

The machine-learning component is treated primarily as the upstream analytical mechanism for generating an authentication score. The central comparison concerns the temporal decision layer.

## 2. Refined Research Questions

### Central RQ

> **How do different temporal decision-layer stabilisation mechanisms affect the security, temporal stability, and responsiveness of continuous smartphone authentication decisions under comparable operating conditions?**

### Supporting RQs

**RQ1 — Authentication-score validity**

> To what extent can the existing contextual smartphone data support a temporally separated per-user authentication score when evaluated against later genuine observations and unseen impostor participants?

**RQ2 — Decision-layer comparison**

> How do alternative temporal decision-layer mechanisms affect authentication security, decision stability, and responsiveness under matched operating conditions?

**RQ3 — Robustness/context dependence**

> How sensitive are the observed security–stability–responsiveness trade-offs to feature composition, irregular temporal gaps, and decision-layer parameter settings?

## 3. Working Hypotheses

- **H1:** A temporally separated per-user authentication model can produce above-chance identity-discrimination performance on later genuine observations and unseen impostor participants using available smartphone contextual data.
- **H2:** Temporal decision-layer mechanisms will reduce authentication-state instability relative to instantaneous thresholding, with magnitude differing across mechanisms.
- **H3:** Greater temporal persistence/stabilisation will involve a responsiveness trade-off, especially impostor detection/recovery latency.
- **H4:** Decision-layer performance will vary with feature composition where location and data-availability cues materially affect the upstream authentication score.

## 4. Stage 1 Findings and Methodological Provenance

The original Stage 1 implementation used the ExtraSensory dataset and included 60 participants and approximately 377,346 rows. Prepared examples represented approximately one minute of activity, with each example based on a 20-second sensor recording.

The original pipeline had important methodological weaknesses:

- random 80/20 row splitting;
- global imputation/scaling leakage;
- SMOTE;
- the same impostors appearing in training and testing;
- a one-vs-rest closed-set target-user formulation;
- predominantly in-sample target-user evaluation;
- authentication probabilities that did not represent a temporally separated continuous-authentication operating protocol;
- substantial location and missingness-related shortcuts;
- hysteresis evaluated on a target stream that was largely in-sample;
- a nominal three-frame TTT corresponding to roughly 180 seconds rather than three seconds;
- overlapping-window “episodes” that were not genuine event episodes.

The original gradient-boosting results were approximately:

- Accuracy: 0.9926
- Precision: 0.8524
- Recall: 0.9291
- F1: 0.8891
- FAR: 0.0053
- FRR: 0.0709
- ROC-AUC: 0.9976

These results are retained as methodological provenance only and are **not** treated as final evidence.

A further Stage 1 audit identified contextual shortcuts. Approximately 40% of feature importance was associated with location-related information; altitude alone accounted for roughly 26% in the original importance analysis. Missingness patterns also differed materially between the target and impostors.

## 5. Literature/Gaps Position

The earlier claim that telecommunications solved hysteresis decades ago while behavioural biometrics had not systematically explored it was considered too broad.

The literature audit identified adjacent work, including:

- Mondal & Bours (2017), involving trust-related continuous authentication;
- Kiyani et al. (2020), involving a dual-threshold approach;
- Zhang et al. (2025), involving a dynamic trust model;
- Raghu, MacIsaac & Scheme (2023), which provides an adjacent methodological precedent by comparing multiple decision-stream post-processing schemes in myoelectric prosthesis control rather than authentication;
- broader review literature on continuous/behavioural authentication.

The refined gap is therefore:

> **No identified published study performs a controlled, matched-operating-point comparison of multiple decision-layer stabilisation mechanisms—such as moving average, EWMA, majority vote, debounce, margin/dual-threshold, hysteresis, trust models, and SPRT—within continuous/behavioural authentication while evaluating them through identity-transition sequences rather than steady-state accuracy alone.**

This remains a cautious literature-gap formulation rather than an absolute claim that no such study exists.

## 6. Current Stage 2 Experimental Architecture

The corrected Stage 2 implementation substantially addresses the Stage 1 weaknesses.

### Cohort and temporal separation

- Primary regular-cadence cohort: 31 participants.
- Genuine-user data are separated chronologically.
- Fitting, calibration, and testing use temporally separated data.
- Impostor pools are separated between fitting/calibration and final testing.
- Final test impostors are unseen during fitting and calibration.

The current protocol describes fitting, calibration, and test impostor pools using separate participant allocations.

### Preprocessing

- Imputation is fitted only on training data.
- Scaling is fitted only on training data.
- SMOTE is not used.
- Class weighting is used where applicable.

### Authentication model

- Per-user authentication models are used.
- The model generates a common score stream.
- Temporal decision mechanisms operate on the same upstream score stream rather than receiving mechanism-specific model refits.
- The score generator uses classifier log-odds and can apply an empirical-CDF normalization fitted on calibration scores.

### Feature composition

The primary feature set is:

`F3_NO_LOC_NO_DEVSTATE`

The rationale is to reduce dependence on potentially shortcut-like location and device-state cues identified during Stage 1.

`F1_ALL` remains relevant as a sensitivity/ablation condition where supported.

The exclusion of location/device-state variables should not be interpreted as proving that those signals are inherently invalid for authentication; rather, the primary condition is intended to reduce dependence on contextual identity shortcuts and make the decision-layer comparison more diagnostically meaningful.

### Temporal benchmark

The benchmark constructs controlled sequences of the form:

> **60 genuine frames → 60 impostor frames → 60 genuine recovery frames**

The sequences are constructed from real participant observations. They are not naturally observed real-world identity-switch episodes.

The implementation preserves the approximately one-minute frame cadence and does not interpolate, synthesize, or resample observations for the identity-transition construction.

Mechanisms begin in the authenticated state because the benchmark begins with a genuine block. This is an explicit benchmark assumption.

## 7. Decision-Layer Mechanisms

Nine mechanisms are currently implemented:

1. Instantaneous threshold
2. Moving average
3. EWMA
4. Majority/sliding-window vote
5. Debounce/persistence
6. Margin/dual-threshold
7. Hysteresis
8. Trust model
9. SPRT

They should be described as alternative temporal decision-layer mechanisms rather than as mathematically equivalent algorithms.

A useful taxonomy is:

- **Temporal smoothing:** moving average, EWMA
- **Voting/persistence:** majority vote, debounce
- **Dual-threshold/state hysteresis:** margin/dual-threshold, hysteresis
- **Stateful trust:** trust model
- **Sequential hypothesis testing:** SPRT
- **Baseline:** instantaneous threshold

## 8. Evaluation Framework

The evaluation separates three dimensions.

### Security

- FAR
- FRR
- related authentication error measures

### Temporal stability

- transition counts
- transition rate per 100 frames
- flip events
- mean run length
- median run length

### Responsiveness

- impostor detection latency
- lockout during genuine recovery
- recovery latency

The corrected detection-latency logic searches for stable rejection only within the impostor interval and requires the stability criterion to be satisfied before the recovery transition.

Recovery latency begins at the recovery transition.

The old overlapping-window episode metric is not used as the primary event metric.

## 9. Statistical Analysis

The current statistical analysis uses:

- participant-level paired differences;
- Wilcoxon signed-rank tests;
- Holm multiple-comparison correction;
- participant-level bootstrap confidence intervals.

The use of participant-level aggregation avoids treating individual frames or controlled sequences as independent subjects.

However, two dependence limitations remain important:

1. The final-test impostor pool is shared across enrolled users, so participant-level results are not perfectly independent with respect to impostor composition.
2. Underlying participant observations may be reused across controlled sequences. The analysis does not treat sequences as independent subjects, but possible cross-sequence reuse should remain explicit in the limitations.

Missing recovery latency should not be converted into zero. Comparisons should report the number of users for whom recovery latency was defined.

## 10. Current Calibration Issue

The primary operating point is a target FAR of 0.05 with a ±0.01 feasibility interval:

> **0.04 ≤ FAR ≤ 0.06**

The corrected calibration logic uses this interval and records infeasible cases rather than silently forcing an apparently matched operating point.

Current feasibility counts are:

| Mechanism | Infeasible user–mechanism combinations |
|---|---:|
| Instantaneous | 1/31 |
| Moving average | 0/31 |
| EWMA | 0/31 |
| Majority vote | 0/31 |
| Debounce | 0/31 |
| Margin/dual threshold | 8/31 |
| Hysteresis | 0/31 |
| Trust model | 0/31 |
| SPRT | 23/31 |
| **Overall** | **32/279** |

Thus, the experiment should **not** claim that every mechanism was exactly matched at FAR = 0.05.

The defensible formulation is:

> “Nine temporal decision-layer mechanisms were evaluated using a calibration-defined target FAR of 5% with a ±1 percentage-point feasibility interval. The target interval was attainable for most mechanism–participant combinations, but not for all, particularly for SPRT and margin-based mechanisms; infeasible cases were retained and explicitly reported.”

## 11. Descriptive Final-Test Results

The current approximate mean final-test results observed during the audit were:

| Mechanism | Transition rate / 100 | FRR |
|---|---:|---:|
| Instantaneous | 2.68 | 4.7% |
| Moving average | 1.54 | 8.9% |
| EWMA | 1.53 | 9.1% |
| Majority vote | 1.58 | 5.8% |
| Debounce | 1.34 | 19.0% |
| Margin/dual threshold | 1.47 | 11.6% |
| Hysteresis | 0.90 | 35.5% |
| Trust model | 0.99 | 25.8% |
| SPRT | 1.32 | 7.4% |

These figures are descriptive. They should not be converted into an overall ranking or presented as evidence that one mechanism is universally preferable.

Participant-level paired tests against the instantaneous baseline showed that transition counts/rates and mean run lengths differed significantly for all mechanisms under Holm correction. FRR increased significantly for several mechanisms, and detection/recovery latency also increased for several mechanisms. Margin/dual-threshold and SPRT did not show significance on every tested metric after Holm correction.

These results support analysis of a security–stability–responsiveness trade-off, but the interpretation must remain mechanism- and metric-specific.

## 12. Additional Pilot/Ablation Evidence

An earlier diagnostic subset involving 12 of the 31 participants produced:

| Feature condition | AUC | EER |
|---|---:|---:|
| All | 0.9983 | 0.0107 |
| Stage-1 comparable | 0.9786 | 0.0586 |
| No location/device-state | 0.9970 | 0.0145 |
| Location only | 0.9276 | 0.1267 |
| Device-state only | 0.7326 | 0.3511 |
| Missingness only | 0.8449 | 0.2320 |

These are diagnostic pilot/ablation results, not final population estimates.

## 13. Remaining Verification and Sensitivity Work

The current Stage 2 design should remain frozen while two secondary analyses are added.

### A. Complete-feasibility sensitivity analysis

Restrict a secondary analysis to enrolled users for whom all nine mechanisms have feasible calibration operating points.

Rules:

- eligibility must be determined from calibration feasibility only;
- final-test results must never determine eligibility;
- primary 31-user analysis remains unchanged;
- rerun the same participant-level comparisons on the subset;
- report the resulting sample size and whether the substantive pattern changes.

Purpose: determine whether mechanism-level conclusions are sensitive to the fact that some mechanisms, particularly SPRT and margin-based mechanisms, do not attain the primary FAR interval for every user.

### B. Operating-point sensitivity analysis

Repeat the calibration/decision analysis at predetermined target FAR values:

- 0.03 with interval 0.02–0.04;
- 0.05 with interval 0.04–0.06;
- 0.07 with interval 0.06–0.08.

Use the same calibration-only operating-point selection rule and the same ±0.01 tolerance.

Purpose: assess whether the observed security–stability–responsiveness pattern depends materially on the selected operating point.

Neither analysis should replace the primary 0.05 analysis.

## 14. Documentation Corrections

### ECDF wording

An empirical CDF is monotone non-decreasing and may contain flat sections because of ties. Repository wording should therefore avoid calling the transformation “strictly monotone”.

Preferred wording:

> “monotone non-decreasing empirical CDF transformation”

### Dependence limitation

The final protocol/report should explicitly state the shared impostor-pool and possible cross-sequence-reuse limitations described above.

## 15. Current Research Position

The current Stage 2 work is substantially improved and methodologically credible, but it should not yet be treated as fully frozen thesis evidence.

No second research pivot is indicated.

The appropriate next stage is:

1. complete the two sensitivity analyses;
2. correct the ECDF terminology;
3. explicitly document dependence limitations;
4. inspect the resulting sensitivity evidence;
5. freeze the Stage 2 design and evidence if no material methodological issue is uncovered;
6. only then build the thesis/research argument from the actual results.

The primary experiment should not be repeatedly redesigned unless the sensitivity analyses reveal a material validity problem.

## 16. Terminology and Claim Discipline

Use:

> “controlled identity-transition sequences constructed from real participant observations”

rather than “real-world identity switches”.

Do not describe the current protocol as demonstrating that all mechanisms were matched exactly at FAR = 0.05.

Do not reuse the original Stage 1 metrics as if they were final continuous-authentication evidence.

Do not treat the nine mechanisms as structurally identical.

Do not treat sequences as independent statistical subjects.

Do not convert undefined recovery latency to zero.

Do not tune operating points from final-test results.

## 17. Open Questions

1. How many users remain in the complete-feasibility subset?
2. Do the qualitative security–stability–responsiveness patterns persist in that subset?
3. How does changing the target FAR to 0.03 or 0.07 affect mechanism feasibility and observed trade-offs?
4. Does the sensitivity evidence materially change the interpretation of the primary results?
5. Are any additional protocol dependencies or data-reuse issues revealed during the sensitivity runs?
6. Does the literature search still support the refined gap wording when the final bibliography is assembled?

## 18. Stop/Falsification Conditions

The work should be reconsidered rather than simply pushed into thesis writing if verification shows that:

- final-test information was used in calibration or participant eligibility;
- temporal separation is not actually enforced;
- unseen impostor status is violated;
- the controlled sequences contain unintended overlap that materially changes the statistical unit;
- mechanism operating points are being selected inconsistently;
- sensitivity analyses materially reverse the interpretation of the primary findings;
- the literature reveals an exact prior matched-operating-point multi-mechanism comparison that materially overlaps the claimed contribution.

These are verification triggers, not conclusions that such problems currently exist.

## 19. Immediate Working State

**Primary design:** retain and freeze provisionally.

**Primary feature set:** `F3_NO_LOC_NO_DEVSTATE`.

**Primary operating point:** FAR target 0.05 ± 0.01.

**Primary cohort:** 31 regular-cadence participants.

**Primary comparison:** nine temporal decision-layer mechanisms under a common score-stream architecture.

**Immediate task:** complete the two sensitivity analyses and documentation corrections.

**Thesis writing:** defer until Stage 2 evidence is frozen.
