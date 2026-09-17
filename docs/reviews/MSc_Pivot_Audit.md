# MSc Research — Supervisor & Pivot Audit

**Project:** Continuous / implicit smartphone authentication — decision-layer stability
**Audit date:** 15 September 2026
**Status of evidence base:** eight uploaded documents + one PDF. **No notebooks, code, output logs, or the dataset itself were available.** All statements about "the experiments" are statements about *reports of* experiments. Findings A–D referenced below are from the previous review (identical-accuracy table; impossible episode count; algebraically dependent stability metrics; TTT incompatible with frame period).

---

## 1. Research Reconstruction

| # | Item | Status | Basis |
|---|---|---|---|
| 1 | Topic | **Clearly established** | Continuous/implicit smartphone authentication via contextual sensors; decision-level stability. |
| 2 | Problem | **Clearly established** | Noise-driven oscillation of authentication state under instantaneous thresholding ("ping-pong"). Consistent across documents. |
| 3 | Original gap | **Weakly established** | "The behavioural biometrics community has not systematically explored [hysteresis]" (*Partial fulfilment*). Refuted by external literature (§4). |
| 4 | Reformulated gap | **Established in the review only** | Not yet adopted in any uploaded document. |
| 5 | Motivation | **Clearly established** | Usability, trust erosion, abandonment, battery. Empirical magnitude not shown (≈1.5 transitions/hour in own data, possibly ≈1 per 2 hours — see §5). |
| 6 | Aim | **Contradictory** | Four aims across *Partial fulfilment*, *CSCD601*, *Extended Abstract*, PDF. |
| 7 | Objectives | **Partially established** | Five in *Partial fulfilment*; Objective 5 (classifier-agnostic) untested. |
| 8 | Research questions | **Contradictory** | Four disjoint RQ sets. |
| 9 | Hypotheses | **Weakly established** | H1/H2 in *CSCD601* only; H1 untested; H2 near-tautological. |
| 10 | Conceptual framework | **Partially established** | Handover analogy stated, never formalised. |
| 11 | Dataset | **Clearly established** | ExtraSensory. |
| 12 | Dataset characteristics | **Partially established / one likely error** | 60 users, ~377k rows, 225 features, 51 labels, 16.5% missing. "20-second sampling intervals" is very likely a mis-description (§5). |
| 13 | Sensors/features | **Partially established** | Feature groups named; final 52/53-feature list not given. |
| 14 | Data collection context | **Clearly established** | In-the-wild, participants' own devices, self-reported labels (Vaizman et al. 2017). |
| 15 | ML models | **Clearly established** | LR, GB, RF (ranking only). GB hyperparameters missing. |
| 16 | Experimental design | **Contradictory** | Offline secondary analysis (empirical docs) vs. within-subjects human study (PDF). |
| 17 | Baselines | **Weakly established** | LR (classifier) and P>0.5 (decision). No mechanism baselines. |
| 18 | Decision mechanisms | **Weakly established** | Margin unreported; TTT = 3 s (inconsistent with frame period); lock rule truncated. |
| 19 | Evaluation metrics | **Partially established** | Standard classification set + three stability metrics, one undefined, two algebraically dependent. |
| 20 | Results | **Partially established, internally inconsistent** | 99.26%/0.53%/7.09%; 597→49; 567→0; SI 0.9502→0.9959. Classification deltas of exactly 0.0% (Finding A); episode count arithmetically impossible (Finding B). |
| 21 | Conclusions | **Overclaimed** | "Complete elimination," "no accuracy impact," "reusable framework." |
| 22 | Claimed contribution | **Partially established** | Five claims; only "problem reframing" survives at full strength. |
| 23 | Limitations | **Missing** | No limitations section in *Partial fulfilment*. |
| 24 | Future work | **Weakly established** | One sentence (adaptive hysteresis). |

**EVIDENCE NOT ESTABLISHED IN THE PROVIDED MATERIALS:** definition of the legitimate class; test-set size; SMOTE-before-or-after-split; the RF selection split; the margin value; the "stable frame" definition; oscillation-window semantics; GB hyperparameters; any ambient-noise or magnetometer experiment; any human-participant study.

---

## 2. Research Evolution

| Stage | Document(s) | RQ / focus | Hypothesis | Method | Contribution claim |
|---|---|---|---|---|---|
| **S1** | *Extended Abstract* | Ambient noise + magnetometer as secondary factors; design choices and validity | None formal | Literature-based critique; no experiment planned | Conceptual positioning; guidelines |
| **S2** | *Abstract.docx* | Same template; RQ replaced with hysteresis/transition logic | None formal | Still critique | Hysteresis inserted into the S1 skeleton; sensor-validity RQ dropped without being tested |
| **S3** | *CSCD601_Rewritten* | Both RQs coexist | H1, H2 | "Experimental… using ExtraSensory" — first dataset mention | Methodological design choices |
| **S4** | PDF (CSCD601 critique) | Handover logic as research-design intervention | Hysteresis reduces ping-pong | Describes a within-subjects human study (70/60/65 thresholds, TTT 2–5 s) | Cross-domain borrowing |
| **S5** | *22427613 – First Semester Exams* (4 Feb 2026, CSCD613 ML with Big Data) | Coursework: justify a Big Data dataset; implementation; feature engineering | — | ExtraSensory ingestion, SMOTE, GB 99.26%, RF Gini | **Dataset selected for Big Data coursework criteria, not to test the hysteresis hypothesis** |
| **S6** | *Partial fulfilment* (Feb 2026) | RQ1 noise→instability; RQ2 hysteresis; RQ3 trade-off | Implicit | S5 pipeline + hysteresis layer | Five contributions incl. "complete elimination" |
| **S7** | *Draft* | RQ1 design choices; RQ2 hysteresis vs. accuracy | — | Skeleton only | — |
| **S8** | Review → reformulated gap | Comparative evaluation of stabilisation policies | — | Proposed | Protocol + first evidence |

**Terminology drift:** "hard handoff protocol" → "handover hysteresis" → "Time-to-Trigger / Margin"; three incompatible ping-pong definitions across PDF, *Partial fulfilment*, and the methodology section. "Behaviour"→"behavioural" corruption from S5 onward.

**Experiments added/removed:** S1–S3 sensor-validity investigation never run and silently dropped. S4 human study never run. S5 classifier built for a different course, carried into S6 as the authentication engine.

### Classification
Mostly **A (normal refinement)** for S1→S3, with two **D-adjacent** risk flags:

1. **Dataset chosen before the RQ was fixed, for a different purpose.** Not HARKing (hypothesis predates data), but dataset fitness for the authentication RQ was inherited, never argued.
2. **Tuned-to-result risk.** Hysteresis parameters unreported, validation split unused, headline result is a perfect "0." Post-hoc tuning cannot be excluded from the materials.

S8 is a legitimate **C (reframing from discovery)**. It becomes HARKing only if presented as the original plan. **Write the evolution into the thesis as a documented refinement.**

---

## 3. The Reformulated Gap

**Old gap** (*Partial fulfilment*): *"While the telecommunications industry solved analogous stability problems decades ago through hysteresis-based handover protocols, the behavioural biometrics community has not systematically explored these techniques."*

**New gap** (previous review, verbatim): *"Decision-layer stabilisation is widely used in continuous authentication but is applied heuristically: mechanisms are introduced individually, compared only against naive thresholding, evaluated with non-standard stability measures, and almost never assessed for the intrusion-tolerance window they introduce. Consequently there is no evidence about which stabilisation policy occupies the best stability–responsiveness operating point, nor a common protocol for establishing it."*

**What changed:** absence claim about one mechanism → comparative claim about a class. The old gap dies to one counterexample; the new one only to a comparative study.

**Why it may be stronger:** does not depend on hysteresis winning; converts the biggest weakness (no baselines) into the research question; testable with existing data.

**Evidence needed to close it:** (i) ≥5 mechanisms on one classifier output, one dataset, one protocol; (ii) a priori stability and responsiveness metrics; (iii) matched-operating-point comparison; (iv) per-user statistics with uncertainty; (v) pre-stated falsification criteria; (vi) an honest ranking, including if hysteresis loses.

---

## 4. Literature Validation (adversarial)

**UPLOADED SOURCE:** the *Partial fulfilment* review covers 2020–2025 CA well but contains no paper on CA evaluation methodology as such (Bours, Mondal) and none on decision post-processing comparisons — the blind spot that produced the old gap.

**EXTERNAL LITERATURE** — searched specifically for work that would invalidate each clause of the new gap.

### Clause: "evaluated with non-standard stability measures" — **substantially weakened**
A standard exists. Bours et al. argue most "continuous" authentication is really periodic and prescribe **ANGA / ANIA** (Average Number of Genuine / Impostor Actions) with a detailed reporting method — [Performance evaluation of continuous authentication systems](https://consensus.app/papers/details/9a94e638497550739397a806385478dc/?utm_source=claude_desktop) (IET Biometrics, 2015). Mondal et al. extend this with a dynamic trust model and a reporting technique — [A study on continuous authentication using a combination of keystroke and mouse biometrics](https://consensus.app/papers/details/a31eaf282d045b95950c3e01c9ec3fa3/?utm_source=claude_desktop) (Neurocomputing, 2017). Kiyani et al. report ANGA/ANIA for a recurrent confidence model with **two thresholds (alert and final)** — [Continuous User Authentication Featuring Keystroke Dynamics Based on Robust Recurrent Confidence Model](https://consensus.app/papers/details/0d58ae55220951f88239003b114b84a5/?utm_source=claude_desktop) (IEEE Access, 2020).

**INFERENCE:** "transitions per hour during genuine use" is a time-normalised ANGA; "detection latency" is a time-normalised ANIA. Adopt ANGA/ANIA-time, cite Bours, and add only what they do not capture.

### Clause: "almost never assessed for the intrusion-tolerance window" — **weakened**
The window is measured per mechanism: 252 actions (Mondal 2017); ~2.5 min via smoothed HMM — [Continuous Authentication of Smartphones Based on Application Usage](https://consensus.app/papers/details/91a5ffa1b22654819139c9ebe90e68eb/?utm_source=claude_desktop) (IEEE TBIOM, 2018); 1.63 min mean lockout across 1,344 simulated attacks — [Trustworthy interaction model](https://consensus.app/papers/details/efa2960bf8915e08a168b9783383fa75/?utm_source=claude_desktop) (Behaviour & IT, 2025). A 2026 preprint proposes a dual-state transition machine with a three-zone decision model to reduce time-to-detect — [VIGIL](https://consensus.app/papers/details/8d6335cdae475aa0baec7b2e394d4438/?utm_source=claude_desktop) (arXiv, 2026, unreviewed).

**INFERENCE:** survives only in narrowed form — quantified *for individual proposals*, not *across competing mechanisms at matched genuine-lockout rates*.

### Clause: "mechanisms introduced individually, compared only against naive thresholding" — **survives**
Ryu et al.'s systematic review finds "a lack of comparative analysis… [of] fusion models" and that security/usability are "generally not addressed thoroughly" — [Continuous Multimodal Biometric Authentication Schemes: A Systematic Review](https://consensus.app/papers/details/a64624f1282052169df7fcacc527bfe8/?utm_source=claude_desktop) (IEEE Access, 2021). No CA paper found placing moving average, EWMA, majority vote, debounce, dual-threshold, HMM/trust and SPRT side by side on one classifier output.

Most important paper found — *not* in CA: Raghu et al. note that post-processing schemes "have largely been tested individually… failing to fully evaluate their trade-offs between smoothing and latency during dynamic use," then **compare eight schemes** under dynamic class transitions, measuring error rates and **decision-stream volatility** — [Decision-Change Informed Rejection Improves Robustness in Pattern Recognition-Based Myoelectric Control](https://consensus.app/papers/details/67adefa95029585297f2e295ef238ac9/?utm_source=claude_desktop) (IEEE JBHI, 2023).

**INFERENCE:** that paper is this design, executed in prosthetics. It confirms the gap in CA, supplies a validated template and metric, and lets the contribution be framed as *transfer of a validated comparative methodology*.

### Summary
- **Supporting:** Ryu 2021; Raghu 2023; Rasnayaka 2023 (uploaded); Bours 2015 (must be added — supplies the metric standard).
- **Weakening:** Bours 2015 and Mondal 2017 (standard exists); Kiyani 2020 (dual threshold + confidence recurrence + ANGA/ANIA already published); Zhang 2025, Mahbub 2018 (window quantified); VIGIL 2026 (state-machine stabiliser, unreviewed).
- **Unresolved:** whether any mechanism dominates at matched operating points; transfer to sensor-based smartphone CA; dependence on decision cadence.

### GAP VERDICT: **Defensible with refinement**

> *Decision-layer stabilisation in continuous authentication is applied one mechanism at a time: each proposal is compared against instantaneous thresholding, on its own dataset, and its usability–security trade-off is reported only for that mechanism. Although ANGA/ANIA-style reporting exists, no study has placed the common stabilisation policies — windowed smoothing, dwell timers, dual-threshold hysteresis, trust/state models and sequential tests — on a single classifier output under a single protocol and compared them at matched genuine-lockout rates. It is therefore unknown whether the choice of mechanism matters beyond the choice of operating point.*

---

## 5. Can the Existing Dataset Answer the New Gap?

Dataset not uploaded; working from documents plus EXTERNAL knowledge of ExtraSensory's public release — **verify against the files**.

### Two corrections that matter
**Correction 1 — decision cadence (EXTERNAL, verify from timestamps).** ExtraSensory recorded a 20-second sensor window **approximately once per minute**. If so, frame period ≈ 60 s, not 20 s. Consequences: TTT = 3 s even more inoperable; baseline 597 transitions spread over ~1,200 hours ≈ **one transition every two hours**; smallest meaningful dwell = one minute. Check consecutive `timestamp` differences in one user file first.

**Correction 2 — previous location-fingerprinting remark was overstated.** Public feature CSVs do **not** contain absolute latitude/longitude; location features are relative. Fingerprinting risk comes from `audio_naive` MFCCs, `discrete:*` device-state flags, `lf_measurements`, and — importantly — **watch-feature availability** (only some users). After median imputation, "watch present/absent" is a constant per user and a near-perfect identity cue for a subset. Must be ablated.

### Requirement matrix

| New-gap requirement | Evidence required | Available? | Exact variable/feature (EXTERNAL naming — verify) | Existing experiment? | Reanalysis possible? | New data? |
|---|---|---|---|---|---|---|
| Frame-level identity score stream | Classifier probability per frame | **Yes** | GB model output | E1 | Yes | No |
| Temporal ordering | Monotonic timestamps per user | **Yes** | `timestamp` in `<uuid>.features_labels.csv` | E1 | Yes | No |
| User identity | Subject partition | **Yes** | Per-user file (UUID) | E1 | Yes | No |
| Multiple users for paired stats | n ≥ 30 | **Yes** (60) | — | — | Yes | No |
| Genuine-segment stability (ANGA-time) | Constant-identity streams | **Yes** | Any single-user stream | E3/E4 | Yes, after metric fix | No |
| **Impostor detection latency (ANIA-time)** | Known identity-change points | **No, natively** | None — identity never changes within a file | None | **Yes, by construction** (splice) | No |
| Context-matched impostor condition | Activity labels to align segments | **Yes** | `label:SITTING`, `label:LYING_DOWN`, `label:FIX_walking`, `label:PHONE_IN_POCKET`, etc. (sparse) | None | Yes | No |
| Motion-only behavioural stream | Feature-group masks | **Yes** | `raw_acc:*`, `proc_gyro:*`, `raw_magnet:*`, `watch_acceleration:*` vs `audio_naive:*`, `discrete:*`, `lf_measurements:*`, `location*` | Partial | Yes | No |
| Missingness pattern | Per-feature NaN | **Yes** | NaN cells; watch groups | E3 | Yes | No |
| Held-out impostor users | Subject-disjoint split | **Yes** | Partition UUIDs | **No** | Yes | No |
| Decision cadence < 1 min | Sub-minute frames | **No** | — | — | **No** | New data |
| Adversarial mimicry / spoofing | Attack recordings | **No** | — | — | No | New data — out of scope |
| Ground-truth authentication events | Device lock logs | **No** | unverified; not an authentication ground truth anyway | — | No | Not needed |

### Classification: **B — Existing dataset is sufficient with additional analysis**
Not A: the responsiveness axis needs a derived splice benchmark. Not C: nothing the refined gap requires is absent; sub-minute cadence and live adversaries are scope limits, not gap requirements. Not D: no new collection justified.

Condition on "B": the splice must be built in **two attack conditions** (cross-context and context-matched via `label:` columns), or latency numbers measure environment change, not identity change.

---

## 6. Existing Experiment Reuse

| Existing experiment | Original purpose | Relevance to new gap | Reusable directly? | Reanalyse? | Modify? | Replace? | Verdict |
|---|---|---|---|---|---|---|---|
| E1 Classifier selection (LR vs GB) | Pick the engine | High | No | Yes | Per-user protocol, held-out impostors, seed, hyperparameters, calibration | No | **Reusable after modification** |
| E2 RF Gini feature selection | Reduce dimensionality | Medium | No | Yes — inside training fold | Add feature-group ablation | No | **Reusable after modification** |
| E3 Baseline stability (P>0.5) | Quantify ping-pong | High — the null arm | No | Yes — ANGA-time; recount | — | — | **Reusable after reanalysis** |
| E4 Hysteresis layer | Demonstrate stabilisation | High — one arm | No | Yes — recompute post-mechanism error rates | TTT in frames; margin reported; component ablation | No | **Reusable after modification** |
| E5 Missingness/imbalance analysis | Big Data coursework | Medium | Yes (descriptive) | — | — | — | **Supporting evidence** |
| E6 Ambient-noise/magnetometer validity | S1–S3 RQ | None | — | — | — | Yes | **No longer relevant** — remove claim |
| E7 Within-subjects human study (PDF) | Methodological critique | None; contradicts record | — | — | — | Yes | **No longer relevant** — remove or rewrite as hypothetical |

---

## 7. ML Experiment Audit (from reports only)

| Aspect | Reported | Verifiable? | Discrepancy / risk |
|---|---|---|---|
| Preprocessing | Median imputation on 101 features; separately "Mean Imputation" | No | Two imputers named for one step. Imputation-before-split not stated. Median-imputed watch features become identity constants. |
| Feature engineering | SMV + moments; RF Gini top 52/53 of 103 | No | 225→2 dropped→"101" fails; 101/103/52/53 inconsistent. RF split not stated → selection leakage possible. |
| Split | Per-user chronological 60/20/20 | Partially | Correct instinct. Impostor users shared across train/test → not subject-independent. |
| Subject-independent evaluation | Not performed | — | Model can memorise impostor identities. |
| Temporal leakage | Chronological split mitigates | Partially | SMOTE interpolates across time-ordered rows. |
| Label leakage | — | No | Legitimate-class definition unstated. |
| Class imbalance | 1:30.5; SMOTE on training | Partially | Pipeline order unverified. |
| Cross-validation | None | — | Single split, single run. |
| Hyperparameters | LR `C=1.0` L2; GB none | No | GB unreproducible. |
| Threshold | P>0.5 | — | Default. Post-SMOTE probabilities calibrated to 1:1 prior; margin on an uncalibrated scale. |
| Hysteresis parameters | Margin unstated; TTT 3 s / 2–5 s / 70-60-65 | No | Contradictory; selection procedure absent; validation split unused. **Test-set influence cannot be excluded.** |
| Metric calculation | Acc/Prec/Rec/F1/FAR/FRR/AUC/EER | Partially | **Verified:** FAR 0.53%, FRR 7.09%, 1:30.36 → precision 0.852, accuracy 99.25%. **Implausible:** identical post-hysteresis metrics (A). **Impossible:** 567 episodes from 597 transitions (B). **Dependent:** SI ↔ transitions (C). |
| Reproducibility | — | No | No seeds, code, or feature list. |

**Explicit report-vs-experiment discrepancies:** (1) Table 5 classification columns cannot have been computed on the hysteresis output; (2) TTT as reported cannot have operated at the data's cadence; (3) "≈5 transitions per user" ≠ 597/60; (4) two imputation methods for one operation; (5) feature-count chain does not add up.

---

## 8. Classification vs. Authentication

| Construct | Demonstrated? | Basis |
|---|---|---|
| Binary classification of a pooled label | **Yes** | Confusion matrix internally consistent. |
| Identity recognition (closed-set) | **Weakly** | Only if positive class is one user; unstated. |
| User verification (open-set, per-enrolee, unseen impostors) | **No** | No per-user models, no held-out impostors, no per-user EER. |
| Continuous authentication | **No** | No detection latency, no ANGA/ANIA, no sequential evaluation on identity changes. |
| Behavioural consistency | **Partially** | Within-user temporal generalisation of *something*; not shown to be behaviour rather than device/context. |
| Security against impostors | **No** | Zero-effort impostors only, seen in training. |

**Defensible terminology now:** *frame-level user classification from contextual sensor features, with a decision-layer stability analysis.* After E1 redo: *user verification.* After splice benchmark with ANGA/ANIA-time: *continuous authentication decision evaluation.* Earn each word.

---

## 9. Re-evaluating Hysteresis

| Option | Literature fit | Dataset fit | Method strength | Novelty | Feasibility | Contribution | MSc fit | Score |
|---|---|---|---|---|---|---|---|---|
| **A — central contribution** | Poor (Kiyani 2020, Mondal 2017, VIGIL) | Poor: task rewards any damping | Weak: unfalsifiable | Low: Schmitt trigger + debounce | High | Low | Poor | **3/10** |
| **B — one component of a broader framework** | Moderate | Moderate | Moderate; scope creep risk | Low–moderate | Moderate | Moderate | Risky | **5/10** |
| **C — one comparative technique among several** | **Strong** (Ryu 2021 gap; Raghu 2023 template) | **Strong** | **Strong**: falsifiable, matched-point design | Moderate: comparison new in CA | High | Moderate–high, independent of winner | **Excellent** | **8/10** |
| **D — reduce/remove** | — | — | — | — | — | Loses narrative and only non-trivial implemented mechanism | Poor | **3/10** |

**Recommendation: Option C.** Hysteresis remains the *handover-derived candidate* — the only asymmetric (lock-easy, unlock-hard) policy in the set — but becomes the hypothesis under test, not the contribution.

---

## 10. Simpler Alternatives — the comparison set

| Mechanism | Params | Why it must be included |
|---|---|---|
| Instantaneous threshold | 1 | The null |
| Moving average, window *k* | 1 | Simplest smoother; if it matches hysteresis, the telecom framing adds nothing |
| EWMA | 1 | Memory without storage; cheapest deployable |
| Majority vote over *k* | 1 | Robust to single-frame spikes |
| Debounce (dwell only) | 1 | **Is** the TTT component alone |
| Dual threshold (margin only) | 2 | **Is** the margin component alone |
| Hysteresis (margin + dwell) | 3 | The candidate |
| Trust model (Mondal/Kiyani-style, alert/final thresholds) | 2–3 | The published CA standard for this problem |
| SPRT | 2 (α, β) | Provably optimal expected time-to-decision at fixed errors; the principled ceiling |

Two-state HMM optional. **Decisive rule:** compare at **matched genuine-lockout rate**, never at default settings.

---

## 11. What the Data Can Prove

### CAN demonstrate
- Frame-level separability with the stated error rates.
- Per-user verification with unseen impostors (after E1 redo).
- Genuine-stream transition rates (ANGA-time) per mechanism with per-user CIs.
- Impostor detection latency (ANIA-time) on **spliced** sequences, two attack conditions.
- Whether mechanism choice matters beyond operating point, at ~1-min cadence, on this population.
- Whether hysteresis's effect comes from margin, dwell, or both.
- How much separability is motion-behavioural vs. environmental/device.

### MAY support but cannot conclusively demonstrate
- Generalisation to other populations/devices.
- Deployability (no on-device cost, no user friction measured).
- That spliced latency approximates real hijack latency.
- Causal attribution to mechanism *structure* rather than parameter count.

### CANNOT demonstrate
- Anything about sub-minute cadence.
- Security against mimicry, replay, spoofing.
- Real user behaviour under the mechanism.
- "Authentication" until §8's conditions are met.
- That the ping-pong problem is severe in the wild — own baseline suggests it is mild at this cadence.

---

## 12. Threats to Validity (pivoted design)

**Internal.** (a) Cross-context splices detect environment → context-matched condition. (b) Parameter tuning on test → validation-only, pre-registered. (c) Degenerate constancy → splice benchmark penalises never-switching. (d) Imputation-constant fingerprints → feature-group ablation; impute within folds. (e) Impostor memorisation → subject-disjoint impostors.

**External.** 60 students; one device generation; ~1-min cadence; one classifier family. Report per-user variance; test aggregated cadences (upward only). State the rest as scope.

**Construct.** ANGA-time and ANIA-time measure the constructs of interest; drop "stability index." Define "ping-pong" once (sign-alternating transitions within a fixed window) and report alongside, not instead of, ANGA-time.

**Statistical conclusion.** Paired per-user Wilcoxon across 60 users at each matched point; bootstrap CIs; Holm correction; effect sizes.

**Ecological.** Weak — offline, coarse cadence, no device, no humans. Frame as *a decision-layer evaluation protocol demonstrated on naturalistic data*.

---

## 13. Minimum Additional Experiments

### 1 — ESSENTIAL: Sound per-user verification baseline
- **RQ:** Frame-level verification performance under a subject-disjoint protocol?
- **Objective:** replace E1 with an evaluation whose numbers can be called verification.
- **Variables:** DV — per-user EER, FAR, FRR.
- **Procedure:** for each of 60 users: train genuine-vs-impostor with impostors from a training user subset; test on the user's chronological tail vs. **held-out** impostor users. Imputation, feature selection, SMOTE, calibration all inside the training fold. Fixed seed; GB hyperparameters reported.
- **Metrics:** EER mean ± sd; Brier score; reliability diagram.
- **Stats:** distribution across users; compare to Kaur et al. 2026 on the same dataset.
- **Threats:** low-data users — per-user n floor, reported.

### 2 — ESSENTIAL: Spliced identity-transition benchmark + mechanism bake-off
- **RQ:** Does mechanism choice matter beyond operating-point choice?
- **Variables:** IV — mechanism × parameters × attack condition; DV — ANGA-time, ANIA-time, miss rate, recovery time.
- **Baseline:** instantaneous threshold. **Intervention:** each mechanism in §10.
- **Procedure:** construct sequences; validation-set sweep; matched-lockout comparison on test sequences.
- **Stats:** paired Wilcoxon across users at each matched point; Holm; bootstrap CIs.
- **Threats:** splice realism; labels used only for alignment, never as features.

### 3 — HIGH VALUE: Component ablation and sensitivity
- Margin-only, dwell-only, both; full grid; heatmaps of ANGA-time and ANIA-time. Broad plateau vs. knife-edge.

### 4 — OPTIONAL: Feature-group ablation (behaviour vs. environment)
- motion-only → +watch → +discrete/lf → +audio → all; rerun Exp 1–2 at each stage.

### 5 — FUTURE WORK: Cadence transfer
- Aggregate to 2- and 5-min cadences; repeat top three mechanisms. A sub-second dataset (e.g., HMOG) is beyond MSc scope — name it.

---

## 14. The Killer Experiment

**Matched-lockout comparison of stabilisation mechanisms on spliced identity transitions.**

**Construction.** For each genuine user *g* and held-out impostor *i*: take *g*'s test-period stream; insert a contiguous block of *i*'s frames of length *L* ∈ {3, 10, 30, 60} min at a random index; record switch and return indices. Condition **X** (cross-context): unconstrained. Condition **M** (matched): *i*'s block drawn from frames sharing *g*'s dominant activity label at the splice point. ≥10 sequences per user per condition. Labels used for alignment only.

**Procedure.** Fixed classifier from Exp 1 → probability stream. Sweep each mechanism on validation sequences. Select the setting whose **genuine-segment lockout rate** equals a common target (e.g., one false lock per 8 h); hold fixed; measure on test sequences: median and P90 **detection latency**, **miss rate** at *L*, **recovery time**.

**Primary output.** One figure per condition: ANGA-time (x) vs. median ANIA-time (y), one curve per mechanism; plus one table at the matched point.

**Pre-registered outcomes**
- **Supports:** at matched ANGA-time, hysteresis's ANIA-time is lower than every single-parameter smoother in both conditions; survives paired Wilcoxon (Holm); ablation shows the advantage depends on asymmetry (margin + dwell jointly).
- **Weakens:** advantage only in condition X, or only in a narrow region, or fully reproduced by dual-threshold alone (dwell inert).
- **Falsifies:** EWMA or majority vote matches hysteresis within CIs (mechanism doesn't matter), **or** trust model / SPRT dominates across the range. Thesis still stands as a negative comparative result with a validated protocol; the handover-inspired claim is dropped.

**Why not rigged:** matched-point rule removes "damp harder"; condition M removes "detect the room"; SPRT provides a principled ceiling hysteresis has no structural reason to beat.

---

## 15. Three Strategies

| Dimension | Existing direction | Full pivot | Hybrid |
|---|---:|---:|---:|
| Gap strength | 2 | 7 | 7 |
| Dataset compatibility | 4 | 7 | 7 |
| Existing work reusable | 9 | 5 | 8 |
| New data required | 10 | 10 | 10 |
| New experiments (fewer = higher) | 8 | 5 | 5 |
| Methodological rigour | 2 | 8 | 8 |
| Novelty | 3 | 6 | 6 |
| MSc feasibility | 8 | 6 | 7 |
| Research risk (lower = higher) | 2 | 6 | 7 |
| Contribution potential | 3 | 7 | 7 |
| **Total** | **41** | **67** | **72** |

Full pivot vs. hybrid differ only in whether the handover story survives. Dropping it costs a coherent introduction, an implemented mechanism with a distinctive property, and continuity with submitted coursework; it buys nothing methodologically.

---

## 16. Decision

# PIVOT BUT PRESERVE THE EXISTING FRAMEWORK

**Why.** Old gap refuted; old design cannot fail; old headline results internally inconsistent. Refined gap survives an adversarial search, is testable with existing data, reachable in weeks of mostly post-processing work. The handover analogy is a legitimate *source* of one candidate — keep it as motivation, not as the lead.

**Existing research:** problem statement, motivation, literature review, dataset critique survive. Handover framing moves from contribution to motivation/hypothesis. Claims about ambient noise/magnetometer, the human study, "complete elimination," "no accuracy impact," "reusable framework" are withdrawn.

**Dataset:** retained; gains a splice benchmark and a feature-group taxonomy.

**Experiments retained:** E1 (per-user), E2 (inside folds), E3 (null arm), E4 (one arm + ablation), E5 (descriptive).

**Reanalysis:** post-mechanism error rates; ANGA-time; validation-only selection.

**New:** Exp 1–3; Exp 4 if time.

**Final contribution:** a validated comparative protocol for decision-layer stabilisation in continuous authentication, transferred from decision-stream post-processing methodology, with first evidence on a naturalistic 60-user dataset about whether mechanism choice matters at matched operating points — including a handover-derived hysteresis policy as one candidate.

---

## 17. Research Architecture

**Working title:** *Does the Mechanism Matter? A Matched-Operating-Point Comparison of Decision-Layer Stabilisation Policies for Continuous Smartphone Authentication*

**Problem.** CA is evaluated by frame-level accuracy, blind to temporal decision behaviour; stabilisers are added heuristically and their usability–security cost reported one mechanism at a time.

**Gap.** As refined in §4.

**Aim.** Determine whether the choice of stabilisation mechanism affects the genuine-lockout / impostor-detection trade-off beyond the choice of operating point.

**Objectives.** (1) Subject-disjoint per-user verification baseline. (2) Spliced identity-transition benchmark, two conditions. (3) Eight stabilisation policies as post-processors over one probability stream. (4) Matched-lockout comparison via ANGA/ANIA-time. (5) Ablate the handover-derived policy. (6) Per-user statistics with pre-registered falsification criteria.

**RQs.** RQ1: At matched genuine-lockout rate, do mechanisms differ in impostor-detection latency? RQ2: Does dual-threshold + dwell outperform single-parameter smoothers and published trust/sequential models? RQ3: Is any advantage attributable to asymmetry? RQ4: Do findings differ between cross-context and context-matched impostors?

**Hypotheses.** H1: mechanisms differ (H0: ANIA-time distributions coincide at matched ANGA-time). H2: hysteresis < single-parameter smoothers. H3: advantage disappears under margin-only or dwell-only. H4: latencies longer under context-matched impostors.

**Conceptual framework.** CA decision as a sequential decision process over a noisy score; stabilisation as a policy trading lockout rate for detection delay; handover hysteresis as one policy class with asymmetric transition costs; Bours ANGA/ANIA as evaluation construct; Raghu et al. as methodological template.

**Dataset / variables.** ExtraSensory; per §5.

**Methodology.** Computational experiment; pre-registered analysis plan; documented research-evolution history.

**Experimental design.** §13 Exp 1–3 (+4).

**Baselines.** Instantaneous threshold; moving average; EWMA; majority vote; dwell-only; margin-only; trust model; SPRT.

**Metrics.** Per-user EER; ANGA-time; ANIA-time (median, P90); miss rate; recovery time; ping-pong rate (defined once); calibration.

**Statistics.** Paired Wilcoxon across users; Holm; bootstrap CIs; effect sizes.

**Limitations.** ~1-min cadence; students; one classifier; zero-effort impostors; splice realism; offline.

**Future work.** Sub-second dataset; on-device cost; adaptive parameters per context.

**Chain check — broken links**
- GAP → RQ: intact.
- RQ → OBJECTIVE: intact.
- OBJECTIVE → DATA: **weak at impostor detection** until the splice benchmark is built and defended.
- DATA → METHOD: **broken at cadence** — state the ~1-min floor; TTT in frames.
- METHOD → EXPERIMENT: intact once parameters are validation-selected.
- EXPERIMENT → METRIC: **broken today** (undefined SI, impossible episodes) — fixed by ANGA/ANIA-time.
- METRIC → RESULT: **broken today** (Finding A) — fixed by recomputing.
- RESULT → CONTRIBUTION: intact only if the contribution is the *comparison*, not the *winner*.

---

## 18. Paper Roadmap — evidence each section needs

| Section | Evidence required |
|---|---|
| Title / Abstract | Final ranking from Exp 2; one matched-point table |
| Introduction | Existing motivation; baseline reframed as "mild but nonzero even at coarse cadence" |
| Problem statement | Existing; add Bours's periodic-vs-continuous distinction |
| Research gap | Refined gap; Ryu 2021, Raghu 2023, Bours 2015, Mondal 2017, Kiyani 2020 |
| Aim / Objectives / RQs / Hypotheses | §17; pre-registered before Exp 2 |
| Justification | Ryu 2021 "lack of comparative analysis"; deployability |
| Literature review | Existing table + new subsection on decision-layer post-processing in CA and comparative post-processing studies in adjacent fields |
| Conceptual framework | Policy-space taxonomy (§10) |
| Methodology | Research-evolution statement; pre-registration; protocol |
| Dataset | Cadence corrected from timestamps; feature-group taxonomy; label sparsity |
| Experimental design | Exp 1–3 specs; splice rules; matched-point rule |
| Results | Per-user EER; ANGA/ANIA curves ×2 conditions; matched-point table; ablation heatmaps; stats |
| Discussion | Interpretation against pre-registered outcomes |
| Threats to validity | §12 |
| Limitations | §11 CANNOT list |
| Conclusion | Answer RQ1 directly, including if null |
| References | Resolve Vaizman duplicate; remove or find "Khan 2020"; AI tools → declaration |

---

## 19. Examiner Attack (proposed design)

1. **"Bours proposed ANGA/ANIA in 2015. What is new?"** — Adopt them; claim the *comparison*, not the metrics.
2. **"Kiyani (2020) already published a two-threshold recurrent confidence model with ANGA/ANIA. How is hysteresis different?"** — Include as an arm; show whether dwell adds anything.
3. **"Spliced identity changes aren't real hijacks."** — Cite precedent (Garabato 2022, Mondal 2018, Zhang 2025); two conditions; state the abrupt-transfer assumption.
4. **"A spliced impostor changes room, Wi-Fi and ambience at once. Aren't you detecting the room?"** — Condition M + motion-only ablation.
5. **"Frames are a minute apart; deployed CA decides every second."** — State as scope; aggregate-cadence sensitivity; name as principal external-validity threat.
6. **"Who is the enrolee, and were impostors seen in training?"** — Exp 1.
7. **"Where were mechanism parameters chosen?"** — Validation-only, pre-registered, full sweep reported.
8. **"Why match on lockout rate rather than latency?"** — Report both projections; lockout is the constraint operators fix.
9. **"SPRT is optimal. Why would anything beat it?"** — It is the ceiling; report honestly either way.
10. **"Your February results claimed zero oscillations and unchanged accuracy. What happened?"** — Research-evolution statement; corrected figures.
11. **"SMOTE then thresholding probabilities — calibrated?"** — Calibration on validation; reliability diagram.
12. **"Median-imputed watch features identify watch owners. Leakage?"** — Feature-group ablation; impute within folds; report watch availability.
13. **"How many comparisons?"** — Holm; pre-specified primary comparison.
14. **"If the curves coincide, what is your contribution?"** — Validated protocol + a null that tells practitioners to pick the cheapest mechanism.
15. **"Your earlier document describes a participant study. Where is it?"** — Remove before submission; if retained, label as a hypothetical design exercise.

---

## 20. Final Verdict

| Dimension | Today | Projected (Exp 1–3 done honestly) |
|---|---:|---:|
| Overall research quality | 4/10 | 7/10 |
| Research maturity | Stage 4 (prototype) | Stage 5–6 |
| Gap strength | 3/10 (original) | **7/10 (refined)** |
| Methodological strength | 3/10 | 8/10 |
| Dataset suitability | **7/10** for refined gap (4/10 for original) | — |
| Evidence strength | 2/10 | — |
| Contribution strength | 3/10 | 7/10 |
| Novelty | 3/10 (mechanism) / 6/10 (comparison in CA) | — |
| MSc dissertation potential | — | 8/10 (hybrid path) |
| Publication potential | — | 5/10 (workshop / biometrics or usable-security venue) |

> **CAN I USE MY EXISTING DATASET TO ADDRESS THE REFORMULATED GAP?**

### YES — but additional analysis/experiments are required
A derived splice benchmark in two attack conditions; a subject-disjoint per-user rerun of the classifier; the mechanism set as post-processors; ANGA/ANIA-time in place of current stability metrics. No new participants, sensors, or collection.

### TOP 5 THINGS TO CHANGE
1. The gap statement — adopt the refined version; cite Bours, Mondal, Kiyani, Ryu, Raghu.
2. The contribution — "does the mechanism matter, at matched operating points."
3. The metrics — ANGA-time / ANIA-time replace transitions, episodes, stability index.
4. The evaluation protocol — per-user, subject-disjoint impostors, validation-only selection, all steps inside folds.
5. The document set — withdraw the human study, sensor-validity findings, identical-accuracy table, uncited citation.

### TOP 5 THINGS TO PRESERVE
1. Problem statement and motivation.
2. The 2020–2025 literature table.
3. ExtraSensory and the dataset critique.
4. The GB pipeline as the fixed engine (after repair).
5. The handover-derived hysteresis mechanism — as one candidate.

### TOP 5 RISKS
1. Cadence ≈ 1 min and baseline instability so mild the genuine-stream comparison is under-powered — make the splice benchmark primary.
2. Context-matched splices hard to build for low-data users (sparse labels) — per-user minimum; report coverage.
3. Feature-group ablation shows the 99% is mostly environment — a finding, but plan for it.
4. Scope creep toward a "framework" — hold at eight mechanisms.
5. Time — weeks, not days, and it is September.

### SINGLE MOST IMPORTANT NEXT STEP
Open one ExtraSensory user file and compute the distribution of consecutive `timestamp` differences. TTT in frames, the meaning of the baseline, splice block lengths, and the cadence limitation all depend on that one number, and no document states it correctly. Ten minutes; do it first.
