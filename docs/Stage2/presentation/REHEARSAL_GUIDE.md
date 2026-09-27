# Viva rehearsal guide

**Deck:** `CSCD601_Viva_Presentation.pptx` — the **official Postgraduate Viva 12-slide
template**, filled in. All twelve official headings are unchanged.
**Paper:** *Does the Handover Margin Earn Its Place? A Factorial Comparison of Temporal
Decision Policies for Context-Based Continuous Smartphone Authentication*
**Estimated delivery:** 9 min 40 s at a normal pace (140 wpm), 10 min 30 s if you speak
slowly. The template's own guidance is 45–50 s per main slide; this deck sits inside it.

Every script below is also in the PowerPoint speaker-notes pane, so you can rehearse in
Presenter View without this file. What this document adds: purpose, the single key point
per slide, likely panel questions with answers grounded in the dissertation, and timings.

---

## Structural note

**Twelve slides, and every official heading kept exactly as issued.** The official
template was used as the file itself — it was opened and its bodies replaced — so the
headings, order, slide master, theme, background artwork, footers, slide numbers and
University of Ghana furniture are inherited rather than recreated.

**How this study maps onto the official sections.** The template is written for a project
that builds a system; this project runs a controlled experiment. Two headings therefore
carry a slightly different reading, and it is worth knowing why before a panel member
asks:

| Official heading | What it holds here | Why |
|---|---|---|
| **System / Model Design** | The decision policy itself — the accept/reject rule, the margin × dwell factorial, and the evaluation contract | There is no system architecture to draw. The "model" under test *is* the decision rule, so the design slide shows the rule and the sequence it acts on |
| **Implementation Work Done** | Tools and versions, the score-dump architecture, the 20 executed factorial cells, and one defect found and fixed | The implementation is an experimental pipeline rather than an application, so "work done" is the executed grid and the reproducibility scaffolding |

Everything else maps directly. Results and Evaluation carries the preregistered test plus
the nine-mechanism evaluation; Conclusion and Future Work carries the limitations first,
then the conclusion, because the limitations bound what can be claimed.

**Other decisions worth knowing.**

- **The deck is 4:3.** That is the official template's own size (10 × 7.5 in), so the
  aspect-ratio question is settled — this is what the department issues.
- **"Margin + dwell" is used throughout, never "hysteresis."** In 3GPP, hysteresis is the
  margin term alone and time-to-trigger is a separate dwell term. The study exists to tell
  those apart, so calling the composed policy "hysteresis" would give away the question.
  The word does not appear anywhere on the slides.
- **A one-line finding was added to the title slide**, in the empty band the template
  leaves between the title and the subtitle. Nothing was moved to make room.
- **Deliberately excluded:** the full 20-cell response-surface table, the ten-mechanism
  tuned-family table, the FAR 0.03/0.07 sensitivity tables, the complete-feasibility
  subset and the post-hoc recovery descriptives. All are in the dissertation and in
  `docs/Stage2/tables/tables.md` if the panel asks for them.

---

## Slide 1 — Title  ·  ≈ 33 s

**Purpose.** Identify the work and give the finding immediately, so everything after it
is heard as evidence rather than suspense.

**What to say.**
> Good morning. My question is narrow and testable: when a continuous authentication
> system turns noisy scores into an authenticated or locked state, does the margin
> borrowed from cellular handover add anything beyond simply requiring evidence to
> persist?
>
> I will give the answer first, because everything after it is the evidence. It did not.
> Under a preregistered test it produced no measurable stability gain, and it locked the
> genuine user out more often than a plain dwell rule.

**Key point.** The answer is negative, it was preregistered, and it is bounded.

**Panel question.** *Why present a negative result at all?*
**Answer.** Because it was preregistered, so it is informative rather than a failed
experiment. The criteria and the verdict wording were frozen before the confirmatory
scores existed — if the margin had worked, the same rules would have said so. A null from
a frozen protocol is evidence; a null found afterwards would not be.

**Before you start.** Replace `[Student Name]` and `Supervisor: [Name]`. Those are the
only placeholders in the deck.

---

## Slide 2 — Presentation Outline  ·  ≈ 27 s

**Purpose.** Give the panel the route. Keep it brisk — this slide earns no marks.

**What to say.**
> Briefly, the route. I start with the problem the study exists to solve, then the
> question and the gap it comes from. The methodology and design sections explain how the
> comparison was made fair. The results section carries the preregistered test. I then
> give the contribution, and I will spend real time on the limitations, because they bound
> what I can claim.

**Key point.** Signal early that the limitations get real time. Panels notice.

---

## Slide 3 — Background and Problem Context  ·  ≈ 44 s

**Purpose.** Establish the one distinction the study depends on, and end on a single
clear problem statement, as the template asks.

**What to say.**
> Everything rests on this distinction. A classifier gives a score per frame; a phone has
> to hold a state. Turning one into the other is a design decision, and it is usually left
> implicit.
>
> The two ribbons are a schematic — I have labelled them, they are not data. Same user,
> same scores. The top row reverses eight times because the score sits near the threshold.
> The bottom row requires persistence and changes once.
>
> The consequence is in the box: this is a separate design layer, and AUC cannot see it,
> because AUC ranks frames and ignores the order they arrive in.

**Key point.** The decision layer is its own design layer, and frame-level accuracy cannot
measure it.

**Panel question.** *Is that schematic real data?*
**Answer.** No, and the slide says so. It illustrates the mechanism. The real version is
slide 7, where one actual test sequence flips 43 times under instantaneous thresholding
and 5 times under margin + dwell.

**Panel question.** *Why not just move the threshold?*
**Answer.** Moving the threshold changes where the boundary is, not the behaviour near it.
Any threshold has scores sitting close to it; the flicker comes from the crossing, not the
level. That is also why I calibrate every policy to a common false-accept target, so no
policy wins simply by sitting somewhere else.

---

## Slide 4 — Aim, Objectives & Questions  ·  ≈ 45 s

**Purpose.** State the aim, four defensible objectives, the research question and the
scope — including what is deliberately excluded.

**What to say.**
> The aim is deliberately narrow. Not whether temporal smoothing works in general, but
> whether the specific component borrowed from handover — the margin — earns the cost of
> adding it to a dwell rule.
>
> Four objectives, each defensible with evidence later: decompose the two factors under
> equal tuning; choose every parameter on calibration data only; evaluate at participant
> level across a vector of outcomes rather than accuracy alone; and test whether the score
> itself means what we want it to mean. That fourth one turns out to matter.
>
> Note the scope line: I exclude any claim about biometric identity, for reasons I will
> come to.

**Key point.** Every objective is testable, and the scope excludes the claim the data
cannot support.

**Panel question.** *Can you defend each objective with evidence?*
**Answer.** Yes, and they map to slides. Objective one is slide 7, the factorial.
Objective two is slide 6, calibration-only selection. Objective three is slide 9, the
participant-level paired test across FAR, FRR, detection and recovery. Objective four is
slide 11, the F3-versus-F7 probe — which is the objective that produced the most
uncomfortable finding, and I report it rather than dropping it.

---

## Slide 5 — Related Work and Identified Gap  ·  ≈ 48 s

**Purpose.** Four sources, then a gap narrow enough to be defensible.

**What to say.**
> The gap has to be stated carefully because it is narrow.
>
> Zeeshan and colleagues justify smoothing in exactly the words quoted, but never isolate
> it. Mondal and Bours do compare decision layers — so it is not true that nobody has —
> but they vary four factors at once and report action-domain measures rather than holding
> a common operating point. Sugrim and colleagues supply the missing methodological piece,
> and Stragapede and colleagues are the warning about what mobile models might really be
> learning.
>
> So the gap is the red box, and the last line is the claim I will defend: the novelty is
> the decomposition, not the classifier or the idea of smoothing.

**Key point.** The novelty is the decomposition under equal tuning at a common operating
point — nothing larger.

**Panel question.** *Hasn't decision-layer comparison been done before?*
**Answer.** Yes, and I say so explicitly on the slide. Mondal and Bours compare fusion
schemes, thresholds, score boosting and trust models on continuous mouse dynamics. But
they sweep all four together and report average genuine and impostor actions rather than
holding a false-accept rate fixed. They establish that the decision layer matters; they do
not isolate the incremental effect of one component.

**Panel question.** *Is that enough for a Master's contribution?*
**Answer.** The contribution is methodological rather than algorithmic: a leakage-aware,
calibration-frozen decomposition showing why stability must be evaluated separately from
accuracy, and why a low transition count cannot be read without FRR and recovery. The
negative result is the demonstration that the framework has teeth — it was capable of
rejecting the hypothesis it was built to test.

---

## Slide 6 — Methodology / Project Approach  ·  ≈ 51 s

**Purpose.** Show the design choices that make the comparison fair. Most methodology
questions attach here.

**What to say.**
> The design choices here are all about making the comparison fair rather than making the
> result good.
>
> ExtraSensory is public and in the wild, but collected for context recognition rather
> than authentication — a limitation I return to. The cohort is the participants whose
> sampling is regular enough that a dwell of two frames means the same thing for everyone,
> fixed before any confirmatory score existed.
>
> Three protections against leakage: chronological rather than random partitions,
> preprocessing fitted on enrolment only, and final-test impostors held out of both
> fitting and calibration.
>
> The most important choice is the frozen score stream. Every mechanism reads the same
> stored scores, so any difference belongs to the decision rule and cannot be a retrained
> classifier.

**Key point.** The score stream is frozen, so every difference reported later is the
decision rule.

**Panel question.** *Why 31 participants and not all 60 in ExtraSensory?*
**Answer.** The 31 are the regular-cadence cohort — participants sampled close enough to
the nominal one-minute interval that a frame-count dwell means the same thing across
people. A dwell of two frames is not comparable between someone sampled every minute and
someone with hour-long gaps. That cohort was defined before the confirmatory score dumps
were generated, not chosen after seeing results.

**Panel question.** *How do you know there is no leakage?*
**Answer.** Four things. Chronological partitions, not random. Preprocessing fitted on
enrolment only. Final-test impostors held out of both fitting and calibration. And
inference at participant level, so 180 frames from one person are not treated as 180
independent observations. The Stage 1 audit in the repository documents what was wrong
with the earlier pipeline on each of these.

**Panel question.** *Ethical approval?*
**Answer.** ExtraSensory is a public, already-anonymised research dataset used under its
published terms, so no further approval was required. I collected no new data.

---

## Slide 7 — System / Model Design  ·  ≈ 51 s

**Purpose.** Show the decision rule, the factorial, and the sequence structure the
outcome measure comes from.

**What to say.**
> This is the design, and the figure on the left is the contract I would hold on to when
> judging the results.
>
> One real test sequence: sixty genuine frames, sixty from an unseen impostor, sixty of
> the genuine user returning. The three rows below are the state under three policies
> reading that identical stream.
>
> The rule is deliberately simple. A margin widens the band a score must cross; a dwell
> requires k consecutive qualifying frames before the state flips. Crossing the two
> factors gives the four cells, and the one in red is the policy under test.
>
> The outcome measure falls out of the structure: a correct trace has exactly two state
> changes, so anything beyond two is excess.

**Key point.** Margin and dwell are separated by construction, and both act on the same
frozen scores.

**Panel question.** *Why is there no system architecture diagram?*
**Answer.** Because the artefact under test is a decision rule, not an application. The
architecture that matters is the one on this slide: a frozen score stream feeding a
policy that emits a state per frame. Slide 8 shows the pipeline that produced it.

**Panel question.** *Are the 60–60–60 sequences realistic?*
**Answer.** No, and I state that as a limitation. They are real observations composed into
a fixed structure. That buys a clean, comparable transition structure — every sequence has
exactly one takeover and one recovery — at the cost of external validity. They are not
naturally observed takeover sessions with interruptions or shared-device use. A field
study is the next step.

---

## Slide 8 — Implementation Work Done  ·  ≈ 57 s

**Purpose.** Evidence of real work: tools, the executed grid, and an honestly reported
defect.

**What to say.**
> What was actually built. A per-user score generator, then a decision layer that replays
> stored scores offline. That mattered practically: fitting the models was ninety-two per
> cent of the runtime, so dumping the scores once made every later rule change essentially
> free — and it is what guarantees all policies see identical evidence.
>
> On the right is the executed factorial. Colour lightens down and to the right in the top
> panel, meaning more stable, and darkens in the same direction below, meaning more
> lockout. Same movement: you cannot buy stability without paying in lockout.
>
> One defect, honestly. A windowed mean disagreed with its reference at exact ties. I
> fixed it, added a regression test that fails against the old code, and reran the
> analysis. One secondary mechanism only; the preregistered test was unaffected.

**Key point.** The pipeline is reproducible, and the one defect found is disclosed with
its blast radius.

**Panel question.** *Why does the surface show cells you cannot compare?*
**Answer.** Because the feasible participant set differs from cell to cell — 6 to 31. A
cell is feasible for a participant only if a threshold exists reaching the calibration FAR
band, and aggressive settings are feasible for fewer, typically easier, participants. So
cell means are not paired contrasts. That is exactly why the confirmatory test on the next
slide pairs within participant.

**Panel question.** *You found a bug. How do I know there are no others?*
**Answer.** You do not, and I would not claim otherwise. What I can show is the process
that caught this one: reference implementations checked frame-by-frame, a regression test
that fails against the old code, and an analysis that is rerun from frozen inputs. The
defect is documented with its measured effect — 0.111% of frame decisions in one secondary
mechanism — rather than quietly patched.

---

## Slide 9 — Results and Evaluation  ·  ≈ 75 s — the slide the viva turns on

**Purpose.** The confirmatory result, read as a directional failure rather than merely an
absence of evidence, plus the evaluation across all nine mechanisms.

**What to say.**
> This is the core result, so I will take it slowly.
>
> Read the p-values first. Both are nought point six nine, so the stability criterion
> fails against both components. But be precise about what that means: failure to reject
> is not proof of equivalence. On its own this could just mean I lacked power, and I will
> show you on the next slide but one that I probably did.
>
> The stronger evidence is the red row. Against dwell alone, adding the margin raises
> false rejection by seven point four points, interval three point two to eleven point
> nine. I prespecified a limit of two. The whole interval sits above it. So this is not an
> underpowered null — it is a positive finding in the wrong direction.
>
> The figure evaluates nine mechanisms at the same target. Every one beats instantaneous
> thresholding, so persistence works. But nothing reaches the bottom-left corner, and the
> most stable are the most locked out. Note SPRT is exploratory — it had the largest grid,
> so the most selection opportunity.

**Key point.** The claim rests on the FRR non-inferiority failure, not on the null.

**Panel question.** *A null usually means you were underpowered. How is this different?*
**Answer.** For the stability criterion that is a fair reading and I accept it — twenty of
thirty participants tied, and slide 11 explains why. But the conclusion does not rest on
that null. It rests on criterion two, where the confidence interval for the FRR difference
is 0.032 to 0.119 and lies entirely above my prespecified bound of 0.02. That is a
positive finding with a direction. Low power makes an effect harder to detect; it does not
manufacture one.

**Panel question.** *Where did the ±0.02 bound come from?*
**Answer.** It is a judgement, declared in the preregistration rather than chosen
afterwards. Two percentage points is roughly the cost of the dwell intervention itself —
dwell raises FRR from 0.042 to 0.052 — so the bound says a margin must not cost more than
the intervention it is added to. The observed penalty was +0.074, more than three times
the bound, so the conclusion does not hinge on the exact value.

**Panel question.** *Why Wilcoxon rather than a t-test, and why Holm?*
**Answer.** Wilcoxon because the paired differences are far from normal — the modal
difference is exactly zero, since most participants have no instability to remove. Holm
because the stability hypothesis is tested against two preregistered comparators, so
without correction I would be taking two shots at the same claim.

**Panel question.** *SPRT looks like the winner. Why not recommend it?*
**Answer.** Because I do not trust the comparison enough. SPRT had a three-dimensional
grid against one or two dimensions for the others, so it had far more chances to find a
setting suiting each participant. That is selection optimism, not necessarily a better
mechanism. It is an interesting secondary result; confirming it needs equalised grids.

---

## Slide 10 — Contribution and Significance  ·  ≈ 60 s

**Purpose.** Separate evidence from interpretation from significance, and connect back to
the original problem.

**What to say.**
> Let me separate the finding from what I think it means, because they are claims of
> different strength.
>
> The evidence is a preregistered null plus a directional failure. No stability gain
> against either component, and a false-rejection penalty against dwell that breaks the
> bound I set in advance.
>
> My interpretation is that persistence is the part of the handover analogy that actually
> transfers. Requiring evidence to hold works. The margin, on this benchmark, mostly
> converts instability into lockout.
>
> The significance is methodological rather than algorithmic, and that is the part I would
> defend hardest. The classifier here is an instrument, not the contribution. What the
> project provides is a way to ask whether a decision rule genuinely improves a
> continuous-authentication system — and the practical rule at the bottom follows directly:
> never report a stability number on its own.

**Key point.** The contribution is the framework and the protocol; the null demonstrates
both work.

**Panel question.** *What is the practical implication for a system designer?*
**Answer.** If you have a reasonably clean score stream and you see state flicker, add a
short dwell first. It is simpler, easier to calibrate, and on this benchmark captured most
of the available stabilisation for about a percentage point of extra false rejection. Do
not reach for a composed margin-plus-dwell policy on the assumption that more machinery
means more stability.

**Panel question.** *State your contribution in one sentence.*
**Answer.** A leakage-aware, calibration-frozen decomposition that isolates one
decision-layer component at a matched operating point, and shows that the component
borrowed from cellular handover does not earn its place on this benchmark.

---

## Slide 11 — Conclusion and Future Work  ·  ≈ 60 s — do not rush this

**Purpose.** Limitations first, because they bound the conclusion; then the conclusion and
the future work that follows from them.

**What to say.**
> I put the limitations before the conclusion because they bound it.
>
> The left panel explains the tied participants. Seventy-two per cent of sequences never
> flip at all, and five participants of thirty carry two thirds of the instability. For
> most people a dwell has already removed everything there was to remove, so there is
> nothing left for a margin to improve. That is the honest reading of my null.
>
> The right panel is more serious. Strip out location and device state, keep only which
> sensors were missing, and mean AUC still sits at nought point seven six. So, explicitly:
> evidence not established in the project materials for any claim that this score is
> behavioural identity independent of context or device.
>
> The conclusion is bounded to this dataset and protocol, and the future work follows
> straight from those two panels.

**Key point.** The study can say what a decision rule does to a score stream. It cannot
say the stream is biometric identity.

**Panel question.** *If missingness alone gives AUC 0.758, is this authentication at all?*
**Answer.** That is the right question and my honest answer is that I cannot rule it out.
The probe does not show missingness drove the primary scores — the full feature set
reaches 0.990, so there is discrimination beyond it — but it does show the score is not a
clean behavioural-identity construct. It could be behaviour, handset, logging process or
context regularity, and this design cannot separate them. What it does not undermine is
the decision-layer result: the comparison holds the score stream fixed, so whatever the
score represents, every policy reads the same one.

**Panel question.** *Why use ExtraSensory if it is not an authentication dataset?*
**Answer.** Because it gives real, continuous, in-the-wild sensor streams from many
participants over weeks, which is what a temporal decision-layer study needs and what
purpose-built authentication datasets rarely have. The cost is construct validity, and I
report it rather than hiding it.

**Panel question.** *What would you do differently?*
**Answer.** Three things, and they are the future work on the slide. Select for
instability — the participants who actually flicker — because the concentration on the
left panel is what cost me power. Use a dataset with the same device across users, or the
same user across devices, so device identity can be separated from user identity. And
equalise the tuning grids across mechanism families so the SPRT result can be confirmed.

---

## Slide 12 — References  ·  ≈ 34 s

**Purpose.** Show the sources are real, consistent and actually used. Do not read them
aloud.

**What to say.**
> These are the eight sources that directly support what I have presented, in APA style.
> Every one is cited on a slide or underpins a design choice: Mondal and Bours and Sugrim
> for the gap, Zeeshan for the claim I am testing, Stragapede for the device confound,
> Vaizman for the dataset, Georgiev and Kapoor for the evaluation-validity design, and
> Baldwin for the preregistration position. The full list is in the dissertation.
>
> Thank you — I am happy to take questions.

**Panel question.** *Baldwin is about preregistering data you have already seen. Does that
apply to you?*
**Answer.** Yes, and I cite it for exactly that reason. My rules were frozen before the
Stage 2 confirmatory score dumps existed and the executed code is byte-identical to the
frozen code. But I had prior access to ExtraSensory through earlier exploratory work, so I
describe this as confirmatory with respect to the frozen dumps and rules, not an
untouched-data replication. Baldwin and colleagues are explicit that preregistration
cannot fully remove researcher bias once data have been seen; the honest remedy is to
declare the prior access, which I do.

---

## Timing at a glance

| Slide | Official heading | Words | ≈ Time |
|---:|---|---:|---:|
| 1 | Title | 77 | 0:33 |
| 2 | Presentation Outline | 62 | 0:27 |
| 3 | Background and Problem Context | 102 | 0:44 |
| 4 | Aim, Objectives & Questions | 105 | 0:45 |
| 5 | Related Work and Identified Gap | 113 | 0:48 |
| 6 | Methodology / Project Approach | 120 | 0:51 |
| 7 | System / Model Design | 119 | 0:51 |
| 8 | Implementation Work Done | 133 | 0:57 |
| 9 | **Results and Evaluation** | 174 | 1:15 |
| 10 | Contribution and Significance | 139 | 1:00 |
| 11 | Conclusion and Future Work | 139 | 1:00 |
| 12 | References | 80 | 0:34 |
| | **Total** | **1,363** | **9:45** |

At 140 words per minute, an unhurried academic pace. If you are running long, compress
slides 5 and 8 — the three literature sentences into one, and the defect story into a
single line. **Never compress slide 9 or slide 11.**

## If you are cut to five minutes

Slides 1, 7, 9, 11. The contract, the result, the bound on it, and the claim. Say on
slide 7 that the score stream is frozen, and on slide 9 that the conclusion rests on the
FRR interval rather than the p-value.

## Rehearsal checklist

- [ ] Replace `[Student Name]` and `Supervisor: [Name]` on slide 1
- [ ] Rehearse slide 9 aloud three times — it is the slide the viva turns on
- [ ] Practise saying "I cannot rule that out" about the F7 probe without becoming
      defensive; it is a limitation you found yourself, not one the panel found
- [ ] Have `docs/Stage2/tables/tables.md` open on a second screen for the full tables
- [ ] Know these four numbers cold: **p = 0.69**, **FRR +0.074 [0.032, 0.119]**,
      **bound +0.02**, **2.012 → 0.466 for a dwell of two**
