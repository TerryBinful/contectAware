# Document 05 — Final Research Blueprint

**Date:** 17 September 2026
**Status:** Independent audit synthesis of Documents 01–04. This is an evidence-derived research design, not a justification of a predetermined idea. Does not constitute the final research paper.

## Purpose

To synthesize Documents 01 (gap validation), 02 (mechanism taxonomy), 03 (methodological framework), and 04 (dataset/RQ feasibility) into one coherent blueprint, and to render a single final verdict on whether the refined pivot is currently defensible.

## Executive summary

The reformulated gap — no published work performs a matched-operating-point, multi-mechanism comparison of decision-layer stabilization mechanisms in continuous/behavioural authentication — survives adversarial literature search (Document 01), though it must be worded narrowly and must not overclaim, since two of its candidate mechanisms (hysteresis, trust accumulation) already have direct CA precedent individually. The eight-mechanism taxonomy (Document 02) is internally coherent and correctly separates score-level from decision-level smoothing. The project's own existing methodological scaffolding (Document 03) is already well-aligned with 2019–2026 biometric-evaluation best practice, needing only a statistical refinement (Friedman/Nemenyi as the primary multi-mechanism secondary test) and clearer terminology hygiene. The dataset (Document 04) is adequate in aggregate but has two concrete, currently unmeasured empirical prerequisites — splice-sequence coverage and context-label match coverage — that must be audited before mechanism results are trusted. No component of this blueprint depends on the "Stage 1 audit" the task brief describes, which could not be located in the project repository; every load-bearing claim below is sourced to either the project's own confirmed files or independently verified external evidence.

---

## 1. Title

**Working title (unchanged from brief, assessed as accurate to the design below):** "Temporal Decision-Layer Stabilisation in Continuous Smartphone Authentication: A Comparative Evaluation of Security, Stability, and Responsiveness."

## 2. Problem

Continuous/behavioural smartphone authentication systems generate noisy, frame-by-frame scores; converting these into stable authenticate/lock decisions without excessive oscillation ("ping-pong") or unacceptable detection delay is an unresolved decision-layer engineering problem, distinct from the accuracy of the underlying score generator itself (Document 01, Document 02).

## 3. Research gap

As validated in Document 01: *"The literature identified in this review provides several single-mechanism validations of temporal decision stabilization in continuous authentication (trust models, dual-threshold logic), and a systematic review documents the field's more general lack of standardized, comparable evaluation protocols. However, the reviewed literature does not establish a controlled, matched-operating-point comparison of multiple alternative decision-layer stabilization mechanisms evaluated on a common authentication score stream within continuous or behavioural authentication."* **Gap rating: Defensible with refinement** — real, unresolved by the literature found, and measurable, but narrower than the project's earlier framing and not a "first-ever mechanism" claim.

## 4. Contribution

The contribution is methodological and empirical, not mechanism-inventive: a systematic, matched-operating-point comparison of six to eight established decision-layer mechanisms (drawn from CA-specific and cross-domain precedent) on a common, fixed authentication score stream, using an open-set identity-transition benchmark constructed from ExtraSensory, reporting security (ANGA-time), responsiveness (ANIA-time), and stability (ping-pong rate) jointly rather than any one in isolation. Hysteresis and trust accumulation should be explicitly presented as **established** mechanisms being placed into this comparison for the first time in the reviewed literature, not as novel proposals (Document 02).

## 5. Research questions

Primary framing (per the task brief) and its mapping onto the project's own pre-registered, more granular RQs (`01_preregistration_template.md`, Document 03):

- **RQ1 (score validity):** Is the upstream authentication score itself valid — subject-independent, free of temporal leakage and feature shortcuts — before any decision-layer mechanism is applied? *(Feasibility: conditionally supported, Document 04 §D.)*
- **RQ2 (decision-layer mechanism comparison):** At a matched genuine-lockout rate, do decision-layer stabilization mechanisms differ in impostor-detection latency, and does hysteresis outperform single-parameter smoothers and published trust/sequential models on that trade-off? *(Maps to preregistration RQ1/RQ2; feasibility: conditionally supported pending the coverage audit, Document 04 §E — the most fully validated RQ of the three.)*
- **RQ3 (robustness/context-dependence):** Do findings differ between cross-context and context-matched impostor conditions, and is any hysteresis advantage attributable to margin, dwell, or their combination? *(Maps to preregistration RQ3/RQ4; feasibility: conditionally supported, with the largest unresolved empirical risk — label-sparsity-driven match coverage, Document 04 §F.)*

## 6. Hypotheses (WORKING — not final; carried from `01_preregistration_template.md`, cross-checked against Documents 01–04)

| | Hypothesis | Null | Status after this audit |
|---|---|---|---|
| H1 | Mechanisms differ in ANIA-time at matched ANGA-time | No difference across mechanisms within CIs | Testable as designed; retained |
| H2 | Hysteresis ANIA-time < each single-parameter smoother | No difference, or hysteresis worse | Testable; must be reported even if falsified (project's own falsification criteria already commit to this) |
| H3 | Hysteresis advantage (if any) requires both margin and dwell jointly | Advantage persists from either component alone | Testable via the existing component-ablation design (Document 03) |
| H4 | ANIA-time is longer in context-matched (M) than cross-context (X) for every mechanism | No difference | Testable, contingent on the context-match coverage audit (Document 04) |

## 7. Conceptual framework

Two layers must be kept analytically and architecturally separate throughout: (A) the **score generator** — the classifier producing a per-frame calibrated probability, and (B) the **decision layer** — the post-hoc mechanism converting that probability stream into a binary authenticated/locked state. Documents 01 and 02 found this distinction to be a real, recurring risk in the literature itself (Mahbub & Chellappa 2016 and arXiv:1808.03319 both apply "smoothing" inside the score generator, not the decision layer, despite surface-level similarity to this project's aims). The cellular-handover analogy is a legitimate framework for the decision layer specifically (margin + dwell = hysteresis, directly paralleling LTE ping-pong-reduction mechanisms), but it does not extend to the score generator, and the thesis must not imply that hysteresis or handover concepts explain or improve score quality — only decision stability and responsiveness.

## 8. Mechanism taxonomy

Per Document 02, eight mechanisms, classified without ranking:

- **Essential baselines:** instantaneous threshold (the reference point / origin of the ping-pong problem), dual-threshold/hysteresis (the project's founding analogy, with the strongest direct CA precedent — Kiyani et al. 2020, *IEEE Access* 8:156177–156189), trust/confidence accumulation (the most repeated direct CA precedent — Mondal & Bours 2017; Zhang et al. 2025; and Kiyani et al. 2020 again, since that paper's mechanism is a hybrid of both — Document 02).
- **Strong candidates:** moving average, EWMA (single CA precedent — MDPI Sensors 2025), majority vote, debounce/persistence.
- **Optional/exploratory:** SPRT / HMM — theoretically rigorous, but highest implementation complexity and the documented risk of reproducing the score-generator/decision-layer conflation if not built carefully.

No mechanism is rated "probably unsuitable." A key open design axis carried into Section 9: EWMA/hysteresis/trust operate on continuous scores; majority vote/debounce operate on already-binarized decisions — this must be handled consistently across the comparison.

## 9. Experimental design

Per `01_preregistration_template.md`, `02_splice_benchmark_spec.md`, `03_mechanism_reference.md` (Level 1, Document 03): per-user chronological 60/20/20 split with subject-disjoint impostor training/test partitioning; all preprocessing (imputation, feature selection, SMOTE) fitted inside the training fold only; one fixed Gradient Boosting classifier per genuine user, held constant across every mechanism arm; an open-set splice benchmark constructed from held-out genuine test-period runs and held-out impostor test-period blocks (lengths 3/10/30/60 minutes) under two conditions — cross-context (X) and context-matched (M); every mechanism consumes the identical calibrated score stream. This design is independently validated as consistent with current open-set biometric evaluation practice (Su et al. 2024, Document 03 §C).

## 10. Evaluation framework

Metrics, corrected for provenance per Document 04: **ANGA-time** (mean genuine minutes between false locks — security/stability) and **ANIA-time** (minutes from impostor onset to sustained detection — responsiveness), both explicitly labeled as the project's **own time-normalized adaptation** of Bours & Mondal's (2015) original action-count ANGA/ANIA metrics (*IET Biometrics* 4(4):220–226, DOI 10.1049/iet-bmt.2014.0070; not a direct reproduction — Document 04 §B), plus miss rate, recovery time, and ping-pong rate as already specified. Matched-operating-point selection (freeze the grid cell matching a pre-registered ANGA-time target on validation only, report on test) is directly validated by Ahmed & Imtiaz (2026) and Sugrim et al. (2019) (Document 03 §A–B). Add raw calibrated-score-distribution reporting per mechanism/user as a supplementary diagnostic (Sugrim et al. 2019's Frequency-Count-of-Scores recommendation), not yet in the existing plan.

## 11. Statistical analysis plan

Primary comparison: hysteresis vs. the best validation-selected single-parameter smoother, paired Wilcoxon signed-rank across n=60 users (minus exclusions), consistent with Demšar (2006)'s two-classifier recommendation. **Refinement recommended in Document 03:** adopt a Friedman omnibus test across all mechanisms as the primary secondary-analysis procedure (testing "does mechanism choice matter at all"), followed by Nemenyi/Bonferroni-Dunn post-hoc comparisons only if significant — retaining the existing Holm-corrected pairwise Wilcoxon as a supplementary sensitivity check rather than the primary secondary procedure. Bootstrap 95% CIs on frontier-curve positions, resampled at the **user** level (not frame or sequence level, since within-user observations are temporally correlated). Effect sizes (matched-pairs rank-biserial) reported alongside every p-value, per the existing plan.

## 12. Ablation studies

Component ablation for hysteresis: full hysteresis (margin+dwell) vs. margin-only vs. dwell-only, at the matched operating point, directly testing H3 — already specified in `03_mechanism_reference.md`/`04_experiment_plan.md` and correctly designed to distinguish whether any observed hysteresis advantage requires both components jointly (a genuine "does hysteresis earn its place" test, addressing the project's own guiding-question requirement not to assume hysteresis is superior). Feature-group ablation (motion-only vs. +watch vs. +discrete/low-frequency vs. +audio vs. all) is marked OPTIONAL and addresses whether the score generator's performance is genuinely behavioural or dependent on easily-learned context proxies (location, phone-state) — relevant to RQ1 but not required for the MSc-scope minimum experiment.

## 13. Threats to validity

- **Internal validity:** SMOTE/preprocessing must be verifiably fitted inside the training fold only in the actual implementation (not merely in the plan) — Demircioğlu (2024) confirms the risk if this is not enforced.
- **Construct validity:** ANGA-time/ANIA-time must be explicitly presented as adapted metrics, not the original Bours & Mondal (2015) definitions, to avoid a construct-validity challenge at examination (Document 04 §B).
- **External validity:** findings are specific to ExtraSensory's ~1-minute, 20-second-window sensing cadence and its abrupt-transfer (theft/pickup) splice construction; gradual co-use scenarios are explicitly out of scope (`02_splice_benchmark_spec.md`) and this must be stated as a limitation, not implied to generalize.
- **Statistical validity:** the unit of analysis must remain the user (n≈60 minus exclusions), never the frame or sequence, to avoid inflated significance from autocorrelated observations (Demšar 2006).
- **Coverage validity:** both untested empirical prerequisites from Document 04 (splice-sequence coverage per user/condition/L; context-label match coverage) directly threaten the statistical power of RQ2 and RQ3 if not audited and reported.

## 14. Minimum viable MSc experiment

Per `04_experiment_plan.md`, Steps 0–4 marked ESSENTIAL: cadence check → frozen pre-registration → Exp 1 (per-user subject-disjoint score-generator baseline) → splice benchmark construction with a completed coverage audit → Exp 2 (mechanism bake-off at the matched operating point, primary + refined secondary statistics). This alone directly answers RQ1 and RQ2 and is sufficient for a defensible MSc contribution if executed as specified.

## 15. Extended experiment (if time and evidence permit)

`04_experiment_plan.md` Steps 5–7 marked HIGH VALUE/OPTIONAL/FUTURE WORK: Exp 3 (hysteresis component ablation, answering RQ3/H3 — recommended to include if at all possible, since it is the test that prevents "hysteresis is assumed superior" from going unchallenged); Exp 4 (feature-group ablation, behavioural-vs-shortcut defence for RQ1); Exp 5 (cadence-transfer robustness check, explicitly future work). SPRT/HMM as a seventh/eighth mechanism arm (Document 02) is an optional stretch extension only, given its documented implementation-complexity and score-generator-conflation risk.

## 16. Execution specification

**MUST RUN:**
1. Cadence check (`05_cadence_check.py`) and freeze the pre-registration.
2. Exp 1 — per-user subject-disjoint score-generator baseline, with preprocessing verifiably fitted inside the training fold only.
3. Splice-benchmark construction **plus the coverage/exclusion audit** (per-user sequence availability by condition and L; context-label match rate) — this must be run and reported before mechanism results, per Document 04's recommendation.
4. Exp 2 — mechanism bake-off: **instantaneous threshold, EWMA, majority vote, debounce, hysteresis, trust model** — the six-mechanism core set per Document 02's reasoned recommendation (EWMA selected over moving average as the representative score-level linear-smoothing baseline, since moving average has no located CA precedent and EWMA does) — at the matched operating point, with primary Wilcoxon and the recommended Friedman/Nemenyi secondary analysis. Moving average is already gridded in the project's own `03_mechanism_reference.md` and may be run as a supplementary seventh arm at no extra design cost, but is not required for the primary six-mechanism inferential comparison.

**SHOULD RUN:**
5. Exp 3 — hysteresis component ablation (margin-only vs. dwell-only vs. full), directly testing H3.
6. Supplementary raw score-distribution reporting per mechanism/user (Sugrim et al. 2019 diagnostic).

**OPTIONAL:**
7. Exp 4 — feature-group ablation.
8. SPRT/HMM as an additional mechanism arm, built explicitly as a post-hoc decision-layer step.
9. Exp 5 — cadence-transfer robustness check.

## 17. Evidence required before writing the final paper

- Completed coverage/exclusion audit results (Document 04, Section C/F) — currently unmet.
- Confirmed implementation (not just design) of fold-only preprocessing in Exp 1's actual code.
- ANGA/ANIA attribution corrected to **Bours & Mondal (2015)**, *IET Biometrics* 4(4):220–226, DOI 10.1049/iet-bmt.2014.0070 — confirmed directly against the IET Digital Library record and two independent secondary citations (Document 04 §B); the project knowledge wiki's venue/year was already correct and only needed both authors named explicitly.
- If the Stage-1-reported original experiment's results are to be mentioned at all in the thesis (e.g., as motivating narrative), they must be labeled explicitly as unverified/reported, or the underlying code/notebook must be located and independently checked first.
- Results of Exp 1 and Exp 2 themselves — no results have been generated in this audit; nothing in Documents 01–05 constitutes an executed experiment.

## 18. Novelty, significance, evidence & defensibility assessment (assessed separately, per project standing instructions)

- **Novelty:** Moderate-low at the mechanism level (all eight mechanisms exist elsewhere), moderate at the comparative-methodology level (no located paper performs this specific matched-operating-point, multi-mechanism CA decision-layer comparison). Novelty claim should rest entirely on the comparison, never on any individual mechanism.
- **Significance:** Moderate — resolves a real, evidence-supported gap in evaluation practice (Baig & Eskeland 2021's documented heterogeneity) with direct practical relevance to how CA systems should be tuned and reported.
- **Evidence (current state):** None yet generated — this blueprint is a design specification, not a results paper. The design itself is well-evidenced against 2019–2026 literature (Document 03).
- **Defensibility:** High for the design as specified; **conditional** on the two unmet empirical prerequisites (coverage audits) being resolved and reported honestly, including if they substantially constrain the usable sample.

## 19. Final verdict

**CONTINUE AS REFINED PIVOT.**

This verdict is conditional, not unconditional: it holds only if (a) the coverage/exclusion audits in Section 17 are run and their results — even if they substantially shrink the usable sample or narrow the claims — are reported honestly rather than adjusted after the fact, (b) the ANGA-time/ANIA-time metrics and the hysteresis/trust mechanisms are presented with the corrected attributions and "established mechanism, novel comparison" framing established in this blueprint, and (c) the Stage-1-reported original-experiment claims are never presented as verified findings unless the underlying artifact is located and independently checked. No evidence gathered across Documents 01–04 supports MAJOR REBUILD REQUIRED or RESEARCH DIRECTION NOT CURRENTLY DEFENSIBLE — the design is sound and well-evidenced. REFINE FURTHER is not selected because the remaining open items (two coverage audits, one metric-attribution correction, one statistical-test refinement) are executable, well-specified next steps within the existing design, not indications that the design itself needs re-scoping.

## References

All references from Documents 01–04 are incorporated by reference; the load-bearing sources for this synthesis specifically are: Baig & Eskeland (2021, [Sensors 21(17):5967](https://pmc.ncbi.nlm.nih.gov/articles/PMC8434648/)); Ahmed & Imtiaz (2026, [arXiv:2606.20680](https://arxiv.org/abs/2606.20680)); Sugrim et al. (2019, [NDSS slides](https://www.ndss-symposium.org/wp-content/uploads/ndss2019_06A-3_Sugrim_slides.pdf)); Su et al. ([arXiv:2407.16133](https://arxiv.org/html/2407.16133v1)); Demšar (2006, [JMLR 7](https://www.jmlr.org/papers/v7/demsar06a.html)); Demircioğlu (2024, [Sci Rep 14:11563](https://www.nature.com/articles/s41598-024-62585-z)); Kiyani et al. (2020, *IEEE Access* 8:156177–156189, DOI 10.1109/ACCESS.2020.3019467, [full text](https://repository.mdx.ac.uk/download/e6ea94d1675e5360972f991d0ac4570614b94b447a3ff5c7818ba87424b9e2b6/1634469/Continuous%20User%20Authentication%20Featuring%20Keystroke%20Dynamics%20Based%20on%20Robust%20Recurrent%20Confidence%20Model%20and%20Ensemble%20Learning%20Approach.pdf)); Bours & Mondal (2015, [IET Digital Library](https://digital-library.theiet.org/doi/abs/10.1049/iet-bmt.2014.0070)); Mondal & Bours (2017, [SciSpace](https://scispace.com/papers/a-study-on-continuous-authentication-using-a-combination-of-4dksurb05q)); Zhang et al. (2025, [tandfonline](https://www.tandfonline.com/doi/full/10.1080/0144929X.2024.2321933)); official [ExtraSensory documentation](http://extrasensory.ucsd.edu/); Vaizman et al. (2017, [IEEE Pervasive Computing 16(4)](http://extrasensory.ucsd.edu/papers/vaizman2017a_pervasiveAcceptedVersion.pdf)); project files `01_preregistration_template.md`, `02_splice_benchmark_spec.md`, `03_mechanism_reference.md`, `04_experiment_plan.md`.

## Implications for the next document

None — this is the final synthesis document in the requested sequence. Any further work (the paper itself) must not begin until the Section 17 evidence-required items are resolved, per both this blueprint and the project's standing instruction not to rush to a final paper before the architecture is stable.
