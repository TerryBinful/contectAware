# STAGE 1 EXECUTIVE REPORT — Evidence-based reconstruction (Phases 0–4)

**Date:** 16 September 2026 · **Scope:** inventory, pipeline reconstruction, model-output audit, authentication-validity audit, dataset/temporal audit, faithful reproduction. **No redesign, tuning, or pivot experiment was performed.**
**Note:** the *Experimental Recovery & Research Pivot Execution Protocol* is not in the repository; Stage 1 followed the six steps in the task message.

Supporting documents: `REPOSITORY_INVENTORY.md`, `ORIGINAL_PIPELINE_RECONSTRUCTION.md`, `AUTHENTICATION_VALIDITY_AUDIT.md`, `DATASET_TEMPORAL_AUDIT.md`, `ORIGINAL_RESULTS_REPRODUCTION.md`.

---

## 1. What did my original pipeline actually do?

One executed Colab notebook (`COMPLETE_ExtraSensory_Analysis_with_Hysteresis.ipynb`, CSCD 613 exam) produced every reported number. It:

1. loaded all 60 ExtraSensory participants, kept 103 phone-accelerometer, gyroscope, **location** and **device-state** features (no magnetometer, audio or watch), dropped 2 → 101;
2. median-imputed and robust-scaled using **all** rows;
3. labelled the participant with the most data (`78A91A4E`) as 1 and the other 59 as 0;
4. split **rows at random** 80/20, picked 52 features by Random-Forest Gini importance, applied SMOTE, trained LR and GB;
5. scored that one participant's **entire** timeline (80% training rows) and counted state changes under τ = 0.5 versus a 0.6/0.4, 3-consecutive-frame rule.

The written paper describes a different pipeline (chronological per-user 60/20/20 splits, per-user imputation, "all test users", TTT = 3 s, unchanged post-hysteresis FAR/FRR). **None of those are in the code** (20 discrepancies listed in `ORIGINAL_PIPELINE_RECONSTRUCTION.md` §4).

## 2. What does the model actually predict?

The probability that a single one-minute example came from participant `78A91A4E` rather than from one of 59 other participants who are all also in the training set. It is a **closed-set, single-subject, frame-independent participant-discrimination score**, calibrated to a SMOTE 50/50 prior. About 40% of its feature importance is GPS/location (altitude alone 26%), and an imputation artefact acts as a shortcut: the target never lacks altitude, so impostor rows with missing altitude (43.8% of them) are rejected with 0.00% FAR, and **every** false accept occurs on rows with real altitude.

## 3. Can its output legitimately serve as a continuous-authentication signal?

**Not in its current form.** It fails 7 of 10 validity criteria on direct evidence: no enrolment/later-data separation (95.7% of the target's test rows have a training neighbour ≤ 90 s away), no unseen impostors (59/59 seen), n = 1 genuine user, the decision-layer stream was 80% in-sample, no impostor stream or identity change was ever evaluated, the decision cadence is ~1/min while the paper claims 3 s, and reported FAR/FRR do not correspond to the hysteresis rule. Its dependence on place/device cues makes the "behavioural" interpretation doubtful. Whether a properly trained per-user score from this dataset could serve as a CA signal is **NOT ESTABLISHED FROM AVAILABLE EVIDENCE**.

What the hysteresis experiment legitimately shows: on one genuine participant's largely in-sample stream, the 0.6/0.4/3-frame rule reduced state changes 597 → 49 and locked frames 4.31% → 2.03%. It shows nothing about impostor detection or security cost.

## 4. Can the old results be reproduced?

**Yes.** Using the public ExtraSensory archive (fingerprinted as identical to the data used) and pinned library versions, every GB and hysteresis number reproduces exactly: 99.26% accuracy, FAR 0.53%, FRR 7.09%, AUC 0.9976, 597 → 49 transitions, 567 → 0 "episodes", Stability Index 0.9502 → 0.9959, identical feature importances. LR differs by at most 0.0021 (non-converged optimiser). LR CV reproduces (0.8137 vs 0.8136); GB 5-fold CV reproduces exactly, fold by fold (0.9951 ± 0.0001).

But **reproducible ≠ valid**, and Table 5's post-hysteresis Accuracy/FAR/FRR are not reproducible because no code ever computed them; when measured on the same stream, rejected-frame rate *does* change (test rows 7.09% → 2.29%).

The previous audit's "Finding B" (597 transitions cannot give 567 episodes) is **resolved**: "episodes" are overlapping 4-frame windows, not episodes. "Finding A" (Δ = 0.0 on all metrics) is **confirmed** as a reporting error. The ~60-s cadence is **confirmed from the primary data** (median gap 60 s; 99.2% of the target's gaps are 59–61 s), so TTT = 3 frames ≈ 180 s.

## 5. What must be fixed before the comparative decision-layer experiment?

**Blocking (must fix):**
1. **Per-user genuine models with chronological separation** — enrolment on each participant's earlier data, testing on later data; no row-level random split; no preprocessing fit on test data.
2. **Unseen impostors** — participant-disjoint impostor sets for training vs testing (or an explicitly declared closed-set design).
3. **Many genuine users**, not one; report per-user distributions.
4. **Identity-change streams** (e.g., spliced genuine→impostor→genuine sequences at run boundaries) so that detection delay, post-decision FAR and false-lock rate can be measured for every decision rule.
5. **Time model** — define persistence in minutes/frames using the real ~60-s cadence; decide how gaps > 90 s and fragmented participants are handled; drop all 20-s and 3-s claims.
6. **Metric definitions** — real EER; episode/ping-pong definitions that count events, not overlapping windows; post-decision error rates computed on the decision-layer output; no Stability Index that merely restates transition rate.
7. **Location/missingness shortcut** — decide, before any mechanism comparison, whether location features and missingness indicators are admissible; at minimum report a feature-group ablation. Otherwise the "stability" being compared is partly stability of *where the phone is*.
8. **Hysteresis initial state and parameter provenance** — state the start state; fix all mechanism parameters on validation data only.

**Documentary (must correct in the write-up):** the 20 discrepancies (D1–D20), especially D1, D2, D6, D8, D9, D12, D18; remove the within-subjects human-study claims; relabel the synthetic "novelty demonstration"; use defensible terminology (`AUTHENTICATION_VALIDITY_AUDIT.md` §6).

**Decisions needed from you before Stage 2:**
- Keep or exclude location and device-state features?
- Include fragmented-cadence participants, or restrict to the ~30 regular ones and state it as a limitation?
- Open-set (unseen impostors) as the primary protocol?

---

**STOP.** Stage 1 is complete. No pivot experiment has been started.
