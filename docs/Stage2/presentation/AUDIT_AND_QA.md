# Deck audit and QA report

For `CSCD601_Viva_Presentation.pptx`, built on the **official Postgraduate Viva 12-slide
template**. Every number that appears on a slide is traced to the frozen analysis output
it came from, and the QA checks were run against the built file rather than the source.

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
| 6 | Cohort size | 31 participants | Manuscript §3.1; `families/mechanism_metrics.csv` `n_users_feasible` max = 31 |
| 7 | Sequence structure | 60 / 60 / 60 frames | `f3/scores/*.parquet`: `transition_idx` 60, `recovery_idx` 120, 180 frames |
| 7 | Figure 5 transitions | 43 / 13 / 5 | `figures/checks/fig5_sequence_schematic_checks.json` |
| 7 | Margin levels | 0, 0.05, 0.10, 0.20 | `factorial/response_surface.csv` `margin` |
| 7 | Dwell levels | 1, 2, 3, 5, 10 | `factorial/response_surface.csv` `dwell` |
| 6 | FAR target and band | 0.05, feasible 0.04–0.05 | `factorial/operating_points.csv` `target_FAR` 0.05, `tolerance` 0.01 |
| 9 | Non-inferiority bound | +0.02 | `PREREGISTRATION_v2.md`; `NI_MARGIN` in `scripts/decision_layer_offline.py` |
| **9** | Participants paired | 30 / 24 | `primary/primary_tests.csv` `n_users_paired` |
| **9** | Excess-transition difference | −0.13 / −0.20 | `primary_tests.csv` `excess_diff_mean` = −0.129444 / −0.199306 |
| **9** | Median difference | 0 / 0 | `primary_tests.csv` `excess_diff_median` |
| **9** | Holm-adjusted p | 0.69 / 0.69 | `primary_tests.csv` `p_holm` = 0.68757 both |
| **9** | FRR difference vs dwell | +0.074 [0.032, 0.119] | `primary_tests.csv` `FRR_diff_mean` 0.074417, `lo` 0.032407, `hi` 0.118676 |
| **9** | FRR difference vs margin | +0.030 [−0.008, 0.069] | `primary_tests.csv` 0.030365, −0.007621, 0.068850 |
| **9** | Detection-failure difference | 0.000 / −0.007 | `primary_tests.csv` `detfail_diff_mean` |
| **9** | 20 of 30 tied | 20 / 30 | Manuscript §4.2; `factorial/participant_metrics.csv` paired at target 0.05 |
| 8 | Instantaneous (0, 1) | 2.012 excess, FRR 0.042 | `factorial/response_surface.csv`, target 0.05 |
| 8 | Dwell (0, 2) | 0.466 excess, FRR 0.052 | same |
| 8 | Margin + dwell (0.20, 2) | 0.000 excess, FRR 0.356 | same |
| 8 | Zero-transition cell support | 8 participants | `response_surface.csv` `n_users_feasible` for m 0.20 / k 2 |
| 8 | Feasible-set range | 6 to 31 | `figures/checks/fig1_factorial_surface_checks.json` |
| 9 | Margin + dwell | 0.20 excess, FRR 0.124 | `families/mechanism_metrics.csv` 0.2028, 0.1244 |
| 9 | Trust model (dual τ) | 0.04 excess, FRR 0.172 | same: 0.0376, 0.1717 |
| 9 | Nine temporal mechanisms | 9 + instantaneous = 10 rows | `families/mechanism_metrics.csv` |
| 11 | Sequences with no excess | 71.7% | `families/sequence_metrics.csv`: 124 of 173 |
| 11 | Top-5 share | 65.6% | same, per-participant means |
| 11 | Participants | 5 of 30 | same |
| 11 | Mean AUC F3 → F7 | 0.990 → 0.758 | `secondary/score_validity_summary.json` |
| 11 | Paired AUC difference | 0.232 [0.191, 0.273] | same, `diff` |
| 10 | p, FRR penalty, bound | 0.69, +0.074, +0.02 | as slide 9 |

All values were recomputed directly from the CSV and JSON files in
`experiment_Files/Stage2/results/mechanism_comparison_v2/analysis/` rather than copied
from the manuscript. No experiment was rerun and nothing under `analysis/` was modified.

### Values quoted in the speaker notes but not on a slide

| Note | Value | Source |
|---|---|---|
| Slide 9 — sensitivity rank correlations | 0.84 at FAR 0.03, 0.89 at 0.07 | Recomputed: 0.8384, 0.8936 (`tables/tables.md` Table 7) |
| Slide 9 — dwell raises FRR 0.042 → 0.052 | +0.010 | `response_surface.csv` |
| Slide 9 — trust model rejects 17% | FRR 0.1717 | `families/mechanism_metrics.csv` |

---

## 3. Citation check

The deck names three sources on slides. All three were verified against primary sources
during the citation audit (`docs/Stage2/CITATIONS_VERIFIED.md`).

| Slide | Cited as | Verified | Note |
|---|---|---|---|
| 5 | Zeeshan et al. (2025), EWMA "to stabilize decisions and avoid flickering" | **Yes** — exact quote, §3.6.5, *Sensors* 25(18) 5711 | The slide says "use EWMA", not "use hysteresis". The paper never uses the word hysteresis, so the deck does not attribute one to it |
| 5 | Mondal and Bours (2015), four factors, action-domain measures | **Yes** — *Information Sciences* 304:28–53 | Title in the manuscript reference list is correct; the deck makes no claim about matched operating points on their behalf |
| 5 | Sugrim et al. (2019), equal-error-rate comparison uninformative | **Yes** — NDSS 2019, quote in the citation audit | The deck does not claim they say a fixed point is *sufficient*, which would overstate them |

No citation appears on a slide that was not verified. The reference list is in the
manuscript; a wall-of-references slide was deliberately omitted.

---

## 4. QA report

Checks run programmatically against the built `.pptx`, not against the source script.

| # | Check | Result |
|---:|---|---|
| 1 | Slide count matches the official template | **12** |
| 2 | All eleven official headings unchanged (slides 2–12) | **Pass** — verified string-for-string against the issued template |
| 3 | `hysteresis` never appears on a slide | **Pass** — zero occurrences |
| 4 | Overclaiming vocabulary: `significant`, `best`, `proves`, `real-world`, `optimal` | **Pass** — zero occurrences |
| 5 | `biometric identity` | 1 occurrence, slide 4, inside the scope line *excluding* that claim. Retained deliberately |
| 6 | Placeholders `[VERIFY]`, `[FIG]`, `TODO`, `TBD` | **Pass** — zero |
| 7 | Intentional metadata placeholders | `[Student Name]`, `Supervisor: [Name]` on slide 1 only |
| 8 | Primary null present on slides 9, 10 and 11 | **Pass** |
| 9 | FRR-inferiority present on slides 9 and 10 | **Pass** |
| 10 | Limitations precede the conclusion | **Pass** — both on slide 11, limitations first, conclusion in the closing band |
| 11 | Slide 9 notes state failure to reject ≠ equality | **Pass** — "failure to reject is not proof of equivalence" |
| 12 | Slide 11 notes carry the evidence-not-established sentence | **Pass** — verbatim |
| 13 | Slide 9 labels SPRT exploratory | **Pass** |
| 14 | Every slide has speaker notes | **Pass** — 12 of 12, 62–174 words |
| 15 | Deliverable in ~10 minutes without reading from slides | **Pass** — 1,363 spoken words ≈ 9 min 45 s at 140 wpm; the template's own budget is 45–50 s per main slide |
| 16 | Figures unaltered | **Pass** — the published renders are used as-is; only surrounding white space was cropped. No axis, value or caption changed |
| 17 | No text runs off a slide or collides with a panel | **Pass** — all 12 slides rendered to PNG and inspected; six collisions found and fixed |

### Notes on template fidelity

| Item | Decision |
|---|---|
| **Headings** | All eleven official headings on slides 2–12 are byte-identical to the issued template. Only slide 1's `[Project Title]` was replaced, which is what that placeholder is for |
| **Typography** | The template overrides the theme: it sets **Arial** explicitly on every run, 36 pt non-bold white titles, 21 pt body in `#232323`. All new text follows those values. The theme's nominal Calibri is not used, because the template does not use it |
| **Aspect ratio** | 4:3 (10 × 7.5 in) — the official template's own size. The earlier 16:9 question is settled |
| **Slide 1 addition** | A one-line finding was placed in the empty band the template leaves between the title and the subtitle. Nothing was moved or resized to make room |
| **Inherited artefact** | On the title slide the template's own white `Rectangle 3` overlaps part of the University of Ghana logo beneath it. This is in the issued file and was left as-is. Deleting that one shape fixes it, if the department is happy for it to be removed |
| **Two headings read differently here** | `System / Model Design` holds the decision rule and factorial rather than a system architecture, and `Implementation Work Done` holds the experimental pipeline rather than an application. Explained in `REHEARSAL_GUIDE.md`, since a panel may ask |
| **Body text sizes** | 12–21 pt depending on the slide. The template's 21 pt applies to full-width bullet lists (slides 2–6, 12); slides pairing a figure with text use 13–17 pt so nothing overflows the official body box |

---

## 5. Reproducing the deck

```bash
cd docs/Stage2/presentation && python3 build_deck.py
soffice --headless --convert-to pdf --outdir . CSCD601_Viva_Presentation.pptx
```

`build_deck.py` opens `assets/official_template.pptx` — the issued 12-slide template,
unmodified — and replaces only the body of each slide. The headings, slide order, slide
master, theme, background artwork, footers, slide numbers and University of Ghana
furniture are inherited, never recreated.

Figures come from `assets/*_crop.png`, which are the published renders in
`docs/Stage2/figures/rendered/` with surrounding white space removed.

`build_deck_legacy_template.py` builds the earlier version of this deck on the
lecture-slide template that was supplied before the official one was found. It is kept
for reference and is not part of the deliverable.
