# FINAL PROTOCOL AUDIT — corrected Stage 2 mechanism comparison

Scope: the corrected final run in `results/mechanism_comparison/`. The pre-correction run is archived,
clearly labelled exploratory, in `results/stage2_exploratory_pre_calibration_fix/` and must not be mixed
with these results. Run-specific counts are in `reports/STAGE2_FINAL_CORRECTED_EXECUTION_REPORT.md`.

## 1. Research question

How do different temporal decision-layer stabilisation mechanisms affect the security, temporal stability
and responsiveness of continuous smartphone authentication decisions under comparable operating conditions?

## 2. Primary cohort

Regular-cadence ExtraSensory participants. Fragmented participants are not in the primary experiment; the
cohort switch (`"cohort"` in the config) supports them as a secondary robustness analysis, not yet run.

## 3. Participant eligibility

≥95% of consecutive gaps within 59–61 s and ≥1,500 frames → 31 of 60 participants. Rule and per-participant
evidence: `results/dataset_audit/` and `manifests/participant_classification.csv`.

## 4. Chronological split

Each enrolled user's frames are ordered by timestamp and split 60/20/20 into enrolment, calibration and test.
`protocol.temporal_split` asserts max(enrolment ts) < min(calibration ts) and max(calibration ts) < min(test ts);
identical timestamps cannot straddle a cut. No random row-level splitting is used anywhere.

## 5. Impostor-pool construction

All 60 participants are partitioned by seed into three disjoint pools: fitting (24), calibration (12), test (24).
For each enrolled user the user itself is removed from every pool. Final-test impostors therefore appear in
neither fitting nor calibration. Verified programmatically per run (`tests/test_leakage.py`), not by comment.

## 6. Feature set

Primary: `F3_NO_LOC_NO_DEVSTATE` (phone motion, audio, ambient). Location and device-state features are excluded
as a **methodological control against contextual and device-state shortcuts**, motivated by the Stage 1 finding
that the original model relied on GPS altitude and a missingness artefact. This is a control, **not** a
demonstration that excluding them is universally harmless: the Stage 2 ablation covering 13 of 31 users found a
small AUC difference (0.998 vs 0.997), which is incomplete evidence and is reported as such. `F1_ALL` is retained
as a sensitivity condition in the Stage 2 ablation infrastructure.

## 7. Preprocessing

Median imputation and RobustScaler, both fitted on **training rows only** (the enrolled user's enrolment frames
plus fitting-pool impostor rows). No SMOTE; class balance is handled with sample weights. No interpolation,
forward-fill, backfill or resampling of observations anywhere in the pipeline.

## 8. Score generation

One GradientBoostingClassifier per enrolled user, trained once and reused by **all nine mechanisms**. No mechanism
refits, re-tunes or re-preprocesses the model, and no mechanism sees test labels. For a given user and sequence
every mechanism consumes the identical score stream (verified: identical sequence sets per mechanism).

## 9. Score normalisation

Raw decision variable = classifier log-odds (`decision_function`), because predicted probabilities compress to
~1e-5 out of sample and destroy threshold resolution. Log-odds are then mapped through an ECDF fitted on
**calibration scores only**. Both transforms are strictly monotone, so ranking, ROC and AUC are unchanged, and no
test data enter the normaliser.

## 10. Calibration procedure

Calibration sequences are built from the enrolled user's calibration partition plus impostors from the calibration
pool. Every mechanism's parameter grid is scored on these sequences alone. Test sequences are never used for
parameter selection, and parameters are frozen before test evaluation (verified: one parameter set per user and
mechanism across all test sequences).

## 11. Exact operating-point rule

Target frame-level FAR = 0.05, tolerance 0.01. A candidate is **feasible iff 0.04 ≤ calibration FAR ≤ 0.06**
(two-sided; the earlier one-sided rule admitted FAR ≈ 0 and is the defect corrected in this run). Among feasible
candidates: closest calibration FAR to 0.05, then lower calibration FRR, then simpler parameters. If no candidate
is feasible, the nearest achievable candidate is used and the record stores
`feasible_operating_point_exists = false`, the achievable FAR range, and whether the nearest candidate lies above
or below the interval. Infeasible cases are counted per mechanism in the execution report.

## 12. Mechanism parameter ranges

Thresholds: quantiles of the pooled calibration scores, refined with calibration **impostor**-score quantiles
spanning FAR ∈ [target − 3·tol, target + 3·tol], so the grid is dense where matching actually happens.
Secondary parameters: moving average w ∈ {3,5,10,20}; EWMA α ∈ {0.1,0.2,0.3,0.5}; majority vote (w,k) ∈
{(3,2),(5,3),(5,4),(10,6),(10,8)}; debounce n ∈ {2,3,5,10}; margin ∈ {0.05,0.1,0.2,0.4}; hysteresis margin ∈
{0.05,0.1,0.2} × TTT ∈ {2,3,5,10} frames; trust model gain ∈ {0.1,0.3,0.6} × decay ∈ {0,0.05,0.2}; SPRT
A,B ∈ {1,2,4,8,16} with Gaussian score models estimated on calibration data only.

## 13. Identity-transition construction

**Controlled identity-transition sequences constructed from real participant observations.** Each sequence is
[genuine 60 frames | impostor 60 frames | genuine recovery 60 frames]; every block is a contiguous run of real
observations (consecutive gaps ≤ 90 s) from one participant. Blocks are spliced and the splice points are
recorded; genuine and recovery blocks never share frames. These are **not** naturally observed handovers.

## 14. Temporal units

Frames. The measured ExtraSensory cadence is ~1 observation per minute (median gap 60 s), so one frame ≈ one
minute. The legacy "TTT = 3 seconds" interpretation is not used anywhere.

## 15. Initial state

AUTHENTICATED. Sequences begin with a genuine block, modelling a session that starts with the enrolled user
present. Recorded in every result file.

## 16. Security metrics

Frame-level FAR and FRR with false-accept and false-reject counts, computed on held-out test sequences at the
calibration-selected parameters. "EER" is never computed as (FAR+FRR)/2; the true ROC-based EER implementation
is used where an EER is reported.

## 17. Stability metrics

State transitions; transitions per 100 frames; flip events (a state change with another change within 3 frames);
mean and median state-run length; fraction of frames authenticated. The legacy overlapping four-frame "episode"
metric is not used. Definitions are unit-tested.

## 18. Responsiveness metrics

Detection latency: frames from the genuine→impostor transition to a stable rejected state **inside the impostor
block** — the detection and its whole confirmation window must precede the recovery transition; otherwise the
sequence is a detection failure and latency is NA, never 0. Recovery latency: measured from the impostor→genuine
recovery transition. Detection and recovery success rates are reported alongside the latencies. Lockout frames
and fraction during genuine periods.

## 19. Statistical analysis

Unit of analysis is the enrolled user: sequence metrics are averaged within user before comparison, so frames are
not treated as independent. Paired Wilcoxon signed-rank tests of each mechanism against the instantaneous
baseline, Holm-corrected across the eight comparisons per metric, with bootstrap 95% CIs. Tests are fixed in
`scripts/analyse_mechanism_comparison.py` in advance, not selected after inspecting results.

## 20. Leakage checks

`tests/test_leakage.py` runs against the generated artefacts and fails on violation: pool disjointness; fitting
never touching test impostors; enrolled user never their own impostor; test impostors drawn only from the unseen
pool; genuine/recovery block disjointness; no duplicate genuine timestamps; block contiguity; identical sequence
sets across mechanisms; no duplicated rows; calibration recorded for every user and mechanism; parameters fixed
at calibration; the matched FAR interval genuinely enforced for feasible cases; infeasible cases recorded; seed
and git commit recorded.

## 21. Exclusions and failures

Recorded per run in `failures.json` (absent when none) and summarised in the execution report.

## 22. Software and environment

Python 3.12.3, numpy 2.0.2, pandas 2.2.2, scikit-learn 1.6.1, scipy 1.18.1, matplotlib. Captured per run in
`experiment_metadata.json` together with the git commit.

## 23. Reproducibility

```bash
python scripts/run_dataset_audit.py --data <csv_dir> --out results/dataset_audit
python scripts/run_mechanism_comparison.py --config configs/mechanism_comparison.json --data <csv_dir> --out results/mechanism_comparison
python scripts/analyse_mechanism_comparison.py --out results/mechanism_comparison
python tests/test_mechanisms.py && python tests/test_leakage.py results/mechanism_comparison
```
Seed, config path, dataset path, git commit and environment are stored in `experiment_metadata.json`.
Dataset: ExtraSensory primary feature files (not committed; MD5 of the archive `9e44b3484b74cd8a370ff22894e0899b`).

## 24. Known limitations

1. Cadence ~1 frame/minute: no sub-minute responsiveness claim is possible; latencies are in minutes.
2. Identity transitions are controlled splices of real observations, not observed device handovers.
3. Feature control excludes location and device state; the supporting ablation is incomplete (13 of 31 users).
4. Cohort is 31 regular-cadence participants; fragmented participants are unrepresented in the primary run.
5. Parameter grids are finite; a mechanism can be limited by grid resolution.
6. Where no feasible operating point exists, that mechanism/user pair is not matched to the common operating
   point and its security/stability comparison is correspondingly weaker.
7. Frame-level metrics only; no user-perceived usability was measured.
8. One score-generator family (gradient boosting); mechanism behaviour under other score distributions is untested.
