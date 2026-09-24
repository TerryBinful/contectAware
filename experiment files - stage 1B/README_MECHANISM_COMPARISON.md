# Post-pivot experiment — decision-layer mechanism comparison

## Research question

> Under a common authentication-score generator and matched operating conditions, how do alternative
> temporal decision-layer stabilization mechanisms differ in their effects on authentication security,
> temporal decision stability, and responsiveness during identity transitions?

## Hypothesis (working, not assuming a winner)

> Alternative decision-layer stabilization mechanisms will exhibit different trade-offs between temporal
> authentication stability, authentication security, and response latency when evaluated at comparable
> operating points on controlled identity-transition sequences.

A null result (mechanisms indistinguishable after operating-point matching) is a valid outcome and is
reported as such.

## Dataset

ExtraSensory primary feature files (Vaizman, Ellis & Lanckriet), 60 participants, 377,346 observations,
225 features. Not committed (≈748 MB); see `README.md` §4 for the download and checksum. The measured
cadence is **~1 observation per minute** (`results/dataset_audit/`), so all temporal parameters are in
**frames** (1 frame ≈ 1 minute). The legacy "TTT = 3 seconds" is not used.

## Participants

- Eligibility: ≥95% of consecutive gaps in 59–61 s and ≥1,500 frames → **31 participants** (primary cohort).
- Fragmented participants are excluded from the primary run and retained for secondary robustness
  (`configs/stage2_secondary_fragmented.json` provides the cohort switch).
- Split: each enrolled user's frames are divided chronologically 60/20/20 into enrolment / calibration / test.
- Impostor pools: participants are partitioned into three **disjoint** sets — fitting (24), calibration (12),
  test (24). Final-test impostors are unseen during fitting and calibration. Saved in
  `results/mechanism_comparison/manifests/participant_split.json`.

## Score generator (fixed; not the contribution)

One gradient-boosting model per enrolled user, trained on that user's enrolment frames plus rows from the
fitting impostor pool. Imputer and scaler are fitted on training rows only; no SMOTE. The **same** model
produces the score stream consumed by all nine mechanisms; no mechanism-specific preprocessing exists.

Two measured properties drive two documented implementation decisions:
1. Predicted probabilities compress to ~1e-5 out-of-sample, so the raw decision variable is the
   **log-odds** (`decision_function`) — a strictly monotone transform (AUC unchanged).
2. Scores are then mapped through an **ECDF fitted on calibration scores only** to put every user on a
   common [0, 1] scale — also strictly monotone, and no test data are involved.

Primary feature set: `F3_NO_LOC_NO_DEVSTATE` (phone motion, audio, ambient), excluding location and
device-state. Justification is empirical: in the Stage 2 ablation (13 users), removing those groups changed
AUC from 0.998 to 0.997, so the exclusion removes contextual-shortcut risk at negligible cost.
`F1_ALL` remains available as a secondary sensitivity analysis.

## Mechanisms (all in `src/mechanisms.py`, unit-tested in `tests/`)

| # | Mechanism | Parameters searched |
|---|---|---|
| 1 | instantaneous threshold | θ |
| 2 | moving average | θ, w ∈ {3,5,10,20} |
| 3 | EWMA | θ, α ∈ {0.1,0.2,0.3,0.5} |
| 4 | majority vote | θ, (w,k) ∈ {(3,2),(5,3),(5,4),(10,6),(10,8)} |
| 5 | debounce | θ, n ∈ {2,3,5,10} |
| 6 | margin / dual threshold | θ, margin ∈ {0.05,0.1,0.2,0.4} |
| 7 | hysteresis | θ, margin ∈ {0.05,0.1,0.2}, TTT ∈ {2,3,5,10} frames |
| 8 | trust model | θ, gain, decay (bounded accumulator, τ_lo=0.4, τ_hi=0.6) |
| 9 | SPRT | A, B ∈ {1,2,4,8,16}; Gaussian score models estimated on calibration only |

Common interface: `reset()`, `update(score, t)`, `state`, `diagnostics()`. Initial state = authenticated.

## Benchmark

Each sequence is `[genuine 60 frames | impostor 60 frames | genuine recovery 60 frames]`, every block a
contiguous run of real observations (gaps ≤ 90 s) from one participant. Blocks are spliced and the splice
points are recorded; nothing is interpolated, resampled or synthesised, and genuine and recovery blocks
never share frames. 6 sequences per user, deterministic given dataset, split, seed and config.

## Operating point

All mechanisms are matched to a common target **frame-level FAR = 0.05 (± 0.01)** on calibration
sequences. Identical selection rule for every mechanism: closest calibration FAR to target subject to the
constraint; tie-break by lower calibration FRR, then by simpler parameters. Test sequences are never used
for tuning. Achieved calibration operating points are recorded per user in `operating_points.csv`.

## Metrics

- **Security:** FAR, FRR, false-accept frames, false-reject frames.
- **Stability:** state transitions, transitions per 100 frames, flip events (a change with another change
  within 3 frames), mean/median state run length, fraction of frames authenticated.
- **Responsiveness:** detection latency (frames to a stable locked state after the identity transition),
  recovery latency, lockout frames/fraction during genuine periods.
- The legacy "567 oscillation episodes" definition is not used; the flip-event definition is unit-tested.

## Statistical analysis

Unit of analysis is the enrolled user (sequences averaged within user). Paired Wilcoxon signed-rank tests
of each mechanism against the instantaneous baseline, Holm-corrected across the 8 comparisons per metric,
plus bootstrap 95% CIs. Tests are fixed in `scripts/analyse_mechanism_comparison.py` in advance.

## Execution

```bash
python scripts/run_mechanism_comparison.py \
    --config configs/mechanism_comparison.json \
    --data /path/to/extrasensory/csv \
    --out results/mechanism_comparison [--resume] [--max-users N]

python scripts/analyse_mechanism_comparison.py --out results/mechanism_comparison
python tests/test_mechanisms.py            # 15 unit tests
```
Colab: `colab/Stage2_ExtraSensory_Colab.ipynb` (same driver pattern; set the mechanism-comparison config).

## Results

`results/mechanism_comparison/`: `mechanism_metrics.csv`, `participant_metrics.csv`, `sequence_metrics.csv`,
`transition_metrics.csv`, `statistical_tests.csv`, `operating_points.csv`, `score_generator_manifest.csv`,
`benchmark/sequence_manifest.csv`, `manifests/`, `experiment_metadata.json`, `figures/`, `tables/`, `logs/`.

## Limitations

1. ~1-minute cadence: nothing can be said about sub-minute responsiveness; latencies are in minutes.
2. Impostor blocks are spliced from a different participant's contiguous recording; the splice is a
   modelled identity transition, not an observed handover.
3. The score generator's out-of-sample probability compression means the operating point must be defined
   on calibration quantiles; absolute score values are not interpretable.
4. Mechanism parameter grids are finite; a mechanism could be disadvantaged by grid resolution.
5. Primary cohort is the regular-cadence subset; fragmented participants are not represented.
6. Results are frame-level; no user-perceived usability measurement is claimed.

## Reproducibility

Config `configs/mechanism_comparison.json`, seed in the config, git commit recorded in
`experiment_metadata.json` of each run directory, environment recorded per run.
