# STAGE 2 — IMPLEMENTATION & RESOURCE AUDIT

Performed before any Stage 2 code was written, on the repository at commit `c98c157` plus the local
Stage 1 working environment. Nothing was modified during the audit.

---

## 1. Scope findings

| Question | Finding |
|---|---|
| What data are actually available? | The full ExtraSensory primary feature set: 60 participant CSVs, 377,346 rows, 225 features + 51 labels, 747.61 MB decompressed, verified in Stage 1 against the notebook's own fingerprints (MD5 of the archive `9e44b3484b74cd8a370ff22894e0899b`). **Not committed to the repository**; it is re-downloadable and is fetched by the Colab package. |
| What preprocessing already exists? | Only inside Stage 1 reproduction code, and only in the *original* (invalid) form: global median imputation, global RobustScaler, SMOTE, random row split. Not reusable for Stage 2 without change. |
| What Stage 1 / Stage 1B outputs exist? | Stage 1: six reports and seven result files (`experiment_Files/stage1_reproduction/results/`). **There is no pre-existing "Stage 1B" folder, code or output in the repository** — the folder name in the instruction refers to where Stage 2 work should go, not to existing work. |
| Participant-selection logic? | None. Stage 1 produced the *evidence* (`dataset_per_user_temporal.csv`) but no selection code. Written fresh in `src/protocol.py`. |
| Temporal-gap analysis? | Descriptive only (`dataset_temporal_audit.py`). It has no segment/run API usable by an experiment. Reimplemented as `protocol.segments`. |
| Feature-engineering code? | Only the Stage 1 prefix filter and RF-importance selection, both entangled with the invalid split. Replaced by declarative prefix-based feature sets. |
| Model/training code? | Stage 1 reproduction only, hard-coded to the original protocol. Hyperparameters reused for comparability; the surrounding protocol is not. |
| Evaluation/metric code? | Stage 1 has a metric function with a known defect (`EER = (FAR+FRR)/2`) and no calibration concept. Not reused. New `src/evaluate.py` implements true EER, calibrated operating points, bootstrap CIs. |
| Configs / manifests / helper modules? | None existed. Created: 5 JSON configs, participant/pool/data manifests, experiment metadata. |
| Dependencies | numpy 2.0.2, pandas 2.2.2, scikit-learn 1.6.1 (already installed locally; pinned in the Colab notebook). No new dependency introduced. |
| Missing files | The *Experimental Recovery & Research Pivot Execution Protocol* is still not in the repository (noted in Stage 1). Not blocking. |
| Assumptions in existing code that conflict with Stage 2 | (a) random row splitting; (b) preprocessing fitted on all rows; (c) single enrolled user; (d) impostors shared between train and test; (e) SMOTE; (f) frame-count TTT treated as 20 s/frame. All are excluded from the Stage 2 code path. |

## 2. Classification

**A. AVAILABLE AND READY TO USE**
- ExtraSensory data (all 60 participants), locally decompressed and schema-validated.
- Stage 1 cadence evidence (`dataset_per_user_temporal.csv`) — used to cross-check the new participant classifier (both give 31 regular participants at ≥95%).
- Stage 1 environment (Python 3.12.3, numpy 2.0.2, pandas 2.2.2, scikit-learn 1.6.1).
- Original model hyperparameters, reused for comparability.

**B. AVAILABLE BUT REQUIRES MODIFICATION**
- None reused as-is. Stage 1 code is kept unmodified as an auditable record; Stage 2 code is separate. (Reuse was rejected deliberately: every Stage 1 preprocessing/evaluation path embeds an invalid protocol assumption.)

**C. MISSING BUT RECONSTRUCTABLE — all now implemented**
- Participant cadence classification and eligibility (`protocol.classify_participants`).
- Segment/gap logic (`protocol.segments`).
- Chronological within-user splits (`protocol.temporal_split`).
- Disjoint impostor pools (`protocol.assign_pools`).
- Feature-set/ablation definitions (`features.py`).
- Train-only preprocessing, class balancing without SMOTE, per-user models (`experiment.py`).
- Calibrated operating points, true EER, ROC/PR, bootstrap CIs (`evaluate.py`).
- Leakage assertions (`protocol.leakage_report`).
- Manifests, metadata, seeds, logging (`scripts/run_stage2.py`).

**D. MISSING AND REQUIRED FROM YOU**
1. **Decision-layer parameters for Stage 3** (TTT in minutes, unlock/lock thresholds, initial state, behaviour across gaps > 90 s). Not needed for Stage 2, required before the naive-vs-hysteresis comparison.
2. **Confirmation of the documented design choices** in README §2 (no SMOTE; calibration-based thresholds).
3. **GitHub credentials** — this environment cannot push; you must push, or supply a token.
4. Optional: whether watch features (37–62% missing, device-dependent) should stay inside `F1_ALL`.

**E. COMPUTATIONALLY POSSIBLE BUT EXPENSIVE**
Measured, not estimated (1 vCPU, 4 GB RAM; primary caps; 225-feature set):

| Run | Measured |
|---|---|
| Gradient boosting, F1_ALL | 69–72 s |
| Logistic regression, F1_ALL | 23–24 s |
| Histogram GB, F1_ALL (optional variant) | 9 s |
| Full primary grid, 372 runs | **≈2.5–3 h sequential** |
| Peak memory | < 1.5 GB (well inside 4 GB) |
| Secondary fragmented cohort (29 users) | a further ≈2.5–3 h |

**F. NOT CURRENTLY EXECUTABLE**
- The Stage 3 decision-layer comparison (blocked on D1).
- Anything requiring sub-minute decisions: the data are ~1 frame/minute (Stage 1 finding). Not fixable with this dataset.
- Direct push to GitHub (no credentials).

## 3. Execution decision

> **PARTIALLY EXECUTABLE IN CURRENT ENVIRONMENT.**
> The pipeline runs here and was validated end-to-end (pilot: 12/12 runs, 0 failures; cost probe: 3/3).
> The full primary grid is ~3 h of single-core compute, which exceeds what this session can reliably
> supervise — two earlier long background jobs in this environment were killed mid-run. The full grid was
> therefore **started** here, and the Colab package exists so it can be completed reliably regardless of
> how far the local run gets. Whatever the local run completes is reported as executed; nothing else is.

## 4. Leakage checks implemented (each aborts the run on failure)

| Check | Where |
|---|---|
| impostor pools disjoint | `check_pools`, per-run |
| final-test impostors unseen during fitting/calibration | per-run, on pools and on actual row owners |
| enrolled user never their own impostor | pool filtering in `sample_pool` |
| genuine train < calibration < test in time | `temporal_split` assertions |
| no row reuse between train and test | per-run |
| no duplicate training rows | per-run |
| preprocessing fitted on training rows only | by construction, recorded per run |
| threshold selection uses calibration only | by construction; test EER threshold labelled `oracle` |
| no random row-wise splitting of temporally correlated frames | by construction (chronological split) |
| location / device-state / missingness leakage | measured, not assumed: feature sets F3–F6 quantify each |
