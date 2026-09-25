# MSc Computer Science Research — Semantic Project Context Index

**Purpose:** Compact, retrieval-friendly representation of the project context established in the MSc research chats and verified against the current repository. This is a semantic index, not a transcript. It is intended to make future research/planning prompts easier to ground consistently.

**Last reconciled:** 17 September 2026

## 1. Research identity

- Degree: MSc Computer Science.
- Research area: continuous / implicit authentication using smartphone sensor and contextual data.
- Current research focus: temporal stability of continuous-authentication decisions.
- Core problem: frame-level authentication evidence can fluctuate; reacting independently to every score can cause repeated authenticated/unauthenticated transitions ("ping-pong" behaviour).
- Current contribution framing: compare temporal decision-layer stabilization mechanisms under comparable operating conditions rather than claim that hysteresis itself is unexplored in continuous authentication.

## 2. Research evolution

- Early direction: ambient noise and magnetometer as authentication signals.
- Later direction: hysteresis-based decision stabilization inspired by telecom handover logic.
- Current direction: refined comparative study of multiple temporal decision mechanisms.
- Mechanisms under consideration: instantaneous threshold, moving average, EWMA, majority vote, debounce/consecutive decisions, dual-threshold/margin, hysteresis, trust/confidence accumulation, and possibly SPRT/HMM where feasible.
- These are candidates, not mandatory components; final inclusion must follow literature, feasibility, dataset cadence, comparability and MSc scope.

## 3. Evidence hierarchy / working rule

- Repository implementation is the primary source of truth for what was actually executed.
- Papers, Word documents and research notes are secondary descriptions.
- If code contradicts the paper, preserve the original implementation, document the discrepancy, and do not silently rewrite history.
- Separate evidence, interpretation and recommendation.
- Do not reuse an empirical number merely because it appears in an earlier paper; require traceability/reproduction.

## 4. Current repository state

Repository: `TerryBinful/contectAware` (public), default branch `main`.

Important areas currently present:
- `docs/Stage1/` — completed forensic reconstruction and audit documents.
- `docs/Claude Experimental Recovery & Research Pivot Execution Protocol.md` — execution protocol.
- `experiment_Files/` — notebooks and Stage 1 reproduction scripts/results.
- Stage 1 contains actual reproduction outputs, so earlier claims that the repository had no outputs/data artefacts are superseded by the current repository state.

Key Stage 1 documents:
- `REPOSITORY_INVENTORY.md`
- `ORIGINAL_PIPELINE_RECONSTRUCTION.md`
- `AUTHENTICATION_VALIDITY_AUDIT.md`
- `DATASET_TEMPORAL_AUDIT.md`
- `ORIGINAL_RESULTS_REPRODUCTION.md`
- `STAGE1_EXECUTIVE_REPORT.md`

## 5. What the original executed pipeline actually did

- Executed notebook: `experiment_Files/COMPLETE_ExtraSensory_Analysis_with_Hysteresis.ipynb`.
- Dataset: all 60 ExtraSensory participants.
- Features retained: 103 phone-accelerometer, gyroscope, location and device-state features; 2 dropped, leaving 101.
- Missing values: median imputation; scaling fit using all rows in the original implementation.
- Target: participant `78A91A4E` versus the other 59 participants.
- Split: random row-level 80/20 split.
- Feature selection: 52 features selected using Random-Forest Gini importance.
- Balancing: SMOTE.
- Models: Logistic Regression and Gradient Boosting.
- Decision stream: scored the target participant's timeline; threshold comparison included τ=0.5 and a 0.6/0.4 three-consecutive-frame hysteresis-style rule.

## 6. Critical interpretation of the original model

The original model is not a clean deployment-style continuous-authentication protocol. It produces a closed-set, single-subject participant-discrimination score: probability that a one-minute example belongs to the target participant rather than one of 59 participants also represented during training.

Stage 1 identified major validity problems:
- no genuine-user enrolment/later-data separation;
- target test rows are heavily temporally adjacent to training data;
- no unseen impostors;
- n=1 genuine user;
- decision-layer stream is largely in-sample;
- no identity-transition evaluation;
- native cadence is approximately one minute, not three seconds;
- reported FAR/FRR were not computed from the hysteresis output;
- substantial dependence on location/device-context cues makes a purely behavioural interpretation questionable.

## 7. Reproduced historical results — interpretation

The historical GB/hysteresis results can be reproduced numerically from the original implementation, including approximately:
- GB accuracy 99.26%;
- FAR 0.53%;
- FRR 7.09%;
- AUC 0.9976;
- 597 → 49 state transitions under the historical hysteresis rule;
- historical overlapping-window count 567 → 0;
- stability-index values reported historically.

Important: reproducibility does not establish methodological validity.

Stage 1 resolved two earlier audit issues:
- The 597 vs 567 issue is explained by the historical "episode" count being overlapping four-frame windows, not independent episodes.
- The historical claim that post-hysteresis Accuracy/FAR/FRR were unchanged (Δ=0.0) is a reporting error; those metrics were not actually computed from the hysteresis output. On the same stream, rejected-frame rate changes.

## 8. Dataset temporal fact

Stage 1 directly verified the primary data used in reproduction: median inter-frame gap is about 60 seconds; 99.2% of the target participant's gaps are 59–61 seconds.

Therefore:
- discard historical 20-second cadence claims;
- discard historical 3-second TTT interpretation;
- express persistence/delay parameters in frames/minutes consistent with the observed cadence;
- define treatment of gaps >90 seconds and fragmented participants before the comparative experiment.

## 9. Reformulated research gap

Original gap (withdrawn): "the field has not systematically explored hysteresis-based techniques" / equivalent absence claim. Published continuous-authentication work already includes temporally persistent trust models and dual-threshold mechanisms.

Current gap to investigate:
- whether a controlled, matched-operating-point, head-to-head comparison of multiple temporal decision-layer stabilization mechanisms exists for continuous/behavioural authentication;
- comparison should isolate the decision layer by feeding mechanisms the same underlying authentication score/probability stream;
- evaluation should include security, temporal stability and responsiveness, not only steady-state accuracy.

Evidence status from the independent 15 Sept 2026 audit:
- original absence claim: falsified / not defensible;
- reformulated comparative gap: defensible with refinement;
- no 2024–2026 paper found in the adversarial search that already closes the specific matched-operating-point multi-mechanism comparison.

Useful literature anchors identified in the audit:
- Mondal & Bours (2017): continuous-authentication trust model.
- Kiyani et al. (2020): dual-threshold / confidence-style decision logic.
- Raghu, MacIsaac & Scheme (2023): multi-scheme post-processing comparison in myoelectric prosthesis control; methodological template from an adjacent domain, not direct CA precedent.
- Ryu & Yeom systematic review: supports a broader observation that design choices/fusion approaches are under-compared, but should not be cited as direct proof of the specific stabilization-mechanism gap.

## 10. Proposed comparative architecture

Common authentication evidence / probability stream
→ decision mechanism A/B/C/...
→ common evaluation framework
→ security + stability + responsiveness metrics.

Principle: mechanisms should use the same model, features, users, samples and score stream wherever possible so that the decision-layer effect is isolated.

## 11. Blocking methodological requirements before Stage 2

1. Train per-user genuine models with chronological enrolment/test separation.
2. Avoid row-level random leakage and fit preprocessing on training/enrolment data only.
3. Define unseen-impostor/open-set handling, or explicitly justify a closed-set protocol.
4. Use many genuine users and report per-user distributions, not one-user results.
5. Construct genuine→impostor→genuine identity-transition streams for transition/delay analysis.
6. Define real operating-point metrics and event definitions before experiments.
7. Decide how location and device-state features/missingness indicators are treated; at minimum perform feature-group ablation if retained.
8. Fix initial state and all mechanism parameters using validation data only.
9. Use the verified ~60-second cadence; parameterize persistence in frames/minutes.

## 12. Current decisions still required

- Whether location and device-state features remain admissible.
- Whether to include fragmented-cadence participants or restrict to regular participants with the limitation explicitly stated.
- Whether open-set/unseen-impostor evaluation is the primary protocol.
- Final mechanism set after feasibility/literature review.
- Final metric definitions and matched operating-point procedure.

## 13. MSc writing requirements from project scaffolding

The final paper structure currently expected is:
- Chapter 1: Introduction/background, motivation, problem statement, objectives, scope, justification/significance, methodology/tools, expected results/use, chapter presentation.
- Chapter 2: Literature review; comprehensive discussion of prior work, analysis of existing knowledge and gaps, at least five related computer-based systems, feature-based comparison including strengths and weaknesses.
- Chapter 3: Analysis and detailed design of proposed system.
- Chapter 4: Implementation, testing and documentation.
- Chapter 5: Conclusion and recommendations.
- Bibliography/references.

Supporting research-work artefacts requested in the project include:
- comparative analysis table: paper/title/authors, problem, technique, methodology, proposed solution, experimental results;
- paper summaries covering aims, methods, novelty/improvement, gaps, limitations, strengths, weaknesses and areas for improvement;
- idea-synthesis notes covering motivation, difficulty, literature obstacles, proposed approach/result and impact.

## 14. Non-negotiable research integrity rules

- Do not optimise for favourable results.
- Do not manufacture missing evidence.
- Do not treat planning templates as executed experiments.
- Do not present historical invalid results as current evidence.
- Clearly label reproduction, new experiment, inference and literature-derived claims.
- Preserve useful earlier work where it remains methodologically valid.
- The current programme is a refined/hybrid pivot: retain useful dataset/pipeline/literature assets while rebuilding the authentication evaluation protocol and comparative decision-layer experiment.

## 15. Retrieval tags

`MSc` `Computer Science` `continuous authentication` `implicit authentication` `behavioural biometrics` `ExtraSensory` `Gradient Boosting` `Logistic Regression` `decision stability` `temporal stabilization` `hysteresis` `moving average` `EWMA` `majority vote` `debounce` `dual threshold` `trust model` `SPRT` `HMM` `matched operating point` `identity transitions` `ping-pong` `FAR` `FRR` `EER` `detection delay` `false lock` `open-set` `location leakage` `temporal leakage` `Stage 1` `research pivot` `reproducibility`
