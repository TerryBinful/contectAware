# AUTHENTICATION VALIDITY AUDIT (Stage 1 — Phases 2 & 3)

**Question 1:** What exactly does the ML model predict?
**Question 2:** Does that output constitute a legitimate continuous-authentication signal?

Evidence: executed notebook code (cells 23, 26–36, 42–46), faithful re-execution, and audit-only diagnostics (`experiment_Files/stage1_reproduction/results/repro_results.json`, `repro_leakage_shortcut_diagnostics.json`, `repro_per_impostor_acceptance_test.csv`). Diagnostics did not modify the model, data, thresholds or results.

---

## 1. What the model predicts

The Gradient Boosting model outputs

> **p(x) = estimated probability that a single one-minute ExtraSensory example x (52 preprocessed features) was recorded by participant `78A91A4E` rather than by one of the other 59 participants in the dataset.**

Precise properties:

| Property | Finding | Evidence |
|---|---|---|
| Task type | Binary, one-vs-rest, **closed-set** participant discrimination | Cell 23 |
| Number of "genuine" users | **1** | Cell 23 (`value_counts().index[0]`) |
| Negative class | Pooled data of 59 other participants | Cell 23 |
| Impostors at test time | The **same 59 people** seen in training (59/59) | Diagnostics |
| Unit of decision | One example ≈ one minute (20-s recording, ~60-s spacing) | `DATASET_TEMPORAL_AUDIT.md` |
| Temporal context | None — each example scored independently | Cells 36, 44 |
| Probability calibration | Trained on SMOTE 1:1 data, so p reflects a 50/50 prior, not the 1:30.5 base rate or any deployment prior | Cell 32 |
| What is *not* predicted | Activity, context labels, "user present", "device changed hands", trust over time | — |

## 2. Criteria for a legitimate continuous-authentication (CA) signal, and how the pipeline fares

| # | Criterion (what a CA verification score needs) | Status | Evidence |
|---|---|---|---|
| C1 | Genuine model built from the account holder's **enrolment** data and evaluated on their **later** data | ✗ | Random row split. 95.7% of the target's test rows have a training row from the same user within ≤90 s |
| C2 | Evaluated against **impostors not seen in training** (or at least with an explicit open/closed-set statement) | ✗ | 59/59 test impostors are in training. Closed set, not declared |
| C3 | More than one genuine user, so results are not an artefact of one person | ✗ | n = 1 (the participant with the most data, itself a selection choice) |
| C4 | The score reflects **the person** (behaviour/biometric), not place, device or data-collection artefacts | ✗ / unresolved | See §3 |
| C5 | Stream evaluated through the decision layer must be **held-out** data | ✗ | 80.0% of the 11,996-frame hysteresis stream was training data |
| C6 | Decision-layer evaluation must include **identity changes** (genuine → impostor) so detection delay and post-decision FAR can be measured | ✗ | Only the genuine stream was replayed. No impostor stream, no switch events |
| C7 | Decision cadence compatible with the claimed timing | ✗ | ~1 decision/min; documents claim TTT = 3 s |
| C8 | Reported error rates correspond to the deployed decision rule | ✗ | FAR/FRR are for τ = 0.5 on random test rows; hysteresis rule never evaluated for FAR/FRR |
| C9 | Thresholds/parameters not tuned on test data | ✓ (as far as recorded) | 0.5 / 0.6 / 0.4 / 3 frames are hard-coded constants with no search. Whether other values were tried earlier is NOT ESTABLISHED FROM AVAILABLE EVIDENCE |
| C10 | SMOTE confined to training data | ✓ | Cell 32 |
| C11 | **All** preprocessing (not only SMOTE) fitted inside the training partition | ✗ | *Added 2026-09-17.* `reproduce_original.py` lines 68–71 fit `SimpleImputer(strategy='median')` and `RobustScaler()` on all 377,346 rows before `train_test_split` (lines 82, 101). Test-set statistics therefore inform imputation and scaling. Likely small in magnitude (test is 20% of rows) but it is a real leak, and C10's ✓ should not be read as certifying preprocessing generally. RF feature selection (lines 84–95) *was* correctly fitted on training data only |

## 3. Is the signal behavioural? (C4 in detail)

**3.1 Location dominates.** Of the 52 selected features, 13 are GPS/location descriptors carrying **37.4% + 3.0% ≈ 40%** of total Gini importance — 9 `location:*` features (37.4%) plus 4 `location_quick_features:*` features (3.0%). [Corrected 2026-09-17: this figure previously read "17", which does not match `results/repro_rf_feature_importance.csv`; recomputation from that file gives 13. The importance percentages were and remain correct.] The top two features overall are `location:min_altitude` and `location:max_altitude` (26.1% together). Altitude largely identifies *where* a participant spends time (home/campus building) and depends on the phone's GPS hardware; it is not a behavioural biometric. Only 3 other participants have a median altitude within 5 m of the target's.

**3.2 An imputation artefact acts as a shortcut.** The target participant has **0%** missing altitude. Across all rows, 42.5% are missing and were imputed with the global median (106.68 m), a value distinct from the target's typical altitude (median 91.9 m).
On held-out impostor rows:

| Impostor test rows | Share | FAR at τ = 0.5 |
|---|---|---|
| altitude missing (imputed) | 43.8% | **0.00%** |
| altitude present | 56.2% | 0.94% |

**100% of false accepts** occur on rows with altitude present. Roughly 44% of the negative class is therefore rejected by a data-availability cue ("does this phone report altitude?"), which says more about the device and its settings than about the person. The headline FAR of 0.53% is diluted by these "free" rejections.

**3.3 Other non-behavioural cues in the selected set.** `location:best_vertical_accuracy`, `location:best_horizontal_accuracy`, `location:num_valid_updates` (GPS hardware/reception), `discrete:app_state:*`, `discrete:ringer_mode:missing`, `discrete:app_state:missing`, `discrete:wifi_status:*` (OS/app/network state, and missingness flags that vary by phone platform). The accelerometer `3d:mean_x/y/z` features (ranks 4, 5, 15) mainly encode the phone's resting orientation relative to gravity — a habit-of-placement cue, arguably behavioural, but also strongly driven by place (desk, pocket, bed).

**3.4 What is NOT established.** How much of the 99.26% accuracy survives without location and missingness cues is **NOT ESTABLISHED FROM AVAILABLE EVIDENCE** — no ablation was run (deliberately not run in Stage 1, which forbids redesign). This is the single most important open question for C4.

## 4. What the temporal (hysteresis) experiment actually measured

- Input: the classifier's p(x) for the target participant's own frames in time order, 80% of them in-sample.
- On this stream, p is very high (median 0.996); 3.05% of frames have p ≤ 0.4 and 2.84% lie in the 0.4–0.6 band.
- Naive rule: 597 state changes; 4.31% of frames locked.
- Hysteresis rule: 49 state changes; 2.03% of frames locked (including the initial 31-frame ≈ 31-min locked period caused by starting in LOCKED).
- So the experiment shows that, **for one genuine user, on mostly in-sample data, a 3-frame/0.6–0.4 rule produces fewer and longer lock periods than τ = 0.5**. That is a real and reproducible property of the rule.
- It shows **nothing** about: detecting an impostor, the delay to lock after a device changes hands, post-hysteresis FAR, or behaviour on unseen data from unseen people.
- Diagnostic only (same model/rules, held-out rows of the target only, concatenated in time order with gaps): naive 177 transitions / 158 windows; hysteresis 17 transitions / 0 windows; locked frames 7.09% → 4.34%. The direction of the effect persists on held-out genuine rows, but those rows are not a contiguous stream, so this is not a valid replacement measurement.

## 5. Verdict

> **As implemented, the model's output is a closed-set, single-subject participant-discrimination score, learned from randomly split, temporally adjacent rows and substantially driven by location and data-availability cues. It is not a legitimate continuous-authentication signal in its current form.**

Specifically: C1, C2, C3, C5, C6, C7, C8 fail on the executed evidence; C4 is doubtful with direct evidence of a shortcut; C9 and C10 pass.

This does **not** mean a score of this *type* can never serve as a CA signal. A per-user score trained on enrolment data and tested chronologically against unseen impostors could. Whether this dataset/feature set yields a usable one is NOT ESTABLISHED FROM AVAILABLE EVIDENCE.

## 6. Defensible terminology for what was done

| Current wording | Defensible wording |
|---|---|
| "authentication model", "authentication engine" | "single-participant one-vs-rest discrimination model (closed-set)" |
| "legitimate user / impostor" | "target participant / other enrolled participants" |
| "FAR / FRR" | "frame-level false-positive / false-negative rate at τ = 0.5 on randomly held-out rows" |
| "continuous authentication decisions" | "per-minute thresholded participant scores" |
| "hysteresis eliminates oscillation" | "on one participant's (largely in-sample) genuine stream, a dual-threshold 3-frame rule reduced state changes from 597 to 49" |
| "behavioural biometrics" | "contextual and device-motion features (including GPS altitude and device-state indicators)" |
