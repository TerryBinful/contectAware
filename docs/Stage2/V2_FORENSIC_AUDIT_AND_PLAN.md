# Stage 2 v2 — Forensic Audit and Next-Step Plan

Audit date: 2026-09-26. Repository `TerryBinful/contectAware`, `main` at `0e1ef97`.
Auditor scope: preregistration↔implementation correspondence, score-dump provenance, operating-point
selection, metric implementations, statistical reproducibility, primary-criterion mechanics, repository
consistency. **No experimental code was changed during this audit.**

Method: every number below was recomputed from the committed output files or read from the committed
source. Claims taken from `V2_RESULTS.md` without independent recomputation are marked *(reported)*.

---

## Part A — Current repository state

### Complete

| Item | Evidence |
|---|---|
| Preregistration frozen before any v2 code | `4802aa5`, commit contains only `docs/Stage2/PREREGISTRATION_v2.md` |
| Analysis code frozen before any v2 score existed | `f42f55c`; `docs/Stage2/V2_ANALYSIS_IMPLEMENTATION_NOTES.md` states no dump existed at writing |
| F3 and F7 score dumps, 31 users each | `results/mechanism_comparison_v2/{f3,f7}/scores/*.parquet`, 31 files each |
| v2 confirmatory analysis executed | `results/mechanism_comparison_v2/analysis/`, `0e1ef97` |
| Analysis code identical to freeze | `git diff --stat f42f55c 0e1ef97 -- src scripts configs` → **empty**. Verified in this audit, not taken on trust |
| Run metadata | `confirmatory: true`, `analysis_code_dirty: false`, seed 20260918, 31 users, `primary_criterion_met: false`, SHA-256 of all three analysis files |
| Primary verdict generated mechanically | `primary/PRIMARY_DECISION.md` written by the script, not by hand |
| v1 exploratory results archived separately | `results/stage2_exploratory_pre_calibration_fix/` with `ARCHIVED_README.md` |

### Incomplete at the time of the audit — all closed on 2026-09-26 except (3)

1. ~~`moving_average` batch simulator does not reproduce the v1 reference class~~ — **fixed and re-run**
   (`d39ee79`, B1).
2. ~~No factorial sensitivity at FAR 0.03 / 0.07~~ — **run as declared secondary sensitivity**
   (`secondary/factorial_far_0.03/`, `factorial_far_0.07/`; §4.2 rules, identical criterion).
3. Literature verification (Part D) has not been performed at any point in the project. **This is the one
   outstanding item and the next phase of work.**

### Superseded — retained, correctly labelled

| Artefact | Status |
|---|---|
| `results/mechanism_comparison/` (v1 corrected run, 31 users) | Superseded as *primary*; still valid exploratory evidence |
| `results/stage2_exploratory_pre_calibration_fix/` | Pre-correction v1; archived with provenance note |
| `results/{primary,pilot,pilot_mechanism,costprobe}/` | Stage 2 ablation and pilots; supporting only |
| `docs/Stage2/STAGE2_FINAL_CORRECTED_EXECUTION_REPORT.md`, `STAGE2_SENSITIVITY_ANALYSIS_REPORT.md` | Describe v1 rules; **now superseded by v2 but not marked as such** (Part B, B5) |

---

## Part B — v2 audit findings

### B0. Rule-by-rule correspondence: preregistration ↔ implementation

| Rule | Preregistration | Implementation | Result |
|---|---|---|---|
| C1 selection band | `target − tol ≤ FAR ≤ target` (one-sided) | `src/decision_v2.py:256` `lo, hi = target - tol, target` | **Match** |
| C1 ordering | min calib FRR, then complexity | `:269` `sorted(elig, key=(frr[i], complexity, far[i], i))` | **Match** (two extra deterministic tie-breaks, disclosed in notes I3) |
| C1 no substitution | infeasible → record, never substitute | `:265–267` returns `(None, rec)` with `feasible=False` | **Match** |
| C2 reachability | reject accept-threshold > max achievable score, structural only | `:215–232`; `S_MAX = 1.0`; trust via fixed point; SPRT via LLR increment | **Match**; no recovery-rate floor present |
| C3 calibration impostors | round-robin over all 12; 24 sequences | `src/benchmark.py` `round_robin`; verified 11–12 distinct impostors/user | **Match** |
| C4 SPRT grid | log-spaced A,B over [0.5,64] 15×15, δ ∈ [−2,2] 21 | `:149–151` `geomspace(0.5,64,15)`, `linspace(-2,2,21)` | **Match** |
| C5 metrics | excess transitions, <2-transition rate, failure rates, censored latencies | `:293–307` `sequence_metrics_v2` | **Match** |
| C5 detection bound | detection + confirmation window inside impostor block | `src/metrics.py:53,64,83` `block_end=recovery_idx` | **Match** |
| C6 trust variant | `trust_model_single`, τ_lo = τ_hi = 0.5 | `family_grid` `tau_lo=0.5, tau_hi=0.5` | **Match** |
| §3 factorial levels | m ∈ {0,.05,.1,.2} × k ∈ {1,2,3,5,10}, θ only tuned | `:147–148`; `factorial_grid` varies θ alone | **Match** |
| §3.1 cell selection | calibration FRR only, per user | `scripts/decision_layer_offline.py:156–164` sorts on `calib_FRR` | **Match**; no test quantity enters |
| §3.1 criteria | Holm across 2 comparisons; mean diff < 0; upper 95% CI < +0.02 | `:196–205`, `NI_MARGIN = 0.02` | **Match** |
| §5 statistics | participant unit, Wilcoxon zsplit, Holm within family, 2000-sample bootstrap | `:142–147`, `N_BOOT = 2000`, `D.holm` | **Match** |
| §4.1 mechanism count | "nine mechanisms" | `FAMILY_ORDER` has **ten** (adds `trust_model_single` per C6) | **Discrepancy — cosmetic** (B4) |

No rule was found to be violated, weakened, or silently reinterpreted. The reachability filter and the
one-sided band are both genuinely enforced.

### B1 — `moving_average` did not reproduce the v1 reference semantics — **RESOLVED 2026-09-26 (`d39ee79`)**

> **Post-fix status.** `_moving_mean` now computes a windowed `np.mean` bit-for-bit. A deterministic
> regression test (`test_moving_average_matches_numpy_mean_on_exact_ties`) was added and **verified to fail
> against the previous implementation**. The offline analysis was re-run on the unchanged frozen dumps.
> **Classified as a secondary-analysis implementation defect.** Measured impact after re-running:
> the preregistered primary factorial and primary tests are **bit-for-bit identical** (md5 unchanged on
> `primary/cell_selection.csv`, `primary/primary_tests.csv`, `primary/frr_difference_curve.csv`,
> `factorial/*.csv`); in the secondary tuned-family table **only the `moving_average` row moved**
> (FRR 0.057885 → 0.060305, FAR 0.046729 → 0.047088; excess transitions, detection failure and recovery
> failure unchanged), the other nine families are identical, and **no significance flipped** in
> `families/statistical_tests.csv`. The original finding is preserved below for the record.

* **File / function:** `experiment_Files/Stage2/src/decision_v2.py:33` `_moving_mean`
* **Preregistered rule:** §2.1 keeps the v1 mechanism families unchanged; `V2_ANALYSIS_IMPLEMENTATION_NOTES.md`
  asserts the batch simulators "must reproduce the v1 classes exactly", verified frame-by-frame.
* **Implementation:** the window mean is computed by cumulative sum,
  `(c[t+1] − c[lo]) / n`, which differs from `np.mean` of the same window by ~7×10⁻¹⁶.
* **Impact, measured on the actual v2 F3 dumps** (8 users, 4,780 (sequence, θ, w) combinations):
  * **106 combinations (2.22%)** produce a different state sequence from `src/mechanisms.MovingAverage`;
  * **952 of 860,400 frame decisions (0.111%)** differ.
  * Cause: θ candidates are score quantiles, so a window mean lands *exactly* on a threshold far more often
    than with random floats; the ~1e-16 offset then flips `>= θ`.
* **Why the bundled test missed it:** `tests/test_decision_v2.py::test_batch_simulators_match_reference_classes`
  uses random score streams, in which exact ties essentially never occur. The test passes 9/9 while the
  defect is live.
* **Scope:** `moving_average` appears **only** in the secondary tuned-family comparison. The primary
  factorial uses `margin_dwell`, which is unaffected. **The primary conclusion does not depend on this.**
* **Severity:** important, not blocking.
* **Recommended action:** replace `_moving_mean` with a windowed `np.mean`, add a tie-inducing fixture to the
  equivalence test, and re-run `decision_layer_offline.py` (**~1.5 min, no model refit**). Record it as a
  DEVIATION that restores stated semantics rather than changing a rule.

*Note on provenance:* this defect was identified in the previous session and a fix was verified locally, but
that fix was never committed. The v2 analysis therefore ran with the unfixed version.

### B2 — The stability test is at a floor; the null rests on FRR, not on stability — **IMPORTANT (interpretive)**

Recomputed from `factorial/participant_metrics.csv` and `primary/cell_selection.csv`:

| Quantity | H vs D (n = 30) |
|---|---|
| Users tied on excess transitions | **20** |
| …of which both cells score exactly 0 | **16** |
| Effective non-tied pairs driving the Wilcoxon | **10** |
| Mean excess transitions | H 0.203, D 0.332 |

With 20 of 30 pairs tied, criterion 1 has very little power, and its p = 0.69 should **not** be read as
evidence that hysteresis and dwell-only are equivalent in stability. It is largely a floor effect: at the
FRR-optimal operating point both already emit ~0 excess transitions.

The conclusion nevertheless holds, because it does not depend on criterion 1. **Criterion 2 fails
decisively and in the informative direction:** FRR difference +0.074, 95% CI [0.032, 0.119], excluding
zero. Hysteresis is measurably *worse* on false rejection than dwell-only at matched FAR. That is a
positive finding, not an absence of evidence.

* **Severity:** important for wording, not a defect.
* **Recommended action:** state the null as "no detectable additional stability benefit, alongside a
  measurable FRR cost", and report the tie count and effective n whenever criterion 1's p-value is quoted.

### B3 — min-FRR selection picks the mildest hysteresis — **IMPORTANT (interpretive)**

Selected cells (recomputed):

* `cell_H`: `m0.05_k2` ×12, `m0.05_k3` ×8, `m0.05_k5` ×6, `m0.1_k2` ×3, `m0.1_k3` ×1 — **m = 0.05 for 26 of 30**
* `cell_D`: `m0_k2` ×25 of 30

Because C1 minimises calibration FRR and stronger stabilisation raises FRR, the rule necessarily selects
the weakest qualifying hysteresis and the weakest qualifying dwell. The primary comparison therefore asks
*"does hysteresis add value at the FRR-optimal operating point?"* — not *"can any hysteresis configuration
beat any dwell configuration?"*

This is preregistered and defensible, and the factorial surface answers the broader question
descriptively: the lowest-excess cells are all strong hysteresis, at severe cost —
`(0.2, 2)`: excess 0.000, FRR 0.356, recovery failure 0.604 (8 users feasible).

* **Severity:** important for claim discipline.
* **Recommended action:** carry this sentence explicitly in the results write-up; do not let the null be
  read as "hysteresis never helps stability at any setting".

### B4 — Preregistration says nine mechanisms, implementation runs ten — **COSMETIC**

`FAMILY_ORDER` includes `trust_model_single`, added under C6 as a disclosure control. Consistent with C6,
inconsistent with §4.1's wording.
**Action:** amend §4.1 to "nine families plus the `trust_model_single` disclosure variant". Do not remove
the variant.

### B5 — Superseded v1 reports are not marked superseded — **COSMETIC**

`docs/Stage2/STAGE2_FINAL_CORRECTED_EXECUTION_REPORT.md`, `STAGE2_SENSITIVITY_ANALYSIS_REPORT.md` and
`FINAL_PROTOCOL_AUDIT.md` describe the v1 symmetric-band rules, the v1 SPRT infeasibility (23/31) and the
v1 stability framing. A reviewer reading them in isolation would take superseded claims as current — most
consequentially "SPRT is structurally infeasible", which **v2 refutes** (SPRT feasible 31/31).
**Action:** add a one-line superseded banner at the top of each, pointing to `V2_RESULTS.md`. Do not delete.

### B6 — Duplicate score dump — **COSMETIC, safe to resolve**

`experiment_Files/Stage2/stage2_v2_scoredump_f3_results/f3` is **byte-identical** to
`results/mechanism_comparison_v2/f3` (verified with `diff -rq`, no differences).
**Action:** safe to delete or move to an archive path; nothing references it. Verified redundant, as the
instruction required, before recommending removal.

### B7 — v1-rule CSVs inside the v2 results area — **COSMETIC, already disclosed**

`f3/operating_points.csv` and `f3/sequence_metrics.csv` were written by the refit driver under the v1
symmetric rule and are **not** inputs to the v2 analysis. `V2_RESULTS.md` discloses this.
**Action:** rename to `*_v1rule_not_used.csv` or move under `f3/unused_v1rule/` so the disclosure survives
without depending on a reader finding the note.

### Findings not substantiated

I looked for, and did **not** find: test information entering calibration or cell selection; mechanism-specific
refitting; final-test impostors in the fitting or calibration pools; failed events silently dropped from
denominators (`detection_failure` / `recovery_failure` are explicit columns, and censored latencies carry a
flag and a cap); the legacy overlapping-episode metric; or any post-hoc test.

---

## Part C — Statistical audit

**Verdict: the reported v2 conclusions are fully reproducible and, with the two wording qualifications in
B2 and B3, defensible.**

Recomputed from `factorial/participant_metrics.csv` + `primary/cell_selection.csv`, independently of the
script's own summary:

| Quantity | My recomputation | `primary_tests.csv` | Match |
|---|---|---|---|
| H vs D, n paired | 30 | 30 | ✓ |
| H vs D, excess mean diff | −0.1294 | −0.129444 | ✓ |
| H vs D, Wilcoxon p (raw) | 0.4748 | 0.474788 | ✓ |
| H vs D, ties / H / D | 20 / 6 / 4 | (reported 20 / 6 / 4) | ✓ |
| H vs D, FRR diff [95% CI] | +0.0744 [0.032, 0.119] | +0.074417 [0.032407, 0.118676] | ✓ |
| H vs M, n paired | 24 | 24 | ✓ |
| H vs M, excess mean diff | −0.1993 | −0.199306 | ✓ |
| H vs M, Wilcoxon p (raw) | 0.3438 | 0.343785 | ✓ |
| H vs M, FRR diff [95% CI] | +0.0304 [−0.008, 0.069] | +0.030365 [−0.007621, 0.068850] | ✓ |
| Holm adjustment | max(2×0.3438, 0.4748) = 0.6876 both | 0.68757 both | ✓ |
| F3 vs F7 AUC | 0.9901 / 0.7585, diff 0.2317 [0.191, 0.273] | 0.990 / 0.758, 0.232 [0.191, 0.273] | ✓ |
| Infeasible combos at FAR 0.05 | **7 of 310** | — | recomputed |

Procedural checks:

* **Pairing** is at enrolled-user level; sequences are averaged within user before any test. Frames are
  never treated as independent.
* **Ties** use `zero_method='zsplit'`, matching v1 and disclosed.
* **Unequal feasible sets** are handled by dropping users lacking either cell of a pair, and the counts are
  recorded (`n_users_without_H`, `n_users_without_comparator`) — not silently imputed.
* **Missing latencies** are reported both conditionally and censored at the block cap with a flag.
* **Holm** is applied within the declared family of two comparisons, as preregistered.

Primary criterion mechanics: criterion 1 fails on both comparisons (Holm p = 0.69), criterion 2 fails on
both, criterion 3 passes on both. The script requires all three on both comparisons, so the verdict
"Hysteresis offers no measurable advantage over its components on this benchmark" **follows mechanically**.
I reproduced the boolean chain and it is correct.

**One substantive improvement over v1 worth recording:** infeasibility fell from 32/279 combinations (v1,
symmetric band) to **7/310** (v2, one-sided band + reachability filter), and SPRT moved from 23/31
infeasible to 0/31. The one-sided band did not cost feasibility; it improved it.

---

## Part D — Literature plan

Not yet performed at any stage. The purpose is an evidence-based novelty assessment, not support-hunting.

| # | Target claim to test | Query focus | Why it matters |
|---|---|---|---|
| 1 | **Kill-shot search:** a prior matched-operating-point comparison of multiple temporal decision-layer mechanisms in continuous/behavioural authentication, evaluated on identity-transition sequences | "comparison of decision fusion / temporal smoothing policies continuous authentication", "operating point matched behavioural biometrics", replication of the Raghu 2023 myoelectric template in authentication | If found, the methodological contribution collapses. Must be searched first and adversarially |
| 2 | Hysteresis / dwell / Time-to-Trigger in behavioural authentication | Mondal & Bours 2017; Kiyani 2020; handover-inspired thresholds | The *original* absence claim is already falsified; confirm the refined claim survives |
| 3 | SPRT in continuous authentication | sequential testing, Wald, trust accumulation | v2 makes SPRT a notable secondary finding; need prior art before any wording |
| 4 | Continuous-authentication metrics: ANGA/ANIA, usability–security trade-off, transition/chatter measures | Are "excess transitions" and "detection/recovery failure" already standardised under other names? | Avoids claiming novelty for a renamed metric |
| 5 | ExtraSensory used for *authentication* rather than activity recognition | Vaizman et al.; downstream reuse | Establishes whether per-user identity modelling on this dataset is itself novel or already done |
| 6 | Device/sensor-availability shortcuts and missingness leakage in mobile sensing | missingness as identity signal, device fingerprinting via sensor availability | Frames the F3/F7 result (AUC 0.758 from missingness alone) against known work |

Deliverable: a short table of verified papers with what each does and does **not** cover, and an explicit
statement of which of the two candidate contributions (methodological framework vs empirical null) survives.

---

## Part E — Is another experiment necessary?

**No. Stage 2 should be frozen, not expanded.** One free correction is recommended first.

| Option | Verdict |
|---|---|
| Re-run `decision_layer_offline.py` after fixing B1 | **Do this.** ~1.5 min, no model refit, closes the only implementation defect. Changes at most 0.11% of frame decisions in the secondary analysis; the primary factorial cannot change |
| Refit the score generators | **Not necessary.** No defect found in fitting, splitting, pooling or preprocessing |
| Factorial at FAR 0.03 / 0.07 | **Optional.** Family results already exist at all three targets; extending the factorial decision is cheap and would strengthen the robustness claim. Preregister it as a declared sensitivity, not a second chance at the primary |
| New mechanisms, datasets, deep learning, subgroup search | **No.** Explicitly out of scope, and the null is a legitimate result |
| Anything aimed at making the primary criterion pass | **No.** The criterion was preregistered and the result stands |

The v2 result is not fragile: the FRR cost of hysteresis versus dwell-only has a CI excluding zero, and
the qualitative ordering of the factorial surface (persistence captures most of the stabilisation; stronger
stabilisation costs FRR and recovery) is visible across many cells, not a single comparison.

---

## Part F — Thesis plan

Proposed structure, ordered so the null lands as a finding rather than a failure.

1. **Introduction and problem.** Decision instability in continuous authentication; the ping-pong framing;
   the cellular-handover analogy as the *motivating* idea, stated as a hypothesis to be tested.
2. **Related work.** Continuous/implicit authentication; contextual sensing; temporal smoothing and
   stabilisation policies; hysteresis and dwell; sequential tests; evaluation metrics. Refined gap:
   absence of a *matched-operating-point comparison evaluated on identity transitions*. No absence claim
   about hysteresis itself (falsified — cite Mondal & Bours 2017, Kiyani et al. 2020).
3. **Stage 1: audit of the original pipeline.** What it did, that it reproduces exactly, and the eight
   validity defects. Framed as provenance and reconstruction evidence, not as results. Cite
   `docs/Stage1/`.
4. **Methodology: a temporally valid evaluation framework.** The separation of score generation from the
   decision layer; chronological splits; participant-disjoint pools with unseen test impostors;
   controlled identity-transition sequences built from real observations; frame-based temporal units
   (~1 min/frame, measured); security / stability / responsiveness separated; explicit missed-event
   accounting. **This is the primary methodological contribution.**
5. **Stage 2 v1: exploratory development.** The corrected run and the three defects an independent review
   found (D1 selection, D2 unreachable re-entry, D3 calibration size). Explicitly exploratory.
6. **Preregistration v2.** The frozen rules, the "hysteresis earns its place" criterion, the null
   commitment, and the audit trail that shows the code was frozen before the scores existed.
7. **Results.** Primary factorial first: the null, with tie count and effective n (B2) and the mildest-cell
   qualification (B3). Then the factorial surface as the substantive finding — persistence captures most
   of the stabilisation; stronger stabilisation buys stability with FRR and recovery failure. Then
   secondary tuned families, flagged for unequal selection optimism, with SPRT as a notable secondary
   result and **not** a headline. Then F3/F7 construct validity.
8. **Discussion.** What the framework can and cannot establish. The trade-off is the result. Hysteresis is
   not vindicated, and did not need to be.
9. **Limitations.** ~1-minute cadence, so no sub-minute claims; controlled splices, not observed
   handovers; each participant used their own phone, so an impostor block is also a device change, and
   missingness alone reaches AUC 0.758 — a residual shortcut that this dataset cannot fully separate;
   31 regular-cadence participants; finite grids; shared test impostor pool limiting strict independence;
   7 infeasible operating points.
10. **Conclusion and future work.** Same-device impostor data; live deployment; sequential policies as the
    indicated next direction.

**Framing to adopt:** the study tested whether a handover-inspired hysteresis mechanism adds temporal
stabilisation beyond its own components and, under preregistered conditions, it did not; temporal
persistence accounted for most of the benefit, and stronger stabilisation imposed security and
responsiveness costs. State it plainly. It is a better thesis than a rescued positive.

---

## Recommended order of work

1. Fix B1, add the tie-inducing test, re-run the offline analysis, record the deviation. *(~15 min, no refit.)*
2. Apply the cosmetic corrections B4–B7 (banners, renames, duplicate removal, §4.1 wording).
3. Update `EXPERIMENT_STATUS.md`, which still predates v2.
4. Literature verification per Part D.
5. Freeze Stage 2 and begin the results and discussion chapters.

## What still requires researcher judgement

1. Whether to extend the factorial to FAR 0.03 / 0.07 as a declared sensitivity, or freeze at 0.05 only.
2. Whether `stage2_v2_scoredump_f3_results/` is deleted or archived (verified redundant either way).
3. Whether the thesis leads with the methodological framework or the empirical null as its primary
   contribution — this is a framing decision the literature verification should inform.

---

# STAGE 2 FREEZE — 2026-09-26

Stage 2 is closed. Experimentation stops here. The next phase is literature verification, then writing.

## What was done at close-out (`d39ee79` onward)

| # | Action | Outcome |
|---|---|---|
| 1 | Fixed `_moving_mean` to a bit-for-bit `np.mean`; added a deterministic tie-inducing regression test, verified to fail against the old code; re-ran **only** the offline decision layer | 10/10 + 18/18 tests pass. No dump regenerated, no model refitted, no calibration rule touched, `PREREGISTRATION_v2.md` unchanged |
| 2 | Verified the preregistered primary is unaffected | `primary/` and `factorial/` outputs **bit-for-bit identical** pre- and post-fix. Only the `moving_average` row of the secondary table moved; no significance flipped |
| 3 | Ran FAR 0.03 and 0.07 through the **identical** §3.1 criterion, labelled secondary | Verdict unchanged at all three targets. Generated decision files state explicitly that they are not the primary |
| 4 | Archived rather than deleted; added `results/PROVENANCE.md`; banners on three superseded v1 documents | Duplicate dump moved to `results/archive/…__duplicate_of_f3`; v1-rule CSVs quarantined under `f3/unused_v1rule/` |
| 5 | Updated this document | B1 marked resolved with measured post-fix evidence |

## Final confirmatory result

**Primary (FAR 0.05, preregistered):** *Hysteresis offers no measurable advantage over its components on
this benchmark.* Criterion 1 not met (Holm p = 0.69 both comparisons), criterion 2 not met (FRR
+0.074 [0.032, 0.119] vs dwell-only; +0.030 [−0.008, 0.069] vs margin-only), criterion 3 met.

## Declared sensitivity (secondary, §4.2) — the verdict is stable, the reason is not

| Target | H vs D excess (Holm p) | H vs M excess (Holm p) | Crit. 1 | Crit. 2 (FRR upper bound) | Verdict |
|---|---|---|---|---|---|
| 0.03 | −0.251 (0.075) | −0.278 (0.179) | not met | not met (+0.108 / +0.061) | no advantage |
| **0.05 (primary)** | −0.129 (0.688) | −0.199 (0.688) | not met | not met (+0.119 / +0.069) | **no advantage** |
| 0.07 | −0.351 (**0.008**) | −0.688 (**0.008**) | **met** | not met (+0.056 / +0.060) | no advantage |

This must be reported carefully. At the loosest target hysteresis **does** show a statistically detectable
reduction in excess transitions — consistent with the floor effect documented in B2, since a looser
operating point leaves more instability to remove. But the FRR non-inferiority requirement fails at
**every** target, so the preregistered conjunctive criterion is not met anywhere. The correct statement is
that the null holds across the operating-point range examined, and that at looser targets hysteresis buys
stability at an FRR cost rather than for free. **It is not a licence to report FAR 0.07 as a hysteresis
win.**

## Freeze conditions

* Frozen inputs: `mechanism_comparison_v2/{f3,f7}/scores/` — immutable, produced at `f42f55c`, seed 20260918.
* Frozen rules: `docs/Stage2/PREREGISTRATION_v2.md`, unmodified since `4802aa5`.
* Analysis code is **no longer byte-identical to the freeze** `f42f55c`; it differs by the three items in
  `d39ee79`, each recorded there and none of which alters a preregistered rule. Anyone re-verifying should
  diff `f42f55c..d39ee79` over `src/`, `scripts/`, `tests/` and read that commit message as the deviation log.
* Reproduction: one command, ~70 s, no refit — see `results/PROVENANCE.md`.

## Out of scope from here (agreed)

No new mechanism, dataset, model family, subgroup analysis or confirmatory hypothesis. No further attempt to
make the primary criterion pass. The null is the result.

## Thesis framing (agreed position)

The contribution is **the methodological framework and the preregistered comparison**: separation of
authentication-score generation from the decision layer; chronological genuine separation; participant-disjoint
pools with unseen test impostors; controlled identity-transition sequences built from real observations;
frame-based temporal parameters grounded in the measured ~1 min cadence; security, stability and
responsiveness reported separately with explicit missed-event accounting; participant-level paired inference;
and a preregistered, conjunctive decision criterion with a committed null.

The **principal empirical result** is the null: a cellular-handover-inspired hysteresis mechanism did not
demonstrate additional temporal stabilisation beyond its own components (dwell and margin) under these
conditions. Temporal persistence alone accounted for most of the observed reduction in excess transitions
(instantaneous 2.012 → dwell k=2 0.466 per sequence), and stronger stabilisation traded stability for
false rejection and recovery failure.

Frame it as neither a failed proposal nor a claim that any mechanism is universally superior. The hysteresis
hypothesis was tested properly and not supported; the trade-off structure is the finding; SPRT is a notable
secondary observation whose larger search space precludes a headline claim; and the F3/F7 probe
(AUC 0.990 vs 0.758) leaves missingness as a stated residual construct-validity limitation that this dataset
cannot fully resolve.

## Next phase

1. Literature verification per Part D, adversarial kill-shot search first.
2. Novelty assessment against what that search returns.
3. Results and discussion chapters on the frozen record above.
