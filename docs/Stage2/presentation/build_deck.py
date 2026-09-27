"""Fill the official Postgraduate Viva 12-slide template with this project's content.

The template is edited IN PLACE, not rebuilt: the file is opened, and only the body of
each slide is replaced. Every official slide heading, the slide order, the slide master,
the theme, the background artwork, the footer, the slide-number placeholders and the
University of Ghana furniture are left exactly as issued.

Template conventions, measured from the supplied file (not assumed):
  slide size   10 x 7.5 in (4:3)
  typeface     Arial, set explicitly on every run (the theme says Calibri; the
               template overrides it, so Arial is what the department actually uses)
  titles       36 pt, NOT bold, white, centred - left untouched on slides 2-12
  title slide  40 pt bold title, 22 pt subtitle, 18 pt byline, all white
  body         21 pt, colour #232323, master bullets (L1 bullet, L2 dash)
  navy         #000066      gold rule  #B08B57     (baked into the background image)
  bands        gold 0.225-0.291 in; navy 0.291-1.397; gold 1.397-1.463; white below
  body box     (0.50, 1.75) 9.00 x 4.95 in; logo at (7.75, 6.99)

Numbers are taken from the frozen analysis CSVs, not from the manuscript. AUDIT_AND_QA.md
records every value and where it was checked.
"""
import copy, os, sys
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, 'assets')
TEMPLATE = os.path.join(ASSETS, 'official_template.pptx')
OUT = os.path.join(HERE, 'CSCD601_Viva_Presentation.pptx')

# ---- the template's own values, reused; nothing new is introduced -----------------
FONT = 'Arial'
NAVY = RGBColor(0x00, 0x00, 0x66)
GOLD = RGBColor(0xB0, 0x8B, 0x57)
INK = RGBColor(0x23, 0x23, 0x23)        # the template's body colour, not pure black
GREY = RGBColor(0x5A, 0x5A, 0x5A)
ACCENT = RGBColor(0xC0, 0x50, 0x4D)     # theme accent2, already in the scheme
PALE = RGBColor(0xEF, 0xEC, 0xE4)       # theme lt2
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BODY_PT = 21                            # the template's body size

L, R = Inches(0.50), Inches(9.50)
TOP, BOT = Inches(1.75), Inches(6.80)
W = R - L

prs = Presentation(TEMPLATE)
S = list(prs.slides)
assert len(S) == 12, f'expected the 12-slide official template, got {len(S)}'


# ---- helpers ----------------------------------------------------------------------
def body_of(slide):
    for sh in slide.shapes:
        if sh.is_placeholder and sh.placeholder_format.idx == 1:
            return sh
    return None


def drop_body(slide):
    """Remove the body placeholder when the slide is laid out with its own shapes."""
    sh = body_of(slide)
    if sh is not None:
        sh._element.getparent().remove(sh._element)


def fill_body(slide, items, size=BODY_PT, box=None):
    """Replace the body placeholder's text. items = (text, level) or (text, level, bold)."""
    sh = body_of(slide)
    if box:
        sh.left, sh.top, sh.width, sh.height = box
    tf = sh.text_frame
    tf.word_wrap = True
    tf.clear()
    for i, it in enumerate(items):
        text, lvl = it[0], it[1]
        bold = it[2] if len(it) > 2 else False
        colour = it[3] if len(it) > 3 else INK
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.level = lvl
        p.text = text
        p.space_after = Pt(7)
        for r in p.runs:
            r.font.name = FONT
            r.font.size = Pt(size if lvl == 0 else size - 3)
            r.font.bold = bold
            r.font.color.rgb = colour
    return sh


def textbox(slide, x, y, w, h, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    return tb, tf


def para(tf, text, size=BODY_PT, bold=False, colour=INK, space_before=6, first=False,
         align=PP_ALIGN.LEFT, italic=False, line=1.0, bullet=False):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_before = Pt(space_before)
    p.line_spacing = line
    p.text = ('•  ' + text) if bullet else text
    for r in p.runs:
        r.font.name, r.font.size, r.font.bold, r.font.italic = FONT, Pt(size), bold, italic
        r.font.color.rgb = colour
    return p


def panel(slide, x, y, w, h, fill=PALE, line=None):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid(); s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line; s.line.width = Pt(1.0)
    s.shadow.inherit = False
    tf = s.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.12)
    tf.margin_top = tf.margin_bottom = Inches(0.07)
    return s, tf


def caption(slide, text, x=L, y=Inches(6.60), w=Inches(7.0)):
    tb, tf = textbox(slide, x, y, w, Inches(0.30))
    para(tf, text, size=11, colour=GREY, first=True, space_before=0)


def picture(slide, name, x, y, max_w, max_h):
    from PIL import Image
    path = os.path.join(ASSETS, name + '_crop.png')
    iw, ih = Image.open(path).size
    sc = min(max_w / iw, max_h / ih)
    w, h = int(iw * sc), int(ih * sc)
    return slide.shapes.add_picture(path, int(x + (max_w - w) / 2),
                                    int(y + (max_h - h) / 2), width=w, height=h)


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text.strip()


# ====================================================================================
# SLIDE 1 — [Project Title]  (the only heading that is meant to be replaced)
# ====================================================================================
s = S[0]
title = s.shapes.title
tf = title.text_frame
tf.clear()
para(tf, 'Does the Handover Margin Earn Its Place?', size=28, bold=True, colour=WHITE,
     first=True, space_before=0, align=PP_ALIGN.CENTER, line=1.0)
para(tf, 'A Factorial Comparison of Temporal Decision Policies for '
         'Context-Based Continuous Smartphone Authentication',
     size=16, colour=WHITE, align=PP_ALIGN.CENTER, space_before=7, line=1.05)

# one-line finding, in the empty band the template leaves between title and subtitle
tb, tf2 = textbox(s, Inches(0.60), Inches(2.06), Inches(8.80), Inches(0.72))
para(tf2, 'Finding: the margin did not earn its place - a short dwell captured most of '
          'the measurable stabilisation, at lower cost.',
     size=15, italic=True, colour=RGBColor(0xE4, 0xD8, 0xC0), first=True,
     space_before=0, align=PP_ALIGN.CENTER, line=1.1)

for sh in s.shapes:                       # the byline text box: fill in what we know
    if sh.name == 'TextBox 5':
        t = sh.text_frame
        t.clear()
        para(t, 'By', size=18, colour=WHITE, first=True, space_before=0,
             align=PP_ALIGN.CENTER)
        para(t, '[Student Name]  |  ID 22427613', size=18, colour=WHITE,
             space_before=0, align=PP_ALIGN.CENTER)
        para(t, 'MSc Computer Science  |  Supervisor: [Name]  |  September 2026',
             size=18, colour=WHITE, space_before=0, align=PP_ALIGN.CENTER)

notes(s, """
Good morning. My question is narrow and testable: when a continuous authentication
system turns noisy scores into an authenticated or locked state, does the margin
borrowed from cellular handover add anything beyond simply requiring evidence to
persist?

I will give the answer first, because everything after it is the evidence. It did not.
Under a preregistered test it produced no measurable stability gain, and it locked the
genuine user out more often than a plain dwell rule.
""")

# ====================================================================================
# SLIDE 2 — Presentation Outline
# ====================================================================================
s = S[1]
fill_body(s, [
    ('Background: why a score stream is not an authentication state', 0),
    ('Aim, objectives and the research question', 0),
    ('Related work and the identified gap', 0),
    ('Methodology: frozen score stream, calibration-only tuning, preregistration', 0),
    ('Design of the decision policies, and what was implemented', 0),
    ('Results: the preregistered test, and evaluation across nine mechanisms', 0),
    ('Contribution, limitations, conclusion and future work', 0),
], size=20)
notes(s, """
Briefly, the route. I start with the problem the study exists to solve, then the
question and the gap it comes from. The methodology and design sections explain how the
comparison was made fair. The results section carries the preregistered test. I then
give the contribution, and I will spend real time on the limitations, because they bound
what I can claim.
""")

# ====================================================================================
# SLIDE 3 — Background and Problem Context
# ====================================================================================
s = S[2]
fill_body(s, [
    ('Continuous authentication keeps confidence in the current phone user after login, '
     'using passive signals.', 0),
    ('A classifier emits a score every frame; a device must hold a persistent state - '
     'authenticated, or locked.', 0),
    ('Near the threshold that state flickers even when the user has not changed. AUC '
     'cannot detect it: it ranks frames and ignores their order.', 0),
], size=18, box=(L, TOP, W, Inches(2.05)))

sx, sy, cw, ch, gap = Inches(0.90), Inches(4.06), Inches(0.268), Inches(0.34), Inches(0.014)
flick = [1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0]
stable = [1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
for row, (seq, lab, cnt) in enumerate([(flick, 'Instantaneous threshold', '8 state changes'),
                                       (stable, 'With a persistence requirement', '1 state change')]):
    y = sy + row * Inches(0.80)
    tb, tf = textbox(s, Inches(5.32), y - Inches(0.02), Inches(4.2), Inches(0.40))
    para(tf, f'{lab}', size=13, bold=True, colour=NAVY, first=True, space_before=0)
    para(tf, cnt, size=13, colour=GREY, space_before=1)
    for i, v in enumerate(seq):
        c = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, sx + i * (cw + gap), y, cw, ch)
        c.fill.solid(); c.fill.fore_color.rgb = NAVY if v else WHITE
        c.line.color.rgb = NAVY; c.line.width = Pt(0.75); c.shadow.inherit = False

p, tf2 = panel(s, L, Inches(5.92), W, Inches(0.70), fill=NAVY)
para(tf2, 'Problem statement: converting a noisy score stream into a stable '
          'authentication state is a design layer in its own right, and frame-level '
          'accuracy cannot measure it.',
     size=16, bold=True, colour=WHITE, first=True, space_before=0, line=1.05)
caption(s, 'Ribbons are an illustrative schematic, not measured data. Filled = '
           'authenticated. Real traces appear on slide 7.', y=Inches(5.52), w=Inches(9.0))

notes(s, """
Everything rests on this distinction. A classifier gives a score per frame; a phone has
to hold a state. Turning one into the other is a design decision, and it is usually left
implicit.

The two ribbons are a schematic - I have labelled them, they are not data. Same user,
same scores. The top row reverses eight times because the score sits near the threshold.
The bottom row requires persistence and changes once.

The consequence is in the box: this is a separate design layer, and AUC cannot see it,
because AUC ranks frames and ignores the order they arrive in.
""")

# ====================================================================================
# SLIDE 4 — Aim, Objectives & Questions
# ====================================================================================
s = S[3]
fill_body(s, [
    ('Aim: to test whether a handover-inspired margin adds useful stabilisation beyond '
     'temporal dwell, at a common calibration-defined operating point.', 0, True, NAVY),
    ('Objectives', 0, True),
    ('Decompose margin and dwell on one frozen score stream under equal tuning.', 1),
    ('Select every operating point from calibration data only, at a decision-layer '
     'FAR target of 0.05.', 1),
    ('Evaluate at participant level on stability, FAR, FRR, detection and recovery - '
     'not frame accuracy alone.', 1),
    ('Test the construct validity of the score itself.', 1),
], size=17, box=(L, TOP, W, Inches(2.95)))

p, tf2 = panel(s, L, Inches(4.88), W, Inches(1.08), fill=NAVY)
para(tf2, 'Research question', size=13, bold=True, colour=GOLD, first=True, space_before=0)
para(tf2, 'At a calibration-defined decision-layer FAR target, does adding a '
          'handover-inspired margin to temporal dwell reduce excess '
          'authentication-state transitions without unacceptable false rejection or '
          'detection failure?',
     size=15, colour=WHITE, space_before=4, line=1.05)

tb, tf = textbox(s, L, Inches(6.02), W, Inches(0.62))
para(tf, 'Scope: one public dataset, one score generator, offline replay. Excluded - '
         'classifier design, live deployment, and any claim about biometric identity.',
     size=14, colour=GREY, first=True, space_before=0, line=1.05)

notes(s, """
The aim is deliberately narrow. Not whether temporal smoothing works in general, but
whether the specific component borrowed from handover - the margin - earns the cost of
adding it to a dwell rule.

Four objectives, each defensible with evidence later: decompose the two factors under
equal tuning; choose every parameter on calibration data only; evaluate at participant
level across a vector of outcomes rather than accuracy alone; and test whether the score
itself means what we want it to mean. That fourth one turns out to matter.

Note the scope line: I exclude any claim about biometric identity, for reasons I will
come to.
""")

# ====================================================================================
# SLIDE 5 — Related Work and Identified Gap
# ====================================================================================
s = S[4]
fill_body(s, [
    ('Zeeshan et al. (2025) use EWMA "to stabilize decisions and avoid flickering" - '
     'but never isolate its effect, report the coefficient, or test a margin.', 0),
    ('Mondal & Bours (2015) do compare decision layers, but sweep fusion, thresholds, '
     'boosting and trust models together, reporting action-domain measures.', 0),
    ('Sugrim et al. (2019) show equal-error-rate comparison is uninformative when a '
     'system has a fixed false-accept requirement; compare at a fixed operating point.', 0),
    ('Stragapede et al. (2023) show mobile behavioural models can identify the device '
     'rather than the user.', 0),
], size=16, box=(L, TOP, W, Inches(3.05)))

p, tf2 = panel(s, L, Inches(4.92), W, Inches(1.18), fill=None, line=ACCENT)
para(tf2, 'Identified gap', size=13, bold=True, colour=ACCENT, first=True, space_before=0)
para(tf2, 'Prior work compares temporal-policy combinations. Evidence is limited on the '
          'incremental effect of a dual-threshold margin when margin and dwell are '
          'decomposed under equal tuning, on a shared score stream, at a '
          'calibration-defined FAR target.',
     size=14, space_before=4, line=1.05)

tb, tf = textbox(s, L, Inches(6.24), W, Inches(0.42))
para(tf, 'The novelty claimed is the decomposition - not the classifier, the dataset, '
         'or temporal smoothing itself.', size=14, bold=True, colour=NAVY, first=True,
     space_before=0)

notes(s, """
The gap has to be stated carefully because it is narrow.

Zeeshan and colleagues justify smoothing in exactly the words quoted, but never isolate
it. Mondal and Bours do compare decision layers - so it is not true that nobody has - but
they vary four factors at once and report action-domain measures rather than holding a
common operating point. Sugrim and colleagues supply the missing methodological piece,
and Stragapede and colleagues are the warning about what mobile models might really be
learning.

So the gap is the red box, and the last line is the claim I will defend: the novelty is
the decomposition, not the classifier or the idea of smoothing.
""")

# ====================================================================================
# SLIDE 6 — Methodology / Project Approach
# ====================================================================================
s = S[5]
fill_body(s, [
    ('Experimental reanalysis of the public ExtraSensory dataset (Vaizman et al., 2017) '
     '- collected for context recognition, not authentication.', 0),
    ('Cohort: 31 participants on a regular ~1-minute cadence, defined before any '
     'confirmatory score was generated. Each is one enrolled user, one-versus-rest.', 0),
    ('Chronological enrolment / calibration / test partitions. Preprocessing fitted on '
     'enrolment only. Final-test impostors unseen during fitting and calibration.', 0),
    ('Per-user gradient-boosting score generator, frozen before any decision policy is '
     'applied. Every policy replays the same stored scores.', 0),
    ('Parameters chosen on calibration data only, at a decision-layer FAR target of 0.05 '
     '(preregistered feasible band 0.04-0.05).', 0),
    ('Participant-level paired inference: Wilcoxon signed-rank, Holm-corrected, with '
     'bootstrap confidence intervals.', 0),
], size=16, box=(L, TOP, W, Inches(3.95)))

p, tf2 = panel(s, L, Inches(5.86), W, Inches(0.82), fill=PALE)
para(tf2, 'Reproducibility: rules, grids, outcomes and the verdict wording were frozen '
          'before the score dumps existed. Executed code is byte-identical to the frozen '
          'code. Public dataset, so no further ethical approval was required.',
     size=14, first=True, space_before=0, line=1.05)

notes(s, """
The design choices here are all about making the comparison fair rather than making the
result good.

ExtraSensory is public and in the wild, but collected for context recognition rather than
authentication - a limitation I return to. The cohort is the participants whose sampling
is regular enough that a dwell of two frames means the same thing for everyone, fixed
before any confirmatory score existed.

Three protections against leakage: chronological rather than random partitions,
preprocessing fitted on enrolment only, and final-test impostors held out of both fitting
and calibration.

The most important choice is the frozen score stream. Every mechanism reads the same
stored scores, so any difference belongs to the decision rule and cannot be a retrained
classifier.
""")

# ====================================================================================
# SLIDE 7 — System / Model Design
# ====================================================================================
s = S[6]
drop_body(s)
picture(s, 'fig5_sequence_schematic', Inches(0.50), Inches(1.72), Inches(3.35), Inches(4.62))

tx = Inches(4.10)
tb, tf = textbox(s, tx, Inches(1.74), Inches(5.42), Inches(1.05))
para(tf, 'Decision rule', size=15, bold=True, colour=NAVY, first=True, space_before=0)
para(tf, 'Accept if score ≥ θ + m/2; reject if score < θ − m/2. '
         'k consecutive qualifying frames flip the state; anything else resets the '
         'counter.', size=16, space_before=4, line=1.05)

gx, gy, gw, gh = tx, Inches(3.10), Inches(2.62), Inches(0.72)
cells = [('Instantaneous', 'm = 0,  k = 1', False), ('Dwell only', 'm = 0,  k > 1', False),
         ('Margin only', 'm > 0,  k = 1', False), ('Margin + dwell', 'm > 0,  k > 1', True)]
tb, tf = textbox(s, gx, Inches(2.80), Inches(5.42), Inches(0.28))
para(tf, 'Factorial:  m ∈ {0, 0.05, 0.10, 0.20}  ×  k ∈ {1, 2, 3, 5, 10}',
     size=12, bold=True, colour=NAVY, first=True, space_before=0)
for i, (name, spec, hot) in enumerate(cells):
    x = gx + (i % 2) * (gw + Inches(0.18))
    y = gy + (i // 2) * (gh + Inches(0.14))
    c, ctf = panel(s, x, y, gw, gh, fill=None, line=ACCENT if hot else NAVY)
    para(ctf, name, size=14, bold=True, colour=ACCENT if hot else NAVY, first=True,
         space_before=0, align=PP_ALIGN.CENTER)
    para(ctf, spec, size=12, colour=GREY, space_before=1, align=PP_ALIGN.CENTER)

p, tf2 = panel(s, tx, Inches(4.84), Inches(5.42), Inches(1.20), fill=PALE)
para(tf2, 'Evaluation contract', size=13, bold=True, colour=NAVY, first=True, space_before=0)
para(tf2, 'Each test sequence is 60 genuine, 60 unseen-impostor and 60 recovery frames. '
          'A correct trace needs exactly two state changes; anything beyond that is an '
          'excess transition.', size=14, space_before=3, line=1.05)
caption(s, 'Figure 5. One real test sequence under three policies, on an identical score '
           'stream.', y=Inches(6.40))

notes(s, """
This is the design, and the figure on the left is the contract I would hold on to when
judging the results.

One real test sequence: sixty genuine frames, sixty from an unseen impostor, sixty of the
genuine user returning. The three rows below are the state under three policies reading
that identical stream.

The rule is deliberately simple. A margin widens the band a score must cross; a dwell
requires k consecutive qualifying frames before the state flips. Crossing the two factors
gives the four cells, and the one in red is the policy under test.

The outcome measure falls out of the structure: a correct trace has exactly two state
changes, so anything beyond two is excess.
""")

# ====================================================================================
# SLIDE 8 — Implementation Work Done
# ====================================================================================
s = S[7]
drop_body(s)
picture(s, 'fig1_factorial_surface', Inches(6.15), Inches(1.70), Inches(3.20), Inches(4.75))

tb, tf = textbox(s, L, Inches(1.74), Inches(5.45), Inches(2.5))
para(tf, 'Built and executed', size=15, bold=True, colour=NAVY, first=True, space_before=0)
para(tf, 'Python, scikit-learn 1.6.1, NumPy, pandas. Score dumps generated from commit '
         'f42f55c with seed 20260918.', size=15, bullet=True, space_before=6, line=1.05)
para(tf, 'Per-frame scores dumped once to Parquet, so every rule change is replayed '
         'offline - model fitting was 92% of runtime.', size=15, bullet=True,
     space_before=6, line=1.05)
para(tf, 'All 20 factorial cells run per participant (3 infeasible at the target), '
         'plus nine further mechanisms for the secondary comparison.', size=15,
     bullet=True, space_before=6, line=1.05)

p, tf2 = panel(s, L, Inches(4.62), Inches(5.45), Inches(1.22), fill=None, line=ACCENT)
para(tf2, 'Challenge resolved', size=13, bold=True, colour=ACCENT, first=True, space_before=0)
para(tf2, 'A windowed-mean defect made one secondary mechanism disagree with its '
          'reference at exact ties. Fixed, regression-tested, and the offline analysis '
          'rerun; the preregistered primary test was unaffected.',
     size=13, space_before=3, line=1.05)

tb, tf = textbox(s, L, Inches(5.92), Inches(5.45), Inches(0.70))
para(tf, 'Preregistration, frozen analysis, figure and table scripts, checks and '
         'rendered outputs are all in the project repository.',
     size=14, bold=True, colour=NAVY, first=True, space_before=0, line=1.05)
caption(s, 'Figure 1. The executed factorial at FAR 0.05: excess transitions (top) and '
           'FRR (bottom).', x=Inches(5.60), y=Inches(6.44), w=Inches(3.9))

notes(s, """
What was actually built. A per-user score generator, then a decision layer that replays
stored scores offline. That mattered practically: fitting the models was ninety-two per
cent of the runtime, so dumping the scores once made every later rule change essentially
free - and it is what guarantees all policies see identical evidence.

On the right is the executed factorial. Colour lightens down and to the right in the top
panel, meaning more stable, and darkens in the same direction below, meaning more lockout.
Same movement: you cannot buy stability without paying in lockout.

One defect, honestly. A windowed mean disagreed with its reference at exact ties. I fixed
it, added a regression test that fails against the old code, and reran the analysis. One
secondary mechanism only; the preregistered test was unaffected.
""")

# ====================================================================================
# SLIDE 9 — Results and Evaluation
# ====================================================================================
s = S[8]
drop_body(s)

rows = [('', 'vs dwell only', 'vs margin only'),
        ('Participants paired', '30', '24'),
        ('Excess transitions, mean paired difference', '−0.13', '−0.20'),
        ('Holm-adjusted p', '0.69', '0.69'),
        ('FRR difference', '+0.074', '+0.030'),
        ('FRR 95% CI', '[0.032, 0.119]', '[−0.008, 0.069]'),
        ('Detection-failure difference', '0.000', '−0.007')]
tbl = s.shapes.add_table(len(rows), 3, Inches(0.50), Inches(1.72),
                         Inches(5.55), Inches(2.12)).table
tbl.columns[0].width = Inches(2.55)
tbl.columns[1].width = Inches(1.55)
tbl.columns[2].width = Inches(1.45)
for ri, row in enumerate(rows):
    tbl.rows[ri].height = Inches(0.30)
    for ci, val in enumerate(row):
        c = tbl.cell(ri, ci)
        c.text = val
        c.margin_left = c.margin_right = Inches(0.06)
        c.margin_top = c.margin_bottom = Inches(0.01)
        c.vertical_anchor = MSO_ANCHOR.MIDDLE
        c.fill.solid()
        c.fill.fore_color.rgb = NAVY if ri == 0 else (PALE if ri in (3, 4, 5) else WHITE)
        p = c.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT if ci == 0 else PP_ALIGN.CENTER
        for r in p.runs:
            r.font.name, r.font.size = FONT, Pt(11.5)
            r.font.bold = (ri == 0) or (ri in (3, 4, 5))
            r.font.color.rgb = WHITE if ri == 0 else (
                ACCENT if (ri in (4, 5) and ci == 1) else INK)

p, tf2 = panel(s, Inches(0.50), Inches(3.98), Inches(5.55), Inches(0.92), fill=NAVY)
para(tf2, 'Margin plus dwell offers no measurable advantage over its components, and is '
          'FRR-inferior to dwell alone.',
     size=15, bold=True, colour=WHITE, first=True, space_before=0,
     align=PP_ALIGN.CENTER, line=1.05)

tb, tf = textbox(s, Inches(0.50), Inches(5.04), Inches(5.55), Inches(1.50))
para(tf, 'The +0.074 FRR penalty breaches the preregistered +0.02 non-inferiority '
         'bound. 20 of 30 participants tied exactly on stability.', size=14,
     bullet=True, first=True, space_before=0, line=1.05)
para(tf, 'Descriptively, a dwell of 2 frames cuts excess transitions from 2.012 to '
         '0.466 per sequence for about +0.01 FRR (unpaired cells).', size=14,
     bullet=True, space_before=6, line=1.05)
para(tf, 'Across nine mechanisms none dominates: the most stable are the most locked '
         'out. Ordering holds at FAR 0.03 and 0.07.', size=14, bullet=True,
     space_before=6, line=1.05)

picture(s, 'fig2_stability_lockout', Inches(6.20), Inches(1.72), Inches(3.25), Inches(4.35))
caption(s, 'Figure 2. Stability-lockout plane. Lower left is better; no mechanism '
           'reaches it.', x=Inches(5.90), y=Inches(6.18), w=Inches(3.9))

notes(s, """
This is the core result, so I will take it slowly.

Read the p-values first. Both are nought point six nine, so the stability criterion fails
against both components. But be precise about what that means: failure to reject is not
proof of equivalence. On its own this could just mean I lacked power, and I will show you
on the next slide but one that I probably did.

The stronger evidence is the red row. Against dwell alone, adding the margin raises false
rejection by seven point four points, interval three point two to eleven point nine. I
prespecified a limit of two. The whole interval sits above it. So this is not an
underpowered null - it is a positive finding in the wrong direction.

The figure evaluates nine mechanisms at the same target. Every one beats instantaneous
thresholding, so persistence works. But nothing reaches the bottom-left corner, and the
most stable are the most locked out. Note SPRT is exploratory - it had the largest grid,
so the most selection opportunity.
""")

# ====================================================================================
# SLIDE 10 — Contribution and Significance
# ====================================================================================
s = S[9]
drop_body(s)
blocks = [('Evidence', 'A preregistered null plus a directional failure: no stability '
                       'gain from the margin (p = 0.69 against both components), and an '
                       'FRR penalty of +0.074 against dwell that breaches the +0.02 bound.'),
          ('Interpretation', 'Persistence is what transfers from the handover analogy. '
                             'The margin does not add measurable value here - it converts '
                             'instability into lockout.'),
          ('Significance', 'Methodological: a leakage-aware, calibration-frozen way to '
                           'test whether a decision rule improves a system, rather than '
                           'merely making its state harder to change.')]
for i, (head, body) in enumerate(blocks):
    y = Inches(1.80) + i * Inches(1.24)
    hd, htf = panel(s, L, y, Inches(2.10), Inches(1.10), fill=NAVY)
    htf.vertical_anchor = MSO_ANCHOR.MIDDLE
    para(htf, head, size=16, bold=True, colour=WHITE, first=True, space_before=0,
         align=PP_ALIGN.CENTER)
    tb, tf = textbox(s, L + Inches(2.28), y + Inches(0.02), Inches(6.72), Inches(1.06),
                     anchor=MSO_ANCHOR.MIDDLE)
    para(tf, body, size=16, first=True, space_before=0, line=1.05)

p, tf2 = panel(s, L, Inches(5.58), W, Inches(0.98), fill=PALE)
para(tf2, 'Practical', size=13, bold=True, colour=NAVY, first=True, space_before=0)
para(tf2, 'For a designer with a comparable score stream, a short dwell is the simplest '
          'defensible first intervention. Always report excess transitions together with '
          'FAR, FRR and recovery - a stability number alone rewards a policy that has '
          'stopped responding.', size=14, space_before=3, line=1.05)

notes(s, """
Let me separate the finding from what I think it means, because they are claims of
different strength.

The evidence is a preregistered null plus a directional failure. No stability gain
against either component, and a false-rejection penalty against dwell that breaks the
bound I set in advance.

My interpretation is that persistence is the part of the handover analogy that actually
transfers. Requiring evidence to hold works. The margin, on this benchmark, mostly
converts instability into lockout.

The significance is methodological rather than algorithmic, and that is the part I would
defend hardest. The classifier here is an instrument, not the contribution. What the
project provides is a way to ask whether a decision rule genuinely improves a
continuous-authentication system - and the practical rule at the bottom follows directly:
never report a stability number on its own.
""")

# ====================================================================================
# SLIDE 11 — Conclusion and Future Work
# ====================================================================================
s = S[10]
drop_body(s)
picture(s, 'fig3_instability_concentration', Inches(0.50), Inches(1.72), Inches(4.20), Inches(2.30))
picture(s, 'fig4_score_validity_f3_f7', Inches(5.30), Inches(1.72), Inches(4.20), Inches(2.30))

for x, head, body in [
    (L, 'Instability is rare and concentrated',
     '71.7% of instantaneous test sequences never flip; 5 of 30 participants carry '
     '65.6% of it. Little for a margin to improve - this limits power.'),
    (Inches(5.30), 'The score is not clean identity evidence',
     'Removing location and device-state features drops mean AUC from 0.990 to 0.758 '
     '(paired difference 0.232 [0.191, 0.273]).')]:
    hd, htf = panel(s, x, Inches(4.10), Inches(4.20), Inches(0.38), fill=NAVY)
    para(htf, head, size=13, bold=True, colour=WHITE, first=True, space_before=0,
         align=PP_ALIGN.CENTER)
    tb, tf = textbox(s, x, Inches(4.54), Inches(4.20), Inches(0.90))
    para(tf, body, size=13, first=True, space_before=0, line=1.05)

p, tf2 = panel(s, L, Inches(5.50), W, Inches(0.62), fill=NAVY)
para(tf2, 'Conclusion: under a preregistered, calibration-frozen comparison, the margin '
          'did not earn its place on this benchmark.',
     size=16, bold=True, colour=WHITE, first=True, space_before=0,
     align=PP_ALIGN.CENTER, line=1.05)

tb, tf = textbox(s, L, Inches(6.22), W, Inches(0.60))
para(tf, 'Future work: a cohort selected for instability; a dataset that separates user '
         'from device; equalised tuning grids so the SPRT result can be confirmed.',
     size=14, colour=INK, first=True, space_before=0, line=1.05)

notes(s, """
I put the limitations before the conclusion because they bound it.

The left panel explains the tied participants. Seventy-two per cent of sequences never
flip at all, and five participants of thirty carry two thirds of the instability. For
most people a dwell has already removed everything there was to remove, so there is
nothing left for a margin to improve. That is the honest reading of my null.

The right panel is more serious. Strip out location and device state, keep only which
sensors were missing, and mean AUC still sits at nought point seven six. So, explicitly:
evidence not established in the project materials for any claim that this score is
behavioural identity independent of context or device.

The conclusion is bounded to this dataset and protocol, and the future work follows
straight from those two panels.
""")

# ====================================================================================
# SLIDE 12 — References
# ====================================================================================
s = S[11]
refs = [
    'Mondal, S., & Bours, P. (2015). A computational approach to the continuous '
    'authentication biometric system. Information Sciences, 304, 28-53.',
    'Sugrim, S., Liu, C., McLean, M., & Lindqvist, J. (2019). Robust performance metrics '
    'for authentication systems. NDSS Symposium 2019.',
    'Zeeshan, N., Bakyt, M., Moradpoor, N., & La Spada, L. (2025). Continuous '
    'authentication in resource-constrained devices via biometric and environmental '
    'fusion. Sensors, 25(18), 5711.',
    'Stragapede, G., Vera-Rodriguez, R., Tolosana, R., & Morales, A. (2023). '
    'BehavePassDB: Public database for mobile behavioral biometrics. Pattern '
    'Recognition, 134, 109089.',
    'Vaizman, Y., Ellis, K., & Lanckriet, G. (2017). Recognizing detailed human context '
    'in-the-wild from smartphones and smartwatches. IEEE Pervasive Computing, 16(4), 62-74.',
    'Georgiev, M., Eberz, S., Turner, H., Lovisotto, G., & Martinovic, I. (2022). Common '
    'evaluation pitfalls in touch-based authentication systems. ACM AsiaCCS 2022.',
    'Kapoor, S., & Narayanan, A. (2023). Leakage and the reproducibility crisis in '
    'machine-learning-based science. Patterns, 4(9), 100804.',
    'Baldwin, J. R., et al. (2022). Protecting against researcher bias in secondary data '
    'analysis. European Journal of Epidemiology, 37(1), 1-10.',
]
fill_body(s, [(r, 0) for r in refs], size=13, box=(L, TOP, W, Inches(4.85)))
tb, tf = textbox(s, L, Inches(6.34), W, Inches(0.40))
para(tf, 'APA 7th. Full reference list and the citation verification record are in the '
         'dissertation and the project repository.',
     size=12, colour=GREY, first=True, space_before=0)

notes(s, """
These are the eight sources that directly support what I have presented, in APA style.
Every one is cited on a slide or underpins a design choice: Mondal and Bours and Sugrim
for the gap, Zeeshan for the claim I am testing, Stragapede for the device confound,
Vaizman for the dataset, Georgiev and Kapoor for the evaluation-validity design, and
Baldwin for the preregistration position. The full list is in the dissertation.

Thank you - I am happy to take questions.
""")

prs.save(OUT)
print(f'wrote {OUT}')
for i, sl in enumerate(prs.slides, 1):
    t = sl.shapes.title.text.replace('\n', ' / ')[:44] if sl.shapes.title is not None else '?'
    n = len(sl.notes_slide.notes_text_frame.text.split())
    print(f'  {i:2d}. {t:46s} notes {n:3d} w')
