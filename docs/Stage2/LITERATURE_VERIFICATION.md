# Literature Verification and Novelty Assessment — Stage 2

Date: 2026-09-26. Phase: post-freeze literature verification (Part D of `V2_FORENSIC_AUDIT_AND_PLAN.md`).
No experimental code or frozen result was touched in producing this document.

**Method.** Adversarial search first: for each candidate novelty claim I searched for prior work that would
invalidate it, before searching for support. Sources: Consensus (Semantic Scholar / PubMed / Scopus / arXiv,
~220M papers), SciSpace (~280M), and targeted web verification for the 3GPP definitions. Evidence level is
marked per item: **[A]** abstract/record verified in an indexed database; **[F]** full text or authoritative
technical source read; **[U]** unverified beyond title/abstract and flagged for follow-up.

**Headline.** The methodological framework is substantially **less novel than assumed**, and two claims must
be weakened materially. The genuine contribution is narrower and more specific than "a temporally valid
evaluation framework". It survives, but it has to be stated precisely.

---

## 1. Kill-shot search: did anyone already do this?

**Target claim.** *No prior work performs a matched-operating-point comparison of multiple temporal
decision-layer mechanisms in continuous/behavioural authentication, evaluated on identity-transition
sequences.*

**Verdict: PARTIALLY FALSIFIED. Must be narrowed.**

| Prior work | What it does | Effect on the claim |
|---|---|---|
| Mondal & Bours (2015), *Information Sciences*, "A computational approach to the continuous authentication biometric system", 43 cit. **[A]** | "We test **all different combinations of fusion techniques, threshold settings, score boosting techniques and static versus dynamic trust models**" on continuous mouse dynamics, and explicitly argue CA performance cannot be reported by a single EER or DET curve. | **The closest prior art found.** A comparative study of decision-layer variants in CA already exists. The "no comparative evaluation" framing cannot stand unqualified. |
| Fonseca et al. (2026), arXiv, "VIGIL" **[A, U]** | Continuous multimodal authentication with **dual-state State Transition Machines with unidirectional transition matrices**, a **three-zone verification decision model**, monotonic decay and backflow elimination. | Conceptually very close: a dual-state latch plus a three-zone (margin-like) decision. Preprint, 0 citations. **Full text must be read before any novelty claim is finalised.** |
| Ryu & Yeom (2021), *IEEE Access*, systematic review, 110 cit. **[A]** | Finds a lack of comparative analysis in CMBA — but of **fusion levels and biometric-type combinations**, not temporal decision layers. | Supports a general "field under-compares design choices" statement only. Do not cite as direct support for the specific gap. |

**Surviving, narrowed formulation** (defensible on current evidence):

> Prior comparative work in continuous authentication compares *fusion strategies, thresholds and trust-model
> variants*. No identified study decomposes a margin-plus-dwell decision rule into its two components and tests
> whether their composition confers an incremental advantage over either alone, at a matched operating point,
> with tuning held equal across cells.

That is a real gap, but it is much smaller than "no comparative evaluation of temporal decision layers exists".

---

## 2. Area-by-area map

### 2.1 Continuous / implicit smartphone authentication — ESTABLISHED

Mature field with several large surveys: Abuhamad et al. (2020), *IEEE IoT-J*, 140+ approaches, 181 cit. **[A]**;
Stylios et al. (2021), *Information Fusion*, 122 cit. **[A]**; Rayani & Changder (2022), 49 cit. **[A]**;
Dahia et al. (2020), *WIREs DMKD*, 52 cit. **[A]**; Mahfouz et al. (2017), 134 cit. **[A]**.

Dominant modalities are touch, keystroke, gait, mouse and app usage. **Contextual/ambient smartphone sensing
as the authentication signal is comparatively rare** — this is where the project sits, and it is a legitimate
point of differentiation, though not itself a methodological contribution.

### 2.2 Temporal decision stabilisation — ESTABLISHED, in every component

| Mechanism | Prior art in continuous authentication |
|---|---|
| Trust model with accumulation/decay | Mondal & Bours (2017), *Neurocomputing*, 132 cit. — "robust dynamic trust model algorithm that can be applied to any continuous authentication system, irrespective of the biometric modality" **[A]**. Also Zhang et al. (2025), *Behaviour & IT* **[A]**. |
| **Margin / dual threshold** | Kiyani et al. (2020), *IEEE Access*, 27 cit. — "a novel perception of **two thresholds, i.e. alert and final threshold**", locking impostors out faster on reaching the alert threshold **[A]**. |
| SPRT / sequential test | Allano et al. (2010), *Pattern Recognition Letters*, 36 cit., SPRT-based sequential fusion with automatic threshold tuning **[A]**. Han et al. (2026) and Michel et al. (2025) use **DP-SPRT for gait-based continuous authentication**, benchmarking against an existing **PrivSPRT** **[A]**. |
| Decision-level fusion / voting | Fridman et al. (2014), *Computers & Electrical Engineering*, 74 cit. **[A]**; Gao et al. (2020) **[A]**; Sivasankaran et al. (2018), ICB **[A]**. |
| State machines / HMM | Mahbub & Chellappa (2018), *IEEE T-BIOM*, 50 cit., HMM for continuous verification **[A]**. |

**Consequence.** Not one of the nine mechanisms is novel in this setting. The project never claimed they were,
and the v2 framing is correct — but the thesis must cite these explicitly rather than presenting the mechanism
set as assembled from adjacent domains.

### 2.3 Hysteresis and time-to-trigger in cellular handover — ESTABLISHED, and our terminology was wrong

Verified against the 3GPP Event A3 definition **[F]**:

* Entering: `Mn + Ofn + Ocn − Hys > Mp + Ofp + Ocp + Off`
* Leaving: `Mn + Ofn + Ocn + Hys < Mp + Ofp + Ocp + Off`
* Time-to-Trigger: the condition must hold **continuously** for the TTT duration before a measurement report
  is sent. Range **0–5120 ms**.
* Ping-pong: UEs switching back and forth between cells when hysteresis and TTT are configured too low.

**Three consequences, all of which improve the thesis.**

1. **Terminological correction.** In 3GPP, *hysteresis* is the **margin** term alone; *time-to-trigger* is the
   separate **dwell** term. They are composed. The project's earlier usage of "hysteresis" to mean margin + TTT
   conflated two distinct 3GPP parameters. Fix this throughout.
2. **The factorial mirrors the source domain exactly.** The `margin m × dwell k` design reproduces the actual
   3GPP decomposition, and the `(m>0, k>1)` cells correspond to a full handover configuration. The null is
   therefore a sharper statement than "hysteresis failed": *composing the margin term with the dwell term did
   not beat either term alone on this benchmark.*
3. **Timescale does not transfer, and this retrospectively explains the "TTT = 3 s" error.** 3GPP TTT spans
   0–5120 ms; the ExtraSensory decision cadence is ~60 s per frame, so the project's dwell values of 2–10
   frames are 2–10 minutes — **three orders of magnitude slower than the mechanism being borrowed from**. The
   original "TTT = 3 seconds" is a plausible handover value transplanted without rescaling. State this as a
   substantive limit on the cross-domain analogy, not merely a units bug.

### 2.4 Evaluation methodology — ESTABLISHED. **This is the claim requiring the largest weakening.**

| Prior work | Finding |
|---|---|
| **Eberz et al. (2017)**, ACM AsiaCCS, 103 cit. **[A]** | Of 25 analysed CA papers, **13 either include impostor data in the negative class or randomly sample training data from the entire dataset**. Quantified: these underestimate error rates by **63%** and **81%** respectively. Also shows systematic (vs random) errors matter and proposes the Gini coefficient. |
| **Georgiev et al. (2022)**, ACM AsiaCCS / FETA **[A]** | Systematic review of 30 touch-dynamics papers: **all overlook at least one pitfall**. Quantifies non-contiguous training data (3.8% EER), attacker data in training (2.55%), and **phone-model mixing (3.2–5.8%)**; cumulative 8.9%. Proposes best practices. |
| **Kapoor & Narayanan (2023)**, *Patterns*, 1068 cit. **[A]** | Leakage across 17 fields, 294 papers; **taxonomy of eight leakage types**; model info sheets. |
| Larracy et al. (2022), IJCB **[A]** | Leakage via processing-step order and a posteriori performance measures in gait biometrics. |
| Parvan (2026), arXiv, ECG-biometrics-bench **[A]** | Names the **"Random Split Fallacy"**; standardises subject-disjoint and cross-session protocols. |
| Bours & Mondal (2015), *IET Biometrics*, 40 cit. **[A]** | **"Most research on alleged CA is in fact periodic authentication"**; argues performance should be reported as **average number of genuine/impostor actions (ANGA/ANIA)**, not FAR/FRR. |

**What this means, plainly.** Every defect Stage 1 found in the original pipeline — random row-level splitting,
impostors shared between train and test, preprocessing fitted on all data, inappropriate single-number metrics —
is a **documented, named, quantified pitfall in this exact literature, published up to nine years earlier**.
Stage 1 is a careful *replication* of known failure modes in a new modality. It is not a methodological
discovery, and must not be written as one.

**A second, sharper consequence.** Bours & Mondal argue that frame-level FAR/FRR is the wrong reporting frame
for CA and that event-based ANGA/ANIA is right. Our v2 design uses **frame-level FAR as the matching variable**
and event-based measures (excess transitions, detection/recovery failure) as outcomes. That hybrid is
defensible — FAR is the natural quantity to hold constant when comparing decision rules — but it is a choice
that runs against a standing recommendation in the field, and the thesis must defend it explicitly rather than
pass over it. Our excess-transition and detection/recovery-failure metrics should be positioned as **variants
within the established ANGA/ANIA family**, not as new inventions.

### 2.5 ExtraSensory, missingness and device confounding — ESTABLISHED as a named open problem

| Prior work | Relevance |
|---|---|
| **Stragapede et al. (2022)**, *Pattern Recognition*, BehavePassDB, 50 cit. **[A]** | States directly that "**there is no way of knowing whether state-of-the-art classifiers in the literature can distinguish between the notion of user and device**", and builds a database that **includes different users on the same device** to address it. |
| Georgiev et al. (2022) **[A]** | Quantifies phone-model mixing as a 3.2–5.8% EER effect. |
| Perelli et al. (2025), IEEE MetroXRAINE **[A]** | HAR sensor features re-identify **individuals or devices** without explicit labels; EER as low as 10.8–14.1%. |
| Malekzadeh et al. (2019), ACM IoT, 92 cit. **[A]** | Motion data enables user re-identification; anonymising autoencoders reduce identification to <7% while keeping activity accuracy >92%. |

**Consequence.** The F3/F7 result (AUC 0.990 vs 0.758) is a sensible probe of a **recognised** problem, not a
new one. The honest position is unchanged and now well-supported: missingness carries substantial
identity-discriminative information; the device-versus-person explanation remains a **plausible, unresolved
construct-validity concern**, not a demonstrated cause. BehavePassDB is the concrete instrument for resolving
it and belongs in future work.

### 2.6 Preregistration — ESTABLISHED as method, not found in this field

Nosek et al. (2018), *PNAS*, 1640 cit. **[A]**; Hardwicke & Wagenmakers (2023), *Nature Human Behaviour*,
108 cit. **[A]**; Bakker et al. (2018), *PLoS Biology* **[A]**. Most directly applicable: **Baldwin et al.
(2020)**, *European Journal of Epidemiology*, 138 cit. **[A]** — preregistration for **secondary data
analysis**, explicitly addressing bias from prior knowledge of the data. That is precisely our situation
(pre-existing ExtraSensory data, an exploratory v1 already seen), and it legitimises the "re-registration after
an exploratory run" posture we adopted.

I found **no instance of a preregistered confirmatory analysis in continuous or behavioural authentication.**
Absence of evidence in a bounded search is not proof of absence, so the claim must be phrased as *"we are not
aware of"*, not *"there is none"*.

---

## 3. Verdict on each candidate contribution

| # | Candidate claim | Verdict | Required wording |
|---|---|---|---|
| 1 | A temporally valid evaluation framework for CA | **WEAKEN HEAVILY** | It is a careful *assembly and application* of established best practice (Eberz 2017; Georgiev 2022; Kapoor & Narayanan 2023; Bours 2015). Claim rigour, not novelty. |
| 2 | Stage 1 identified methodological defects | **WEAKEN** | A replication of documented pitfalls in a new modality. Valuable as provenance and as a worked case; not a discovery. |
| 3 | Comparative evaluation of temporal decision layers | **NARROW** | Mondal & Bours (2015) already compared decision-layer variants. Our specific contribution is the equal-tuning factorial, not comparison per se. |
| 4 | **Margin × dwell factorial testing incremental value, θ-only tuning per cell** | **SURVIVES** | No precedent found. This is the strongest genuine claim. Mirrors the 3GPP decomposition exactly. |
| 5 | **Preregistered conjunctive criterion with a committed null in CA** | **SURVIVES, softly** | Preregistration is established; its application here appears to be the first in this field. Phrase as "we are not aware of". |
| 6 | Contextual/ambient sensing as CA signal with a temporal decision layer | **SURVIVES, modest** | Most CA work uses touch/keystroke/gait/mouse. Differentiating but not a methodological contribution. |
| 7 | New stability/responsiveness metrics | **WEAKEN** | Position as variants in the established ANGA/ANIA family (Bours 2015), not new measures. |
| 8 | SPRT as a notable mechanism | **DROP any novelty** | SPRT in CA is established (DP-SPRT, PrivSPRT, Allano 2010). Keep as a secondary descriptive observation only. |
| 9 | Hysteresis unexplored in behavioural authentication | **ALREADY WITHDRAWN — keep withdrawn** | Falsified: Kiyani (2020) dual threshold; Mondal & Bours (2017) trust models. |

---

## 4. Proposed contribution statement, literature-calibrated

> Continuous-authentication evaluation is known to be vulnerable to random-split, shared-impostor and
> preprocessing leakage, and to single-number reporting that obscures temporal behaviour. Applying these
> established corrections to contextual smartphone sensing, this study asks a question the comparative
> literature has not: whether a cellular-handover-inspired decision rule — a score **margin** composed with a
> **dwell** requirement, the two parameters 3GPP combines to suppress ping-pong handover — provides any
> incremental stabilisation over either component alone. Using a preregistered, conjunctive criterion with a
> committed null, a fixed per-user score generator, unseen participant-disjoint impostors and controlled
> identity-transition sequences, the composition did **not** demonstrate an advantage over its components.
> Temporal persistence alone accounted for most of the observed reduction in excess transitions, and stronger
> stabilisation traded stability against false rejection and recovery failure.

This is defensible against everything found above. It claims rigour where the field already has standards,
and novelty only where the search found none.

---

## 5. Outstanding verification

| # | Item | Why it matters | Status |
|---|---|---|---|
| 1 | **Full text of Fonseca et al. (2026), VIGIL** | Dual-state STM plus three-zone verification is the nearest live threat to claim 4. If it already decomposes margin from dwell, claim 4 weakens further. | **[U]** — must read before finalising |
| 2 | **Full text of Mondal & Bours (2015)** | Determines exactly which decision-layer variants were compared and whether at matched operating points. Directly bounds claim 3. | **[U]** — must read before finalising |
| 3 | Systematic check for preregistration in biometrics venues | Claim 5 currently rests on absence of evidence. | Not done |
| 4 | Whether any CA study matches operating points on FAR rather than reporting ANGA/ANIA | Needed to defend our matching variable against Bours' recommendation. | Not done |

Claims 3, 4 and 5 should not be written into the thesis as final until items 1 and 2 are read in full.

---

## 6. Sources

Search tools: Consensus (Semantic Scholar, PubMed, Scopus, arXiv) and SciSpace. 3GPP Event A3 definitions
verified at [WirelessBrew — Measurement report Event A3 in 5G NR](https://wirelessbrew.com/5g-nr/measurement-report-event-a3-in-5g-nr/),
consistent with [RF Essentials — A3 Event](https://rfessentials.com/resources/rf-glossary/a3-event/) and
[3GLTEInfo — LTE Measurement Events](https://www.3glteinfo.com/lte/architecture/ran/measurement-events/).

Key papers, with database records:
Mondal & Bours 2015 *Inf. Sci.* · Mondal & Bours 2017 *Neurocomputing* · Bours & Mondal 2015 *IET Biometrics* ·
Kiyani et al. 2020 *IEEE Access* · Eberz et al. 2017 *ACM AsiaCCS* · Georgiev et al. 2022 *ACM AsiaCCS* ·
Kapoor & Narayanan 2023 *Patterns* · Larracy et al. 2022 *IJCB* · Parvan 2026 *arXiv* ·
Stragapede et al. 2022 *Pattern Recognition* · Perelli et al. 2025 *IEEE MetroXRAINE* ·
Malekzadeh et al. 2019 *ACM IoT* · Allano et al. 2010 *Pattern Recognition Letters* ·
Fridman et al. 2014 *Comput. Electr. Eng.* · Mahbub & Chellappa 2018 *IEEE T-BIOM* ·
Ryu & Yeom 2021 *IEEE Access* · Abuhamad et al. 2020 *IEEE IoT-J* · Stylios et al. 2021 *Inf. Fusion* ·
Nosek et al. 2018 *PNAS* · Baldwin et al. 2020 *Eur. J. Epidemiol.* · Hardwicke & Wagenmakers 2023 *Nat. Hum. Behav.* ·
Fonseca et al. 2026 *arXiv* (unverified beyond abstract) · Han et al. 2026 and Michel et al. 2025 (DP-SPRT).
