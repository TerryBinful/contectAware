# Deck audit and QA report

For `CSCD601_Viva_Presentation.pptx`. Every number that appears on a slide is traced to
the frozen analysis output it came from, and the checks prescribed in the deck brief
were run against the built file rather than against the source text.

---

## 1. One discrepancy found — flagged, not silently resolved

The manuscript's tuned-family table (§4.3) reports **moving average** with
**FRR 0.058** and **censored recovery latency 5.0 frames**. The frozen CSV gives
**0.0603** and **5.28**.

| Value | Manuscript §4.3 | `families/mechanism_metrics.csv` | Gap |
|---|---:|---:|---:|
| Moving average, FRR | 0.058 | 0.0603 | 0.0023 |
| Moving average, recovery latency (censored) | 5.0 | 5.28 | 0.28 |

Every other value in that table — all nine other mechanisms, across excess transitions,
FRR, test FAR, recovery failure and recovery latency — matches the CSV exactly.

**Most likely cause.** `moving_average` is the one mechanism affected by the
secondary-analysis defect fixed at Stage 2 close-out: the windowed mean was accumulated
with `np.cumsum`, which differs from `np.mean` by about 7e-16 and flipped `>= θ` at
exact ties (2.22% of sequence/θ/window combinations; 0.111% of frame decisions). See
`experiment_Files/Stage2/src/decision_v2.py` and `docs/Stage2/figures/CHECKS.md`. The
manuscript row appears to predate that fix.

**How the deck handles it.** Neither number appears on any slide. The deck cites moving
average only as an unlabelled marker inside Figure 2, which is generated from the
current CSV and is therefore correct. **No action is required for the viva**, but the
manuscript row should be corrected to 0.060 and 5.3 before submission. Nothing in the
argument depends on it: `moving_average` belongs to the secondary descriptive family
comparison, not the preregistered primary test.

---

## 2. Numerical audit — every figure shown on a slide

| Slide | Claim on the slide | Value | Source |
|---:|---|---|---|
| 5 | Cohort size | 31 participants | Manuscript §3.1; `families/mechanism_metrics.csv` `n_users_feasible` max = 31 |
| 5 | Sequence structure | 60 / 60 / 60 frames | `f3/scores/*.parquet`: `transition_idx` 60, `recovery_idx` 120, 180 frames |
| 5 | Figure 5 transitions | 43 / 13 / 5 | `figures/checks/fig5_sequence_schematic_checks.json` |
| 6 | Margin levels | 0, 0.05, 0.10, 0.20 | `factorial/response_surface.csv` `margin` |
| 6 | Dwell levels | 1, 2, 3, 5, 10 | `factorial/response_surface.csv` `dwell` |
| 6 | FAR target and band | 0.05, feasible 0.04–0.05 | `factorial/operating_points.csv` `target_FAR` 0.05, `tolerance` 0.01 |
| 6 | Non-inferiority bound | +0.02 | `PREREGISTRATION_v2.md`; `NI_MARGIN` in `scripts/decision_layer_offline.py` |
| **7** | Participants paired | 30 / 24 | `primary/primary_tests.csv` `n_users_paired` |
| **7** | Excess-transition difference | −0.13 / −0.20 | `primary_tests.csv` `excess_diff_mean` = −0.129444 / −0.199306 |
| **7** | Median difference | 0 / 0 | `primary_tests.csv` `excess_diff_median` |
| **7** | Holm-adjusted p | 0.69 / 0.69 | `primary_tests.csv` `p_holm` = 0.68757 both |
| **7** | FRR difference vs dwell | +0.074 [0.032, 0.119] | `primary_tests.csv` `FRR_diff_mean` 0.074417, `lo` 0.032407, `hi` 0.118676 |
| **7** | FRR difference vs margin | +0.030 [−0.008, 0.069] | `primary_tests.csv` 0.030365, −0.007621, 0.068850 |
| **7** | Detection-failure difference | 0.000 / −0.007 | `primary_tests.csv` `detfail_diff_mean` |
| **7** | 20 of 30 tied | 20 / 30 | Manuscript §4.2; `factorial/participant_metrics.csv` paired at target 0.05 |
| 8 | Instantaneous (0, 1) | 2.012 excess, FRR 0.042 | `factorial/response_surface.csv`, target 0.05 |
| 8 | Dwell (0, 2) | 0.466 excess, FRR 0.052 | same |
| 8 | Margin + dwell (0.20, 2) | 0.000 excess, FRR 0.356 | same |
| 8 | Zero-transition cell support | 8 participants | `response_surface.csv` `n_users_feasible` for m 0.20 / k 2 |
| 8 | Feasible-set range | 6 to 31 | `figures/checks/fig1_factorial_surface_checks.json` |
| 9 | Margin + dwell | 0.20 excess, FRR 0.124 | `families/mechanism_metrics.csv` 0.2028, 0.1244 |
| 9 | Trust model (dual τ) | 0.04 excess, FRR 0.172 | same: 0.0376, 0.1717 |
| 9 | Nine temporal mechanisms | 9 + instantaneous = 10 rows | `families/mechanism_metrics.csv` |
| 10 | Sequences with no excess | 71.7% | `families/sequence_metrics.csv`: 124 of 173 |
| 10 | Top-5 share | 65.6% | same, per-participant means |
| 10 | Participants | 5 of 30 | same |
| 10 | Mean AUC F3 → F7 | 0.990 → 0.758 | `secondary/score_validity_summary.json` |
| 10 | Paired AUC difference | 0.232 [0.191, 0.273] | same, `diff` |
| 11 | p, FRR penalty, bound | 0.69, +0.074, +0.02 | as slide 7 |

All values were recomputed directly from the CSV and JSON files in
`experiment_Files/Stage2/results/mechanism_comparison_v2/analysis/` rather than copied
from the manuscript. No experiment was rerun and nothing under `analysis/` was modified.

### Values quoted in the speaker notes but not on a slide

| Note | Value | Source |
|---|---|---|
| Slide 6 — sensitivity rank correlations | 0.84 at FAR 0.03, 0.89 at 0.07 | Recomputed: 0.8384, 0.8936 (`tables/tables.md` Table 7) |
| Slide 8 — dwell raises FRR 0.042 → 0.052 | +0.010 | `response_surface.csv` |
| Slide 9 — trust model rejects 17% | FRR 0.1717 | `families/mechanism_metrics.csv` |

---

## 3. Citation check

The deck names three sources on slides. All three were verified against primary sources
during the citation audit (`docs/Stage2/CITATIONS_VERIFIED.md`).

| Slide | Cited as | Verified | Note |
|---|---|---|---|
| 3 | Zeeshan et al. (2025), EWMA "to stabilize decisions and avoid flickering" | **Yes** — exact quote, §3.6.5, *Sensors* 25(18) 5711 | The slide says "use EWMA", not "use hysteresis". The paper never uses the word hysteresis, so the deck does not attribute one to it |
| 3 | Mondal and Bours (2015), four factors, action-domain measures | **Yes** — *Information Sciences* 304:28–53 | Title in the manuscript reference list is correct; the deck makes no claim about matched operating points on their behalf |
| 3 | Sugrim et al. (2019), equal-error-rate comparison uninformative | **Yes** — NDSS 2019, quote in the citation audit | The deck does not claim they say a fixed point is *sufficient*, which would overstate them |

No citation appears on a slide that was not verified. The reference list is in the
manuscript; a wall-of-references slide was deliberately omitted.

---

## 4. QA report

Checks run programmatically against the built `.pptx`, not against the source script.

| # | Check | Result |
|---:|---|---|
| 1 | Slide count 10–12 | **11** |
| 2 | `hysteresis` never labels the composed policy | **Pass** — 2 occurrences, both on slide 4 defining the analogy and the terminology |
| 3 | Overclaiming vocabulary: `significant`, `best`, `proves`, `proven`, `real-world`, `biometric identity`, `optimal` | **Pass** — zero occurrences on slides |
| 4 | `novel` | 1 occurrence, slide 3: "The novelty claimed is the decomposition, not the classifier, the dataset, or temporal smoothing itself" — a narrowing statement, retained deliberately |
| 5 | Placeholders `[VERIFY]`, `[FIG]`, `TODO`, `TBD` | **Pass** — zero |
| 6 | Intentional metadata placeholders | `[Name]`, `[Supervisor]` on slide 1 only, as the brief allows |
| 7 | Primary null appears on slides 7 **and** 11 | **Pass** — both |
| 8 | FRR-inferiority appears on slides 7 **and** 11 | **Pass** — both |
| 9 | Limitations precede the contribution claim | **Pass** — slide 10 before slide 11 |
| 10 | Slide 7 notes state failure to reject ≠ equality | **Pass** — "failure to reject is not proof of equivalence" |
| 11 | Slide 10 notes carry the evidence-not-established sentence | **Pass** — verbatim |
| 12 | Slide 8 notes state cells are unpaired | **Pass** |
| 13 | Slide 9 labels SPRT exploratory | **Pass** |
| 14 | Every slide has speaker notes | **Pass** — 11 of 11, 77–148 words each |
| 15 | Deliverable in ~10 minutes without reading from slides | **Pass** — 1,335 spoken words ≈ 9 min 30 s at 140 wpm |
| 16 | Figures unaltered | **Pass** — the rendered PNGs are used as published; only surrounding white space was cropped. No axis, value or caption changed |
| 17 | No text runs off a slide or collides with a panel | **Pass** — every slide rendered to PNG and inspected; five collisions found and fixed |

### Deviations from the deck brief, and why

| Brief said | Deck does | Reason |
|---|---|---|
| 16:9 widescreen | **4:3 (10 × 7.5 in)** | The master brief makes the supplied template the visual authority and forbids changing its layout conventions. The template is 4:3. Changing it would mean rebuilding the background artwork rather than inheriting it. **Flagged for the candidate** — a one-line rebuild if the department wants 16:9 |
| Minimum 36 pt titles, 28 pt body | Titles **40 pt**; body **17–24 pt** | Titles exceed the minimum. Body sits below it because the template is 4:3, so a slide is 10 in wide rather than 13.3 in, and the master's own body style is 28 pt for full-width bullet lists. Slides that pair a figure with text cannot hold 28 pt in a half-width column. Sizes were chosen per slide for legibility at projection distance |
| 70–120 words of speaker notes per slide | **77–148** | The notes are a spoken script rather than a summary, as the master brief requires. Total delivery time is the binding constraint and it is met with buffer |
| Optional slide 12 (reproducibility, commit, seed) | **Omitted** | The brief says to omit it if it crowds the scientific story. At 11 slides the talk is already at 9 min 30 s. The commit, seed and library version are in the manuscript §3.8 and the repository |

---

## 5. Reproducing the deck

```bash
cd docs/Stage2/presentation && python3 build_deck.py
soffice --headless --convert-to pdf --outdir . CSCD601_Viva_Presentation.pptx
```

`build_deck.py` opens `assets/template_source.pptx` — the supplied departmental
template, unmodified — strips its four sample slides, and adds the eleven new slides on
the template's own layouts. The slide master, theme, colour scheme, fonts, background
images and University of Ghana furniture are inherited, never reproduced, so the output
is genuinely the same deck rather than an imitation of it.

Figures come from `assets/*_crop.png`, which are the published renders in
`docs/Stage2/figures/rendered/` with surrounding white space removed.
