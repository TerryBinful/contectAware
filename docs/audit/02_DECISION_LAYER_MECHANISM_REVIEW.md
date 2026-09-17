# Document 02 — Decision-Layer Mechanism Review

**Date:** 17 September 2026
**Status:** Independent audit document. Does not constitute the final research paper.

## Purpose

To build a neutral taxonomy of candidate temporal decision-layer stabilization mechanisms, assess each against a common set of criteria, and classify each as an essential baseline, strong candidate, optional/exploratory, or probably unsuitable for the MSc study — **without** ranking mechanisms against each other or predicting which will perform best. Predicting a "winner" before the comparative experiment is run would be a methodological error the project brief explicitly rules out.

## Methodology / scope

Eight mechanisms are reviewed: instantaneous threshold, moving average, exponentially weighted moving average (EWMA), majority vote, debounce/persistence (Time-to-Trigger style), dual-threshold/hysteresis, trust/confidence accumulation, and (as an optional extension) sequential/model-based methods (SPRT, HMM). Each is assessed on 16 criteria spanning theoretical foundation, evidentiary support, and MSc-scope practicality. A criterion score of "unclear" or "no evidence found" is reported honestly rather than inferred.

## Criteria used (16)

1. Core decision rule (one-sentence definition)
2. Number of tunable parameters
3. State/memory requirement (stateless vs. requires history window)
4. Responsiveness behaviour (frames needed to flip decision after a genuine context change)
5. Theoretical foundation / originating field
6. Direct continuous-authentication precedent (source, if any)
7. Cross-domain precedent (source, if any)
8. Sensitivity to noise magnitude in the underlying score
9. Sensitivity to irregular/missing sampling (relevant given ExtraSensory's ~60 s, gap-prone cadence — see Document 04)
10. Behaviour under sustained impostor presence (does it eventually trigger, and how fast?)
11. Interaction with class imbalance / oversampling-adjusted scores
12. Interpretability of its internal state to a human auditor
13. Computational cost (real-time feasibility on a smartphone-class device)
14. Implementation complexity for an MSc-scope experiment
15. Whether it is purely post-hoc on any generic score stream, or requires modifying the score generator itself
16. Existing comparative literature classifying/benchmarking this mechanism against siblings (any domain)

## Evidence and analysis by mechanism

### 1. Instantaneous threshold (baseline)

- **Rule:** classify authenticated if score ≥ τ at every single time step, independently.
- **Parameters:** 1 (τ).
- **State:** none — memoryless.
- **Responsiveness:** immediate (1 frame).
- **Foundation:** classical decision theory; not itself a "stabilization mechanism" — it is the absence of one.
- **CA precedent:** implicit in nearly all CA papers as the default/naive baseline; not usually named or evaluated as a method in its own right.
- **Cross-domain precedent:** universal.
- **Noise sensitivity:** maximal — no smoothing, so ping-pong effect is expected to be worst here.
- **Missing-data sensitivity:** low, because there's no window to be broken by gaps.
- **Sustained-impostor behaviour:** triggers instantly; best-case detection latency, but also worst-case false-trigger rate.
- **Class-imbalance interaction:** fully inherits any bias in the underlying score from oversampling/SMOTE; no mitigation.
- **Interpretability:** maximal — single comparison, trivial to audit.
- **Computational cost:** negligible.
- **Implementation complexity:** trivial.
- **Post-hoc vs. score-layer:** purely post-hoc; the canonical reference point every other mechanism must be compared against.
- **Comparative literature:** used universally as the baseline comparator, e.g. implicitly in Raghu et al. (2023, [arXiv:2409.14169](https://arxiv.org/abs/2409.14169)) and in the reformulated gap's own framing.
- **Classification: Essential baseline.** Cannot be omitted — it is the reference point that "improvement" is measured against, and the origin of the ping-pong problem this study investigates.

### 2. Moving average (simple/rolling window)

- **Rule:** classify on the mean of the last *n* scores.
- **Parameters:** 1 (window size *n*), plus τ.
- **State:** requires a rolling window of *n* past scores.
- **Responsiveness:** delayed by up to *n* frames; genuine rapid transitions are smeared.
- **Foundation:** classical signal processing / time-series smoothing.
- **CA precedent:** **no direct CA-specific paper was located** implementing a plain rolling average as a named decision-layer mechanism (distinct from EWMA or trust-model variants). This must be stated plainly rather than assumed.
- **Cross-domain precedent:** ubiquitous in signal processing and process control (general knowledge, not separately cited here since EWMA — its generalization — is documented in Criterion 5/6 of the next mechanism).
- **Noise sensitivity:** substantially reduced vs. instantaneous threshold; magnitude of reduction scales with *n*.
- **Missing-data sensitivity:** moderate — a fixed *sample-count* window (rather than time window) implicitly stretches over irregular real time when sampling gaps occur, which is a material risk for ExtraSensory's gap-prone ~60 s cadence (see Document 04).
- **Sustained-impostor behaviour:** eventually triggers, but with a lag proportional to *n*; also averages in early "innocent" frames from the same window, delaying detection compared to threshold.
- **Class-imbalance interaction:** smooths but does not correct any generator-level bias.
- **Interpretability:** high — simple arithmetic, easy to explain in a viva.
- **Computational cost:** negligible (O(1) with a running sum).
- **Implementation complexity:** trivial.
- **Post-hoc vs. score-layer:** purely post-hoc.
- **Comparative literature:** treated as the simplest smoothing member of the "linear filter" family in general signal-processing texts and in the NIST control-chart literature discussed under EWMA; no direct comparative CA study found.
- **Classification: Strong candidate.** Simple, well-understood, easy to implement correctly, and a natural first rung above the naive baseline — but its **complete absence of direct CA precedent** should be stated explicitly in the paper, not glossed over.

### 3. Exponentially weighted moving average (EWMA)

- **Rule:** \(z_t = \lambda x_t + (1-\lambda) z_{t-1}\), classify on \(z_t\) vs. τ.
- **Parameters:** 2 (λ, τ).
- **State:** single running value \(z_{t-1}\) — lighter memory than a full window.
- **Responsiveness:** tunable via λ; typical λ = 0.2–0.3 gives a smoother, slower-to-react filter than moving average with an equivalent window (per [NIST Engineering Statistics Handbook §6.3.2.4](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc324.htm)).
- **Foundation:** statistical process control; formalized by Roberts (1959), with variance/design guidance from Hunter (1986) and Lucas & Saccucci (1990), per the NIST handbook.
- **CA precedent:** [MDPI Sensors 25(18):5711, 2025](https://www.mdpi.com/1424-8220/25/18/5711) uses EWMA with an adaptive, context-driven threshold in a resource-constrained continuous-authentication system, evaluated against a fixed-threshold ablation (single mechanism, not a multi-mechanism bake-off).
- **Cross-domain precedent:** NIST control-chart literature (statistical process control), one of the most mature and formally analyzed smoothing techniques found in this review.
- **Noise sensitivity:** substantially reduced, with an explicit, well-understood parameter (λ) controlling the tradeoff.
- **Missing-data sensitivity:** better-behaved than a fixed-count moving average under irregular sampling, because it only needs the immediately preceding smoothed value, not a full window of past samples — though the effective "time constant" still assumes roughly regular spacing.
- **Sustained-impostor behaviour:** triggers exponentially rather than after a hard window — behaviour is well-characterized analytically (unlike ad hoc window mechanisms), which supports rigorous statistical claims in the thesis.
- **Class-imbalance interaction:** smooths but does not correct generator bias, same as moving average.
- **Interpretability:** high — one extra parameter, well-documented meaning.
- **Computational cost:** negligible; O(1) update.
- **Implementation complexity:** trivial.
- **Post-hoc vs. score-layer:** purely post-hoc; the MDPI 2025 paper's variant additionally adapts τ, which would blur the decision-layer/score-layer distinction if replicated exactly — the MSc study should isolate the smoothing effect from the adaptive-threshold effect if it wants a clean mechanism comparison.
- **Comparative literature:** formally the best-documented single-parameter smoothing filter of all reviewed mechanisms, with an authoritative textbook-grade reference (NIST).
- **Classification: Strong candidate — arguably essential baseline alongside instantaneous threshold**, given its formal statistical grounding and existing (if single-mechanism) CA precedent.

### 4. Majority vote (sliding-window vote)

- **Rule:** classify authenticated if more than half (or a set fraction) of the last *n* binary decisions are "authenticated."
- **Parameters:** 2 (window *n*, vote fraction).
- **State:** requires the last *n* binary decisions.
- **Responsiveness:** delayed similarly to moving average; behaves as a nonlinear (rank-based) filter rather than a linear one.
- **Foundation:** ensemble decision theory / classical "urn model" voting analysis in ML.
- **CA precedent:** **no direct CA-specific paper was located** implementing sliding-window majority vote as a named decision-layer mechanism. This is the second mechanism (with plain moving average) for which no authentication-specific citation was found in this search — must be flagged, not assumed away.
- **Cross-domain precedent:** general ensemble-learning literature (majority-vote classifier theory); commonly used informally in embedded/wearable activity-recognition post-processing, though a specific, citable, peer-reviewed reference for that informal usage was not verified in this pass.
- **Noise sensitivity:** robust to isolated single-frame errors; behaves differently from linear smoothing under bursty (correlated) noise.
- **Missing-data sensitivity:** if the window is sample-count based, irregular real-time spacing changes what "recent" means, same risk as moving average.
- **Sustained-impostor behaviour:** requires a majority of the window to flip, so genuine transitions and impostor onsets are detected with similar delay to moving average, but discretely rather than continuously.
- **Class-imbalance interaction:** operates on already-thresholded binary decisions, so it inherits whatever bias the *instantaneous threshold* step introduces — this makes it structurally different from the other mechanisms, which mostly smooth continuous scores before a single downstream threshold.
- **Interpretability:** high — easy to explain ("more than half of the last n said yes").
- **Computational cost:** negligible.
- **Implementation complexity:** low-moderate (requires deciding whether to smooth before or after binarization — see below).
- **Post-hoc vs. score-layer:** post-hoc, but operates on **decisions**, not scores — this is an important structural distinction from moving average/EWMA/hysteresis, which smooth continuous scores. The taxonomy in Document 03 should treat "smooths scores" vs. "smooths decisions" as an explicit design axis.
- **Comparative literature:** included as one of the 8 compared mechanisms in Raghu et al. (2023) in myoelectric control (cross-domain, not CA).
- **Classification: Strong candidate**, but with an explicit caveat that it operates at a different point in the pipeline (post-threshold) than the score-smoothing mechanisms, and has no direct CA precedent.

### 5. Debounce / persistence (fixed dwell-time requirement)

- **Rule:** only accept a state change after it has persisted continuously for *k* consecutive frames (or *T* seconds).
- **Parameters:** 1 (persistence count/time).
- **State:** requires tracking the current candidate state and its run-length.
- **Responsiveness:** delayed by exactly *k* frames/seconds for every transition, uniformly.
- **Foundation:** embedded-systems/electronics engineering (Schmitt-trigger-style debounce logic for noisy digital signals); this is a well-established engineering pattern rather than a statistically formalized one.
- **CA precedent:** the project's earlier "Time-to-Trigger" framing is explicitly a telecom-handover-inspired instance of this same debounce logic — no independent, non-handover-framed CA paper implementing plain debounce was located in this search.
- **Cross-domain precedent:** ubiquitous in embedded systems and digital-signal debouncing (general engineering knowledge; only lower-tier web sources were found articulating this formally, so it is cited here as an engineering-practice concept rather than a peer-reviewed result).
- **Noise sensitivity:** effective against short noise bursts shorter than *k*; **ineffective** against noise that persists for ≥ *k* frames (a documented weakness of pure debounce vs. margin-based hysteresis).
- **Missing-data sensitivity:** run-length counting is disrupted by irregular sampling, since "*k* consecutive frames" means different real-world time spans under ExtraSensory's variable cadence.
- **Sustained-impostor behaviour:** triggers only after *k* consistent impostor-like frames — deliberately trades detection latency for stability.
- **Class-imbalance interaction:** operates downstream of any single-frame decision, so — like majority vote — it inherits upstream bias rather than mitigating it.
- **Interpretability:** high — very easy to explain and audit.
- **Computational cost:** negligible.
- **Implementation complexity:** trivial.
- **Post-hoc vs. score-layer:** purely post-hoc, on decisions.
- **Comparative literature:** not found benchmarked formally against sibling mechanisms in any domain reviewed here (Raghu et al.'s 8-mechanism set does not include a plain debounce variant by this name, though "onset locking" in that paper is conceptually related).
- **Classification: Strong candidate** as the "simplest possible fix" comparator for the handover-hysteresis analogy, but its known weakness (no defense against sustained noise) should be stated as a testable hypothesis, not asserted as fact before the experiment.

### 6. Dual-threshold / hysteresis (margin-based)

- **Rule:** two thresholds τ_high > τ_low; once authenticated, only de-authenticate if score falls below τ_low (and vice versa) — creating a "dead zone" that resists small oscillations around a single boundary.
- **Parameters:** 2 (τ_high, τ_low), sometimes reparametrized as (τ, margin).
- **State:** current state plus current score; no full window required.
- **Responsiveness:** depends on how far the score must travel to cross the far threshold — potentially the *most* responsive mechanism among the smoothing family (no fixed delay), but also the mechanism most sensitive to the score's noise amplitude relative to the margin width.
- **Foundation:** control theory / classical hysteresis (Schmitt trigger); the direct cellular-handover analogy is exactly this pattern applied with an added margin to prevent ping-pong between base stations.
- **CA precedent:** Kiyani et al. (2020, *IEEE Access* 8:156177–156189, DOI 10.1109/ACCESS.2020.3019467, confirmed by direct retrieval of the [published article](https://repository.mdx.ac.uk/download/e6ea94d1675e5360972f991d0ac4570614b94b447a3ff5c7818ba87424b9e2b6/1634469/Continuous%20User%20Authentication%20Featuring%20Keystroke%20Dynamics%20Based%20on%20Robust%20Recurrent%20Confidence%20Model%20and%20Ensemble%20Learning%20Approach.pdf)) — this is the **strongest direct CA precedent** of any mechanism reviewed. **Nuance confirmed on direct reading:** the paper's mechanism (a "robust recurrent confidence model") is structurally a hybrid — it accumulates trust/confidence across actions (like the trust-accumulation mechanism below) *and* uses two thresholds (alert, final/lockout) to gate behaviour, which is why it also serves as the strongest CA precedent for trust accumulation, not hysteresis alone. It means neither hysteresis nor trust accumulation is a novel mechanism in CA; the potential novelty is strictly in comparing each, in isolated form, systematically against siblings.
- **Cross-domain precedent:** LTE handover ping-pong-reduction literature ([IJFCC vol.4](https://www.ijfcc.org/vol4/391-W203.pdf); [IOP Conf. Series 640:012118](https://iopscience.iop.org/article/10.1088/1757-899X/640/1/012118)) — the project's own founding analogy, independently confirmed as a real, mature telecom technique with adaptive-margin variants (e.g., ANN-tuned margins accounting for user/device speed).
- **Noise sensitivity:** reduces oscillation specifically around a single boundary, but a margin too narrow relative to noise amplitude will not prevent ping-pong, and a margin too wide will suppress genuine transitions — margin width vs. noise amplitude is the key tunable tradeoff, directly mirroring the telecom handover-margin literature's own core design question.
- **Missing-data sensitivity:** relatively robust — since it does not require a fixed-count window, it degrades more gracefully under irregular real-time sampling than moving average or majority vote.
- **Sustained-impostor behaviour:** once the "dead zone" is crossed, transitions immediately — no artificial persistence delay like debounce — so hysteresis alone, without a separate persistence term, is a genuinely different mechanism family from debounce despite the project's earlier documents sometimes discussing them together as "handover-inspired."
- **Class-imbalance interaction:** operates on the continuous score before any final binarization, similar to EWMA — it does not correct generator-level bias.
- **Interpretability:** moderate — two thresholds and a "current state" latch are slightly less intuitive to a lay audience than a single threshold or a simple average, but still auditable.
- **Computational cost:** negligible.
- **Implementation complexity:** low — the main design decision is whether margins are fixed or adaptive (matching the ANN-tuned handover-margin precedent).
- **Post-hoc vs. score-layer:** purely post-hoc.
- **Comparative literature:** not benchmarked against sibling decision mechanisms within CA; benchmarked within telecom handover against alternative margin-tuning strategies (adaptive vs. fixed), not against fundamentally different mechanism families like majority vote or SPRT.
- **Classification: Essential baseline for this specific study** — it is the mechanism the whole handover analogy was built around, has the strongest direct CA precedent of any candidate (which reframes its role from "novel contribution" to "established mechanism being placed into a comparative framework for the first time"), and must be included for the thesis narrative to be coherent.

### 7. Trust / confidence accumulation

- **Rule:** maintain a running trust score that increases with consistent "authenticated" evidence and decays (linearly, exponentially, or via a domain-specific decay function) otherwise; classify on the trust score vs. a threshold.
- **Parameters:** typically 2–4 (increase rate, decay rate, threshold, sometimes a floor/ceiling).
- **State:** single running trust value (similar memory profile to EWMA, but with an asymmetric or nonlinear update rule rather than a fixed linear blend).
- **Responsiveness:** tunable independently for the "gain trust" and "lose trust" directions — a structural flexibility EWMA and hysteresis do not have (they are typically symmetric).
- **Foundation:** trust-management models from security/HCI literature, applied to the authentication decision itself rather than to network routing or reputation systems (its more common origin domain).
- **CA precedent:** the **strongest and most repeated** direct CA precedent of any mechanism — Mondal & Bours (2017, keystroke+mouse), Zhang et al. (2025, mouse dynamics HHT+LSBT features, [tandfonline](https://www.tandfonline.com/doi/full/10.1080/0144929X.2024.2321933)), and Kiyani et al. (2020, keystroke dynamics, *IEEE Access* 8:156177–156189, DOI 10.1109/ACCESS.2020.3019467 — see dual-threshold/hysteresis entry above for the hybrid-mechanism nuance) all implement trust-accumulation mechanisms, each independently, each as a single-mechanism validation.
- **Cross-domain precedent:** trust-decay models in general security/reputation systems (a lower-tier source, an ijctjournal paper on "adaptive trust-decay cybersecurity models," was found but is flagged as low-tier and should be used cautiously if at all).
- **Noise sensitivity:** reduced, similarly to EWMA, but the asymmetric gain/decay design can be tuned to be more forgiving of transient dips than of transient spikes (or vice versa) — a genuinely distinct behavioural profile from EWMA's symmetric response.
- **Missing-data sensitivity:** depends entirely on how decay is defined — if decay is time-based (decays per elapsed second) it degrades gracefully under sampling gaps; if decay is per-observation (decays per received frame regardless of elapsed time) it inherits the same fixed-count fragility as moving average and majority vote. This design choice must be made explicitly and justified in Document 03.
- **Sustained-impostor behaviour:** by design, meant to accumulate distrust over sustained anomalous behaviour and eventually lock out — this is the mechanism most directly framed, in its own source literature, around security/lockout behaviour rather than pure oscillation suppression.
- **Class-imbalance interaction:** does not correct generator bias; if anything, a biased generator that occasionally misclassifies the genuine user could cause slow, cumulative false distrust — an interaction worth testing empirically rather than assuming.
- **Interpretability:** moderate — asymmetric accumulation rules are somewhat harder to explain intuitively than a single threshold or average, though still far more transparent than a black-box sequential model.
- **Computational cost:** negligible.
- **Implementation complexity:** moderate — more design decisions (gain rate, decay rate, decay basis) than EWMA or hysteresis.
- **Post-hoc vs. score-layer:** purely post-hoc, typically on the continuous score.
- **Comparative literature:** each existing paper validates its own single trust-model variant; no comparison across trust-model parameterizations, let alone against sibling mechanism families, was found.
- **Classification: Essential baseline for this specific study** — alongside hysteresis, this is the mechanism with the deepest existing CA-specific precedent, which similarly reframes the contribution from "proposing trust accumulation" to "placing an established mechanism into a systematic, matched-operating-point comparison for the first time."

### 8. Sequential/model-based methods (SPRT, HMM) — optional extension

- **Rule (SPRT):** accumulate a log-likelihood ratio between two hypotheses (genuine/impostor) each frame; decide as soon as the ratio crosses an upper or lower bound, otherwise keep sampling.
- **Rule (HMM):** treat the true authentication state as a latent Markov variable; infer the most likely state sequence (e.g., via Viterbi) or filtered belief (e.g., via a forward algorithm) given the observed score sequence.
- **Parameters:** SPRT — 2 decision bounds plus the assumed likelihood models; HMM — transition matrix, emission model, at least 2–4 effective parameters depending on parameterization.
- **State:** SPRT — running log-likelihood sum; HMM — full belief distribution over states (or Viterbi path history).
- **Responsiveness:** SPRT is provably the fastest sequential test for a given error-rate pair under its optimality assumptions (Wald's original result, foundational to the field); HMM responsiveness depends on transition-probability design.
- **Foundation:** classical sequential hypothesis testing (Wald) and hidden Markov modelling — both mathematically the most rigorous mechanisms in this taxonomy, at the cost of requiring explicit probabilistic modelling assumptions the simpler mechanisms do not.
- **CA precedent:** Mahbub & Chellappa (2016, MSHMM, [arXiv:1610.07935](https://arxiv.org/pdf/1610.07935)) and the app-usage HMM/MSHMM verification model ([arXiv:1808.03319](https://arxiv.org/pdf/1808.03319)) both use HMM-family smoothing in CA — but, as established in Document 01, **both apply the smoothing inside the score generator** (emission-probability smoothing for unseen observations), not as a post-hoc decision-layer stabilizer on top of an already-computed score. This is the clearest instance in the entire review of the score-generator/decision-layer conflation the project brief warns against; using either paper as precedent for a *decision-layer* HMM mechanism would misrepresent what they actually did.
- **Cross-domain precedent:** SPRT in sensor-network sequential detection (Marano et al. 2006, [IEEE TSP 54(11):4105–4117](http://acsp.ece.cornell.edu/papers/MaranoMattaWillettTong06SP_2.pdf)) — confirmed to be about SPRT/dead-zone detection in a sensor-network architecture (SENMA), **not** cellular handover, despite surface-level relevance; it is legitimate cross-domain precedent for SPRT as a general sequential-decision method, not evidence of any telecom-handover connection.
- **Noise sensitivity:** theoretically well-characterized (SPRT has closed-form error-rate/sample-size tradeoffs under its assumptions); practically sensitive to whether the assumed likelihood model matches the true score distribution.
- **Missing-data sensitivity:** SPRT and HMM both formally accommodate irregular timing more gracefully than fixed-window methods if time-aware transition/likelihood models are used — but this requires deliberate design, not an out-of-the-box guarantee.
- **Sustained-impostor behaviour:** designed explicitly for exactly this question (optimal detection speed for a given false-alarm rate) — the strongest theoretical foundation of any mechanism for this specific criterion.
- **Class-imbalance interaction:** requires an explicit likelihood/emission model, which itself must be estimated from (possibly imbalanced) training data — a additional modelling step none of the simpler mechanisms require.
- **Interpretability:** low relative to the other seven mechanisms — log-likelihood ratios and latent-state posteriors are harder to explain to a non-specialist audience or examiner without additional exposition.
- **Computational cost:** higher than the other mechanisms, though still trivial for a smartphone-class device at this problem scale.
- **Implementation complexity:** high — requires explicit distributional assumptions and correct handling of the score-generator/decision-layer boundary (see above).
- **Post-hoc vs. score-layer:** **ambiguous by design** — can be built either way, but the two CA precedents found both build it into the score generator, which is a documented risk of reproducing that conflation if this mechanism is included without care.
- **Comparative literature:** SPRT-style sequential detectors are a mature, separately-studied family in signal detection theory; not benchmarked against the other seven mechanisms in this list in any single source found.
- **Classification: Optional / exploratory.** Theoretically the most rigorous mechanism family, but the highest implementation complexity, the lowest interpretability, and the clearest risk of accidentally reproducing the score-generator/decision-layer conflation. Recommended only as a stretch extension if time and evidence permit, not as part of the minimum viable experiment (see Document 05).

## Summary classification table

| Mechanism | Direct CA precedent | Classification |
|---|---|---|
| Instantaneous threshold | Implicit universal baseline | Essential baseline |
| Moving average | None found | Strong candidate |
| EWMA | MDPI Sensors 2025 (single-mechanism) | Strong candidate (arguably essential) |
| Majority vote | None found (operates on decisions, not scores) | Strong candidate |
| Debounce/persistence | None found independent of handover framing | Strong candidate |
| Dual-threshold/hysteresis | Kiyani et al. 2020 (strongest CA precedent — as part of a hybrid trust+dual-threshold model) | Essential baseline |
| Trust/confidence accumulation | Mondal & Bours 2017; Zhang et al. 2025; Kiyani et al. 2020 (strongest, most repeated CA precedent) | Essential baseline |
| SPRT / HMM | Only as score-generator smoothing, not decision-layer (Mahbub & Chellappa 2016; arXiv:1808.03319) | Optional/exploratory |

No mechanism is rated "probably unsuitable" — all eight are theoretically applicable to the ExtraSensory score stream; the meaningful differentiation is in implementation risk (sequential/model-based methods) and evidentiary novelty positioning (hysteresis and trust accumulation are established in CA and therefore cannot be marketed as new mechanisms, only their systematic comparison can be).

## Conclusions

**Evidence:** Two mechanisms (hysteresis, trust accumulation) have direct, repeated CA precedent; two (moving average, majority vote) have zero CA-specific precedent found in this search; one (debounce) has precedent only under the project's own handover framing; EWMA has one single-mechanism CA precedent; SPRT/HMM precedent exists in CA only at the wrong architectural layer (score generator, not decision layer).

**Interpretation:** The strongest, most defensible experimental design is a comparison set of instantaneous threshold, EWMA, majority vote, debounce, hysteresis, and trust accumulation — six mechanisms spanning score-level smoothing (EWMA, hysteresis, trust), decision-level smoothing (majority vote, debounce), and the no-smoothing baseline (instantaneous threshold) — with SPRT/HMM as an optional seventh/eighth if scope allows, explicitly built as a post-hoc decision-layer step to avoid reproducing the score-generator conflation found in the two located HMM papers.

**Recommendation:** Do not present hysteresis or trust accumulation as novel mechanisms in the thesis narrative — present them as established mechanisms being placed, for the first time in the reviewed literature, into a systematic matched-operating-point comparison against five to seven sibling mechanisms. This is a more defensible framing than any claim of mechanism-level novelty.

## References

1. NIST/SEMATECH e-Handbook of Statistical Methods, §6.3.2.4, EWMA Control Charts (Roberts 1959; Hunter 1986; Lucas & Saccucci 1990). [https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc324.htm](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc324.htm)
2. MDPI Sensors 25(18):5711 (2025). Continuous Authentication in Resource-Constrained Devices via Biometric and Environmental Fusion. [https://www.mdpi.com/1424-8220/25/18/5711](https://www.mdpi.com/1424-8220/25/18/5711)
3. Kiyani, A.T., Lasebae, A., Ali, K., Ur Rehman, M. & Haq, B. (2020). Continuous user authentication featuring keystroke dynamics based on robust recurrent confidence model and ensemble learning approach. *IEEE Access*, 8, 156177–156189. DOI: 10.1109/ACCESS.2020.3019467. [https://repository.mdx.ac.uk/download/e6ea94d1675e5360972f991d0ac4570614b94b447a3ff5c7818ba87424b9e2b6/1634469/Continuous%20User%20Authentication%20Featuring%20Keystroke%20Dynamics%20Based%20on%20Robust%20Recurrent%20Confidence%20Model%20and%20Ensemble%20Learning%20Approach.pdf](https://repository.mdx.ac.uk/download/e6ea94d1675e5360972f991d0ac4570614b94b447a3ff5c7818ba87424b9e2b6/1634469/Continuous%20User%20Authentication%20Featuring%20Keystroke%20Dynamics%20Based%20on%20Robust%20Recurrent%20Confidence%20Model%20and%20Ensemble%20Learning%20Approach.pdf) (confirmed by direct retrieval of the published article).
4. IOP Conf. Series 640:012118. Ping-pong reduction for handover process using adaptive hysteresis margin. [https://iopscience.iop.org/article/10.1088/1757-899X/640/1/012118](https://iopscience.iop.org/article/10.1088/1757-899X/640/1/012118)
5. IJFCC, vol. 4. LTE handover hysteresis-margin analysis. [https://www.ijfcc.org/vol4/391-W203.pdf](https://www.ijfcc.org/vol4/391-W203.pdf)
6. Mondal, S. & Bours, P. (2017). A study on continuous authentication using a combination of keystroke and mouse biometrics. *Neurocomputing*. [https://scispace.com/papers/a-study-on-continuous-authentication-using-a-combination-of-4dksurb05q](https://scispace.com/papers/a-study-on-continuous-authentication-using-a-combination-of-4dksurb05q)
7. Zhang et al. (2025). Trustworthy interaction model: continuous authentication via mouse dynamics. *Behaviour & Information Technology*. DOI: 10.1080/0144929X.2024.2321933. [https://www.tandfonline.com/doi/full/10.1080/0144929X.2024.2321933](https://www.tandfonline.com/doi/full/10.1080/0144929X.2024.2321933)
8. Marano, S., Matta, V., Willett, P. & Tong, L. (2006). Cross-Layer Design of Sequential Detectors in Sensor Networks. *IEEE Transactions on Signal Processing*, 54(11), 4105–4117. DOI: 10.1109/TSP.2006.880254. [http://acsp.ece.cornell.edu/papers/MaranoMattaWillettTong06SP_2.pdf](http://acsp.ece.cornell.edu/papers/MaranoMattaWillettTong06SP_2.pdf)
9. Mahbub, U. & Chellappa, R. (2016). PATH: Person Authentication using Trace Histories. arXiv:1610.07935. [https://arxiv.org/pdf/1610.07935](https://arxiv.org/pdf/1610.07935)
10. (2018). Application-usage HMM/MSHMM continuous verification. arXiv:1808.03319. [https://arxiv.org/pdf/1808.03319](https://arxiv.org/pdf/1808.03319)
11. Raghu, S.T.P., MacIsaac, D. & Scheme, E. (2023). Decision-change Informed Rejection Improves Robustness in Pattern Recognition-based Myoelectric Control. *IEEE JBHI*, 27(12), 6051–6061. DOI: 10.1109/JBHI.2023.3316599. [https://arxiv.org/abs/2409.14169](https://arxiv.org/abs/2409.14169)

## Implications for the next document

Document 03 must design the experimental framework around the "score-level smoothing vs. decision-level smoothing" axis identified here as a genuine structural difference (EWMA/hysteresis/trust operate on continuous scores; majority vote/debounce operate on binarized decisions) — this affects where in the pipeline each mechanism plugs in and therefore how a "common score stream, matched operating point" comparison must be engineered so that every mechanism is fed the same information fairly. Document 03 must also specify, as an explicit design decision rather than an afterthought, whether time-based or count-based windows/decay are used for every mechanism given ExtraSensory's irregular ~60 s cadence (flagged as a live risk for moving average, majority vote, and count-based trust decay in this document). Finally, Document 03 should treat SPRT/HMM as optional and, if included, must specify how the decision-layer implementation will be kept architecturally distinct from the score generator to avoid the conflation documented in Mahbub & Chellappa (2016) and arXiv:1808.03319.
