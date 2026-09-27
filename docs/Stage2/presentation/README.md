# Viva presentation — Stage 2

A 10-minute MSc dissertation viva deck for *Does the Handover Margin Earn Its Place?*,
built on the supplied departmental PowerPoint template.

| File | What it is |
|---|---|
| `CSCD601_Viva_Presentation.pptx` | The deck. 11 slides, 4:3, speaker notes on every slide |
| `CSCD601_Viva_Presentation.pdf` | PDF export, for a machine without PowerPoint |
| `REHEARSAL_GUIDE.md` | **Start here.** Per-slide purpose, spoken script, key point, likely panel questions with grounded answers, timings, and the structural note |
| `AUDIT_AND_QA.md` | Every number traced to its source CSV; the QA checks; one flagged discrepancy |
| `build_deck.py` | Regenerates the deck from the template and the frozen figures |
| `assets/` | The unmodified template, and the published figures with white space cropped |

## Before the viva

1. Replace `[Name]` and `[Supervisor]` on slide 1 — the only placeholders in the deck.
2. Confirm the projector aspect ratio. **The deck is 4:3**, matching the supplied
   template. On a 16:9 projector it letterboxes with bars at the sides; it does not
   crop or distort. Converting is a one-line change if the department prefers 16:9.
3. Read `REHEARSAL_GUIDE.md` and rehearse slide 7 aloud. That is the slide the viva
   turns on.

## How it was built

The deck is not a redesign. `build_deck.py` opens the supplied template, removes its
four sample slides, and adds new ones on the template's own layouts, so the slide
master, theme, colour scheme, Calibri type, navy and gold background artwork and
University of Ghana furniture are all inherited rather than reproduced.

Measured from the template and reused unchanged: navy `#000066`, gold rule `#B2875A`,
title band 0.32–1.53 in, 44 pt centred white titles, 28 pt body, logo at (7.75, 6.99).
The only addition is theme accent 2 (`#C0504D`, already in the template's colour
scheme) reserved for one job — marking the policy under test.

## Numbers

Every value on a slide was recomputed from
`experiment_Files/Stage2/results/mechanism_comparison_v2/analysis/` rather than copied
from the manuscript. Nothing under `analysis/` was read-modified and no experiment was
rerun. One manuscript-versus-CSV discrepancy was found in the moving-average row of
§4.3 — it does not appear on any slide, and `AUDIT_AND_QA.md` records it for correction
before submission.

```bash
cd docs/Stage2/presentation && python3 build_deck.py
soffice --headless --convert-to pdf --outdir . CSCD601_Viva_Presentation.pptx
```
