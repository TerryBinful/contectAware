# Viva presentation — Stage 2

A 10-minute MSc dissertation viva deck for *Does the Handover Margin Earn Its Place?*,
built on the **official Postgraduate Viva 12-slide template**. All twelve official
headings are unchanged.

| File | What it is |
|---|---|
| `CSCD601_Viva_Presentation.pptx` | The deck. 12 slides, 4:3, speaker notes on every slide |
| `CSCD601_Viva_Presentation.pdf` | PDF export, for a machine without PowerPoint |
| `REHEARSAL_GUIDE.md` | **Start here.** Per-slide purpose, spoken script, key point, likely panel questions with grounded answers, timings, and the structural note |
| `AUDIT_AND_QA.md` | Every number traced to its source CSV; the QA checks; one flagged discrepancy |
| `build_deck.py` | Regenerates the deck from the official template and the frozen figures |
| `build_deck_legacy_template.py` | The earlier build against the lecture-slide template supplied before the official one. Kept for reference; not a deliverable |
| `assets/` | The unmodified official template, the earlier template, and the published figures with white space cropped |

## Before the viva

1. Replace `[Student Name]` and `Supervisor: [Name]` on slide 1 — the only placeholders.
2. Read `REHEARSAL_GUIDE.md` and rehearse slide 9 aloud. That is the slide the viva turns
   on.

## How it was built

The deck is not a redesign or a look-alike. `build_deck.py` opens the issued template and
replaces only the **body** of each slide, so the headings, slide order, slide master,
theme, background artwork, footers, slide numbers and University of Ghana furniture are
all inherited.

Measured from the template and followed exactly: **Arial** on every run (the template
overrides the theme's Calibri), 36 pt non-bold white titles, 21 pt body in `#232323`,
navy `#000066`, gold rule `#B08B57`, navy band 0.29–1.40 in, body box (0.50, 1.75)
9.00 × 4.95 in. The only addition is theme accent 2 (`#C0504D`, already in the template's
colour scheme), reserved for one job — marking the policy under test.

Two official headings carry a slightly different reading for an experimental project:
`System / Model Design` holds the decision rule and the factorial rather than a system
architecture, and `Implementation Work Done` holds the experimental pipeline rather than
an application. Both are explained in the rehearsal guide, since a panel may ask.

## Numbers

Every value on a slide was recomputed from
`experiment_Files/Stage2/results/mechanism_comparison_v2/analysis/` rather than copied
from the manuscript. Nothing under `analysis/` was modified and no experiment was rerun.
One manuscript-versus-CSV discrepancy was found in the moving-average row of §4.3 — it
does not appear on any slide, and `AUDIT_AND_QA.md` records it for correction before
submission.

```bash
cd docs/Stage2/presentation && python3 build_deck.py
soffice --headless --convert-to pdf --outdir . CSCD601_Viva_Presentation.pptx
```
