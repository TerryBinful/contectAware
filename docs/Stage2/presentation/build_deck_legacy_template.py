"""Build the MSc viva deck on top of the departmental PowerPoint template.

The deck is NOT designed from scratch. It opens the supplied template, removes its
sample slides, and adds new ones on the template's own layouts, so the slide master,
theme, colour scheme, fonts, background artwork and University of Ghana furniture are
inherited rather than reproduced.

Template facts, measured from the supplied file (see PRESENTATION_NOTES.md):
  slide size      10 x 7.5 in (4:3)
  theme fonts     Calibri (major and minor)
  navy            #000066   gold rule  #B2875A      (baked into the background images)
  content bands   gold rule 0.247-0.320 in; navy title band 0.320-1.533 in;
                  gold rule 1.533-1.613 in; white body below
  master styles   title 44 pt, centred, white; body L1 28 pt, L2 24 pt, bullets   and -
  master logo     UG mark at (7.75, 6.99) 2.25 x 0.44 in on every content slide

Numbers come from the reconciled manuscript, cross-checked against the frozen analysis
CSVs. AUDIT.md records every value and where it was checked.
"""
import copy, os, sys
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, 'assets')
TEMPLATE = os.path.join(ASSETS, 'template_source.pptx')
OUT = os.path.join(HERE, 'CSCD601_Viva_Presentation.pptx')

# ---- the template's own palette; nothing new is introduced -------------------------
NAVY = RGBColor(0x00, 0x00, 0x66)      # background band colour
GOLD = RGBColor(0xB2, 0x87, 0x5A)      # background rule colour
INK = RGBColor(0x00, 0x00, 0x00)       # master body colour (tx1)
GREY = RGBColor(0x59, 0x59, 0x59)      # captions and source lines
ACCENT = RGBColor(0xC0, 0x50, 0x4D)    # theme accent2, reserved for margin + dwell
PALE = RGBColor(0xEF, 0xEC, 0xE4)      # theme lt2, used for quiet panel fills
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FONT = 'Calibri'

# content band, chosen to clear the title band above and the UG logo below
L, R = Inches(0.50), Inches(9.50)
TOP, BOT = Inches(1.80), Inches(6.80)
W = R - L

prs = Presentation(TEMPLATE)
LAY = {l.name: l for l in prs.slide_layouts}

# ---- strip the template's sample slides, keeping master/layouts/theme intact --------
ids = prs.slides._sldIdLst
for sld in list(ids):
    rId = sld.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
    prs.part.drop_rel(rId)
    ids.remove(sld)


# ---- small helpers -----------------------------------------------------------------
def add(layout_name):
    return prs.slides.add_slide(LAY[layout_name])


def set_title(slide, text, size=40):
    """Title inherits the master's white centred style; only the size is set."""
    ph = slide.shapes.title
    ph.text_frame.text = text
    p = ph.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.runs[0]
    r.font.size, r.font.bold, r.font.name = Pt(size), True, FONT
    return ph


def drop_empty_placeholders(slide):
    """Remove body placeholders left unused, so no 'Click to add text' prompt renders."""
    for sh in list(slide.shapes):
        if sh.is_placeholder and sh.placeholder_format.idx != 0 and not sh.has_text_frame:
            sh._element.getparent().remove(sh._element)
        elif sh.is_placeholder and sh.placeholder_format.idx != 0 and not sh.text_frame.text:
            sh._element.getparent().remove(sh._element)


def textbox(slide, x, y, w, h, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.04)
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    return tb, tf


def para(tf, text, size=24, bold=False, colour=INK, bullet=False, space_before=6,
         align=PP_ALIGN.LEFT, italic=False, first=False, line=0.95):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_before = Pt(space_before)
    p.line_spacing = line
    if bullet:
        # the master's L1 bullet, applied to a plain text box
        p.text = '•  ' + text
    else:
        p.text = text
    for r in p.runs:
        r.font.size, r.font.bold, r.font.name, r.font.italic = Pt(size), bold, FONT, italic
        r.font.color.rgb = colour
    return p


def rule(slide, x, y, w, colour=GOLD, h=Inches(0.035)):
    """The template's gold hairline, reused as a quiet separator."""
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    s.fill.solid(); s.fill.fore_color.rgb = colour
    s.line.fill.background(); s.shadow.inherit = False
    return s


def panel(slide, x, y, w, h, fill=PALE, line=None, radius=False):
    s = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE, x, y, w, h)
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid(); s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line; s.line.width = Pt(1.0)
    s.shadow.inherit = False
    if radius:
        s.adjustments[0] = 0.08
    tf = s.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.12)
    tf.margin_top = tf.margin_bottom = Inches(0.08)
    return s, tf


def source(slide, text, y=Inches(6.86)):
    tb, tf = textbox(slide, L, y, Inches(7.0), Inches(0.32))
    para(tf, text, size=11, colour=GREY, first=True, space_before=0)
    return tb


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text.strip()


def picture(slide, name, x, y, max_w, max_h):
    """Place a rendered figure, scaled to fit the box and centred inside it."""
    from PIL import Image
    path = os.path.join(ASSETS, name + '_crop.png')
    iw, ih = Image.open(path).size
    scale = min(max_w / iw, max_h / ih)
    w, h = int(iw * scale), int(ih * scale)
    return slide.shapes.add_picture(path, int(x + (max_w - w) / 2), int(y + (max_h - h) / 2),
                                    width=w, height=h)


# ====================================================================================
# 1. Title and the one-sentence answer
# ====================================================================================
s = add('Title Slide')
for sh in list(s.shapes):                      # use the layout's art, place text freely
    if sh.is_placeholder:
        sh._element.getparent().remove(sh._element)

tb, tf = textbox(s, Inches(0.70), Inches(0.42), Inches(8.60), Inches(1.95))
para(tf, 'Does the Handover Margin Earn Its Place?', size=28, bold=True, colour=WHITE,
     first=True, space_before=0, align=PP_ALIGN.CENTER, line=1.0)
para(tf, 'A Factorial Comparison of Temporal Decision Policies for '
         'Context-Based Continuous Smartphone Authentication',
     size=19, colour=WHITE, align=PP_ALIGN.CENTER, space_before=8, line=1.05)

rule(s, Inches(3.60), Inches(2.62), Inches(2.80))

tb, tf = textbox(s, Inches(0.90), Inches(2.86), Inches(8.20), Inches(1.00))
para(tf, 'The margin did not earn its place: a short dwell captured most of the '
         'measurable stabilisation, at lower cost.',
     size=18, italic=True, colour=RGBColor(0xE8, 0xDC, 0xC8), first=True,
     space_before=0, align=PP_ALIGN.CENTER, line=1.1)

tb, tf = textbox(s, Inches(0.90), Inches(4.00), Inches(8.20), Inches(1.00))
para(tf, 'MSc Computer Science  |  CSCD 601  |  Dissertation Viva', size=15,
     colour=WHITE, first=True, space_before=0, align=PP_ALIGN.CENTER)
para(tf, 'Candidate: [Name]     Student ID: 22427613     Supervisor: [Supervisor]',
     size=15, colour=WHITE, align=PP_ALIGN.CENTER, space_before=6)
para(tf, 'Department of Computer Science  |  27 September 2026', size=13,
     colour=RGBColor(0xC8, 0xC8, 0xD8), align=PP_ALIGN.CENTER, space_before=6)

notes(s, """
Good morning. My question is narrow and testable: when a continuous
authentication system turns noisy scores into an authenticated or locked state,
does the margin borrowed from cellular handover add anything beyond simply
requiring evidence to persist?

I will give the answer first. It did not. Under a preregistered test it produced no
measurable stability gain, and it locked the genuine user out more often than a
plain dwell. Let me show you why the question matters.
""")

# ====================================================================================
# 2. Problem: scores are not states
# ====================================================================================
s = add('Title and Content'); drop_empty_placeholders(s)
set_title(s, 'Scores are not states')

tb, tf = textbox(s, L, TOP, Inches(4.45), Inches(3.4))
para(tf, 'A classifier emits a score every frame. A device must hold a persistent '
         'state: authenticated, or locked.', size=21, first=True, space_before=0, line=1.05)
para(tf, 'Scores that sit near the threshold make the state flicker even when the '
         'user has not changed.', size=21, space_before=12, line=1.05)
para(tf, 'A high AUC cannot detect this. AUC ranks frames; it says nothing about '
         'the behaviour of the state over time.', size=21, space_before=12, line=1.05)

# schematic: two state ribbons. Illustrative, and labelled as such.
sx, sy, cw, ch, gap = Inches(5.22), Inches(2.25), Inches(0.268), Inches(0.42), Inches(0.014)
flick = [1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0]
stable = [1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
for row, (seq, lab) in enumerate([(flick, 'Instantaneous threshold'),
                                  (stable, 'With a persistence requirement')]):
    y = sy + row * Inches(1.32)
    tb, tf = textbox(s, sx, y - Inches(0.32), Inches(4.2), Inches(0.30))
    para(tf, lab, size=14, bold=True, colour=NAVY, first=True, space_before=0)
    for i, v in enumerate(seq):
        c = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, sx + i * (cw + gap), y, cw, ch)
        c.fill.solid(); c.fill.fore_color.rgb = NAVY if v else WHITE
        c.line.color.rgb = NAVY; c.line.width = Pt(0.75); c.shadow.inherit = False
    tb, tf = textbox(s, sx, y + ch + Inches(0.03), Inches(4.2), Inches(0.28))
    para(tf, ('8 state changes' if row == 0 else '1 state change') + '  -  same user, same scores',
         size=13, colour=GREY, first=True, space_before=0)

tb, tf = textbox(s, sx, Inches(5.05), Inches(4.2), Inches(0.9))
para(tf, 'Filled = authenticated.  Illustrative schematic, not measured data; '
         'real traces appear on the next slides.', size=12, italic=True, colour=GREY,
     first=True, space_before=0, line=1.1)

notes(s, """
Everything rests on this distinction. A classifier gives a score per frame; a phone
has to hold a state. Turning one into the other is a design decision, and it is
usually left implicit.

The two ribbons are a schematic - I have labelled them, they are not data. Same
user, same scores. The top row reverses eight times because the score sits near the
threshold. The bottom row requires persistence and changes once.

The consequence is that AUC cannot see the difference: it ranks frames and ignores
their order. A system can score well and still behave badly.
""")

# ====================================================================================
# 3. Gap and research question
# ====================================================================================
s = add('Title and Content'); drop_empty_placeholders(s)
set_title(s, 'The gap and the question')

tb, tf = textbox(s, L, TOP, W, Inches(3.0))
para(tf, 'Stabilisation is usually asserted, not decomposed. Zeeshan et al. (2025) '
         'use EWMA "to stabilize decisions and avoid flickering" - without isolating '
         'its effect.', size=19, first=True, space_before=0, line=1.05)
para(tf, 'Mondal and Bours (2015) do compare decision layers, but sweep four factors '
         'together and report action-domain measures, not a matched-operating-point '
         'contrast.', size=19, space_before=10, line=1.05)
para(tf, 'Sugrim et al. (2019) show why equal-error-rate comparison is uninformative '
         'when a system has a fixed false-accept requirement.',
     size=19, space_before=10, line=1.05)

p, tf2 = panel(s, L, Inches(4.86), W, Inches(1.38), fill=NAVY)
para(tf2, 'Research question', size=15, bold=True, colour=GOLD, first=True, space_before=0)
para(tf2, 'At a calibration-defined decision-layer FAR target, does adding a '
          'handover-inspired margin to temporal dwell reduce excess '
          'authentication-state transitions without unacceptable false rejection '
          'or detection failure?',
     size=17, colour=WHITE, space_before=5, line=1.05)

source(s, 'The novelty claimed is the decomposition, not the classifier, the dataset, '
          'or temporal smoothing itself.')

notes(s, """
The gap is narrow and I do not want to overstate it. It is not true that nobody has
compared decision layers.

What is missing is one contrast. Zeeshan and colleagues justify smoothing in exactly
the words quoted, but never isolate it and never test a margin. Mondal and Bours do
compare decision layers, but vary four factors at once and report action-domain
measures rather than holding a common operating point. Sugrim and colleagues supply
the missing piece: comparing at equal error rates tells an implementer nothing when
they have a fixed false-accept requirement.

So the defensible question is the one in the box - does the margin add anything to
dwell, tuned equally, on one score stream, at one operating point?
""")

# ====================================================================================
# 4. What transfers from handover
# ====================================================================================
s = add('Title and Content'); drop_empty_placeholders(s)
set_title(s, 'What transfers from handover')

colw = Inches(4.35)
for i, (head, lines) in enumerate([
        ('Cellular handover', ['Switch when a neighbour cell exceeds the serving '
                               'cell by a hysteresis margin,', 'and holds that lead '
                               'for a time-to-trigger.']),
        ('Continuous authentication', ['Change state when the score crosses a '
                                       'dual threshold,', 'and stays across k '
                                       'consecutive frames.'])]):
    x = L + i * (colw + Inches(0.30))
    hd, htf = panel(s, x, TOP, colw, Inches(0.46), fill=NAVY)
    para(htf, head, size=17, bold=True, colour=WHITE, first=True, space_before=0,
         align=PP_ALIGN.CENTER)
    tb, tf = textbox(s, x, TOP + Inches(0.54), colw, Inches(1.25))
    para(tf, ' '.join(lines), size=17, first=True, space_before=0, line=1.05)

y = Inches(3.62)
p, tf2 = panel(s, L, y, W, Inches(1.18), fill=PALE)
para(tf2, 'Shared', size=14, bold=True, colour=NAVY, first=True, space_before=0)
para(tf2, 'Noisy sequential evidence  -  costly state reversals  -  a responsiveness '
          'against stability trade-off', size=17, space_before=4, line=1.05)

p, tf2 = panel(s, L, y + Inches(1.30), W, Inches(1.28), fill=None, line=ACCENT)
para(tf2, 'Not shared', size=14, bold=True, colour=ACCENT, first=True, space_before=0)
para(tf2, 'Handover arbitrates competing radio links. Authentication weighs identity '
          'hypotheses, where false accept and false reject are asymmetric security '
          'outcomes.', size=17, space_before=4, line=1.05)

source(s, 'Terminology: in the analogy the hysteresis term is the margin; '
          'time-to-trigger is the dwell. The composed policy is called margin + dwell.')

notes(s, """
The analogy is where the idea comes from, so it needs a boundary.

Two things transfer. Both domains face noisy evidence arriving in sequence, and in
both a reversal is expensive. That gives the same responsiveness-against-stability
tension.

What does not transfer is at the bottom. Handover arbitrates between radio links
that are interchangeable. Authentication weighs identity hypotheses where the errors
are asymmetric - a false accept is a security failure, a false reject is an
annoyance.

One terminology point for the rest of the talk: in 3GPP, hysteresis is the margin
and time-to-trigger is the dwell. So I never call the composed policy hysteresis.
Telling those two apart is the whole study.
""")

# ====================================================================================
# 5. The evaluation contract
# ====================================================================================
s = add('Title and Content'); drop_empty_placeholders(s)
set_title(s, 'The evaluation contract')

picture(s, 'fig5_sequence_schematic', Inches(0.42), Inches(1.78), Inches(3.55), Inches(4.85))

tx = Inches(4.25)
tb, tf = textbox(s, tx, Inches(1.85), Inches(5.30), Inches(3.5))
para(tf, 'ExtraSensory, 31-participant regular-cadence cohort. Chronological '
         'enrolment, calibration and test partitions; final-test impostors unseen '
         'during fitting and calibration.', size=18, first=True, space_before=0,
     line=1.05)
para(tf, 'One frozen per-user gradient-boosting score stream. Every policy is '
         'replayed offline on identical scores, so any difference is the decision '
         'rule, not the classifier.', size=18, space_before=11, line=1.05)
para(tf, 'Each test sequence: 60 genuine, 60 unseen-impostor, 60 recovery frames.',
     size=18, space_before=11, line=1.05)

p, tf2 = panel(s, tx, Inches(5.48), Inches(5.30), Inches(1.06), fill=PALE)
para(tf2, 'A correct trace needs exactly two state changes. Anything beyond that '
          'is an excess transition.', size=16, bold=True, colour=NAVY, first=True,
     space_before=0, line=1.05)

source(s, 'Figure 5. Controlled identity-transition sequence, real observations, '
          'composed to a fixed structure.')

notes(s, """
This is the experimental contract, and it is what I would hold on to when judging
the results.

On the left is one real test sequence: sixty genuine frames, sixty from an impostor
neither the model nor the calibration has seen, then sixty of the genuine user
returning. The rows below are the state under three policies on that identical
stream.

The critical choice is that the score stream is frozen. Every mechanism reads the
same stored scores, so any difference belongs to the decision rule and cannot be a
retrained classifier.

The outcome measure falls out of the structure: a correct trace has exactly two
state changes, so anything beyond two is excess. One caveat - these are real
observations composed into a fixed structure, not observed takeovers.
""")

# ====================================================================================
# 6. Factorial design and the preregistered test
# ====================================================================================
s = add('Title and Content'); drop_empty_placeholders(s)
set_title(s, 'Design and preregistered test')

gx, gy, gw, gh = L, Inches(2.06), Inches(2.25), Inches(0.92)
tb, tf = textbox(s, gx, gy - Inches(0.36), Inches(4.75), Inches(0.30))
para(tf, 'margin m \u2208 {0, 0.05, 0.10, 0.20}   \u00d7   dwell k \u2208 {1, 2, 3, 5, 10}',
     size=13, bold=True, colour=NAVY, first=True, space_before=0)
cells = [('Instantaneous', 'm = 0,  k = 1', False), ('Dwell only', 'm = 0,  k > 1', False),
         ('Margin only', 'm > 0,  k = 1', False), ('Margin + dwell', 'm > 0,  k > 1', True)]
for i, (name, spec, hot) in enumerate(cells):
    x = gx + (i % 2) * (gw + Inches(0.22))
    y = gy + (i // 2) * (gh + Inches(0.22))
    c, ctf = panel(s, x, y, gw, gh, fill=None, line=ACCENT if hot else NAVY)
    para(ctf, name, size=15, bold=True, colour=ACCENT if hot else NAVY, first=True,
         space_before=0, align=PP_ALIGN.CENTER)
    para(ctf, spec, size=13, colour=GREY, space_before=2, align=PP_ALIGN.CENTER)

tb, tf = textbox(s, gx, Inches(4.28), Inches(4.72), Inches(1.5))
para(tf, 'Parameters chosen on calibration data only, at a calibration-defined '
         'decision-layer FAR target of 0.05 (feasible band 0.04-0.05).',
     size=16, first=True, space_before=0, line=1.05)
para(tf, 'The participant is the unit of inference; paired tests, Holm-corrected.',
     size=16, space_before=8, line=1.05)

cx = Inches(5.55)
hd, htf = panel(s, cx, Inches(1.95), Inches(3.95), Inches(0.44), fill=NAVY)
para(htf, 'Margin + dwell earns its place only if', size=15, bold=True, colour=WHITE,
     first=True, space_before=0, align=PP_ALIGN.CENTER)
crit = [('1', 'fewer excess transitions after Holm correction'),
        ('2', 'FRR non-inferior: CI upper bound below +0.02'),
        ('3', 'detection failure non-inferior')]
for i, (n, t) in enumerate(crit):
    y = Inches(2.52) + i * Inches(0.86)
    c, ctf = panel(s, cx, y, Inches(3.95), Inches(0.72), fill=PALE)
    para(ctf, f'{n}.  {t}', size=15, first=True, space_before=0, line=1.05)
tb, tf = textbox(s, cx, Inches(5.18), Inches(3.95), Inches(0.9))
para(tf, 'against BOTH dwell only and margin only.', size=15, bold=True, colour=NAVY,
     first=True, space_before=0, align=PP_ALIGN.CENTER)

source(s, 'Rules, grids, outcomes and the verdict wording were frozen before the '
          'confirmatory score dumps existed.')

notes(s, """
The design is deliberately plain. Two factors, a margin and a dwell, crossed to give
the four cells on the left. The one in red is the policy under test.

Two things protect it. Every parameter is chosen on calibration data only, at a five
per cent false-accept target with a preregistered feasible band - the test data never
touches the threshold, the cell, or who is included. And the participant is the unit
of inference, so I am not treating a hundred and eighty frames from one person as
independent.

On the right are the three criteria I fixed in advance. They must hold against both
components. Note criterion two: false rejection must not rise by more than two
points. That one decides the result.
""")

# ====================================================================================
# 7. Primary result
# ====================================================================================
s = add('Title and Content'); drop_empty_placeholders(s)
set_title(s, 'Primary result')

rows = [
    ('', 'vs dwell only', 'vs margin only'),
    ('Participants paired', '30', '24'),
    ('Excess transitions, mean paired difference', '-0.13', '-0.20'),
    ('Median paired difference', '0', '0'),
    ('Holm-adjusted p', '0.69', '0.69'),
    ('FRR difference [95% CI]', '+0.074  [0.032, 0.119]', '+0.030  [-0.008, 0.069]'),
    ('Detection-failure difference', '0.000', '-0.007'),
]
tw, th = Inches(8.55), Inches(2.62)
gt = s.shapes.add_table(len(rows), 3, Inches(0.72), Inches(1.84), tw, th).table
gt.columns[0].width = Inches(4.15)
gt.columns[1].width = Inches(2.20)
gt.columns[2].width = Inches(2.20)
for ri, row in enumerate(rows):
    gt.rows[ri].height = Inches(0.34)
    for ci, val in enumerate(row):
        cell = gt.cell(ri, ci)
        cell.text = val
        cell.margin_left = cell.margin_right = Inches(0.08)
        cell.margin_top = cell.margin_bottom = Inches(0.02)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY if ri == 0 else (
            PALE if ri in (4, 5) else WHITE)
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT if ci == 0 else PP_ALIGN.CENTER
        for r in p.runs:
            r.font.name, r.font.size = FONT, Pt(15)
            r.font.bold = (ri == 0) or (ri in (4, 5))
            r.font.color.rgb = WHITE if ri == 0 else (
                ACCENT if (ri == 5 and ci == 1) else INK)

p, tf2 = panel(s, Inches(0.72), Inches(4.72), tw, Inches(1.02), fill=NAVY)
para(tf2, 'Margin plus dwell offers no measurable advantage over its components on '
          'this benchmark, and is FRR-inferior to dwell alone.',
     size=18, bold=True, colour=WHITE, first=True, space_before=0,
     align=PP_ALIGN.CENTER, line=1.05)

tb, tf = textbox(s, Inches(0.72), Inches(5.88), tw, Inches(0.95))
para(tf, 'Against dwell, 20 of 30 participants tied exactly. The +0.074 FRR penalty '
         'breaches the preregistered +0.02 bound.', size=15, colour=INK, first=True,
     space_before=0, line=1.05)

source(s, 'Source: primary/primary_tests.csv, target FAR 0.05.', y=Inches(6.92))

notes(s, """
This is the core result, so I will take it slowly.

Read the p-values first. Both are nought point six nine, so the stability criterion
fails against both components. But be precise about what that means: failure to
reject is not proof of equivalence. On its own this could just mean I lacked power,
and I will show you shortly that I probably did.

The stronger evidence is the red row. Against dwell alone, adding the margin raises
false rejection by seven point four points, interval three point two to eleven point
nine. I prespecified a limit of two. The whole interval sits above it. So this is not
an underpowered null - it is a positive finding in the wrong direction.

Hence the verdict in the box, which was also fixed in advance. And one number hints
at the power problem: twenty of thirty participants tied exactly.
""")

# ====================================================================================
# 8. Response surface
# ====================================================================================
s = add('Title and Content'); drop_empty_placeholders(s)
set_title(s, 'Reading the surface')

picture(s, 'fig1_factorial_surface', Inches(0.45), Inches(1.78), Inches(3.05), Inches(4.90))

tx = Inches(3.80)
tb, tf = textbox(s, tx, Inches(1.90), Inches(5.72), Inches(2.3))
para(tf, 'Stability improves down and to the right. Lockout worsens along the '
         'same direction.', size=20, bold=True, colour=NAVY, first=True,
     space_before=0, line=1.05)
para(tf, 'Instantaneous (0, 1):  2.012 excess transitions, FRR 0.042', size=18,
     space_before=12, line=1.05)
para(tf, 'Dwell (0, 2):  0.466 excess transitions, FRR 0.052', size=18,
     space_before=7, line=1.05)
para(tf, 'Margin + dwell (0.20, 2):  0.000 excess, FRR 0.356', size=18,
     colour=ACCENT, space_before=7, line=1.05)

p, tf2 = panel(s, tx, Inches(4.42), Inches(5.72), Inches(1.30), fill=None, line=ACCENT)
para(tf2, 'Zero flips is not success. The zero-transition cells are supported by as '
          'few as 8 participants and reject the genuine user more than a third of '
          'the time.', size=16, first=True, space_before=0, line=1.05)

tb, tf = textbox(s, tx, Inches(5.86), Inches(5.72), Inches(0.95))
para(tf, 'Cells are NOT paired: feasible participant sets differ from 6 to 31. Read '
         'the broad shape only.', size=15, bold=True, colour=NAVY, first=True,
     space_before=0, line=1.05)

source(s, 'Figure 1. Response surface at target FAR 0.05.', y=Inches(6.92))

notes(s, """
This is the whole surface at the primary operating point. Margin down the rows,
dwell across; stability on top, lockout below.

Take only the shape. Colour lightens down and to the right in the top panel - more
stable - and darkens in the same direction below - more lockout. Same movement. You
cannot buy stability without paying in lockout.

The three numbers make it concrete. A dwell of two takes excess transitions from two
point nought to nought point four seven for about one extra point of false rejection.
The most aggressive cell reaches exactly zero - and rejects the genuine user
thirty-six per cent of the time. Zero flips is not success; it is a system that has
stopped responding.

Two cautions: that cell rests on eight participants, and these cells are not paired.
""")

# ====================================================================================
# 9. No mechanism escapes the trade-off
# ====================================================================================
s = add('Title and Content'); drop_empty_placeholders(s)
set_title(s, 'No mechanism escapes it')

picture(s, 'fig2_stability_lockout', Inches(0.45), Inches(1.80), Inches(3.95), Inches(4.75))

tx = Inches(4.65)
tb, tf = textbox(s, tx, Inches(1.92), Inches(4.90), Inches(3.0))
para(tf, 'Nine temporal mechanisms, all calibrated to the same FAR target. '
         'Lower left is better.', size=18, first=True, space_before=0, line=1.05)
para(tf, 'Every mechanism beats instantaneous on stability. None dominates on both '
         'axes.', size=18, bold=True, colour=NAVY, space_before=11, line=1.05)
para(tf, 'The most stable are the most locked out: margin + dwell 0.20 excess at '
         'FRR 0.124; trust model 0.04 at FRR 0.172.', size=18, space_before=11,
     line=1.05)

p, tf2 = panel(s, tx, Inches(5.06), Inches(4.90), Inches(0.90), fill=PALE)
para(tf2, 'Debounce - a short dwell - is the simplest defensible first intervention.',
     size=17, bold=True, colour=NAVY, first=True, space_before=0, line=1.05)

tb, tf = textbox(s, tx, Inches(6.06), Inches(4.90), Inches(0.80))
para(tf, 'SPRT is exploratory: it had the largest parameter grid, so the greatest '
         'selection opportunity.', size=13, italic=True, colour=GREY, first=True,
     space_before=0, line=1.05)

source(s, 'Figure 2. Stability-lockout plane; small markers are FAR 0.03 and 0.07.',
       y=Inches(6.92))

notes(s, """
The obvious next question is whether some other rule escapes the trade-off. It does
not.

Nine mechanisms, same false-accept target. Horizontal is lockout, vertical is
instability, and note the broken axis - instantaneous sits an order of magnitude
above the rest.

Two readings. Every temporal mechanism beats instantaneous, so persistence does work.
But nothing reaches the bottom-left corner. The most stable are the most locked out;
the trust model is the extreme, almost perfectly stable while rejecting the genuine
user seventeen per cent of the time.

The open markers are the same mechanisms at three and seven per cent, and the short
trails say the ordering is not an artefact of choosing five. I flag SPRT as
exploratory - largest grid, most selection opportunity.
""")

# ====================================================================================
# 10. Threats to validity
# ====================================================================================
s = add('Title and Content'); drop_empty_placeholders(s)
set_title(s, 'Threats to validity')

picture(s, 'fig3_instability_concentration', Inches(0.50), Inches(1.80), Inches(4.25), Inches(2.62))
picture(s, 'fig4_score_validity_f3_f7', Inches(5.25), Inches(1.80), Inches(4.25), Inches(2.62))

for x, head, body in [
    (Inches(0.50), 'Instability is rare and concentrated',
     '71.7% of instantaneous test sequences never flip. Five of 30 participants '
     'carry 65.6% of it. There is little for a margin to improve, which limits power.'),
    (Inches(5.25), 'The score is not clean identity evidence',
     'Removing location and device-state features drops mean AUC from 0.990 to 0.758; '
     'paired difference 0.232 [0.191, 0.273].')]:
    hd, htf = panel(s, x, Inches(4.56), Inches(4.25), Inches(0.42), fill=NAVY)
    para(htf, head, size=14, bold=True, colour=WHITE, first=True, space_before=0,
         align=PP_ALIGN.CENTER)
    tb, tf = textbox(s, x, Inches(5.06), Inches(4.25), Inches(1.15))
    para(tf, body, size=15, first=True, space_before=0, line=1.05)

p, tf2 = panel(s, Inches(0.50), Inches(6.18), Inches(9.0), Inches(0.60), fill=None, line=ACCENT)
para(tf2, 'ExtraSensory is a context-recognition dataset, not an authentication '
          'dataset. The sequences are real observations, composed - not observed takeovers.',
     size=14, bold=True, colour=ACCENT, first=True, space_before=0,
     align=PP_ALIGN.CENTER, line=1.05)

notes(s, """
I put the limitations before the contribution because they bound it.

The left panel explains the tied participants. Under instantaneous thresholding,
seventy-two per cent of sequences never flip at all, and five participants of thirty
carry two thirds of the instability. For most people a dwell has already removed
everything there was to remove, so there is nothing left for a margin to improve.
That is a power limitation, and it is the honest reading of my null.

The right panel is more serious. Strip out location and device state, keep only which
sensors were missing, and mean AUC still sits at nought point seven six.

So, explicitly: evidence not established in the project materials for any claim that
this score is behavioural identity independent of context or device.
""")

# ====================================================================================
# 11. Contribution and the closing answer
# ====================================================================================
s = add('Title and Content'); drop_empty_placeholders(s)
set_title(s, 'Contribution and answer')

blocks = [('Evidence', 'A preregistered null: no stability gain from the margin '
                       '(p = 0.69 against both components), and an FRR penalty of '
                       '+0.074 against dwell that breaches the +0.02 bound.'),
          ('Interpretation', 'Persistence is what transfers from handover. The margin '
                             'does not add measurable value here - it converts '
                             'instability into lockout.'),
          ('Recommendation', 'Evaluate the decision layer separately from the '
                             'classifier, and always report excess transitions with '
                             'FAR, FRR and recovery together.')]
for i, (head, body) in enumerate(blocks):
    y = Inches(1.86) + i * Inches(1.32)
    hd, htf = panel(s, L, y, Inches(2.30), Inches(1.16), fill=NAVY)
    para(htf, head, size=17, bold=True, colour=WHITE, first=True, space_before=0,
         align=PP_ALIGN.CENTER)
    htf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tb, tf = textbox(s, L + Inches(2.48), y + Inches(0.04), Inches(6.52), Inches(1.10),
                     anchor=MSO_ANCHOR.MIDDLE)
    para(tf, body, size=17, first=True, space_before=0, line=1.05)

rule(s, L, Inches(5.86), W)
tb, tf = textbox(s, L, Inches(6.00), W, Inches(0.70))
para(tf, 'The margin did not earn its place on this benchmark.', size=22, bold=True,
     colour=NAVY, first=True, space_before=0, align=PP_ALIGN.CENTER)

notes(s, """
To close, let me separate the finding from what I think it means.

The evidence is a preregistered null plus a directional failure: no stability gain
against either component, and a false-rejection penalty against dwell that breaks the
bound I set in advance.

My interpretation is that persistence is the part of the analogy that transfers.
Requiring evidence to hold works; the margin, here, mostly converts instability into
lockout.

The recommendation is the part I would defend hardest: evaluate the decision layer
separately from the classifier, and never report a stability number alone - report it
with false accepts, false rejects and recovery, or a policy that has simply stopped
responding will look like your best one.

So, bounded to this dataset and protocol: the margin did not earn its place. Thank
you.
""")

prs.save(OUT)
print(f'wrote {OUT}')
print(f'slides: {len(prs.slides.__iter__.__self__._sldIdLst)}')
for i, sl in enumerate(prs.slides, 1):
    t = sl.shapes.title.text if sl.shapes.title is not None else '(title slide)'
    n = len(sl.notes_slide.notes_text_frame.text.split())
    print(f'  {i:2d}. {t[:46]:48s} notes {n:3d} words')
