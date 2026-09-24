# EXPERIMENT STATUS — post-pivot mechanism comparison

Last updated: 2026-09-24. Repository `TerryBinful/contectAware`, branch `main`, commit `af89900`.

## Current research direction

> Under a common authentication-score generator and matched operating conditions, how do alternative
> temporal decision-layer stabilization mechanisms differ in authentication security, temporal decision
> stability, and responsiveness during identity transitions?

The February 2026 hysteresis claims (597 transitions, 567 → 0 episodes, 99.26%, FAR 0.53%, FRR 7.09%,
Δ = 0.0%) are treated as prior unverified claims only. Stage 1 showed they reproduce exactly from the old
code but were produced under a protocol that cannot support authentication conclusions. None of them are
carried into the post-pivot results.

## Repository inspection (performed before writing code)

| Item | Finding |
|---|---|
| Structure | `docs/`, `experiment_Files/` (legacy notebooks + Stage 1 reproduction), `experiment files - stage 1B/` (Stage 2 + post-pivot package) |
| Branch / commits | `main`; `ef16807` (legacy) → `c98c157` (Stage 1) → `87bfed0`, `2b53d43` (Stage 2) → `b8d69bb`, `af89900` (post-pivot) |
| Existing cadence code | Stage 1 `dataset_temporal_audit.py` (descriptive only). No `05_cadence_check.py` exists in the repository. Cadence logic now lives in `src/protocol.py` and is driven by `scripts/run_dataset_audit.py` — one checker, not two |
| Existing classifier code | Stage 2 `src/experiment.py` per-user pipeline. **Reused**, extended with `ScoreGenerator`/`fit_score_generator`; `run_user` untouched |
| Existing evaluation code | Stage 2 `src/evaluate.py` (reused for bootstrap CIs). Legacy Stage 1 metric function not reused (its "EER" was (FAR+FRR)/2) |
| Tests / configs | None existed before Stage 2; now `tests/`, `configs/` |
| Dependencies | numpy 2.0.2, pandas 2.2.2, scikit-learn 1.6.1, scipy 1.18.1, matplotlib. No new dependency added |
| Data | Present in the execution environment (60 files, verified MD5), **not committed** |

## Gate results

| Gate | Status | Evidence |
|---|---|---|
| Dataset access | PASS | 60 participants, 377,346 observations, schema validated |
| Cadence audit | PASS | median gap 60 s, 71.0% of gaps 59–61 s, 8.4% > 90 s → 1 frame ≈ 1 minute; `results/dataset_audit/` |
| 3-second TTT retired | DONE | all temporal parameters in frames |
| Feature audit | DONE | primary set excludes location/device-state; empirical basis: Stage 2 ablation AUC 0.998 → 0.997 |
| GB pipeline verified | DONE | Stage 1 audit + Stage 2 rebuild; no SMOTE, preprocessing fitted on training rows only, chronological splits |
| Score validity | DOCUMENTED | per-user identity score, not activity classification; log-odds + calibration-only ECDF (both monotone) |
| Participant splitting | DONE | disjoint fit(24)/calibration(12)/test(24) pools; `manifests/participant_split.json` |
| Benchmark | DONE | contiguous blocks only, splices recorded, no interpolation, genuine/recovery disjoint |
| Nine mechanisms | DONE | `src/mechanisms.py`, 15/15 unit tests |
| Operating-point matching | DONE | calibration FAR 0.05 ± 0.01, identical rule for all mechanisms |
| Pilot | PASS | 2 users; caught and fixed 2 defects (threshold rounding; block overlap) |
| Full run | **EXECUTED** | 31 users, 179 sequences, 9 mechanisms, 1,611 rows, 0 failures |
| Statistics / figures / tables | DONE | `statistical_tests.csv`, 8 figures, 4 tables |
| Push to GitHub | **BLOCKED** | no credentials in the execution environment; commits `b8d69bb`, `af89900` are local |

## Failure log

| Class | Problem | Resolution |
|---|---|---|
| CODE | Theta grid rounded to 4 d.p. collapsed all thresholds to 0.0 (scores ~1e-5) | Raw score switched to log-odds; ECDF normaliser fitted on calibration only; dense unrounded quantile grid |
| CODE | Genuine and recovery blocks could share frames | Exclusion-aware window sampling; audit column verifies 0 overlap |
| COMPUTATION | Benchmark window search too slow | Cumulative-sum start search |
| COMPUTATION | Long background jobs killed repeatedly by the sandbox | `--resume` added to both drivers; full run completed in segments |
| REPRODUCIBILITY | No GitHub credentials | Git bundle handed to the researcher |

## Outstanding decision for the researcher

The matched operating point is a fixed calibration FAR of 0.05. An alternative is to match every mechanism
to the instantaneous baseline's calibration EER. This changes the operating-point definition, so it has not
been changed unilaterally.
