# Citation verification

Nine citations checked against primary sources (publisher pages, Crossref, PMC/Europe PMC
full text, arXiv, the NDSS proceedings PDF), plus Consensus and SciSpace. Verbatim quotes
only; where full text was unreachable, that is stated and the quote is marked as coming
from the abstract.

**Headline: five of the nine need correcting before submission.** Items 1, 2, 5, 6 and 9
are wrong as currently described — wrong year, wrong title, wrong modality, or a paper
that does not exist. Items 3, 4, 7 and 8 stand, with caveats on 4 and 8.

## Summary table

| # | Citation as used | Verified? | Action |
|---|---|---|---|
| 1 | Allano et al. (2010), SPRT precedent in continuous authentication | **PARTIAL** | Paper exists; it is **not** continuous authentication. Reword the citing sentence. |
| 2 | Baldwin et al. (2020), preregistering secondary data analysis | **PARTIAL** | **Year is 2022**, not 2020. And it does *not* endorse preregistering already-seen data. |
| 3 | Kapoor & Narayanan (2023), leakage taxonomy, *Patterns* | **VERIFIED** | Use as is. Cite "eight leaf types", not eight top-level categories. |
| 4 | Zeeshan et al. (2025), *Sensors*, "stabilize decisions and avoid flickering" | **VERIFIED** | Quote is real, but the paper is about **EWMA, not hysteresis**, and offers no evidence. |
| 5 | Mahbub & Chellappa (2018), HMM continuous **face** verification | **NOT VERIFIED** | **No such paper exists.** Replace or drop. |
| 6 | Han et al. (2026) and Michel et al. (2025), differentially private SPRT | **SPLIT** | Michel: real, **not** authentication. Han: real **and is** authentication. Keep Han, recast Michel. |
| 7 | Sugrim et al. (NDSS 2019), robust performance metrics | **VERIFIED** | Safe for Section 4.4, with one caveat. |
| 8 | Stragapede et al. (2022), BehavePassDB, user–device confounding | **VERIFIED** | Strongly supported. Fix year to 2023 if citing the journal volume. |
| 9 | Mondal & Bours (2015), *Information Sciences* 304:28–53 | **PARTIAL** | DOI right; **title and modality wrong**; and it does **not** isolate a component at a matched operating point. |

---

## 1. Allano et al. (2010) — PARTIALLY VERIFIED

**Full reference.** Allano, L., Dorizzi, B., & Garcia-Salicetti, S. (2010). Tuning cost
and performance in multi-biometric systems: A novel and consistent view of fusion
strategies based on the Sequential Probability Ratio Test (SPRT). *Pattern Recognition
Letters*, 31(9), 884–890.
**DOI.** [10.1016/j.patrec.2010.01.028](https://doi.org/10.1016/j.patrec.2010.01.028)
(HAL record: https://hal.science/hal-00620905v1)

**Quote (abstract; full text paywalled).**
> "In this paper we propose a novel sequential score fusion strategy for multi-biometric
> systems. The strategy's aim is to reduce the cost of a multi-biometric system by
> dynamically fusing the optimal number of systems required to take the final decision.
> This way we optimise at the same time cost and performance in the system. The novelty of
> this paper lies in the automatic tuning of the decision parameters (thresholds) at a
> desired level of performance by revisiting the Sequential Probability Ratio Test (SPRT)."

**Notes.** This is *sequential multi-modal score fusion* for one-shot verification —
deciding how many biometric subsystems to invoke before a single decision — not continuous
or implicit authentication. There is no temporal user-session model. It can be cited as an
SPRT-in-biometrics precedent; the citing sentence must not imply session-level or
over-time verification. Two traps: the venue is a journal (*Pattern Recognition Letters*),
not a conference; and a different, real 2008 paper (Allano, Garcia-Salicetti & Dorizzi, "A
Low Cost Incremental Biometric Fusion Strategy for a Handheld Device", SSPR/SPR 2008, LNCS
5342, 842–851, [10.1007/978-3-540-89689-0_88](https://doi.org/10.1007/978-3-540-89689-0_88))
is *incremental* fusion, **not** SPRT — and has a different author order.

## 2. Baldwin et al. — PARTIALLY VERIFIED (year is wrong)

**Full reference.** Baldwin, J. R., Pingault, J.-B., Schoeler, T., Sallis, H. M., &
Munafò, M. R. (**2022**). Protecting against researcher bias in secondary data analysis:
challenges and potential solutions. *European Journal of Epidemiology*, 37(1), 1–10.
**DOI.** [10.1007/s10654-021-00839-0](https://doi.org/10.1007/s10654-021-00839-0)
(PMC8791887, PMID 35025022)

**Quote** (§"Prior knowledge of the data", Europe PMC full text).
> "As such, pre-registration cannot fully protect against researcher bias when researchers
> have previously accessed the data."

**Quote** (§"Declare prior access to data").
> "On the one hand, even if data have been accessed previously, pre-registration is likely
> to reduce QRPs by encouraging researchers to commit to a pre-specified analytic strategy.
> On the other hand, pre-registration does not fully protect against researcher bias where
> data have already been accessed, and can lend added credibility to study claims, which
> may be unfounded."

**Notes.** Two corrections. **(a) The version of record is 2022**, not 2020 — a 2020
preprint exists under a *different* title ("…Challenges and solutions"), which is the
likely source of the wrong year; pick one version and match the year to the title. **(b)
The source does not license what it is being used for.** It says preregistration "cannot
fully protect" when the data have been seen, calls the question debatable, and points to
**multiverse analysis** as the more rigorous solution. If the paper cites it to justify a
preregistration written after the data were inspected, that overstates it. The honest use —
and the one that matches what this project actually did — is: declare prior access, and
note the multiverse recommendation as a limitation.

## 3. Kapoor & Narayanan (2023) — VERIFIED

**Full reference.** Kapoor, S., & Narayanan, A. (2023). Leakage and the reproducibility
crisis in machine-learning-based science. *Patterns*, 4(9), 100804.
**DOI.** [10.1016/j.patter.2023.100804](https://doi.org/10.1016/j.patter.2023.100804)
(PMC10499856, PMID 37720327)

**Quote** (Summary/abstract).
> "Based on our survey, we introduce a detailed taxonomy of eight types of leakage, ranging
> from textbook errors to open research problems."

**Notes.** The eight are *leaf* types under three parents: [L1.1] no test set; [L1.2]
pre-processing on training and test set; [L1.3] feature selection on training and test set;
[L1.4] duplicates in datasets; [L2] model uses illegitimate features; [L3.1] temporal
leakage; [L3.2] non-independence between training and test samples; [L3.3] sampling bias in
test distribution. Do not describe them as eight top-level categories. **L3.1 and L3.2 are
the ones that bear directly on this paper** — they are exactly the failures the Stage 1
audit found in the original pipeline.

## 4. Zeeshan et al. (2025) — VERIFIED, but weak for the use it is put to

**Full reference.** Zeeshan, N., Bakyt, M., Moradpoor, N., & La Spada, L. (2025).
Continuous Authentication in Resource-Constrained Devices via Biometric and Environmental
Fusion. *Sensors*, 25(18), 5711.
**DOI.** [10.3390/s25185711](https://doi.org/10.3390/s25185711) (PMC12473775, PMID 41012948)

**Quote** (§3.6.5 "Temporal Smoothing for Continuous Use", immediately before the EWMA
recursion; Europe PMC full text).
> "To stabilize decisions and avoid flickering, we use EWMA."

**Notes.** Three cautions. **(a) The word "hysteresis" appears zero times** in the full
text; "flickering" appears exactly once, in the sentence quoted. The mechanism is EWMA
low-pass smoothing of the fused score, not a dual-threshold band — citing this as
justification for *hysteresis* is an inference the source does not make. **(b) It is
assertion, not evidence**: no λ value is reported, and there is no ablation isolating the
smoothing effect. **(c)** Hysteresis-like behaviour appears separately in §3.6.6 "Adaptive
Thresholding" (τ_min/τ_max), which is not what the flickering sentence is about. Cite it as
a design-rationale statement from the literature — which is, usefully, exactly the kind of
unevidenced stability claim this paper sets out to test.

## 5. Mahbub & Chellappa (2018), HMM continuous face verification — **NOT VERIFIED**

**No such paper exists.** There is no Mahbub & Chellappa paper, 2018 or otherwise, applying
an HMM or hidden-state temporal model to continuous **face** verification on mobile
devices. The Mahbub–Chellappa HMM line of work is unambiguously non-face.

Correct alternatives, depending on what the sentence needs:

- **Hidden-state temporal model, continuous mobile authentication (app usage):** Mahbub,
  U., Komulainen, J., Ferreira, D., & Chellappa, R. (**2019**). Continuous Authentication
  of Smartphones Based on Application Usage. *IEEE T-BIOM*, 1(3), 165–180.
  [10.1109/TBIOM.2019.2918307](https://doi.org/10.1109/TBIOM.2019.2918307) (arXiv:1808.03319,
  which is where the 2018 date comes from). Abstract: *"An empirical investigation of
  active/continuous authentication for smartphones is presented in this paper by exploiting
  users' unique application usage data, i.e., distinct patterns of use, modeled by a
  Markovian process. Variations of Hidden Markov Models (HMMs) are evaluated for continuous
  user verification…"* Note **four authors and 2019** — "Mahbub & Chellappa (2018)" is wrong
  on both.
- **Hidden-state, location traces:** Mahbub, U., & Chellappa, R. (2016). PATH: Person
  Authentication using Trace Histories. IEEE UEMCON 2016.
  [10.1109/UEMCON.2016.7777911](https://doi.org/10.1109/UEMCON.2016.7777911)
- **Face on mobile, but no HMM:** Mahbub, U., Patel, V. M., Chandra, D., Barbello, B., &
  Chellappa, R. (2016). Partial face detection for continuous authentication. IEEE ICIP
  2016, 2991–2995. [10.1109/ICIP.2016.7532908](https://doi.org/10.1109/ICIP.2016.7532908)
- **HMM + continuous mobile authentication, other group:** Roy, A., Halevi, T., & Memon, N.
  (2014). An HMM-based behavior modeling approach for continuous mobile authentication.
  ICASSP 2014. [10.1109/ICASSP.2014.6854310](https://doi.org/10.1109/ICASSP.2014.6854310)
  (touch/IMU, not face.)

No paper was found combining all three of HMM, face, and continuous mobile authentication.
If the argument needs that combination, it currently has no citation and the claim should
be dropped or softened.

## 6. Differentially private SPRT — SPLIT VERDICT (do not drop both)

**6a. Michel et al. — exists, but is NOT authentication.**
Michel, T., Basu, D., & Kaufmann, E. (2025). DP-SPRT: Differentially Private Sequential
Probability Ratio Tests. arXiv:2508.06377 (v1 8 Aug 2025; v2 4 Feb 2026).
https://arxiv.org/abs/2508.06377

> "We revisit Wald's celebrated Sequential Probability Ratio Test for sequential tests of
> two simple hypotheses, under privacy constraints. We propose DP-SPRT, a wrapper that can
> be calibrated to achieve desired error probabilities and privacy constraints, addressing
> a significant gap in previous work." *(abstract)*

A case-insensitive search of the full PDF for `authenticat|biometric|login|intrusion|smartphone|behavio(u)?ral`
returns **zero matches**. Cite it only as the DP-SPRT *method* source, never as an
authentication reference.

**6b. Han et al. (2026) — exists AND is about authentication.**
Han, Z., Li, Y., & Zhao, Y. (2026). Design and Application of a Multi-Modal Continuous
Identity Authentication System for Complex Sports Scenarios. *2026 5th International
Symposium on Computer Applications and Information Technology (ISCAIT)*, 1409–1412.
**DOI.** [10.1109/ISCAIT69154.2026.11477459](https://doi.org/10.1109/ISCAIT69154.2026.11477459)

> "Gait-based Continuous Authentication (CA) has become an important security technique for
> mobile and IoT systems, yet existing methods face a critical privacy-efficiency tradeoff:
> differential privacy noise increases decision latency, while raw data transmission risks
> timing-based side-channel leakage. To address this issue, we propose a privacy-preserving
> framework based on the Differentially Private Sequential Probability Ratio Test
> (DP-SPRT)." *(abstract, as indexed by Consensus)*

**Caveats.** Metadata confirmed via Crossref; the abstract text is **single-source**
(Consensus — IEEE Xplore was unreachable and SciSpace does not index it). It is a four-page
paper in a minor symposium with zero citations, it borrows DP-SPRT's mechanism wholesale,
and the modality is **gait in sports scenarios**, not smartphone context. Keep it, but do
not lean on it.

## 7. Sugrim et al. (NDSS 2019) — VERIFIED; safe for Section 4.4

**Full reference.** Sugrim, S., Liu, C., McLean, M., & Lindqvist, J. (2019). Robust
Performance Metrics for Authentication Systems. *Network and Distributed Systems Security
(NDSS) Symposium 2019*, San Diego, CA.
**DOI.** [10.14722/ndss.2019.23351](https://doi.org/10.14722/ndss.2019.23351)
**PDF.** https://www.ndss-symposium.org/wp-content/uploads/2019/02/ndss2019_06A-3_Sugrim_paper.pdf

**Answer to the question that decides Section 4.4: it does both.**

*Against EER* (abstract):
> "In this work, we show that several of the common metrics used for reporting performance,
> such as maximum accuracy (ACC), equal error rate (EER) and area under the ROC curve
> (AUROC), are inherently flawed."

*Against EER* (§VII):
> "If we are only given the EER to evaluate a system and we have a specific target for our
> TPR or FPR, we are unable to determine from the EER if our target will be met. This
> information is not knowable because many ROCs (and thus many classifiers) have the same
> EER."

*For a fixed operating point* (Figure 9 caption):
> "Comparing systems with a specific FPR target in mind is done by finding the highest TPR
> for that FPR. To find the highest, TPR draw a vertical line at that FPR and then identify
> the ROC that crosses the line at the highest point. A similar procedure works for specific
> TPR targets with horizontal lines."

*For a fixed operating point* (§IX-A-2, case study):
> "In Figure 9, we display the ROC curves for all three systems. We assumed that the
> implementer has a fixed requirement on the FPR of 0.1. To choose a system that meets our
> requirements, we drew a solid black vertical line at our FPR limit. Thus, we can visually
> identify the system that has the highest TPR for our FPR limit. In this case, Keystroke is
> the clear winner, even though it does not have the lowest EER. Thus, potential implementers
> would not able to assess a proposed system when given only the EER."

*(The grammatical slip "would not able to" is in the original.)*

**Caveat.** The paper's *primary* recommendation is to report the unnormalised frequency
count of scores (FCS) together with the ROC, and to read the local slope — not that a single
fixed point suffices (§IX-A-2: *"when considering both the the TPR value for a fixed FPR and
the slope around a fixed FPR"*). Safe phrasing: "Sugrim et al. show that EER-to-EER
comparison is uninformative, and demonstrate selection between systems at a fixed FPR
requirement." Do not claim they say a matched operating point is sufficient.

## 8. Stragapede et al., BehavePassDB — VERIFIED

**Full reference.** Stragapede, G., Vera-Rodriguez, R., Tolosana, R., & Morales, A.
BehavePassDB: Public Database for Mobile Behavioral Biometrics and Benchmark Evaluation.
*Pattern Recognition*, 134, 109089 (**February 2023**).
**DOI.** [10.1016/j.patcog.2022.109089](https://doi.org/10.1016/j.patcog.2022.109089)
**Preprint (quoted here).** arXiv:2206.02502 (v1 June 2022) — https://arxiv.org/abs/2206.02502

**Quote** (abstract) — the most citable one:
> "However, there is no way of knowing whether state-of-the-art classifiers in the
> literature can distinguish between the notion of user and device."

**Quote** (§II-B, on prior datasets) — closest to "the model may learn the device":
> "In light of this, it is difficult to assess how much of the authentication performance it
> to be attributed to the system identifying the device rather than the user." *[sic]*

**Quote** (§II-C "Device Bias"):
> "In light of this, it would be interesting to investigate how much of the authentication
> effectiveness should be attributed to the models extracting and recognizing features
> belonging to the device rather than the user."

**Notes.** User–device confounding is not incidental to this paper: "device bias" is an
index term, §II-C is titled "Device Bias", and §IV-D quantifies the effect (magnetometer and
linear accelerometer lose 20% and 13% AUC in absolute terms when the device confound is
removed, other modalities about 5%). Database: 81 users, 4 sessions ≥24 h apart, 8 tasks, 15
sensors, participants' own Android phones, with a skilled-forgery protocol in which the
impostor uses the *same device* — which is what makes the confound measurable. **Fix the
year to 2023 if citing the *Pattern Recognition* volume and pages**; 2022 is correct only for
the arXiv preprint.

## 9. Mondal & Bours (2015) — PARTIALLY VERIFIED; the reference and the claim both need fixing

**Correct full reference.** Mondal, S., & Bours, P. (2015). **A computational approach to
the continuous authentication biometric system.** *Information Sciences*, 304, 28–53.
**DOI.** [10.1016/j.ins.2014.12.045](https://doi.org/10.1016/j.ins.2014.12.045)
(ScienceDirect PII S0020025514011979; NISlab, Gjøvik University College)

**The DOI is right; the title in the draft is wrong.** "A study on continuous authentication
using a combination of keystroke and mouse biometrics" is a **different paper** — Mondal &
Bours in *Neurocomputing* (PII S0925231216314321, 2017). Two Mondal & Bours papers have been
conflated.

**Abstract, verbatim in full** (p. 28):
> "In this paper, we investigate the performance of a continuous biometric authentication
> system under various different analysis techniques. We test these on a publicly available
> continuous mouse dynamics database, but the techniques can be applied to other biometric
> modalities in a continuous setting also. We test all different combinations of fusion
> techniques, threshold settings, score boosting techniques and static versus dynamic trust
> models. We extensively describe the way that performance is reported when analyzing the
> performance of a continuous authentication system. Contrary to a biometric system for
> access control at the start of a session can the performance not simply be reported by a
> single EER value or a DET curve. We show that the optimal performance we can reach with our
> new techniques improves significantly over the best known performance on the same dataset."

*(The inverted clause "Contrary to a biometric system … can the performance not simply be
reported" is verbatim in the original.)*

**(a) What it compares.** A full-factorial sweep of four decision-layer factors
simultaneously — "all different combinations" of: fusion scheme (average vs weighted);
threshold setting (fixed/global vs user-specific); score boosting (with vs without the Score
Boost algorithm); trust model (static, in 3-level and 4-level variants, vs dynamic).

**(b) Modality and data.** **Mouse dynamics only — there is no keystroke data in this
paper.** Keywords list "Mouse Dynamics" and not keystroke. 49 genuine users, from a
pre-existing public mouse-dynamics corpus (secondary-data reuse, not the authors' own
collection). *The dataset name and per-user sample counts could not be confirmed from a second
source — the paper is fully paywalled (Unpaywall: `oa_status: closed`, no repository copy) —
so treat those specifics as unverified.*

**(c) Does it isolate a single decision-layer component at a matched operating point? — NO,
on two independent grounds.**

1. **It varies several factors at once, by design.** The abstract's own words: "We test **all
   different combinations** of fusion techniques, threshold settings, score boosting
   techniques and static versus dynamic trust models." That is a combinatorial grid reported
   as a results table, not a one-factor-at-a-time ablation, and no factorial effect
   decomposition is claimed.
2. **It reports ANGA/ANIA and explicitly repudiates fixed-error-rate reporting.** Results are
   given as Average Number of Genuine Actions before a false lockout and Average Number of
   Impostor Actions before detection — action-domain metrics with no FAR axis on which to fix
   a point. The abstract states the position outright: *"Contrary to a biometric system for
   access control at the start of a session can the performance not simply be reported by a
   single EER value or a DET curve."*

*Confidence note: the ANGA/ANIA finding and the four-factor sweep are confirmed from two
independent fetches, and the anti-EER/DET stance is a direct abstract quote. The absence of a
matched-FAR isolation is a strong inference from those two facts rather than a direct
quotation, because the "Result analysis" section could not be read. If the positioning claim
is load-bearing, obtain the PDF through the institution and check that section for any table
holding one error rate constant.*

**What this means for the paper's positioning.** Do **not** cite Mondal & Bours (2015) as
prior work that isolated a single decision-layer component at a matched operating point — it
does the opposite on both counts. Cited accurately it *supports* the positioning: it is the
canonical demonstration that continuous-authentication decision layers have been evaluated by
sweeping many factors jointly and reporting action-domain metrics, with its own authors
arguing that single-EER/DET reporting does not apply. That leaves the gap this paper fills,
and it pairs naturally with Sugrim et al. (2019), who supply the matched-FPR protocol Mondal
and Bours declined to use. Suggested framing:

> Prior comparative work in continuous authentication varies fusion, thresholding, boosting
> and trust-model choices in combination and reports action-domain metrics (ANGA/ANIA) rather
> than matched-FAR contrasts (Mondal & Bours, 2015). We instead isolate a single decision rule
> at a fixed false-accept operating point, following the reporting discipline of Sugrim et al.
> (2019).

This does *not* rescue an unqualified "no prior work compares decision-layer mechanisms"
claim, which `docs/Stage2/LITERATURE_VERIFICATION.md` already records as falsified. What is
defensible is the narrower claim: prior work compares *combinations* at *unmatched* operating
points; this paper isolates *one factor* at a *matched* one.
