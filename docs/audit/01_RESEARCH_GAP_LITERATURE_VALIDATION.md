# Document 01 — Research Gap & Literature Validation Report

**Date:** 17 September 2026
**Status:** Independent audit document. Does not constitute the final research paper.

## Purpose

To independently validate or falsify the refined research gap for the pivot study — "no published work performs a controlled, matched-operating-point comparison of multiple temporal decision-layer stabilization mechanisms against each other within continuous/behavioural authentication, evaluated on identity-transition sequences rather than steady-state accuracy alone" — by actively searching for literature that could invalidate it, not merely support it.

## Evidence-provenance note (read before the rest of this document)

The task brief describes a "repository Stage 1 audit" establishing specific implementation facts (60 participants, one-vs-rest model, random row-level 80/20 split, SMOTE, a reproducible Gradient Boosting result, 597→49 transition reduction, and a list of identified methodological problems). **I could not locate this audit, or any code/notebook it would describe, in the project's file repository.** The repository currently contains only: `01`–`06` planning/scaffolding files, `07_research_state_audit_independent.md` (my own 15 Sept 2026 audit), the pre-existing `MSc_Pivot_Audit.md` and `Review_1_Key_Findings.md`, and the primary `.docx` drafts — none of which describe an executed one-vs-rest model, a row-level split, or confirmed SMOTE application; my prior audit explicitly flagged that **no code, notebook, or output log exists in this project**. Per the project's evidence rules, I am treating the Stage 1 audit's facts as **user-reported evidence**, not as independently verified primary evidence, and I flag every claim sourced from it accordingly (marked **[Stage-1, reported]** below). If that audit or its underlying code exists (e.g., in a separate coding-agent workspace), uploading it to this project would let me verify it directly instead of taking it on trust. This distinction matters because Document 04 and Document 05 depend on exactly which of these facts are confirmed vs. reported.

## Methodology / scope

I ran independent web and academic searches (not a re-read of the project's existing `06_literature_to_add.md`) across: continuous/implicit/behavioural/sensor-based/contextual/trust-based/temporal authentication; decision-level post-processing; threshold adaptation; dual-threshold and hysteresis mechanisms; persistence/debounce; temporal smoothing (moving average, EWMA, majority vote); sequential decision methods; confidence/trust accumulation. I fetched and read full content (not just snippets) for every paper cited below as Level 1 or Level 2 evidence. Where a search surfaced only non-authoritative or SEO-style pages (several "debounce" and "hysteresis" hits), I discarded them in favour of authoritative sources (NIST, IEEE, arXiv preprints with named authors, peer-reviewed journals).

## Evidence hierarchy applied in this document

- **A — Direct authentication evidence:** the paper performs continuous/behavioural authentication and implements or evaluates a temporal decision mechanism.
- **B — Closely related biometric decision-stream evidence:** biometric or authentication-adjacent work on decision-stream evaluation, metrics, or comparison methodology, without necessarily implementing the same mechanisms.
- **C — Cross-domain methodological precedent:** the mechanism or evaluation idea is well-established in another field (telecom handover, statistical process control, sensor networks, ensemble ML) and is being considered for transfer, not cited as authentication precedent.

## Evidence

### A — Direct authentication evidence

| Paper | Venue/Year | Mechanism studied | Compared against alternatives? | Matched operating point? | Relevance |
|---|---|---|---|---|---|
| Mondal & Bours, *A study on continuous authentication using a combination of keystroke and mouse biometrics* — confirmed to exist ([SciSpace record](https://scispace.com/papers/a-study-on-continuous-authentication-using-a-combination-of-4dksurb05q)), *Neurocomputing*, 2017 | 2017 | Dynamic trust model (score persists/decays over time rather than reacting to every instantaneous classification) | No — single mechanism, no alternative decision-layer mechanisms evaluated against it | No | Falsifies the *original* absence claim ("the field has never used temporal persistence"); does **not** address the reformulated comparative gap |
| Kiyani, Lasebae, Ali, Ur Rehman & Haq, *Continuous user authentication featuring keystroke dynamics based on robust recurrent confidence model and ensemble learning approach*, *IEEE Access* 8:156177–156189, 2020, DOI 10.1109/ACCESS.2020.3019467 — confirmed by direct retrieval of the published article ([MDX repository, full text](https://repository.mdx.ac.uk/download/e6ea94d1675e5360972f991d0ac4570614b94b447a3ff5c7818ba87424b9e2b6/1634469/Continuous%20User%20Authentication%20Featuring%20Keystroke%20Dynamics%20Based%20on%20Robust%20Recurrent%20Confidence%20Model%20and%20Ensemble%20Learning%20Approach.pdf)) | 2020 | A trust/confidence-accumulation model ("robust recurrent confidence model") that additionally uses two thresholds — alert and final/lockout — to switch operating mode as confidence declines; structurally a **hybrid of trust accumulation and dual-threshold/hysteresis logic**, not a pure margin-only mechanism | No — single mechanism | No | Falsifies the original absence claim for both dual-threshold and trust-accumulation mechanisms; does not address the comparative gap |
| Zhang et al., dynamic trust model for continuous authentication via mouse dynamics (HHT + LSBT features), *Behaviour & Information Technology* ([tandfonline.com](https://www.tandfonline.com/doi/full/10.1080/0144929X.2024.2321933)) | 2025 (published online Feb 2025) | Trust model with lockout on accumulated distrust | No — single mechanism; no comparison to hysteresis/moving average/EWMA/majority vote/SPRT | No | Confirms trust-model mechanisms remain an active, single-mechanism research line in 2025; does not close the comparative gap |
| Mahbub & Chellappa, *PATH: Person Authentication using Trace Histories*, arXiv:1610.07935, 2016 | 2016 | Marginally Smoothed HMM (MSHMM) — smoothing applied to **emission probabilities inside the score generator**, not to a post-hoc decision layer | No | No | **Important boundary case**: demonstrates that "temporal smoothing" in this literature is often applied *upstream*, inside score generation, not *downstream* as an explicit decision-layer stabilizer. This is exactly the score-generator/decision-layer conflation the project brief warns against, and supports keeping that separation explicit in Documents 02–05 |
| App-usage HMM/MSHMM verification model, arXiv:1808.03319 | ~2018 | HMM with Laplacian/marginal smoothing, Markov-chain verification, modified edit-distance — four *score-generation* variants compared against each other | Yes, but only among score-generation variants, not decision-layer mechanisms | Not stated as matched-FAR/FRR | Same boundary case as above: a same-paper comparison of multiple models exists, but it compares alternative **score generators**, not alternative **decision-layer stabilizers** applied to one common score stream. This is the closest thing found to "multiple mechanisms compared in one paper," but it is the wrong layer for the reformulated gap |

### B — Closely related biometric decision-stream / metrics evidence

| Paper | Venue/Year | What it shows | Relevance |
|---|---|---|---|
| Ryu & Yeom, *Continuous Multimodal Biometric Authentication Schemes: A Systematic Review* ([SciSpace PDF](https://scispace.com/pdf/continuous-multimodal-biometric-authentication-schemes-a-1vjrr8x4cg.pdf)) | ~2021 | Finds a lack of comparative analysis, but specifically of **fusion levels** (feature/score/decision-level fusion) and biometric-type combinations, not of decision-layer temporal-stabilization mechanisms | Supports a general "the field under-compares design choices" pattern; **should not** be cited as direct precedent for the stabilization-mechanism gap specifically — this is a narrower match than earlier project documents implied |
| Baig & Eskeland, *Security, Privacy, and Usability in Continuous Authentication: A Survey*, *Sensors* 21(17):5967, 2021, DOI 10.3390/s21175967 ([PMC8434648](https://pmc.ncbi.nlm.nih.gov/articles/PMC8434648/)) | 2021 | Explicitly compiles reported performance across many CA studies and shows they use **heterogeneous metrics, datasets, participant counts, and operating conditions** with no standardized matched-operating-point protocol; states methods "need to be compared using... same accuracy, same FAR, and FRR" but does not itself define or implement such a protocol | **Direct, citable support** for the reformulated gap's methodological premise: the field's own survey literature identifies the absence of a standardized, matched comparison protocol, though it frames this as a general evaluation problem, not specifically about temporal decision mechanisms |
| Sugrim, Liu, McLean & Lindqvist, *Robust Performance Metrics for Authentication Systems*, NDSS 2019 ([slides](https://www.ndss-symposium.org/wp-content/uploads/ndss2019_06A-3_Sugrim_slides.pdf)) | 2019 | Demonstrates with real data (SVC2004 vs. a keystroke dataset) that EER-based ranking can **reverse** when the same two systems are compared at a matched FPR=0.1 operating point instead (SVC2004: EER 0.185, TPR 0.60; Keystroke: EER 0.198, TPR 0.776 — Keystroke wins on TPR at matched FPR despite the *worse* EER) | Directly supports the methodological necessity of matched-operating-point comparison in **behavioural-biometric authentication specifically** (keystroke dynamics is a CA modality) — the strongest single piece of Level-B evidence that single-threshold metrics (accuracy, raw EER) can mislead system-vs-system ranking |
| Raghu, MacIsaac & Scheme, *Decision-change Informed Rejection Improves Robustness in Pattern Recognition-based Myoelectric Control*, *IEEE JBHI* 27(12):6051–6061, 2023, DOI 10.1109/JBHI.2023.3316599 ([arXiv:2409.14169](https://arxiv.org/abs/2409.14169)) | 2023 | Compares **8** existing decision-stream post-processing schemes (majority vote, Bayesian fusion, onset locking, outlier detection, confidence-based rejection, confidence scaling, prior adjustment, adaptive windowing) plus 2 new ones, on error rate *and* decision-stream volatility | The strongest available template for the reformulated gap's comparative design — but it is myoelectric prosthesis control, not authentication. A legitimate transfer argument, not existing CA precedent |

### C — Cross-domain methodological precedent (not authentication evidence)

Handover hysteresis-margin literature (LTE ping-pong reduction, e.g. [IJFCC vol.4](https://www.ijfcc.org/vol4/391-W203.pdf); [IOP Conf. Series 640:012118](https://iopscience.iop.org/article/10.1088/1757-899X/640/1/012118)); SPRT foundational statistics (Wald's original test; sensor-network sequential detection, [Marano, Matta, Willett & Tong, *IEEE Trans. Signal Processing* 54(11):4105–4117, 2006](http://acsp.ece.cornell.edu/papers/MaranoMattaWillettTong06SP_2.pdf)); EWMA control charts ([NIST Engineering Statistics Handbook §6.3.2.4](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc324.htm), attributing the method to Roberts 1959, Hunter 1986, Lucas & Saccucci 1990); majority-vote ensembles (NeurIPS urn-model analysis). These establish that each *individual* mechanism is a mature, well-defined technique elsewhere — they are legitimate methodological precedent for transfer, but none is authentication evidence and none constitutes a multi-mechanism CA comparison.

### Deliberate "kill-the-gap" search of 2024–2026 literature

I searched specifically for any recent paper that already performs the comparative, matched-operating-point evaluation the reformulated gap claims is missing, in a continuous/behavioural-authentication context:

- [JISEM 2025 systematic literature review on continuous authentication](https://jisem-journal.com/index.php/journal/article/view/12787) — no stabilization-mechanism comparison; does not name this as an open gap.
- [MDPI Sensors 25(18):5711, *Continuous Authentication in Resource-Constrained Devices via Biometric and Environmental Fusion*, 2025](https://www.mdpi.com/1424-8220/25/18/5711) — proposes **one** mechanism (EWMA with adaptive, context-driven thresholding) against a fixed-threshold ablation; not a multi-mechanism bake-off.
- Zhang et al. 2025 (above) — single trust-model mechanism, no comparison.
- No 2024–2026 paper was found performing a matched-operating-point, multi-mechanism comparison of decision-layer stabilizers specifically within continuous/behavioural authentication.

I did not find a paper that closes the reformulated gap. This is a negative result from a bounded search, not a certified absence — see novelty-risk assessment below.

## Analysis

### 1. What exactly has already been compared?

Within CA specifically: single decision mechanisms evaluated against a naive/instantaneous baseline (trust models: Mondal & Bours 2017, Zhang 2025; dual-threshold: Kiyani 2020) or alternative **score-generation** models compared against each other (Mahbub & Chellappa 2016; app-usage HMM 2018). Fusion **levels** (not decision-layer mechanisms) have been compared and found under-studied (Ryu 2021). Outside CA, in myoelectric control, 8 decision-stream post-processing schemes have been rigorously compared against each other on matched error-rate and volatility metrics (Raghu 2023).

### 2. What has not been compared?

No source found compares ≥2 genuinely alternative **decision-layer** stabilization mechanisms (e.g., hysteresis vs. EWMA vs. majority vote vs. debounce) applied to a **common** authentication score stream, evaluated at **matched operating points**, within continuous/behavioural authentication.

### 3. Are there studies comparing multiple temporal decision mechanisms in continuous authentication?

Not found. The closest analogues compare score-generation variants (arXiv:1808.03319), not post-hoc decision-layer mechanisms.

### 4. Are there studies comparing individual mechanisms but not systematically?

Yes — this is the dominant pattern (Mondal & Bours 2017; Kiyani 2020; Zhang 2025). Each paper proposes and validates one mechanism against a naive baseline, never against sibling mechanisms.

### 5. Are there studies using matched operating points?

Not within CA decision-layer comparisons. Sugrim et al. (2019) demonstrate the *need* for matched-operating-point comparison using a keystroke-dynamics example, but do not apply it to decision-layer mechanism comparison. Baig & Eskeland (2021) document the absence of standardization across the field generally.

### 6. Are stability and responsiveness evaluated alongside security?

Rarely, and not together with matched operating points, within CA. Raghu et al. (2023) evaluate error rate jointly with decision-stream volatility, but outside CA.

### 7. Does the refined gap survive?

**Yes, on a narrower basis than the project's prior literature file implied.** The gap survives my adversarial search: no paper was found that performs the specific comparison. But two of its previously-cited supporting citations need re-scoping — Ryu (2021) supports a fusion-level gap, not a decision-layer-mechanism gap, and should be cited only for the general "field under-compares" pattern, not as direct precedent.

### 8. What wording should be used to avoid an overclaim?

Avoid "no one has ever compared temporal mechanisms in authentication" (false — single-mechanism validations exist and the score-generation-layer literature does make comparisons). Avoid "the field has never used hysteresis/trust/margin logic" (falsified directly by Mondal & Bours 2017 and Kiyani 2020). Prefer:

> "The literature identified in this review provides several single-mechanism validations of temporal decision stabilization in continuous authentication (trust models, dual-threshold logic), and a systematic review documents the field's more general lack of standardized, comparable evaluation protocols. However, the reviewed literature does not establish a controlled, matched-operating-point comparison of multiple alternative decision-layer stabilization mechanisms evaluated on a common authentication score stream within continuous or behavioural authentication."

## Conclusions

**Strongest supporting evidence:** Baig & Eskeland (2021) documenting the field's heterogeneous, non-standardized evaluation practice; Sugrim et al. (2019) demonstrating empirically (in a behavioural-biometric example) that single-threshold metrics can reverse system rankings versus matched-operating-point comparison; the deliberate 2024–2026 search finding no closing paper.

**Strongest counterexamples (to the *original*, not reformulated, gap):** Mondal & Bours (2017) and Kiyani et al. (2020) — both already implement temporal/margin-style decision logic in CA. These must be cited and discussed, not omitted, in any literature review going forward — omitting them would be an integrity risk if an examiner finds them independently.

**Unresolved areas:** Whether a matched-operating-point multi-mechanism comparison already exists in venues not indexed by the search tools used (a residual risk inherent to any literature search); whether more recent (2026) preprints not yet indexed close the gap before submission — this should be re-checked shortly before the final paper is written.

**Novelty-risk assessment:** Moderate-low. The mechanism-level building blocks are all published elsewhere (in CA singly, or in adjacent domains comparatively); the novelty is specifically the **combination**: applying a systematic, matched-operating-point, multi-mechanism comparison methodology (of the kind demonstrated feasible by Raghu et al. 2023 in myoelectric control) to the CA decision layer. This is a legitimate, moderate methodological-contribution novelty claim — not a "first-ever mechanism" claim.

**Recommended final gap wording:** As given in "8" above. This wording should be used verbatim (or lightly edited) in Document 05 and in any future paper draft.

## References

1. Mondal, S. & Bours, P. (2017). A study on continuous authentication using a combination of keystroke and mouse biometrics. *Neurocomputing*. [https://scispace.com/papers/a-study-on-continuous-authentication-using-a-combination-of-4dksurb05q](https://scispace.com/papers/a-study-on-continuous-authentication-using-a-combination-of-4dksurb05q)
2. Kiyani, A.T., Lasebae, A., Ali, K., Ur Rehman, M. & Haq, B. (2020). Continuous user authentication featuring keystroke dynamics based on robust recurrent confidence model and ensemble learning approach. *IEEE Access*, 8, 156177–156189. DOI: 10.1109/ACCESS.2020.3019467. [https://repository.mdx.ac.uk/download/e6ea94d1675e5360972f991d0ac4570614b94b447a3ff5c7818ba87424b9e2b6/1634469/Continuous%20User%20Authentication%20Featuring%20Keystroke%20Dynamics%20Based%20on%20Robust%20Recurrent%20Confidence%20Model%20and%20Ensemble%20Learning%20Approach.pdf](https://repository.mdx.ac.uk/download/e6ea94d1675e5360972f991d0ac4570614b94b447a3ff5c7818ba87424b9e2b6/1634469/Continuous%20User%20Authentication%20Featuring%20Keystroke%20Dynamics%20Based%20on%20Robust%20Recurrent%20Confidence%20Model%20and%20Ensemble%20Learning%20Approach.pdf) — confirmed by direct retrieval of the published article; previously verified only via a citing thesis, now upgraded to primary-source confirmation.
3. Zhang et al. (2025). Trustworthy interaction model: continuous authentication via mouse dynamics. *Behaviour & Information Technology*. DOI: 10.1080/0144929X.2024.2321933. [https://www.tandfonline.com/doi/full/10.1080/0144929X.2024.2321933](https://www.tandfonline.com/doi/full/10.1080/0144929X.2024.2321933)
4. Mahbub, U. & Chellappa, R. (2016). PATH: Person Authentication using Trace Histories. arXiv:1610.07935. [https://arxiv.org/pdf/1610.07935](https://arxiv.org/pdf/1610.07935)
5. (2018). Application-usage HMM/MSHMM continuous verification. arXiv:1808.03319. [https://arxiv.org/pdf/1808.03319](https://arxiv.org/pdf/1808.03319)
6. Ryu, H. & Yeom, S. Continuous Multimodal Biometric Authentication Schemes: A Systematic Review. [https://scispace.com/pdf/continuous-multimodal-biometric-authentication-schemes-a-1vjrr8x4cg.pdf](https://scispace.com/pdf/continuous-multimodal-biometric-authentication-schemes-a-1vjrr8x4cg.pdf)
7. Baig, A.F. & Eskeland, S. (2021). Security, Privacy, and Usability in Continuous Authentication: A Survey. *Sensors*, 21(17), 5967. DOI: 10.3390/s21175967. [https://pmc.ncbi.nlm.nih.gov/articles/PMC8434648/](https://pmc.ncbi.nlm.nih.gov/articles/PMC8434648/)
8. Sugrim, S., Liu, C., McLean, M.C. & Lindqvist, J. (2019). Robust Performance Metrics for Authentication Systems. NDSS 2019. [https://www.ndss-symposium.org/wp-content/uploads/ndss2019_06A-3_Sugrim_slides.pdf](https://www.ndss-symposium.org/wp-content/uploads/ndss2019_06A-3_Sugrim_slides.pdf)
9. Raghu, S.T.P., MacIsaac, D. & Scheme, E. (2023). Decision-change Informed Rejection Improves Robustness in Pattern Recognition-based Myoelectric Control. *IEEE Journal of Biomedical and Health Informatics*, 27(12), 6051–6061. DOI: 10.1109/JBHI.2023.3316599. [https://arxiv.org/abs/2409.14169](https://arxiv.org/abs/2409.14169)
10. IOP Conf. Series 640:012118 — Ping-pong reduction for handover process using adaptive hysteresis margin. [https://iopscience.iop.org/article/10.1088/1757-899X/640/1/012118](https://iopscience.iop.org/article/10.1088/1757-899X/640/1/012118)
11. Marano, S., Matta, V., Willett, P. & Tong, L. (2006). Cross-Layer Design of Sequential Detectors in Sensor Networks. *IEEE Transactions on Signal Processing*, 54(11), 4105–4117. DOI: 10.1109/TSP.2006.880254. [http://acsp.ece.cornell.edu/papers/MaranoMattaWillettTong06SP_2.pdf](http://acsp.ece.cornell.edu/papers/MaranoMattaWillettTong06SP_2.pdf)
12. NIST/SEMATECH e-Handbook of Statistical Methods, §6.3.2.4, EWMA Control Charts. [https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc324.htm](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc324.htm)

## Implications for the next document

Document 02 must build a mechanism taxonomy that keeps the score-generator/decision-layer distinction explicit at every entry, because the closest "multi-mechanism CA comparisons" found here (Mahbub & Chellappa 2016; arXiv:1808.03319) compare score-generation variants, not decision-layer stabilizers — conflating these would misrepresent the state of the art. Document 02 should treat Mondal & Bours (2017) and Kiyani et al. (2020) as the direct-evidence baseline for trust-model and dual-threshold/hysteresis mechanisms respectively (both already have CA precedent, so neither can be marketed as "novel" mechanisms — only their *systematic comparison* is potentially novel), and should use Raghu et al. (2023)'s 8-mechanism set as the structural template for which mechanisms are worth including. Majority vote and moving average/EWMA currently have **no direct CA-specific evidence** located in this search — Document 02 must flag this explicitly rather than assume they transfer cleanly.
