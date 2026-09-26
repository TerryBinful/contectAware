# Stage 2 — Decision-layer stabilisation mechanisms for continuous authentication

Reproducible comparison of nine decision mechanisms (plus one supplementary) that turn the **same**
per-frame authentication-score stream into AUTH/LOCKED decisions, evaluated on ExtraSensory with a
controlled identity-transition benchmark at a matched genuine false-lock rate.

Results are **generated**, never typed: see `results/<label>/RESULTS_REPORT.md`
(`main` = primary run, `pilot` = pipeline check). Design rationale: `docs/Stage2/`.

## Research question and hypothesis
At a matched genuine false-lock rate, how do mechanisms differ in security (FAR_frame, FRR_time),
stability (transitions, ping-pong) and responsiveness (detection and recovery delay)?
Working hypothesis: they show **different trade-offs**; no winner is assumed and a null result is valid.
Confirmatory test, H1–H4 and falsification criteria: `docs/Stage2/PREREGISTRATION_FROZEN.md`.

## Pipeline
| Stage | What | Output (`results/<label>/`) |
|---|---|---|
| A audit | download + MD5, cadence (`../05_cadence_check.py`), feature inventory, eligibility | `dataset_audit/` |
| B split | cohort, per-user disjoint impostor roles (train / calibration / test) | `participant_split.json` |
| C scoring | Exp 1 fixed score generator per genuine user + **gate** (median test AUC ≥ 0.60) | `baseline/` |
| D benchmark | genuine streams + spliced target→impostor→return sequences (X, M), leakage checks | `benchmark/` |
| E sweep_val | every grid cell of every mechanism on validation | `sweeps/sweep_val.csv` |
| F select | matched operating points, SHA-256 frozen before test | `operating_points.csv`, `.frozen.json` |
| G evaluate | selected cells on test (+val), sanity checks, test frontier | `participant_metrics.csv`, `sequence_metrics.csv`, `transition_metrics.csv`, `mechanism_metrics.csv` |
| H stats | Friedman + Kendall W + Nemenyi, Wilcoxon + Holm, bootstrap CIs, rank-biserial | `statistical_tests.csv`, `friedman_ranks.csv` |
| I report | tables, figures, metadata, report | `tables/`, `figures/`, `experiment_metadata.json`, `RESULTS_REPORT.md` |

Dataset: ExtraSensory (60 participants; regular-cadence cohort, 1 frame ≈ 60 s). Classifier:
per-user HistGradientBoosting on phone accelerometer + gyroscope, Platt-calibrated on validation.
Mechanisms: `docs/Stage2/MECHANISM_DEFINITIONS.md`. Metrics: `docs/Stage2/METRIC_DEFINITIONS.md`.
Operating point: pooled validation false-lock rate 1 per 8 h (±15%), mean false-lock duration ≤ 30 frames,
lowest validation detection delay. Statistics: unit of analysis = genuine user.

## Run
```bash
pip install -r requirements.txt
python -m pytest -q tests                                     # 79 tests, ~1 min
python scripts/run_experiment.py --config configs/pilot.yaml  # ~2 min
python scripts/check_reproducibility.py --config configs/pilot.yaml
python scripts/run_experiment.py --config configs/main.yaml   # primary run (resumable)
```
Google Colab: open `notebooks/stage2_colab.ipynb` and run all cells.
Options: `--until <stage>`, `--force <stage…|all>`, `--label`, `--data-dir`; env `CA_DATA_DIR`, `CA_WORK_DIR`.
Failures are classified (DATA / CODE / DEPENDENCY / METHODOLOGY / COMPUTATION / REPRODUCIBILITY)
and recorded in `results/<label>/failures.json`.

## Configurations
| Config | Status | Purpose |
|---|---|---|
| `configs/main.yaml` | primary | pre-registered design |
| `configs/pilot.yaml` | pilot | 8 genuine users; pipeline and runtime check |
| `configs/sens_motion_dynamics.yaml` | sensitivity | drops absolute-level motion features (device-fingerprint check) |
| `configs/sens_original_features.yaml` | sensitivity | Stage 1 feature pool incl. location / device state |
| `configs/sens_all_participants.yaml` | sensitivity | includes fragmented-cadence participants |

## Layout
`src/ca_stability/` package (config, provenance, data, audit, splits, scoring, benchmark, mechanisms/,
metrics, evaluate, stats, tables, figures, report, pipeline, cli) · `configs/` · `scripts/` · `tests/`
(incl. synthetic end-to-end and leakage-injection tests) · `notebooks/` · `data/` (raw data git-ignored)
· `results/` (committed outputs) · `work/` (git-ignored caches keyed by config hash).

## Limitations
Spliced transitions (not real hand-overs); one phone per participant (device cues may ease impostor
detection); ~1-min decision cadence; student-heavy convenience sample; validation-matched operating
point transfers imperfectly to test; finite grids. Details in each run's report.

## Reproducibility
Fixed master seed (all streams derived with SHA-256), MD5-verified data, config hash + code fingerprint +
git SHA in `experiment_metadata.json`, operating points hashed before test, and an automated
re-run comparison (`scripts/check_reproducibility.py`) that requires identical outputs.
