# Does the Handover Margin Earn Its Place? A Factorial Comparison of Temporal Decision Policies for Context-Based Continuous Smartphone Authentication

## Abstract

Continuous smartphone authentication is commonly evaluated as a frame-level classification problem, although a deployed system must convert noisy score streams into persistent authentication states. That conversion can introduce a distinct stability problem: repeated authenticated/unauthenticated reversals near a decision boundary. Cellular handover offers an appealing analogue because it combines a margin with a time-to-trigger, but the margin has rarely been isolated from temporal persistence under a common score stream and a calibration-defined operating point.

This study evaluates whether the margin component earns its place. A fixed per-user gradient-boosting score generator was trained on chronologically separated ExtraSensory data, and decision policies were applied offline to identical controlled 60-frame genuine, 60-frame impostor and 60-frame recovery sequences. The preregistered factorial comparison separated margin and dwell: instantaneous thresholding, dwell only, margin only, and margin plus dwell. Parameters were selected using calibration data only at a decision-layer false-accept-rate (FAR) target of 0.05, with a one-sided feasibility band of 0.04–0.05. Participant-level paired tests compared the selected margin-plus-dwell policy with its components.

The preregistered hypothesis was not supported. Margin plus dwell did not reduce excess state transitions relative to dwell alone or margin alone after Holm correction (both adjusted p = 0.69). Relative to dwell alone, its false rejection rate (FRR) was 0.074 higher (95% bootstrap confidence interval 0.032–0.119), exceeding the preregistered non-inferiority bound of 0.02. Descriptively, dwell of two frames reduced mean excess transitions from 2.012 to 0.466 per sequence for an approximately 0.01 increase in FRR, whereas more aggressive margin-plus-dwell settings traded further stability for lockout. The broader tuned-family comparison showed the same stability–lockout trade-off. However, 71.7% of instantaneous test sequences had no excess transition, and a missingness-only feature set achieved mean AUC 0.758, limiting construct validity and power.

The evidence therefore does not support transferring the handover margin as a beneficial addition in this benchmark. A modest dwell captures most measurable stabilisation at lower cost. The contribution is a leakage-aware, calibration-frozen decision-layer decomposition showing why temporal stability must be evaluated separately from authentication accuracy and why lower transition counts cannot be interpreted without FRR, FAR drift and recovery behaviour.

**Keywords:** continuous authentication; smartphone sensing; decision layer; hysteresis margin; time-to-trigger; temporal persistence; false acceptance rate; state stability.

## 1. Introduction

Continuous authentication seeks to maintain confidence in the current device user after initial login. Passive smartphone signals—including movement, location, ambient context and device state—can support this aim without repeatedly interrupting the user. Yet a classifier score is not itself an authentication decision. A practical system must transform a stream of scores into a persistent authenticated or unauthenticated state.

This distinction creates a decision-layer problem. If scores oscillate around a threshold, instantaneous thresholding can repeatedly reverse the state even when the underlying user identity has not changed. Such instability is different from classification error: a system may have high area under the receiver operating characteristic curve (AUC) yet behave poorly over time. Conversely, a mechanism can suppress transitions simply by remaining locked out. Stability therefore cannot be judged independently of security, usability and responsiveness.

Cellular handover provides a useful but imperfect analogy. A handover is commonly delayed until a candidate signal exceeds the serving signal by a hysteresis margin and satisfies a time-to-trigger. In authentication, a dual-threshold margin can reduce boundary chatter, while a dwell requirement can demand persistent evidence before a state change. The analogy is attractive because both domains manage noisy sequential evidence and costly state reversals. It is incomplete because authentication compares user hypotheses rather than radio links, false acceptance and false rejection are asymmetric security outcomes, and recovery after an impostor segment is not equivalent to network mobility.

The key empirical question is therefore not whether any temporal policy smooths a score stream, but whether the margin contributes useful stabilisation beyond simpler persistence. Prior continuous-authentication work has compared combinations of fusion, threshold, boosting and trust-model choices using action-domain measures. It has not established that a margin adds value to dwell under an equal-tuning factorial contrast at a common calibration-defined FAR. This study tests that narrower claim.

The research question is:

> **At a calibration-defined decision-layer FAR target, does adding a handover-inspired margin to temporal dwell reduce excess authentication-state transitions without unacceptable false rejection or detection failure?**

The contributions are:

- a controlled decomposition of margin and dwell on one frozen score stream;
- a calibration-only, participant-specific operating-point procedure with explicit feasibility handling;
- participant-level evaluation of stability, FAR, FRR, detection and recovery rather than frame-level accuracy alone;
- evidence that the margin adds no measurable stability advantage over its components in this benchmark and is FRR-inferior to dwell alone;
- construct-validity analyses showing that instability is concentrated and that score discrimination partly reflects missingness, location or device-state structure.

## 2. Related Work

### 2.1 Continuous authentication and temporal decisions

Continuous-authentication studies use behavioural and contextual signals such as touch, gait, application use, location and other sensor-derived features. The upstream model commonly outputs scores or short-window decisions, but a deployed system must decide when accumulated evidence warrants locking or re-authenticating. These are separate design layers: a strong classifier can still produce an unstable state sequence, and a stable state sequence can conceal prolonged false rejection.

Temporal approaches include smoothing, voting, dwell/debounce rules, dual thresholds, trust accumulation, hidden-state models and sequential hypothesis tests. Mahbub et al. model application-usage patterns as a Markovian process for continuous smartphone verification; this supports hidden-state temporal modelling but is not a face-authentication study. Roy et al. apply an HMM-based behavioural model to continuous mobile authentication. Allano et al. use SPRT for sequential score fusion in multibiometric verification; their system is a biometric SPRT precedent, not a session-level continuous-authentication study. Michel et al.'s DP-SPRT is likewise a general privacy-preserving sequential-test method, not an authentication evaluation.

Zeeshan et al. state that EWMA is used to stabilise decisions and avoid flickering in a resource-constrained continuous-authentication design. Their paper motivates smoothing but does not isolate its effect, report the EWMA coefficient, or evaluate a dual-threshold hysteresis margin. This illustrates the methodological gap: temporal stabilisation is often asserted as a design choice rather than decomposed experimentally.

### 2.2 Decision-layer comparison and the gap

Mondal and Bours evaluate combinations of fusion, threshold setting, score boosting and static or dynamic trust models on continuous mouse dynamics. They report action-domain measures such as average genuine actions before false lockout and average impostor actions before detection rather than a matched-FAR component contrast. Their work establishes that the decision layer matters, but its multi-factor sweep does not isolate the incremental effect of a margin added to dwell.

Sugrim et al. show why EER-to-EER comparison is insufficient when a system has a specific false-positive requirement, and demonstrate comparison at a fixed false-positive operating point. A fixed point alone is not a complete performance description, but a calibration-defined FAR target makes the present component contrast more interpretable than comparing policies at unrelated thresholds.

The defensible gap is therefore narrow:

> Prior work compares temporal decision-layer combinations, but evidence is limited on the incremental effect of a dual-threshold margin when margin and dwell are decomposed under equal tuning on a shared score stream at a calibration-defined FAR target.

This is not a claim that decision-layer mechanisms have never been compared. The novelty is the controlled margin-by-dwell decomposition and its security–stability–responsiveness evaluation, not the classifier, the dataset, or temporal smoothing itself.

### 2.3 Evaluation validity

Evaluation design can dominate reported biometric performance. Leakage can arise through preprocessing, temporal overlap, non-independent samples or repeated identities across partitions. Touch-authentication evaluations likewise show that sample construction, temporal contiguity, attacker data and device mixing can materially change reported error rates. The present design therefore freezes chronological partitions, fits preprocessing on enrolment data only, keeps final-test impostors out of model fitting and calibration, and conducts inference at participant level.

Device and context shortcuts remain a separate concern. Stragapede et al. show that mobile behavioural-biometric models can identify the device rather than the user. The ExtraSensory corpus was created for in-the-wild context recognition, not authentication, and includes each participant's everyday devices, heterogeneous missingness and context-rich features. These properties make it useful for controlled reanalysis but prevent strong claims about identity biometrics.

## 3. Method

### 3.1 Dataset and cohort

The study reuses the public ExtraSensory dataset, which contains smartphone and smartwatch sensor-derived examples from 60 participants, typically sampled at approximately one-minute intervals with gaps. It was collected for context recognition rather than authentication. The analysis uses the 31-participant regular-cadence cohort defined before the confirmatory score dumps were generated.

Each participant is treated as an enrolled user in a one-versus-rest authentication task. The design uses chronological enrolment, calibration and test partitions. Impostor participants are separated into fitting, calibration and final-test pools so that final-test impostors are unseen during model fitting and parameter calibration.

### 3.2 Score generator

A per-user gradient-boosting model produces a continuous authentication score for each frame. Training-only preprocessing and the score model are fixed before any decision policy is applied. Every temporal mechanism receives the same stored score sequences, so mechanism effects are separated from classifier retraining.

The primary F3 feature configuration retains location and device-state information. A secondary F7 configuration contains only missingness indicators and is used solely as a descriptive score-validity probe. No decision mechanism is evaluated on F7.

### 3.3 Controlled sequences

Each test sequence contains 180 frames: 60 genuine frames, 60 frames from an unseen impostor, and 60 genuine recovery frames. These are controlled identity-transition sequences assembled from real participant observations; they are not naturally observed takeover sessions. Six test sequences and 24 calibration sequences are available per enrolled participant.

A correct state trace requires two transitions: authenticated to unauthenticated after impostor arrival, then unauthenticated to authenticated after the genuine user returns. Excess transitions count reversals beyond this minimum.

**Figure 5. The sequence-level evaluation contract.** A 180-frame controlled identity-transition sequence contains genuine, unseen-impostor and genuine-recovery segments of 60 frames each. The policy outputs an authentication state at every frame; the minimum correct trajectory has two state changes. Excess transitions, segment-specific errors, failure rates and boundary-corrected latencies are computed on this common trace. See `docs/Stage2/figures/rendered/fig5_sequence_schematic.{png,pdf}`.

### 3.4 Decision policies

The confirmatory factorial grid varies two factors:

- margin \(m \in \{0, 0.05, 0.10, 0.20\}\);
- dwell \(k \in \{1, 2, 3, 5, 10\}\).

| Cell | Margin | Dwell | Interpretation |
|---|---:|---:|---|
| Instantaneous | 0 | 1 | One threshold, immediate switching |
| Dwell only | 0 | >1 | Consecutive evidence required |
| Margin only | >0 | 1 | Dual threshold, immediate switching |
| Margin + dwell | >0 | >1 | Margin and persistence composed |

The composed cell is called **margin + dwell**, not hysteresis. In the handover analogy the hysteresis term is the margin; time-to-trigger is a separate dwell term. This terminology is used consistently throughout the revision.

A secondary tuned-family analysis also includes moving average, EWMA, majority vote, debounce, dual-threshold margin, margin + dwell, dual-threshold trust, single-threshold trust and SPRT. The family comparison is descriptive and secondary because families have unequal grid sizes and therefore unequal selection opportunity.

### 3.5 Calibration

For each participant and candidate policy, parameters are selected using calibration data only. Scores are transformed by a calibration-fitted monotone non-decreasing empirical cumulative distribution function. The primary target is decision-layer FAR 0.05 with the preregistered one-sided feasibility interval 0.04–0.05. Reachability constraints exclude candidates that cannot produce the required state behaviour.

Within each factorial class, selection minimises calibration excess transitions under the frozen tie-break rules. The test set does not influence candidate selection, threshold choice, feasibility or inclusion.

The phrase **calibration-defined decision-layer FAR target** is important. Stateful policies can alter FAR through memory and initial state, not only through a score threshold. The procedure therefore does not imply identical score-level operating characteristics across policies.

### 3.6 Outcomes

The primary stability outcome is mean excess transitions per 180-frame sequence. Security, usability and responsiveness outcomes are FAR over impostor frames, FRR over genuine and recovery frames, detection and recovery failure, boundary-corrected detection and recovery latency, and state-transition count.

The participant is the inferential unit. Sequence metrics are averaged within participant before paired comparison. This avoids frame-level pseudoreplication, although shared impostor pools and reuse of source observations across controlled sequences induce residual dependence between participant summaries.

### 3.7 Confirmatory criteria

The preregistered claim that margin + dwell earns its place required all of the following against both dwell-only and margin-only comparators:

1. fewer participant-level excess transitions after Holm adjustment;
2. FRR non-inferiority, with the upper bound of the 95% bootstrap confidence interval below +0.02;
3. detection-failure non-inferiority.

Paired excess-transition differences use Wilcoxon signed-rank tests. Holm correction is applied across the two primary stability comparisons. Confidence intervals are participant-level bootstrap intervals over paired differences.

### 3.8 Reproducibility

The analysis rules, grids, outcomes and mechanical verdict were frozen before the F3 and F7 score dumps existed. The score dumps were produced from commit `f42f55c` using scikit-learn 1.6.1 and seed 20260918. The executed analysis code is byte-identical to the frozen code. No preregistered rule, grid, metric or criterion was changed after score generation.

Prior access to the dataset and earlier exploratory work must still be disclosed. Preregistration after prior access reduces analytical flexibility but cannot fully remove researcher bias. Accordingly, the result is described as confirmatory with respect to the frozen Stage 2 score dumps and rules, not as an untouched-data replication.

## 4. Results

### 4.1 Margin-by-dwell surface

At the target FAR of 0.05, the response surface shows a consistent descriptive pattern: increasing dwell or margin reduces excess transitions, while stronger settings increase FRR and recovery failure. Cell-level means are unpaired because feasible participant sets differ across candidate cells and must not be interpreted as direct treatment contrasts.

**Figure 1. Factorial response surface at target FAR 0.05.** Rows vary margin and columns vary dwell. The upper panel reports excess transitions and the lower panel FRR. Broadly, stability improves down and to the right while lockout worsens; the preregistered paired comparisons, not apparent differences between unpaired cells, support the primary claims. See `docs/Stage2/figures/rendered/fig1_factorial_surface.{png,pdf}`.

| Factorial cell | Feasible participants | Excess transitions / sequence | FRR | Test FAR | Recovery failure |
|---|---:|---:|---:|---:|---:|
| Instantaneous (0,1) | 30 | 2.012 | 0.042 | 0.043 | 0.042 |
| Dwell (0,2) | 29 | 0.466 | 0.052 | 0.049 | 0.044 |
| Dwell (0,3) | 22 | 0.194 | 0.059 | 0.062 | 0.035 |
| Margin (0.05,1) | 20 | 0.913 | 0.061 | 0.035 | 0.063 |
| Margin (0.10,1) | 22 | 0.521 | 0.068 | 0.033 | 0.073 |
| Margin + dwell (0.05,2) | 14 | 0.288 | 0.079 | 0.053 | 0.055 |
| Margin + dwell (0.05,3) | 20 | 0.187 | 0.140 | 0.063 | 0.155 |
| Margin + dwell (0.10,3) | 17 | 0.059 | 0.210 | 0.062 | 0.320 |
| Margin + dwell (0.20,2) | 8 | 0.000 | 0.356 | 0.073 | 0.604 |

Zero excess transitions is not evidence of a good authentication policy by itself: the most aggressive settings are supported by small feasible subsets and accompany severe false rejection and recovery failure.

### 4.2 Primary paired comparison

The preregistered hypothesis was not supported. Margin + dwell did not significantly reduce excess transitions relative to either component. Its detection-failure criterion was met, but its FRR non-inferiority criterion failed against both components.

| Criterion | Margin + dwell vs dwell only | Margin + dwell vs margin only |
|---|---:|---:|
| Paired participants | 30 | 24 |
| Mean excess-transition difference / sequence | -0.13 | -0.20 |
| Median difference | 0 | 0 |
| Holm-adjusted p | 0.69 | 0.69 |
| FRR difference [95% CI] | +0.074 [0.032, 0.119] | +0.030 [-0.008, 0.069] |
| Detection-failure difference [95% CI] | 0.000 [0.000, 0.000] | -0.007 [-0.021, 0.000] |
| Recovery-failure difference | +0.103 | -0.004 |
| Censored detection-latency difference | +0.50 frames | +1.08 frames |

Against dwell only, 20 of 30 participants tied on excess transitions, six favoured margin + dwell and four favoured dwell. Against margin only, 13 of 24 tied, seven favoured margin + dwell and four favoured margin. The evidence supports the mechanical verdict:

> **Margin plus dwell offers no measurable advantage over its components on this benchmark and is FRR-inferior to dwell alone.**

### 4.3 Tuned-family comparison

All temporal families reduced excess transitions relative to instantaneous thresholding, but none escaped a broader trade-off. Mechanisms with the fewest transitions generally produced higher FRR, recovery failure or recovery latency. This family comparison is descriptive because feasible participant sets and tuning-grid sizes differ.

**Figure 2. Stability–lockout plane.** Each mechanism is positioned by mean FRR and mean excess transitions at the primary target, with trails to targets 0.03 and 0.07. Lower left is preferable, but no mechanism dominates across both axes. See `docs/Stage2/figures/rendered/fig2_stability_lockout.{png,pdf}`.

| Mechanism | n | Excess / sequence [95% CI] | FRR | Test FAR | Recovery failure | Recovery latency, censored |
|---|---:|---:|---:|---:|---:|---:|
| Instantaneous | 30 | 2.01 [0.97, 3.31] | 0.042 | 0.043 | 0.042 | 2.7 |
| Moving average | 31 | 0.53 [0.26, 0.87] | 0.058 | 0.047 | 0.041 | 5.0 |
| EWMA | 31 | 0.52 [0.23, 0.91] | 0.067 | 0.045 | 0.041 | 6.1 |
| Majority vote | 31 | 0.43 [0.21, 0.68] | 0.048 | 0.052 | 0.041 | 3.8 |
| Debounce (dwell) | 31 | 0.32 [0.12, 0.56] | 0.049 | 0.056 | 0.041 | 3.9 |
| Margin (dual threshold) | 26 | 0.40 [0.14, 0.74] | 0.083 | 0.038 | 0.103 | 7.5 |
| Margin + dwell | 30 | 0.20 [0.10, 0.31] | 0.124 | 0.059 | 0.145 | 12.0 |
| Trust model (dual threshold) | 31 | 0.04 [0.00, 0.09] | 0.172 | 0.059 | 0.138 | 19.1 |
| Trust model (single threshold) | 31 | 0.17 [0.08, 0.29] | 0.080 | 0.049 | 0.041 | 7.8 |
| SPRT | 31 | 0.32 [0.15, 0.55] | 0.036 | 0.047 | 0.035 | 2.7 |

SPRT is a notable secondary result: after expanding its frozen parameter grid, it was feasible for all 31 participants, reduced excess transitions by roughly sixfold, and did not increase mean FRR or test FAR. This result is exploratory because SPRT had the largest candidate grid and therefore the greatest selection opportunity.

### 4.4 Concentration of instability

Under instantaneous thresholding at the primary target, 124 of 173 test sequences (71.7%) contained no excess transition. Ten of 30 participants never flipped spuriously, while the five most unstable participants accounted for 65.6% of participant-level mean excess transitions.

**Figure 3. Concentration of instability.** Participants are ranked from most to least unstable under instantaneous thresholding. See `docs/Stage2/figures/rendered/fig3_instability_concentration.{png,pdf}`.

This concentration explains the many zero paired differences in the primary test. If dwell alone already eliminates the small amount of instability present for most participants, there is little remaining variation through which a margin could demonstrate incremental value.

### 4.5 Score validity

The F3 score generator achieved mean participant-level test AUC 0.990. Under the missingness-only F7 probe, mean AUC remained 0.758. The paired mean decrease was 0.232 with 95% bootstrap confidence interval 0.191–0.273; AUC fell for 30 participants, was unchanged for one and rose for none.

**Figure 4. F3 versus missingness-only F7 score validity.** Removing location and device-state features removes most, but not all, discriminative power. See `docs/Stage2/figures/rendered/fig4_score_validity_f3_f7.{png,pdf}`.

The probe does not show that missingness alone drove the primary scores, nor does it identify whether retained discrimination represents behaviour, handset, logging process or context. It does show that the upstream score is not a clean behavioural-identity construct.

### 4.6 Sensitivity analyses

The qualitative family ordering persisted when the calibration target was changed to FAR 0.03 or 0.07. Rank correlations for excess-transition ordering relative to the primary target were 0.84 at target 0.03 and 0.89 at target 0.07; corresponding FRR-rank correlations were 0.81 and 0.89. The complete-feasibility/no-SPRT subset contained 25 participants and reproduced the full-cohort pattern.

## 5. Discussion

### 5.1 The margin does not earn its place

The preregistered question has a negative answer on this benchmark. Adding a margin to dwell did not produce a detectable reduction in excess transitions relative to either component, and it increased FRR relative to dwell alone beyond the prespecified non-inferiority limit. The distinctive handover component therefore failed to justify its additional lockout cost.

The simplest explanation is not that temporal stabilisation is ineffective. On the contrary, a short dwell removes most excess transitions at small descriptive cost. Persistence, not the margin, carries most of the useful transfer from the handover analogy.

### 5.2 Stability is not superiority

Every temporal mechanism can appear successful if judged only by transition count. The strongest margin-plus-dwell and trust settings approach zero excess transitions by delaying or preventing re-authentication. This converts instability into false rejection and recovery failure rather than solving the authentication problem.

Temporal policies require a vector of outcomes: excess transitions, FAR, FRR, detection failure, recovery failure and censored latency. A single stability metric rewards policies that become inert. Likewise, frame-level AUC cannot describe decision-state behaviour.

### 5.3 What transfers from handover

The handover analogy remains useful as a conceptual framework, but only in parts. Shared features include sequential noisy evidence, costly state reversal and a need to balance responsiveness against stability. Dwell or time-to-trigger transfers naturally because it requires persistence before a transition.

The analogy breaks where authentication outcomes are asymmetric and identity evidence is not a relative signal-strength contest. A handover margin defines a region in which the current state persists; in authentication this persistence can prolong false acceptance or false rejection.

### 5.4 Contribution and novelty

The contribution is methodological and empirical rather than algorithmic. The study holds the score stream fixed, decomposes margin and dwell, freezes calibration rules before confirmatory score generation, evaluates at a decision-layer FAR target and uses participant-level paired inference. The classifier is an experimental instrument.

The novelty claim must remain narrow. Continuous-authentication decision layers, trust models, smoothing, dwell, margins and sequential tests are not new. What this study adds is an equal-tuning decomposition of the incremental margin effect under a common benchmark and a finding that the margin does not improve stability enough to justify its cost.

### 5.5 Limitations

The most serious limitation is construct validity. ExtraSensory was collected for context recognition on participants' everyday devices, not identity authentication. Location, device state and missingness can reveal participant- or handset-specific structure. Mean F3 AUC is near ceiling, while missingness alone remains discriminative. The study cannot separate behavioural identity, context regularity, device identity and logging patterns.

The controlled sequences are synthetic compositions of real observations. They standardise transition structure but do not represent naturally observed takeover sessions, interruptions, shared-device use or long-term behavioural drift. Source observations can recur across sequences, and enrolled-user summaries share a final-impostor pool; participant-level averaging reduces but does not eliminate dependence.

The regular-cadence cohort contains only 31 participants. Instability is concentrated in a small subset, leaving many zero paired differences and limited power. The study must not claim that margins are universally ineffective; it establishes no measurable advantage under this dataset, score generator, calibration protocol and benchmark.

Candidate families have unequal grid sizes, so the secondary family comparison carries unequal selection optimism. This concern is greatest for SPRT. The preregistration was also written after prior exploration of the dataset and broader project. A fresh dataset would be required for an independent confirmatory replication.

### 5.6 Practical implications

For a system designer using a similarly clean score stream, a short dwell or debounce rule is a more defensible first intervention than a composed margin-plus-dwell policy. It is simpler, easier to calibrate and captured most measured stabilisation at lower FRR and recovery cost.

No deployment recommendation follows directly. The practical result is a design principle, not a production threshold: evaluate temporal policies on held-out sequential data, calibrate them at a security-relevant operating point and report state stability together with both security and recovery outcomes.

## 6. Conclusion

This study asked whether the margin borrowed from cellular handover adds measurable value when combined with dwell for context-based continuous smartphone authentication. Under a preregistered, calibration-frozen factorial comparison, it did not. Margin plus dwell failed to reduce excess transitions relative to dwell or margin alone after multiplicity correction and was FRR-inferior to dwell alone.

The stronger finding is that decision-layer design materially changes authentication behaviour even when the upstream score stream is fixed. Simple dwell removed most instability, whereas stronger stabilisation increasingly paid for low transition counts through false rejection, recovery failure and delayed recovery.

The defensible contribution is not a universal rejection of hysteresis margins. It is a controlled demonstration that the margin did not earn its place here, together with a reproducible framework for testing whether decision rules improve a continuous-authentication system rather than merely making its state harder to change.

## Data and Code Availability

The complete analysis, frozen preregistration, score-dump provenance, generated tables, figure scripts, checks and rendered figures are maintained in the project repository. The primary evidence is under `experiment_Files/Stage2/results/mechanism_comparison_v2/analysis/`; paper figures and tables are under `docs/Stage2/figures/` and `docs/Stage2/tables/`.

## References

Allano, L., Dorizzi, B., & Garcia-Salicetti, B. (2010). Tuning cost and performance in multi-biometric systems: A novel and consistent view of fusion strategies based on the Sequential Probability Ratio Test (SPRT). *Pattern Recognition Letters, 31*(9), 884–890. https://doi.org/10.1016/j.patrec.2010.01.028

Baldwin, J. R., Pingault, J.-B., Schoeler, T., Sallis, H. M., & Munafò, M. R. (2022). Protecting against researcher bias in secondary data analysis: Challenges and potential solutions. *European Journal of Epidemiology, 37*(1), 1–10. https://doi.org/10.1007/s10654-021-00839-0

Georgiev, M., Eberz, S., Turner, H., Lovisotto, G., & Martinovic, I. (2022). Common evaluation pitfalls in touch-based authentication systems. *Proceedings of the 2022 ACM on Asia Conference on Computer and Communications Security*. https://doi.org/10.1145/3488932.3517401

Kapoor, S., & Narayanan, A. (2023). Leakage and the reproducibility crisis in machine-learning-based science. *Patterns, 4*(9), 100804. https://doi.org/10.1016/j.patter.2023.100804

Mahbub, U., Komulainen, J., Ferreira, D., & Chellappa, R. (2019). Continuous authentication of smartphones based on application usage. *IEEE Transactions on Biometrics, Behavior, and Identity Science, 1*(3), 165–180. https://doi.org/10.1109/TBIOM.2019.2918307

Michel, T., Basu, D., & Kaufmann, E. (2025). DP-SPRT: Differentially private sequential probability ratio tests. *arXiv*. https://arxiv.org/abs/2508.06377

Mondal, S., & Bours, P. (2015). A computational approach to the continuous authentication biometric system. *Information Sciences, 304*, 28–53. https://doi.org/10.1016/j.ins.2014.12.045

Roy, A., Halevi, T., & Memon, N. (2014). An HMM-based behavior modeling approach for continuous mobile authentication. *2014 IEEE International Conference on Acoustics, Speech and Signal Processing*. https://doi.org/10.1109/ICASSP.2014.6854310

Stragapede, G., Vera-Rodriguez, R., Tolosana, R., & Morales, A. (2023). BehavePassDB: Public database for mobile behavioral biometrics and benchmark evaluation. *Pattern Recognition, 134*, 109089. https://doi.org/10.1016/j.patcog.2022.109089

Sugrim, S., Liu, C., McLean, M., & Lindqvist, J. (2019). Robust performance metrics for authentication systems. *Network and Distributed System Security Symposium*. https://doi.org/10.14722/ndss.2019.23351

Vaizman, Y., Ellis, K., & Lanckriet, G. (2017). Recognizing detailed human context in-the-wild from smartphones and smartwatches. *IEEE Pervasive Computing, 16*(4), 62–74. https://doi.org/10.1109/MPRV.2017.3971131

Zeeshan, N., Bakyt, M., Moradpoor, N., & La Spada, L. (2025). Continuous authentication in resource-constrained devices via biometric and environmental fusion. *Sensors, 25*(18), 5711. https://doi.org/10.3390/s25185711
