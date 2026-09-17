# Execution prompt — Exp 4 feature-group ablation (paste into Claude)

Copy everything below the line into Claude (Claude Code, with the dataset and the repo on disk).

---

You are running a computational audit for an MSc dissertation on continuous smartphone
authentication. Your job is to **compute**, not to estimate, infer, or reassure.

## Absolute rules

1. **Never report a number you did not compute in this session.** Every figure in your
   final answer must be traceable to a command you ran and an output file you wrote. If
   you are tempted to state a value from reasoning or recollection, write instead:
   `EVIDENCE NOT ESTABLISHED — not computed.`
2. **Do not silently work around failures.** If a step errors, runs out of memory, or a
   file is missing, report the failure verbatim and stop that branch. Do not substitute a
   smaller sample, a different model, or a simplified protocol without saying so
   explicitly and prominently.
3. **Do not tune anything on test data.** No threshold, hyperparameter, or feature choice
   may be selected using test-partition labels or scores.
4. **Report deviations.** If you change anything about the specified protocol for any
   reason, list every deviation in a section headed `DEVIATIONS FROM SPEC`.
5. **State the unit of analysis in every aggregate.** For anything aggregated across
   participants, the unit is the participant, never the frame. Frames are autocorrelated
   at ~60 s cadence and frame-level statistics will overstate significance.
6. Print library versions, row counts, and wall time for each stage.

## Background you need (established, verified against raw outputs — do not re-litigate)

The dataset is **ExtraSensory** (UCSD): 60 users, 377,346 rows, ~60 s frame cadence,
13,505 h total span. Per-user CSVs named `<UUID>.features_labels.csv`.

An earlier pipeline (`reproduce_original.py`) built a one-vs-rest classifier for the
single highest-volume participant and reported 99.26% accuracy and 0.53% FAR, then
replayed the score stream through an instantaneous threshold and a hysteresis rule,
reducing state transitions from **597 to 49** and ping-pong windows from **567 to 0**
(Stability Index 0.9502 → 0.9959). Those numbers reproduce exactly and are not in
dispute.

What **is** established as wrong with that pipeline:

- **Random row-level split** on ~60 s series: 93.3% of the target's test rows have a
  same-user training row within 90 s. Adjacent frames are near-duplicates.
- **Closed-set impostors**: all 59 test impostors also appear in training.
- **n = 1 genuine user**, selected as the one with the most data.
- **Location dominance**: 13 of 52 selected features are location-prefixed, carrying
  ≈40% of Gini importance; `location:min_altitude` + `location:max_altitude` alone carry
  26.1%.
- **A missingness shortcut**: the target has **0%** missing altitude; impostor test rows
  are **43.8%** missing. FAR on altitude-missing impostor rows is **0.00%**; on
  altitude-present rows **0.94%**. **100%** of false accepts fell on altitude-present
  rows.
- **Preprocessing leakage**: `SimpleImputer` and `RobustScaler` were fitted on all
  377,346 rows before the train/test split.
- **Score saturation**: median genuine-stream p = 0.996; only 3.05% of frames at p ≤ 0.4
  and 2.84% in the 0.4–0.6 band.

## The question you are answering

**How much per-participant authentication performance survives when location features and
data-availability cues are removed?** If the answer is "almost none", there is no
behavioural authentication signal in this dataset to stabilise, and the project's planned
decision-layer work needs a different dataset. That verdict must be reached by
computation, not assumption, and reached now rather than later.

A critical trap to avoid: **do not run this ablation under the original protocol.** Under
a random row-level split, near-duplicate adjacent frames let *any* expressive feature set
score well by memorising neighbours, so a motion-only arm would look strong for reasons
unrelated to behaviour and would falsely exonerate the pipeline. The protocol below
removes that confound. Absolute numbers under it will be **much worse** than 0.9926
accuracy; that is expected and correct, and those two sets of numbers must never be
compared to each other.

## Task A — environment and reproduction check (do this first)

Run the existing `reproduce_original.py` (or the minimum subset of it needed) and confirm
these exact values from its `results/repro_results.json`:

| Quantity | Expected |
|---|---|
| `naive_transitions` | 597 |
| `hyst_transitions` | 49 |
| `ping_pong_count` | 567 |
| `hyst_ping_pong` | 0 |
| `stability_naive` | 0.9502 |
| `stability_hyst` | 0.9959 |
| `total_frames` | 11995 |
| `time_span_hours` | 222.32 |
| `gb_acc` | 0.9926 |

Report each as match / mismatch with the value you actually obtained. If your environment
does not reproduce these, **stop and report that**, because nothing downstream is
comparable until it does. (Logistic-regression figures may differ by ≤0.0021 because
lbfgs hits `max_iter=1000`; that is known and acceptable.)

## Task B — the ablation

Use `exp4_feature_ablation.py` if it is present in the repo (under
`experiment_Files/Stage1/`). It has been validated on synthetic data but **never run on
the real dataset** — treat its output as unverified until you have inspected it. Run:

```
python exp4_feature_ablation.py <csv_dir> --targets 10
```

If that script is not present, implement the following protocol yourself, exactly:

- **Feature pool**: columns prefixed `raw_acc`, `proc_gyro`, `location`, `discrete`. Note
  that `location` also matches `location_quick_features`.
- **Arms**:
  - `all` — the full pool
  - `no_location` — pool minus every `location`-prefixed feature
  - `motion_only` — `raw_acc` + `proc_gyro` only
  - `location_only` — `location`-prefixed only
  - `discrete_only` — `discrete`-prefixed only
  - `missingness_only` — discard every sensor **value**; use only binary "was this
    feature NaN" indicators for the full pool
- **Target participants**: the 10 with the most rows, each evaluated separately.
- **Genuine split**: chronological. Train on the earliest 60% of that participant's
  timeline by timestamp, test on the remainder, dropping a 30-minute embargo immediately
  after the boundary. Never a random row split.
- **Impostor split**: partition the other 59 users into two disjoint halves by user ID
  (seeded, reproducible). Train impostors come from one half, test impostors from the
  other. Assert and report that the intersection is empty.
- **Preprocessing**: fit `SimpleImputer(strategy='median')` then `RobustScaler()` on the
  **training partition only**, then apply to test. Drop columns that are entirely NaN in
  training. For `missingness_only`, no imputation or scaling is needed.
- **Model**: `HistGradientBoostingClassifier(max_iter=200, learning_rate=0.1,
  max_depth=6, min_samples_leaf=50, l2_regularization=1.0, class_weight='balanced')`.
  Do **not** use SMOTE; handle imbalance with class weights only.
- **No feature selection inside arms.** Selecting features separately per arm would
  confound the comparison this experiment exists to make.
- **Metrics**: primary is **EER computed threshold-free from the ROC**. Also report AUC,
  and FAR/FRR at a fixed 0.5 threshold. Per participant, per arm.
- **Statistics**: paired Wilcoxon signed-rank across participants, each arm against
  `all`, on EER. Report n, medians, median delta, statistic and p.

## Task C — targeted diagnostics (run these regardless)

1. **Missingness shortcut, quantified.** For each of the 10 target participants, compute
   the fraction of their own rows missing `location:min_altitude`, and the fraction of
   the other 59 users' rows missing it. Report the distribution, not just the target.
   Is the original target's 0% typical or exceptional?
2. **Altitude separability without a model.** Per-user median `location:min_altitude`,
   and for each target participant how many other users fall within 5 m. This bounds how
   much identity information altitude alone carries.
3. **Ambiguity-band mass.** For the best-performing arm and for `motion_only`, take each
   target participant's chronological *test* stream, produce the score sequence in
   timestamp order, and report the fraction of frames with p ≤ 0.4 and the fraction in
   0.4–0.6. This determines whether a stabilisation-mechanism comparison is even viable
   downstream: the original stream had only 2.84% in the ambiguity band, which is too
   saturated for competing mechanisms to differentiate on. Report per participant and the
   median across participants.
4. **Transitions on a valid stream.** For those same test streams at a 0.5 threshold,
   count state transitions and transitions per hour. Compare to the original's 597
   transitions over 222.32 h (2.69/h). State plainly whether instability is worse, similar
   or better once leakage is removed — computed, not predicted.

## Deliverable

Return, in this order:

1. **Task A verification table** — expected vs obtained, match/mismatch per row.
2. **Ablation table** — one row per arm: n participants, median EER, mean ± SD EER,
   median AUC, feature count.
3. **Paired statistics table** — each arm vs `all`.
4. **The four diagnostics from Task C**, with per-participant detail where specified.
5. **`DEVIATIONS FROM SPEC`** — every departure, or "none".
6. **`NOT ESTABLISHED`** — an explicit list of every question in this prompt you could
   not answer by computation, and why.
7. **Your own reading of what the numbers mean**, with interpretation clearly separated
   from the computed evidence, and explicitly flagged where you are inferring rather than
   measuring. Include the alternative explanation you consider most plausible for
   whatever pattern you find.

Attach or inline the raw JSON/CSV outputs. Do not summarise them away — I need the
underlying values, including the per-participant rows, not just the aggregates.
