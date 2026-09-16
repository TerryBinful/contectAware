# Research State Audit — Independent Verification (15 September 2026)

This audit was produced independently by cross-reading every primary file in the project and by running my own adversarial literature searches. It does not simply restate the pre-existing `MSc_Pivot_Audit.md` — where our conclusions agree, I say so and give my own evidence; where I found nuances, gaps, or corrections, I flag them explicitly. No dataset files, notebooks, or output logs exist in this project — every dataset/experiment claim below is the author's own narrative report, not independently inspectable data, unless marked otherwise.

Legend: **[E]** Evidence · **[I]** Interpretation (my reasoning) · **[R]** Recommendation. Primary > Secondary > Inference, per project standing instructions.

---

## 1. What the research currently is

**[E]** Two documents describe two different "current" states, dated six months apart:
- `Partial_fulfilment.docx` (Feb 2026, ~4,100 words) is a completed empirical write-up: "Unified Telecom-Inspired Stability Metrics: Continuous Authentication using Hysteresis-Based Decision Logic." It claims a gradient-boosting classifier on ExtraSensory reaches 99.26% accuracy / FRR 7.09% / FAR 0.53%, that raw decisions oscillate 597 times with 567 "oscillation episodes" (Stability Index 0.9502), and that adding a hysteresis layer "eliminates oscillation episodes entirely (567→0)" while leaving classification metrics unchanged (Δ=0.0% on every metric in Table 5).
- The five scaffolding files (`01`–`04`, `06`) dated around the current session describe a *not-yet-executed* pivot: a matched-operating-point comparison of nine decision-layer stabilization mechanisms (instantaneous threshold, moving average, EWMA, majority vote, debounce, margin/dual-threshold, hysteresis, trust model, SPRT/HMM) on identity-transition sequences spliced from ExtraSensory, with a pre-registration template whose RQs/hypotheses/falsification criteria are still unfilled.

**[I]** The "current" research is therefore not one thing but two coexisting, partly contradictory layers: a completed but internally inconsistent single-mechanism study (Feb 2026), and an unexecuted but methodologically sounder comparative plan (Sept 2026). I independently re-derived the arithmetic problem in Table 5 of `Partial_fulfilment.docx`: 597 raw transitions cannot mathematically produce 567 "episodes" under any reasonable episode definition (an episode requires ≥2 transitions in and 1 out, so 567 episodes need ≥1,701 transitions at minimum) — this is a genuine internal contradiction in the primary document, not a claim I am taking on trust from `Review_1_Key_Findings.md`; I re-checked the numbers myself against the source table.

**[R]** Treat the Sept 2026 comparative plan as the live research; treat the Feb 2026 paper as a historical artifact whose *numbers* cannot be reused until recomputed, but whose *pipeline* (GB classifier, feature set, ExtraSensory usage) can be reused as a starting point.

---

## 2. How the research has evolved

I reconstructed this by reading the documents myself (not by trusting the prior audit's table), in the order their internal content implies:

| Stage | Document | Focus | What changed |
|---|---|---|---|
| S1 | `Extended_Abstract.docx` | Methodological critique of ambient noise + magnetometer as auth signals | Original proposed RQ; never tested |
| S2 | `Abstract.docx` | RQ fully replaced by hysteresis/transition-logic template | Sensor-validity RQ silently dropped, not resolved |
| S3 | `CSCD601_Rewritten_22427613.docx` | Both RQs coexist (ambient sensors AND hysteresis); ExtraSensory named | H1 (ambient data supports CA) stated but never tested; H2 (hysteresis reduces instability) stated |
| S4 (referenced only) | Excluded PDF per `README.md` | Within-subjects human study, on-device, no audio/GPS | Not present in this project; contents known only second-hand; contradicts S5–S6's offline/ExtraSensory approach |
| S5 | `22427613_-_First_Semester_Exams.docx`, `Semester_Exams_Polished_Final.docx` | Big Data coursework: dataset justification, feature engineering, GB pipeline build | ExtraSensory + GB engine constructed for a Big Data assignment, prior to the hysteresis RQ being finalised |
| S6 | `Partial_fulfilment.docx` (Feb 2026) | Hysteresis-on-decisions empirical paper | Absence-based novelty claim ("field hasn't explored hysteresis") introduced; internally inconsistent results |
| S7 | `Continuous_Authentication_Research_Paper_Draft.docx` | Skeleton draft, placeholders unfilled | No new content |
| S8 | `MSc_Pivot_Audit.md` + `01`–`04`/`06` scaffolding (Sept 2026) | Reformulated gap: comparative, matched-operating-point mechanism bake-off | Proposes dropping absence claim, adding genuine comparison |

**[I]** S1→S2 is a genuine scope narrowing (defensible exploratory refinement — the ambient-sensor RQ was abandoned, not disguised as having been tested). S3 is a transitional stage where both RQs are asserted without either being resolved — this is the point where the project's coherence chain (problem→gap→RQ→data→method) first breaks, because H1 is stated as a hypothesis and never subjected to any experiment in any later document. S5→S6 is the higher-risk transition: the dataset and ML pipeline were built for a Big Data *coursework* deliverable (feature engineering, missingness, imbalance) before the authentication-specific hysteresis hypothesis existed, and were then repurposed as "the CA authentication engine" in S6 without an explicit argument for why a classification pipeline built for a different assignment is fit for an *authentication* (not activity-classification) research question. This is a scope-fit assumption, not HARKing in the strict sense (the hysteresis hypothesis predates the S6 write-up by only weeks), but it needs to be argued, not inherited silently, in any pivot.

**[R]** In the next document, add one explicit paragraph justifying why the ExtraSensory + GB pipeline (originally a Big Data classification exercise) is valid instrumentation for a continuous-authentication decision-stability study. Do not let this justification be implicit.

---

## 3. Original research gap

**[E]** Verbatim, `Partial_fulfilment.docx` Problem Statement: *"While the telecommunications industry solved analogous stability problems decades ago through hysteresis-based handover protocols, the behavioural biometrics community has not systematically explored these techniques."*

**[E — my own verification, not from the prior audit]** I independently searched for and confirmed the existence of published counter-examples to this absence claim:
- Mondal & Bours (2017), *Neurocomputing* — a continuous authentication trust-model that explicitly persists/decays trust over time rather than reacting to every instantaneous classifier score (a temporal-persistence mechanism functionally adjacent to hysteresis). Confirmed to exist via independent search ([SciSpace record](https://scispace.com/papers/a-study-on-continuous-authentication-using-a-combination-of-4dksurb05q)).
- Kiyani et al. (2020), *IEEE Access* — evaluates ANGA/ANIA-style dual-threshold (alert/final) decision logic with a recurrent confidence model, which is structurally a margin/dual-threshold mechanism, one of the nine mechanisms in the student's own `03_mechanism_reference.md`. Confirmed to exist via [MDX repository thesis citing it](https://repository.mdx.ac.uk/download/b91919d0945d463dfcae9373031d407e40219b260bcb4f90491f1a3b6031ab8a/4707753/ATKiyani%20thesis%20EMBARGO.pdf).

**[I]** The literal claim "the field has not explored [temporal/margin-based decision stabilization]" is false: at least two mechanism-classes in the student's own mechanism-reference list already have published precedent in continuous authentication specifically (not just in telecom or myoelectric control). The absence-based novelty argument as stated in `Partial_fulfilment.docx` does not survive scrutiny.

**Verdict: WEAK / falsified as stated.** This is not new — it matches the prior audit's conclusion — but I want to be explicit that I reached it through my own independent literature check, not by trusting the citation list already in the project.

---

## 4. The recently reformulated gap

**[E]** The reformulated gap appears only in `MSc_Pivot_Audit.md` (the pre-existing review); it does not yet appear worded in the student's own primary drafts. Restated from that document: *no published study performs a controlled, matched-operating-point comparison of multiple decision-layer stabilization mechanisms (moving average, EWMA, majority vote, debounce, margin/dual-threshold, hysteresis, trust models, SPRT) against each other within continuous/behavioural authentication, evaluated on identity-transition sequences rather than steady-state accuracy alone.*

**[I]** This is a narrower, more defensible claim than the original: it does not assert absence of *any* temporal mechanism (falsified above), but absence of a *systematic head-to-head comparison* of many mechanisms at matched false-accept/lockout rates, specifically in CA. That is a materially different and much harder claim to falsify with a single counter-paper.

---

## 5. Is the reformulated gap genuinely supported by current literature? (Independent adversarial search)

I ran my own web/scholar searches — not a re-read of `06_literature_to_add.md` — specifically hunting for a paper that would kill this gap.

**[E] Papers verified to exist and checked for content:**

| Paper | Verified? | What it actually shows |
|---|---|---|
| Raghu, MacIsaac & Scheme (2023), *IEEE JBHI* 27(12):6051–6061, [doi:10.1109/JBHI.2023.3316599](https://doi.org/10.1109/JBHI.2023.3316599) ([arXiv:2409.14169](https://arxiv.org/abs/2409.14169)) | Confirmed real, peer-reviewed | Compares **8** existing post-processing/decision-stream schemes (majority vote, Bayesian fusion, onset locking, outlier detection, confidence-based rejection, confidence scaling, prior adjustment, adaptive windowing) plus 2 new ones, on decision-stream volatility and error rate — in **myoelectric prosthesis control**, not authentication. This is genuinely the strongest available methodological template for the reformulated gap's comparative design, but it is a transfer argument (method borrowed from an adjacent domain), not existing CA precedent. |
| Ryu & Yeom, *Continuous Multimodal Biometric Authentication Schemes: A Systematic Review* | Confirmed real ([SciSpace PDF](https://scispace.com/pdf/continuous-multimodal-biometric-authentication-schemes-a-1vjrr8x4cg.pdf)) | Reports a lack of comparative analysis, but of **fusion levels** (feature/score/decision-level fusion) and biometric-type combinations — **not** of decision-layer temporal-stabilization mechanisms. This is a real but *narrower* match than the prior audit implied; cite it for "the field under-compares design choices" generally, not as direct precedent for the specific stabilization-mechanism gap. |
| Mondal & Bours (2017), *Neurocomputing* | Confirmed real | Single trust-model mechanism, no comparison to alternatives. |
| Kiyani et al. (2020), *IEEE Access* | Confirmed real | Single dual-threshold mechanism, no comparison to alternatives. |
| Zhang et al. (2025), Behaviour & Information Technology, dynamic trust model, mouse dynamics ([tandfonline.com](https://www.tandfonline.com/doi/full/10.1080/0144929X.2024.2321933)) | Confirmed real, fetched and read | Single trust-model mechanism (HHT + LSBT features), 32 participants, 1,344 simulated attacks all detected, average lockout 1.63 min. **No comparison** to hysteresis, moving average, EWMA, majority vote, or SPRT. |
| Kaur et al. (2025/26), *IEEE Access*, CNN-LightGBM, "Novel Explainable CNN-LightGBM Model for Smartphone Continuous Authentication" ([IEEE Xplore doc 11426908](https://ieeexplore.ieee.org/document/11426908/)) | Confirmed real (DOI/Xplore record exists) | Exact accuracy/EER numbers **not independently confirmed** by me (page content did not render extractable metrics) — treat any specific number attributed to this paper as **EVIDENCE NOT ESTABLISHED** until directly verified from the PDF. |

**[E] Deliberate "kill-the-gap" search of 2024–2026 literature** (queries: comparative decision-stabilization mechanisms in continuous authentication; hysteresis vs. moving average in CA; matched-operating-point stabilization comparisons; recent systematic reviews):
- [JISEM 2025 systematic literature review on CA](https://jisem-journal.com/index.php/journal/article/view/12787) — no stabilization-mechanism comparison; does not name this as a gap.
- [MDPI Sensors 25(18):5711 (2025), "Continuous Authentication in Resource-Constrained ..."](https://www.mdpi.com/1424-8220/25/18/5711) — proposes **one** mechanism (EWMA with adaptive thresholding) against a fixed-threshold ablation, not a multi-mechanism bake-off.
- No 2024–2026 paper was found that performs the specific matched-operating-point, multi-mechanism comparison the reformulated gap identifies as missing, in a continuous/behavioural-authentication context.

**[I]** The reformulated gap survives my adversarial search, but on a narrower basis than the project's existing literature file implies: the Ryu citation supports a general "field under-compares design choices" pattern, not the specific stabilization-mechanism claim; the Raghu paper is the best template but is a cross-domain transfer, not CA precedent. I could not find a paper that already closes the gap, despite deliberately searching for one.

**Verdict: DEFENSIBLE WITH REFINEMENT** (independently confirmed) — not Strong, because dual-threshold and trust-model mechanisms already exist in published CA work so any "novel metric/mechanism" framing must be dropped; not Weak, because the specific comparative, matched-operating-point study design was not found anywhere in my search.

---

## 6. Can the existing dataset answer the reformulated gap?

**[E]** No ExtraSensory CSV files, notebooks, or output logs exist anywhere in this project (confirmed directly from the file listing — 17 files, all `.md`/`.py`/`.docx`, zero data files). `05_cadence_check.py` exists but has never been run against real data inside this project (no output file present).

**[E — externally verified, since no primary data exists to check]** I fetched the official ExtraSensory documentation directly (not the student's description of it): the dataset's mobile app performs **a 20-second sensor recording session automatically once per minute**; examples are "typically" at 1-minute intervals but not guaranteed continuous (gaps can occur) ([extrasensory.ucsd.edu](http://extrasensory.ucsd.edu/)). This **independently confirms** the prior audit's "Correction 1": the frame period is ≈60 seconds, not 20 seconds as `Partial_fulfilment.docx` and the coursework documents state. A TTT=3s claim is therefore inoperable at native cadence (3 seconds is smaller than one frame) regardless of which document's number is used.

**[E]** Because the raw dataset itself was never uploaded to this project, none of the following are independently verifiable and remain author self-report only: exact per-user timestamp gaps, the true feature list surviving to 101/52/53 columns, watch-vs-phone-only sensor availability per user, or label sparsity patterns. **EVIDENCE NOT ESTABLISHED IN THE PROJECT MATERIALS** for all dataset-internals claims beyond what the official ExtraSensory documentation states in general.

**[I]** The externally-confirmed dataset properties (per-user structure, timestamped minute-level examples, sparse multi-label activity annotations, 60 users) are structurally compatible with the splice-benchmark design in `02_splice_benchmark_spec.md` (which needs identity-labeled sequences with timestamps to construct cross-context/context-matched transition blocks). This makes a conditional "yes" plausible, but it is conditional on the ~60-second cadence being compatible with the block lengths (L ∈ {3,10,30,60} minutes) and TTT values actually planned — at 60s/frame, TTT=3s must be redefined (e.g., in frames, not seconds) before any pre-registration is frozen.

**Verdict: CONDITIONALLY YES**, matching the prior audit's "B — sufficient with additional analysis" classification, but I flag this as *provisional*, not confirmed: the single most decisive unexecuted step in this entire project is running `05_cadence_check.py` against the student's actual local ExtraSensory files, because every quantitative claim above about the "real" dataset (as opposed to the officially documented general dataset) still rests on inference from external documentation, not on this project's own primary data.

---

## 7–8. Which experiments remain useful, and which can be reanalysed

**[E]** Re-reading `Partial_fulfilment.docx` myself, Table 5 shows GB Accuracy/FAR/FRR identical to Table 3's Accuracy/FAR/FRR (99.26%/0.53%/7.09%) both before and after the hysteresis layer, a 0.0% delta on every classification metric while transitions drop 597→49 and episodes 567→0. I independently re-derived that this is arithmetically implausible for any hysteresis mechanism that changes even one decision near a threshold — changing the decision sequence necessarily changes at least some classification outcomes unless the hysteresis layer was applied only to a metric that is definitionally decoupled from per-instance accuracy. This confirms `Review_1_Key_Findings.md`'s "Finding A" from the primary source myself rather than taking it on trust.

| Item | My independent assessment | Reusable? |
|---|---|---|
| Problem framing / motivation (decision instability, ping-pong analogy) | Sound, well-grounded conceptually | Yes, as-is |
| Literature review's gap-mapping table (16 rows, Feb 2026 doc) | Content itself is fine; only the *absence* framing/conclusion is wrong | Yes, reframe conclusion only |
| Big Data dataset justification & 4-V critique (coursework docs) | Legitimate methodological work, independent of the auth RQ | Yes, as supporting material |
| LR baseline (74.54%) | Internally consistent, no red flags found in my read | Yes |
| GB confusion-matrix numbers (Table 3, pre-hysteresis) | Internally consistent within Table 3 itself | Yes, as the *raw* baseline — but must be re-verified against actual code, none of which exists in this project |
| Hysteresis result (Table 5, post-hysteresis) | Arithmetically implausible (Finding A); cannot be reused as evidence of "elimination" | No — must be recomputed from scratch with instrumented code |
| Oscillation-episode count (567 from 597 transitions) | Mathematically inconsistent with any standard episode definition (Finding B) | No — recount definition and rerun |
| Ambient noise / magnetometer strand (S1) | Never executed in any document | No — either drop or run for the first time, framed honestly as new work |
| Human-participant study (S4, referenced only) | Not located in this project; contradicts every other document's offline/ExtraSensory method | Cannot assess — the source document is absent from this project |
| TTT = 3s claim | Inoperable at confirmed ~60s native cadence | No — must be redefined in frame units |

**[R]** Reanalysable with the existing (recovered/re-run) pipeline: the classification baseline (LR/GB on ExtraSensory) and the literature gap-table's factual content. Not reanalysable without new code: any transition/oscillation/hysteresis-effect number, because no notebook or script implementing them exists in this project to inspect or rerun.

---

## 9. What evidence is missing

**[E, exhaustive from file listing]**
1. Raw ExtraSensory data files — absent. Cadence, missingness, and imbalance numbers are all self-reported, not independently checkable from this project.
2. Any code, notebook, or script beyond `05_cadence_check.py` (unrun) — absent. No way to verify how 225→101→52/53 feature counts were derived, what CV scheme was used, whether train/test/subject splits were disjoint, or whether SMOTE was applied before or after splitting.
3. Output logs, confusion matrices as raw artifacts, or saved model files — absent. Table 3/5 numbers cannot be traced to any reproducible source.
4. A resolved decision on the excluded human-participant PDF — its content is known only second-hand via `README.md`'s description; I have not read it because it is not in this project.
5. Any executed instance of the Sept 2026 pivot plan (pre-registration freeze, splice benchmark construction, mechanism bake-off) — all four planning documents (`01`–`04`) have unfilled template fields.
6. A resolved citation for the dataset paper — I independently confirmed the correct citation is Vaizman, Ellis & Lanckriet (2017), *IEEE Pervasive Computing* 16(4):62–74, doi:10.1109/MPRV.2017.3971131 ([arXiv:1609.06354](https://www.arxiv.org/abs/1609.06354); [official dataset site](http://extrasensory.ucsd.edu/)). `Van_Der_Walt.docx`'s "2018, vol 17(4), doi:.../MPRV.2018.2875891" is the wrong citation — confirmed by me directly against the publisher/arXiv record, not merely flagged as "conflicting" the way the prior review did.

---

## 10. Continue / pivot / hybrid

**[I]** Weighing the above: the original absence-based gap is falsified (§3); the reformulated comparative gap survives my adversarial search but only on a narrower evidentiary basis than previously stated (§5); the dataset is conditionally adequate pending the one unrun verification step (§6); roughly half the "completed" experimental claims cannot be reused as evidence because they are either unreproducible (no code) or arithmetically inconsistent (§7–8).

A full pivot (new dataset/new empirical study) is not justified — the literature review, dataset, and baseline classifier are legitimate assets and no evidence says ExtraSensory *cannot* answer the reformulated question. Continuing the current (Feb 2026) direction unchanged is not justified either — its headline result (Finding A/B) does not survive scrutiny and its novelty claim is literally false as worded.

**Recommendation: hybrid/refined pivot** — preserve the problem framing, literature base, dataset choice, and GB pipeline; drop the absence-based novelty claim and the untested ambient-noise/human-participant strands; reframe the contribution around the comparative, matched-operating-point mechanism evaluation; recompute all oscillation/hysteresis-effect numbers from instrumented code before any of them is used as evidence again.

---

## FINAL VERDICTS

**RESEARCH STATE:** Two coexisting layers — a completed but internally inconsistent single-mechanism study (Feb 2026, hysteresis-only, Finding A/B unresolved) and an unexecuted, more rigorous comparative pivot plan (Sept 2026, template fields still blank). No dataset, code, or output artifacts exist in this project to independently verify any quantitative claim; all such numbers are currently author self-report.

**GAP VERDICT:** Original gap ("field hasn't explored hysteresis-style decision stabilization at all") — **Weak / falsified**, contradicted by confirmed published work (Mondal & Bours 2017; Kiyani et al. 2020). Reformulated gap ("no matched-operating-point comparison of multiple stabilization mechanisms in continuous authentication exists") — **Defensible with refinement**, independently confirmed by my own adversarial search; no 2024–2026 paper was found that already closes it, though the supporting citations should be used more precisely (Ryu 2021 supports a general under-comparison pattern, not this specific claim; Raghu 2023 is the best template but is cross-domain transfer, not CA precedent).

**DATASET VERDICT:** Conditionally sufficient (matches prior "Option B" classification), but this is provisional, not confirmed — the ~60-second (not 20-second) cadence is independently confirmed from official ExtraSensory documentation, not from this project's own data, because no raw data files exist here. The single decisive unexecuted step is running the cadence check against the student's actual local files and redefining TTT in frame units.

**EXPERIMENT REUSABILITY VERDICT:** Problem framing, literature gap-table content, dataset justification, and the LR baseline are reusable as-is. The GB baseline confusion matrix is internally consistent but unverifiable without code. The hysteresis-effect numbers (transitions 597→49, episodes 567→0, Δ=0.0% on all classification metrics) are **not reusable as evidence** — independently re-derived to be arithmetically implausible — and must be recomputed from instrumented code. The ambient-noise/magnetometer and human-participant strands were never executed in any document present in this project and cannot be counted as existing evidence.

**PIVOT RECOMMENDATION:** Hybrid/refined pivot. Keep the dataset, GB pipeline, and literature base; replace the absence-based novelty claim with the comparative mechanism-evaluation framing; drop or explicitly reframe-as-future-work the untested ambient-sensor and human-participant strands.

**MOST IMPORTANT NEXT STEP:** Run `05_cadence_check.py` against the actual local ExtraSensory data files (not yet done — no output exists) to confirm the true frame period on the student's own copy of the data, and use that confirmed value to fix the TTT/block-length parameters in `01_preregistration_template.md` before freezing anything else.

---

## Direct answer to: "Can I use my existing dataset and research to address the reformulated gap?"

**Evidence-based answer: Conditionally yes, with three explicit conditions**, not an unqualified yes:

1. **[E]** The dataset (ExtraSensory) is structurally compatible with the comparative splice-benchmark design — confirmed via its official documentation (per-user, timestamped, minute-level examples, 60 users) — but this project contains no raw copy of it, so the specific numeric properties claimed in the coursework documents (feature counts, missingness, imbalance ratio) remain **EVIDENCE NOT ESTABLISHED IN THE PROJECT MATERIALS** until checked against the student's actual files.
2. **[E]** The existing GB classification pipeline and literature review are reusable *as instrumentation and background*, but none of the existing "hysteresis works" results (Feb 2026) can be reused as evidence for the reformulated gap — they are internally inconsistent and unreproducible without code that does not exist in this project. They would need to be **redone**, not cited, as part of the pivot's own experimental section.
3. **[I]** No published study was found, despite a deliberate search for one, that already performs the specific matched-operating-point multi-mechanism comparison the reformulated gap targets — so the question is answerable *in principle* with this dataset and this general approach, but only once the unresolved cadence/TTT issue (§6/§9) is fixed and the comparative experiments (currently only planning templates) are actually run.

So: the dataset and general research programme can plausibly address the reformulated gap, but "existing research" in the sense of already-completed experiments cannot — the Feb 2026 results must be treated as withdrawn pending recomputation, not as supporting evidence for the pivot.
