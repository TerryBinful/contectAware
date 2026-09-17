# Pre-registration — Decision-Layer Stabilisation Comparison

**Status:** DRAFT — fill every `[ ]`, date it, and freeze before running Experiment 2. Do not edit after freezing; append amendments with dates instead.

**Frozen on:** `[YYYY-MM-DD]`
**Frame period (from 05_cadence_check.py):** `[  ]` seconds (median), `[  ]` s (IQR)

---

## 1. Research questions

- **RQ1.** At a matched genuine-lockout rate, do decision-layer stabilisation mechanisms differ in impostor-detection latency?
- **RQ2.** Does a dual-threshold + dwell-time policy derived from cellular handover (hysteresis) outperform single-parameter smoothers and published trust/sequential models on that trade-off?
- **RQ3.** Is any hysteresis advantage attributable to the joint effect of margin and dwell (asymmetry), rather than either component alone?
- **RQ4.** Do findings differ between cross-context (X) and context-matched (M) impostors?

## 2. Hypotheses (state the null explicitly)

| | Hypothesis | Null |
|---|---|---|
| H1 | Mechanisms differ in ANIA-time at matched ANGA-time | ANIA-time distributions coincide across mechanisms within CIs |
| H2 | Hysteresis ANIA-time < each single-parameter smoother (MA, EWMA, MV, dwell-only, margin-only) | No difference or hysteresis worse |
| H3 | Hysteresis advantage disappears under margin-only and under dwell-only | Advantage persists under one component alone |
| H4 | ANIA-time is longer in condition M than X for every mechanism | No difference |

## 3. Primary comparison (ONE, to control multiplicity)

- Mechanism A: hysteresis (margin + dwell)
- Mechanism B: `[best single-parameter smoother on VALIDATION — name it here before test]`
- Operating point: genuine false-lock rate = `[e.g. 1 per 8 h]` (ANGA-time target)
- Condition: `[M — context-matched, unless justified otherwise]`
- Test: paired Wilcoxon signed-rank across users on median ANIA-time; α = 0.05
- Secondary comparisons: all others, Holm-corrected

## 4. Fixed design decisions

| Decision | Value | Rationale |
|---|---|---|
| Classifier | Gradient Boosting, hyperparameters: `[n_estimators, depth, lr, seed]` | Held fixed across all mechanisms |
| Enrolment protocol | One model per genuine user; impostor users in training ∩ test = ∅ | Subject-disjoint verification |
| Split | Per-user chronological 60/20/20; impostor-user split `[list UUIDs or seed]` | |
| Imputation | Median, fitted on training fold only | |
| Feature selection | RF Gini, fitted on training fold only; top `[k]` | |
| SMOTE | Training fold only, after split | |
| Calibration | `[Platt / isotonic / none]` on validation fold | Margins defined on calibrated P |
| Splice block lengths L | {3, 10, 30, 60} min | |
| Sequences per user per condition | ≥ `[10]` | |
| Per-user minimum test frames | `[  ]` | Users below are excluded and listed |
| ANGA-time target for matching | `[  ]` false locks per hour | |
| Parameter sweep grids | see 03_mechanism_reference.md §Grids | Selected on validation ONLY |

## 5. Outcome measures (defined once, here)

- **ANGA-time**: mean minutes of genuine use between false locks (genuine segments only).
- **ANIA-time**: minutes from impostor-block onset to first sustained lock (sustained = `[n]` consecutive locked frames). Report median and P90.
- **Miss rate**: fraction of impostor blocks with no lock before block end, per L.
- **Recovery time**: minutes from impostor-block end to restored authentication.
- **Ping-pong rate**: sign-alternating transitions within `[W]` frames, per hour. Reported alongside ANGA-time, never instead of it.
- **Calibration**: Brier score, reliability diagram (engine only).

## 6. Falsification criteria (commit now)

- **H2 falsified if:** the best single-parameter smoother's median ANIA-time is within `[Δ]` minutes of hysteresis at the matched point and the paired test is non-significant, in condition M.
- **Handover framing dropped if:** H3 null holds (one component alone reproduces the effect), OR trust model / SPRT dominates hysteresis across the sweep.
- **"Mechanism matters" (H1) rejected if:** all mechanism curves lie within each other's bootstrap CIs across the ANGA-time range `[  ]` to `[  ]`.

## 7. What will be reported regardless of outcome

Full sweep tables for every mechanism; per-user ANIA-time distributions; excluded users and why; the research-evolution statement (S1→S8); all negative results.

## 8. Analyst degrees of freedom explicitly closed

No metric will be added after test-set results are seen. No mechanism will be added after test-set results are seen. No operating point will be changed after test-set results are seen. Any deviation is appended below with a date and reason.

### Amendments
- `[date] — [what changed] — [why]`
