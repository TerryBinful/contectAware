# Stage 2 — Valid-protocol continuous-authentication experiment

This folder contains the Stage 2 research package. It is **new work**; nothing in `docs/stage1_recovery_audit/`
or `experiment_Files/` was modified. Stage 1 established that the original results reproduce exactly but were
produced under a protocol that cannot support authentication claims. Stage 2 rebuilds the measurement under a
protocol that can.

## 1. What Stage 2 tests

> Under a valid authentication protocol — chronological enrolment, unseen impostors, per-user models —
> how well can an ExtraSensory frame be attributed to the enrolled user, and **how much of that performance
> depends on location, device state, or data-availability (missingness) shortcuts?**

Stage 2 deliberately stops before the decision-layer (naive vs hysteresis) comparison. That comparison needs a
valid score stream first; Stage 2 produces exactly that (`score_streams/*.npz`, time-ordered, with segment ids).

## 2. Mandatory protocol decisions (as instructed)

| Decision | Implementation | Code |
|---|---|---|
| Keep location and device-state features; ablation mandatory | 6 feature sets incl. full, no-location/no-device-state, location-only, device-state-only, missingness-only | `src/features.py` |
| Primary cohort = regular cadence (~30 users, ≥95% of gaps 59–61 s) | `regular_min_frac = 0.95`, `min_frames_per_user = 1500` → **31 participants** | `src/protocol.py`, `configs/stage2_primary.json` |
| Fragmented participants kept for secondary analysis | `configs/stage2_secondary_fragmented.json`; same segment logic | `src/protocol.py` |
| Never fabricate continuity across gaps | Segments recomputed at `max_gap_s = 90`; no interpolation/ffill/bfill anywhere in the codebase | `protocol.segments` |
| Unseen impostors as the main protocol | Three **disjoint** participant pools: fit (24), calibration (12), test (24); enrolled user removed from all pools | `protocol.assign_pools` |
| Final metrics on held-out evaluation data | Test = enrolled user's final 20% (later in time) + rows from test-pool participants only | `experiment.run_user` |
| No protocol violation may pass silently | Every run asserts 8 leakage checks and **raises**, aborting that run | `protocol.leakage_report` |

### Deliberate design choices that differ from the original pipeline (documented, not silent)

| Choice | Reason |
|---|---|
| **No SMOTE.** Class balance handled by impostor row-capping plus `sample_weight` / `class_weight` | Stage 1 showed SMOTE inflated the CV estimate; synthetic minority points derived from genuine frames also blur the genuine/impostor boundary |
| Imputer and scaler fitted on **training rows only** | Original fitted them on all 377,346 rows |
| Operating points chosen on **calibration** data | Original reported τ = 0.5 only, and never evaluated the decision rule's own error rates |
| `EER_test_oracle` is reported but never used to set an operating point | It is an upper bound on achievable performance, flagged as oracle to prevent misuse |
| Per-user models (one per enrolled user) | Original trained a single model for a single user and generalised from it |

## 3. Structure

```
experiment files - stage 1B/
├── README.md                     this file
├── configs/                      stage2_primary | pilot | secondary_fragmented | fast_hgb | costprobe (JSON)
├── src/                          data_io.py  features.py  protocol.py  evaluate.py  experiment.py
├── scripts/run_stage2.py         CLI driver (also --dry-run pre-flight audit)
├── colab/Stage2_ExtraSensory_Colab.ipynb   self-contained Colab runner (clones this repo, runs the same code)
├── results/                      pilot/ costprobe/ primary/  (generated; raw data never stored here)
├── reports/                      resource audit + execution report
└── logs/                         copies of run logs
```

## 4. Required input

ExtraSensory primary feature files — **not** committed (≈748 MB decompressed).

```bash
curl -O http://extrasensory.ucsd.edu/data/primary_data_files/ExtraSensory.per_uuid_features_labels.zip
# 225,374,973 bytes, md5 9e44b3484b74cd8a370ff22894e0899b
unzip ExtraSensory.per_uuid_features_labels.zip -d raw
mkdir csv && for f in raw/*.gz; do gunzip -c "$f" > "csv/$(basename "$f" .gz)"; done
```
Expected schema: 60 files, each with `timestamp`, 225 feature columns, 51 `label:` columns, `label_source`.
`scripts/run_stage2.py` validates this and exits with code 2 if it does not hold.

## 5. How to run

```bash
python -m venv venv && . venv/bin/activate
pip install numpy==2.0.2 pandas==2.2.2 scikit-learn==1.6.1

# pre-flight audit only (no training)
python scripts/run_stage2.py --config configs/stage2_primary.json --data /path/csv --out results/primary --dry-run

# full primary grid: 31 users x 6 feature sets x 2 models = 372 runs (~3 h, 1 CPU core)
python scripts/run_stage2.py --config configs/stage2_primary.json --data /path/csv --out results/primary

# quick check / secondary cohort
python scripts/run_stage2.py --config configs/stage2_pilot.json --data /path/csv --out results/pilot --max-users 2
python scripts/run_stage2.py --config configs/stage2_secondary_fragmented.json --data /path/csv --out results/secondary
```

**Colab:** open `colab/Stage2_ExtraSensory_Colab.ipynb`, run cells 1–9. It installs pinned dependencies, clones this
repository, downloads and verifies the data, runs the pre-flight audit, executes the same driver, writes figures and
produces a single zip to return for analysis.

## 6. Outputs (all machine-readable)

| File | Content |
|---|---|
| `manifests/input_data_manifest.csv` | per-file size and MD5 of every input CSV |
| `manifests/participant_classification.csv` | per participant: frames, median gap, gap fractions, segments, cadence class, primary eligibility |
| `manifests/participant_pools.json` | the three disjoint impostor pools and the enrolled candidates |
| `experiment_metadata.json` | full config, seeds, feature-set definitions, library versions, git commit, timestamp |
| `per_run_results.csv` | one row per (user × feature set × model): AUC, AP, EER, all operating points, split sizes, runtimes |
| `run__<user>__<set>__<model>.json` | the same plus ROC curve points and all leakage-check records |
| `per_impostor/*.csv` | per test-impostor participant: n rows, mean score, FAR at the calibrated threshold |
| `score_streams/*.npz` | genuine test frames (timestamp, score, segment id) and impostor scores with owner uuid — the input for the Stage 3 decision-layer comparison |
| `ablation_summary.csv` | per feature set × model: mean AUC/EER/FAR/FRR with bootstrap 95% CIs across users |
| `failures.json` | any failed run with its traceback (absent if none) |
| `logs/run.log` | full execution log |

## 7. How each requirement is enforced

- **Temporal validity** — `protocol.temporal_split` asserts `max(train ts) < min(calib ts)` and `max(calib ts) < min(test ts)`; equal timestamps cannot straddle a cut. Test frames carry `segment id` so a later decision layer can respect gaps.
- **Unseen impostors** — pools are disjoint by construction, checked by `check_pools`, and re-checked per run against the actual row owners (`test_impostor_rows_from_unseen_participants_only`).
- **No fabricated continuity** — the codebase contains no interpolation, `fillna(method=...)`, resampling or reindexing over time. Missing *values* are median-imputed (fitted on training rows) which is a value operation, not a temporal one; `F6_MISSINGNESS_ONLY` exists to measure what that imputation carries.
- **Preprocessing leakage** — imputer/scaler fitted on training rows only, recorded in each run's leakage checks.
- **Threshold leakage** — operating points derive from calibration data; the test-set EER threshold is labelled `oracle` and used for nothing.
- **Reproducibility** — one seed in the config drives pool assignment, row sampling and models; environment and git commit are saved per run directory.

## 8. Known limitations and open items

1. **Feature-level identity cues remain possible** inside the retained feature sets (e.g. GPS accuracy, app state). The ablations quantify their contribution but do not remove them from `F1`/`F2` by design.
2. **Impostor rows are sampled**, not exhaustive, to bound runtime; caps are in the config and recorded per run.
3. **Fragmented cohort** is implemented but is secondary; interpreting its results requires the segment structure to be taken into account.
4. **No decision-layer (hysteresis) comparison here.** Its parameters (TTT in minutes, thresholds, initial state, gap handling) must be fixed on calibration data and confirmed before Stage 3.
5. Scores are not calibrated probabilities across users; comparisons use per-user thresholds.
