# EXPERIMENT_STATUS — Stage 2 mechanism comparison

Last updated 2026-09-25. Every number below is copied from a generated file named next to it;
the authoritative source is always the file, not this page.

## A. Repository, branch, commits, files
- Repository: `TerryBinful/contectAware`, base `main` @ `7fe3066`.
- Branch: `experiment/stage2-mechanism-comparison` (local; not pushed — no credentials in the build environment).
- Commits (oldest → newest):
  - `4e67d66` scaffold;
  - `643d843` benchmark, metrics, sweeps, stats, figures, report, tests;
  - `b60c9d4` frozen pre-registration and sensitivity configs;
  - `129ee9c` pilot results;
  - `54f22d0` report decision-rule section, `compare_runs.py`, docs, notebook, manifest;
  - a final commit containing the primary and sensitivity results and this file.
- **Where the computation ran.** The computational stages of `main` ran on code identical to `54f22d0`: between `129ee9c` and `54f22d0` only `report.py`, `tables.py` and the new `compare_runs.py` changed (`git diff --stat 129ee9c 54f22d0 -- experiment_Files/Stage2/src experiment_Files/Stage2/configs experiment_Files/Stage2/scripts`). All reports were regenerated at `54f22d0`.
- **Reproducibility check.** `main` was then re-run from scratch at `54f22d0` into a fresh work directory: every scientific output was identical (`results/main/reproducibility_check.json`). The same holds for the pilot.
- **What was added.**
  - Repository root: `docs/Stage2/` (this file, pre-registration, metric and mechanism definitions) and `experiment_Files/Stage2/`.
  - `experiment_Files/Stage2/` contains `src/ca_stability/`, `configs/`, `scripts/`, `tests/`, `notebooks/stage2_colab.ipynb`, `results/`, `README.md`, `experiment_manifest.yaml`, `requirements.txt` and `pyproject.toml`.
  - `experiment_Files/05_cadence_check.py` was **extended**, not duplicated: it gained a JSON/CSV/importable API, and the analysis itself is unchanged.

### Repository inspection record (done before any code was written)
Existing assets:
- Stage 1 audit documents, including the authentication-validity criteria C1–C11;
- the planning specs: pre-registration template, splice benchmark, mechanism reference, experiment plan;
- `05_cadence_check.py`;
- the Stage 1 scripts: `reproduce_original.py`, `exp4_feature_ablation.py` (corrected HGB protocol, never run on real data), leakage diagnostics and the temporal audit.

Stage 1 established that the original 99.26% pipeline was a closed-set, randomly row-split model with location and missingness shortcuts, and that it is not a valid continuous-authentication signal. Stage 2 therefore:
- **reuses** the corrected HGB protocol and the planning specs;
- **does not reuse** the original model;
- **uses** the cadence checker instead of writing a second one.

## B. Dataset
- **Source.** ExtraSensory per-uuid archive, MD5 `9e44b3484b74cd8a370ff22894e0899b` (verified; identical to Stage 1). Raw data is not committed.
- **Size.** 60 participants and 377,346 frames; pooled median gap 60.0 s (`results/main/dataset_audit/dataset_summary.json`).
- **Cadence.** 34 participants have regular cadence and 26 fragmented, and the split is bimodal with no participant in between (`fig01_cadence.png`).
- **Primary cohort: 33 participants.**
  - 34 regular-cadence participants, minus one (`7D9BB102`) excluded because it has fewer than 300 validation and test stream frames (`eligibility.csv`).
  - The 33 act both as genuine users and as the impostor pool.
- **Primary features.** Phone accelerometer and gyroscope (52 features). Location, device-state, audio, watch and magnetometer features are excluded; the feature inventory (`feature_inventory.csv`) records which Stage 1 features each group corresponds to.

## C. Protocol actually executed
- **Participant split and classifier.**
  - Chronological 60/20/20 split per participant, with a 30-minute embargo.
  - Per genuine user, impostors split into disjoint roles: 50% train, 25% calibration, 25% test.
  - Per-user HGB model, Platt-calibrated on validation.
- **Gate:** median test AUC 0.969 ≥ 0.60, so it passed.
- **Benchmark.**
  - 172 genuine streams and 2,112 spliced sequences, split 1,056 validation and 1,056 test.
  - Context-matched coverage 1.0, so condition M was selected.
  - All 8 leakage checks passed; the sanity checks passed.
- **Mechanism sweep.** Nine primary mechanisms plus supplementary HMM, 8,337 grid cells, swept on validation.
- **Operating point.** Target 0.125 false locks/h, ±15%, with a mean false-lock duration ≤ 30 frames (amendment A1). Selected points were SHA-256-frozen before test (`operating_points.frozen.json`), and the best smoother on validation was margin.
- **Test evaluation.** Test partition evaluated at the primary target and at two sensitivity targets (0.5/h and 1/24 h).
- **Statistics.** Per participant, with n = 33 users.
- **Amendments** (full text in `PREREGISTRATION_FROZEN.md`):
  - A1: the lockout admissibility rule;
  - A2: disclosure that pilot test outputs existed before the primary run;
  - A3: the sensitivity configurations.

## D. Execution log (what ran, what failed, how it was fixed)
| When | Event | Class | Resolution |
|---|---|---|---|
| pilot | Rate-only selection chose absorbing "never unlock" cells (up to 95% of genuine time locked) | METHODOLOGY | Amendment A1, decided on pilot validation data before the pilot's evaluate stage |
| pilot | Report stage `KeyError` (column naming) | CODE | Fixed; pilot rerun from scratch |
| pilot | Reproducibility re-run | — | Identical |
| main | Primary run, all stages | — | Completed, about 2.5 minutes |
| sensitivity | Background process killed between sessions during `sens_all_participants` | COMPUTATION (environment) | Resumed from checkpoints (completed stages and cached sweeps skipped), completed |
| main | Reproducibility re-run from scratch | — | Identical |

The test-suite (79 tests) passes. It covers:
- the definition of every mechanism on the specification's fixtures;
- bit-exact agreement between the per-frame reference and vectorised implementations;
- the metric definitions;
- statistics helpers;
- a synthetic end-to-end run;
- injected-leakage tests that must fail;
- refusal to evaluate test data if `operating_points.csv` has been modified.

## E. Results (primary run; test data; medians over users; `results/main/RESULTS_REPORT.md`)
**Trade-offs at the matched operating point.** Figures are FAR_frame M / FRR_time / mean false-lock duration in frames, from tables T5 and T6:

| Mechanism | FAR_frame M | FRR_time | Mean false-lock duration (frames) |
|---|---|---|---|
| Threshold | 0.433 | 0.0011 | 1.3 |
| Moving average | 0.430 | 0.0032 | 1.7 |
| EWMA | 0.459 | 0.0029 | 2.0 |
| Majority vote | 0.400 | 0.0053 | 3.0 |
| Debounce | 0.350 | 0.0086 | 4.1 |
| Margin | 0.314 | 0.0058 | 4.0 |
| Hysteresis | 0.261 | 0.0159 | 9.2 |
| Trust | 0.346 | 0.0187 | 7.4 |
| SPRT | 0.197 | 0.0262 | 20.4 |
| HMM (supplementary) | 0.260 | 0.0210 | 15.1 |

Mechanisms that accept fewer impostor frames lock genuine users out for longer. No mechanism is best on all three families.

**Other results**
- **Detection delay:** medians are 0–2 frames (minutes) for every mechanism, so the primary outcome has little room to separate mechanisms.
- **Test false-lock rate:** 0.155–0.235/h against the validation-matched 0.125/h (T9).
- **Friedman tests:** mechanisms differ on detection delay, first lock, recovery, misses, FAR_frame, FRR_time, ping-pong and lockout. They do not differ on false locks/h (p = 0.126) or transitions/h (p = 0.191), which were matched.

**Pre-registered rules, applied mechanically** (report §7.3):
- **H1:** supported.
- **H2 (hysteresis vs margin):** detection-delay difference +0.5 frames, 95% CI −0.5 to 1, p = 0.921 → falsified.
- **H3:** not supported.
- **Handover-framing rule:** triggered by SPRT.
- **H4:** not supported (0 of 9).

**Sensitivity** (`results/SENSITIVITY_SUMMARY.md`):
- The FAR-versus-lockout trade-off pattern appears in all four runs.
- **Motion dynamics only** (absolute-level features removed): median AUC falls to 0.934 and every mechanism's FAR_frame rises. In this run H2 and H3 are *supported* (best smoother: debounce).
- **Original feature pool:** hysteresis is significantly *slower* than margin.
- **All 56 participants:** hysteresis is significantly *slower* than margin.
- **Conclusion:** the direction of the hysteresis-versus-smoother contrast depends on the score stream. It is not a stable finding.

## F. Evidence quality
**Strengths**
- Open-set, unseen impostors.
- No temporal adjacency: 0% of test frames are within 90 s of a training frame, against 95.7% in Stage 1.
- Operating points frozen before test.
- Per-participant inference with multiplicity control.
- Deterministic, verified reproduction.

**Weaknesses**
- Spliced (not real) hand-overs.
- One phone per participant, so a device-fingerprint confound is possible, and the sensitivity run shows it is material for absolute numbers.
- One-minute decision cadence.
- Ceiling effect on detection delay.
- Imperfect transfer of the operating point from validation to test.
- A student-heavy sample of 33 users.

## G. Reproducibility
- **Reproduce:** from `experiment_Files/Stage2/`, run `python scripts/run_experiment.py --config configs/main.yaml`, or use the Colab notebook.
- **Recorded provenance:** git SHA, code fingerprint, config hash, seed, dataset fingerprint, environment and stage timings are in `experiment_metadata.json`.
- **Verification:** `scripts/check_reproducibility.py` re-runs from scratch and requires identical outputs.

## H. Outstanding decisions for the researcher
1. Ratify amendment A1 (30-frame lockout cap) and the 1-per-8-hours target, or choose different values. Any change requires a new results label.
2. Framing:
   - H2 and H3 are falsified in the primary run; the handover-framing rule was triggered by SPRT in every run; the contrast's direction is design-sensitive.
   - The evidence supports a trade-off paper ("stabilisers move cost between impostor access and genuine lockout") rather than a "hysteresis is better" paper.
3. Whether the device-fingerprint concern should make the motion-dynamics feature set primary in future work. This cannot be changed for this pre-registered run.
4. Whether to add a genuine-cost criterion that includes lockout time (e.g. matching on FRR_time) in a follow-up pre-registration.
5. Push the branch: `git push -u origin experiment/stage2-mechanism-comparison`.
