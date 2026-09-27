# Viva rehearsal guide

**Deck:** `CSCD601_Viva_Presentation.pptx` (11 slides, 4:3)
**Paper:** *Does the Handover Margin Earn Its Place? A Factorial Comparison of Temporal
Decision Policies for Context-Based Continuous Smartphone Authentication*
**Estimated delivery:** 9 min 30 s at a normal speaking pace (140 wpm); 10 min 20 s if
you speak slowly. Buffer to the 10-minute limit is deliberate.

Every script below is also in the PowerPoint speaker-notes pane, so you can rehearse
in Presenter View without this file. This document adds what the notes pane cannot:
purpose, the single key point, likely panel questions and grounded answers.

---

## Structural note

**Eleven slides.** Not eighteen. The departmental sample sequence allocates slides to
sections that this study does not have — there is no study area, no population
sampling, no questionnaire, no geographical context. Forcing those headings would have
produced empty slides and pushed the delivery past ten minutes. The sequence below
covers every element of the departmental structure, but merged where the research
warrants it.

| Departmental section | Where it lives | Why |
|---|---|---|
| Title, candidate, department, supervisor | Slide 1 | Unchanged |
| Introduction and background | Slide 2 | Compressed to the one distinction the study turns on: a score is not a state |
| Statement of the problem (2 slides) | Slides 2–3 | One slide of problem, one of gap. Two full slides of problem statement would repeat the introduction |
| Research questions | Slide 3 | Placed with the gap, so the question visibly follows from it |
| General and specific objectives | Folded into slides 3 and 6 | The objectives restate the research question and the three preregistered criteria. Reading them twice wastes a minute |
| Literature review (2 slides) | Slide 3, plus the framework on slide 4 | Only the three sources that establish the gap. A survey slide would not survive a 10-minute budget |
| Methodology (4 slides) | Slides 5–6 | Two slides: the evaluation contract, then the design and the preregistered test |
| Results (2 slides) | Slides 7–9 | **Expanded to three.** This is where a viva is won or lost, and the study has one confirmatory result plus two descriptive displays that guard against misreading it |
| Discussion | Slides 8–9 (inline) and 11 | Interpretation sits beside each display rather than in one block, so evidence and interpretation stay visibly separate |
| Conclusion | Slide 11 | |
| Recommendations and limitations | Slides 10–11 | **Limitations come first, on their own slide.** They bound the contribution, so the panel should see them before the claim |
| References | Cited in place on slides 3, 4, 5 | A wall-of-references slide is never read. Full list is in the paper |

**Other decisions worth knowing before you are asked.**

- **The deck is 4:3, not 16:9.** The supplied departmental template is 10 × 7.5 in, and
  the brief made that template the visual authority. Changing the aspect ratio would
  have meant rebuilding the background artwork, the navy title band and the University
  of Ghana furniture rather than inheriting them. If the viva room projects 16:9, the
  deck will letterbox with bars at the sides — it will not crop or distort. Ask the
  department which the room uses; if they want 16:9 it is a one-line rebuild.
- **The deck was built on top of the template file itself**, not redrawn to look like
  it. The slide master, theme, colour scheme, fonts, background images and logo are
  inherited, so the file is genuinely the same deck.
- **"Margin + dwell" is used everywhere, never "hysteresis."** In 3GPP, hysteresis is
  the margin term alone and time-to-trigger is a separate dwell term. The study exists
  to tell those apart, so calling the composed policy "hysteresis" would give away the
  question. The word appears twice on slide 4, both times defining the analogy.
- **Deliberately excluded from the deck:** the full response-surface table (20 cells),
  the tuned-family table (10 mechanisms × 7 metrics), the FAR 0.03 / 0.07 sensitivity
  tables, the complete-feasibility subset, the post-hoc recovery descriptives, and the
  reference list. All are in the paper and in `docs/Stage2/tables/tables.md` if the
  panel asks. Slide 9 shows the family comparison as a picture instead of a table
  because ten rows of seven numbers cannot be read in sixty seconds.

---

## Slide 1 — Title and the one-sentence answer

**≈ 33 s**

**Purpose.** Identify the work and give the panel the finding immediately, so that
everything after it is heard as evidence rather than suspense.

**What to say.**
> Good morning. My question is narrow and testable: when a continuous authentication
> system turns noisy scores into an authenticated or locked state, does the margin
> borrowed from cellular handover add anything beyond simply requiring evidence to
> persist?
>
> I will give the answer first. It did not. Under a preregistered test it produced no
> measurable stability gain, and it locked the genuine user out more often than a plain
> dwell. Let me show you why the question matters.

**Key point.** The answer is negative, it was preregistered, and it is bounded to this
benchmark.

**Panel question.** *Why present a negative result at all?*
**Answer.** Because it was preregistered, so it is informative rather than a failed
experiment. The criteria and the verdict wording were frozen before the confirmatory
scores existed — if the margin had worked, the same rules would have said so. A null
from a frozen protocol is evidence; a null found after the fact would not be.

**Before you start.** Replace `[Name]` and `[Supervisor]` on the title slide. Those are
the only two placeholders in the deck.

---

## Slide 2 — Scores are not states

**≈ 42 s**

**Purpose.** Establish the one distinction the whole study depends on, and pre-empt the
question "isn't this just a classifier problem?"

**What to say.**
> Everything rests on this distinction. A classifier gives a score per frame; a phone
> has to hold a state. Turning one into the other is a design decision, and it is
> usually left implicit.
>
> The two ribbons are a schematic — I have labelled them, they are not data. Same user,
> same scores. The top row reverses eight times because the score sits near the
> threshold. The bottom row requires persistence and changes once.
>
> The consequence is that AUC cannot see the difference: it ranks frames and ignores
> their order. A system can score well and still behave badly.

**Key point.** The decision layer is a separate design layer, and frame-level accuracy
cannot measure it.

**Panel question.** *Is this schematic real data?*
**Answer.** No, and the slide says so. It is an illustration of the mechanism. The real
version is slide 5, where one actual test sequence flips 43 times under instantaneous
thresholding and 5 times under margin + dwell.

**Panel question.** *Why not just move the threshold?*
**Answer.** Moving the threshold changes where the boundary is, not the behaviour near
it. Any threshold has scores sitting close to it; the flicker comes from the crossing,
not from the level. That is why a temporal rule is needed at all — and it is also why
I calibrate every policy to a common false-accept target, so no policy wins by sitting
at a different threshold.

**Transition.** "So the decision layer needs separate evaluation — and that is where the
literature is thin."

---

## Slide 3 — The gap and the question

**≈ 52 s**

**Purpose.** Establish a defensible, narrow gap and state the research question.

**What to say.**
> The gap is narrow and I do not want to overstate it. It is not true that nobody has
> compared decision layers.
>
> What is missing is one contrast. Zeeshan and colleagues justify smoothing in exactly
> the words quoted, but never isolate it and never test a margin. Mondal and Bours do
> compare decision layers, but vary four factors at once and report action-domain
> measures rather than holding a common operating point. Sugrim and colleagues supply
> the missing piece: comparing at equal error rates tells an implementer nothing when
> they have a fixed false-accept requirement.
>
> So the defensible question is the one in the box — does the margin add anything to
> dwell, tuned equally, on one score stream, at one operating point?

**Key point.** The novelty is the decomposition under equal tuning at a common
operating point — not the classifier, the dataset, or smoothing.

**Panel question.** *Hasn't decision-layer comparison been done before?*
**Answer.** Yes, and I say so explicitly. Mondal and Bours (2015) compare fusion
schemes, thresholds, score boosting and trust models on continuous mouse dynamics. But
they sweep all four together and report average genuine and impostor actions rather
than holding a false-accept rate fixed. So they establish that the decision layer
matters; they do not isolate the incremental effect of one component. That is the gap
I fill, and it is a narrow one.

**Panel question.** *Why is this enough for a Master's contribution?*
**Answer.** The contribution is methodological rather than algorithmic: a leakage-aware,
calibration-frozen decomposition that shows why stability must be evaluated separately
from accuracy, and why a low transition count cannot be read without FRR, FAR drift and
recovery. The negative result is the empirical demonstration that the framework has
teeth — it was capable of rejecting the hypothesis it was built to test.

**Transition.** "Before the design, let me be explicit about what the handover analogy
does and does not give us."

---

## Slide 4 — What transfers from handover

**≈ 48 s**

**Purpose.** Present the conceptual framework and, more importantly, its boundary. Also
fixes the terminology for the rest of the talk.

**What to say.**
> The analogy is where the idea comes from, so it needs a boundary.
>
> Two things transfer. Both domains face noisy evidence arriving in sequence, and in
> both a reversal is expensive. That gives the same responsiveness-against-stability
> tension.
>
> What does not transfer is at the bottom. Handover arbitrates between radio links that
> are interchangeable. Authentication weighs identity hypotheses where the errors are
> asymmetric — a false accept is a security failure, a false reject is an annoyance.
>
> One terminology point for the rest of the talk: in 3GPP, hysteresis is the margin and
> time-to-trigger is the dwell. So I never call the composed policy hysteresis. Telling
> those two apart is the whole study.

**Key point.** Persistence transfers from the analogy; the margin is the part under
test, and the analogy itself does not guarantee it transfers.

**Panel question.** *Why borrow from telecommunications at all?*
**Answer.** Because handover is a mature, standardised solution to a structurally
similar problem: noisy sequential evidence where reversing state is costly. The
standard has settled on two separate devices — a margin and a time-to-trigger — which
makes it a good source of hypotheses. My study takes the analogy seriously enough to
test it rather than assume it, and the honest finding is that only half of it
transfers.

**Panel question.** *Isn't a dual threshold just Schmitt-trigger hysteresis, which is
well established in signal processing?*
**Answer.** Mechanically, yes — and I am not claiming the mechanism is new. What is not
established is whether it helps *here*: on an authentication score stream, combined
with dwell, at a matched operating point. That is an empirical question about this
application, and the answer on this benchmark is that it does not.

---

## Slide 5 — The evaluation contract

**≈ 55 s**

**Purpose.** Show the panel exactly what was evaluated and what protects the result
from leakage. This is the methodology slide that most questions attach to.

**What to say.**
> This is the experimental contract, and it is what I would hold on to when judging the
> results.
>
> On the left is one real test sequence: sixty genuine frames, sixty from an impostor
> neither the model nor the calibration has seen, then sixty of the genuine user
> returning. The rows below are the state under three policies on that identical
> stream.
>
> The critical choice is that the score stream is frozen. Every mechanism reads the same
> stored scores, so any difference belongs to the decision rule and cannot be a
> retrained classifier.
>
> The outcome measure falls out of the structure: a correct trace has exactly two state
> changes, so anything beyond two is excess. One caveat — these are real observations
> composed into a fixed structure, not observed takeovers.

**Key point.** The score stream is frozen, so every difference reported later is the
decision rule.

**Panel question.** *Why 31 participants and not all 60 in ExtraSensory?*
**Answer.** The 31 are the regular-cadence cohort — participants whose sampling is close
enough to the nominal one-minute interval for a frame-count dwell to mean the same
thing across people. A dwell of two frames is not comparable between someone sampled
every minute and someone with hour-long gaps. That cohort was defined before the
confirmatory score dumps were generated, not chosen after seeing results.

**Panel question.** *Are the 60–60–60 sequences realistic?*
**Answer.** No, and I state that as a limitation. They are real observations composed
into a fixed structure. That buys a clean, comparable transition structure — every
sequence has exactly one takeover and one recovery, so excess transitions mean the same
thing everywhere. What it costs is external validity: these are not naturally observed
takeover sessions, with interruptions, shared device use or long-term behavioural
drift. A field study would be the next step.

**Panel question.** *How do you know there is no leakage?*
**Answer.** Four things. Partitions are chronological, not random. Preprocessing is
fitted on enrolment data only. Final-test impostors are held out of both model fitting
and calibration. And inference is at participant level, so frames from one person are
not treated as independent observations. The Stage 1 audit in the repository documents
what was wrong with the earlier pipeline on each of these points.

---

## Slide 6 — Design and the preregistered test

**≈ 54 s**

**Purpose.** Show that the factorial isolates the margin, and that the success criteria
were fixed in advance.

**What to say.**
> The design is deliberately plain. Two factors, a margin and a dwell, crossed to give
> the four cells on the left. The one in red is the policy under test.
>
> Two things protect it. Every parameter is chosen on calibration data only, at a five
> per cent false-accept target with a preregistered feasible band — the test data never
> touches the threshold, the cell, or who is included. And the participant is the unit
> of inference, so I am not treating a hundred and eighty frames from one person as
> independent.
>
> On the right are the three criteria I fixed in advance. They must hold against both
> components. Note criterion two: false rejection must not rise by more than two points.
> That one decides the result.

**Key point.** The comparison is a controlled decomposition with criteria fixed before
the data were seen.

**Panel question.** *Why a FAR target of 0.05, and why not compare at EER?*
**Answer.** Because Sugrim and colleagues show that equal-error-rate comparison is
uninformative when a system has a fixed false-accept requirement — many different
classifiers share an EER. Fixing the false-accept rate makes the comparison
interpretable for an implementer with a security budget. I chose 0.05 as a common
operating point and then repeated the whole analysis at 0.03 and 0.07 as a
sensitivity check; the ordering held, with rank correlations of 0.84 and 0.89.

**Panel question.** *Where did the ±0.02 non-inferiority margin come from?*
**Answer.** It is a judgement, and I declared it in the preregistration rather than
choosing it afterwards. Two percentage points of additional false rejection is roughly
the cost of the dwell intervention itself — dwell raises FRR from 0.042 to 0.052 — so
the bound says a margin must not cost more than the intervention it is added to. I
would defend it as conservative; the observed penalty was +0.074, more than three times
the bound, so the conclusion does not hinge on the exact value.

**Panel question.** *You preregistered after already working with the data. Is that
still preregistration?*
**Answer.** Partly, and I describe it accurately in the paper. The rules were frozen
before the Stage 2 confirmatory score dumps existed, and the executed code is
byte-identical to the frozen code. But I had prior access to ExtraSensory through
earlier exploratory work, so I call this confirmatory with respect to the frozen score
dumps and rules, not an untouched-data replication. Baldwin and colleagues are explicit
that preregistration cannot fully remove researcher bias once data have been seen — the
honest remedy is to declare the prior access, which I do.

---

## Slide 7 — Primary result

**≈ 63 s — the most important minute of the talk**

**Purpose.** Deliver the confirmatory result, and make sure the panel reads it as a
directional failure rather than merely an absence of evidence.

**What to say.**
> This is the core result, so I will take it slowly.
>
> Read the p-values first. Both are nought point six nine, so the stability criterion
> fails against both components. But be precise about what that means: failure to reject
> is not proof of equivalence. On its own this could just mean I lacked power, and I
> will show you shortly that I probably did.
>
> The stronger evidence is the red row. Against dwell alone, adding the margin raises
> false rejection by seven point four points, interval three point two to eleven point
> nine. I prespecified a limit of two. The whole interval sits above it. So this is not
> an underpowered null — it is a positive finding in the wrong direction.
>
> Hence the verdict in the box, which was also fixed in advance. And one number hints at
> the power problem: twenty of thirty participants tied exactly.

**Key point.** The claim does not rest on the null. It rests on the FRR
non-inferiority failure, which is a positive result with an interval excluding the
bound.

**Panel question.** *A null result usually means you were underpowered. How is this
different?*
**Answer.** For the stability criterion, that is a fair reading and I accept it —
twenty of thirty participants tied, and slide 10 explains why. But the conclusion does
not rest on that null. It rests on criterion two, where the confidence interval for the
FRR difference is 0.032 to 0.119 and lies entirely above my prespecified bound of 0.02.
That is a positive finding with a direction: the margin makes lockout measurably worse.
Low power makes it harder to detect an effect; it does not manufacture one.

**Panel question.** *Why Wilcoxon rather than a t-test?*
**Answer.** The paired differences are far from normal — the modal difference is exactly
zero, because most participants have no instability to remove. A signed-rank test does
not assume normality and handles that mass at zero more honestly than a t-test would.

**Panel question.** *Why Holm correction?*
**Answer.** Because the stability hypothesis is tested against two comparators, dwell
and margin, and both were preregistered as primary. Without correction I would be
taking two shots at the same claim. Holm is uniformly more powerful than Bonferroni
while controlling the family-wise error rate, so it costs nothing to use it.

**Transition.** "Let me show you the surface those cells came from, because it explains
how easy it would be to misread this."

---

## Slide 8 — Reading the surface

**≈ 58 s**

**Purpose.** Show the descriptive landscape and immediately disarm the trap in it —
that a cell showing zero excess transitions looks like the winner.

**What to say.**
> This is the whole surface at the primary operating point. Margin down the rows, dwell
> across; stability on top, lockout below.
>
> Take only the shape. Colour lightens down and to the right in the top panel — more
> stable — and darkens in the same direction below — more lockout. Same movement. You
> cannot buy stability without paying in lockout.
>
> The three numbers make it concrete. A dwell of two takes excess transitions from two
> point nought to nought point four seven for about one extra point of false rejection.
> The most aggressive cell reaches exactly zero — and rejects the genuine user
> thirty-six per cent of the time. Zero flips is not success; it is a system that has
> stopped responding.
>
> Two cautions: that cell rests on eight participants, and these cells are not paired.

**Key point.** Zero excess transitions is a failure mode, not an optimum — and the
surface is descriptive, not a set of treatment contrasts.

**Panel question.** *Why are the cells not comparable?*
**Answer.** Because the feasible participant set differs from cell to cell — from 6 to
31. A cell is only feasible for a participant if a threshold exists that reaches the
calibration FAR band. Aggressive settings are feasible for fewer people, and typically
for the easier ones, so a cell mean is computed over a different and non-random subset.
Comparing two cell means is therefore not a paired contrast. That is exactly why the
confirmatory test on slide 7 pairs within participant.

**Panel question.** *Which setting would you actually deploy?*
**Answer.** On this evidence, a dwell of two frames with no margin. It removes about
three quarters of the excess transitions for roughly one percentage point of extra
false rejection, and it is simpler to calibrate. But I would not call that a deployment
recommendation — it is a design principle from one dataset and one score generator.
The recommendation I do stand behind is the evaluation protocol.

---

## Slide 9 — No mechanism escapes it

**≈ 53 s**

**Purpose.** Generalise beyond the factorial: the trade-off is structural, not a
property of the margin alone.

**What to say.**
> The obvious next question is whether some other rule escapes the trade-off. It does
> not.
>
> Nine mechanisms, same false-accept target. Horizontal is lockout, vertical is
> instability, and note the broken axis — instantaneous sits an order of magnitude above
> the rest.
>
> Two readings. Every temporal mechanism beats instantaneous, so persistence does work.
> But nothing reaches the bottom-left corner. The most stable are the most locked out;
> the trust model is the extreme, almost perfectly stable while rejecting the genuine
> user seventeen per cent of the time.
>
> The open markers are the same mechanisms at three and seven per cent, and the short
> trails say the ordering is not an artefact of choosing five. I flag SPRT as
> exploratory — largest grid, most selection opportunity.

**Key point.** The stability–lockout trade-off is structural. No mechanism dominates.

**Panel question.** *SPRT looks like the winner. Why not recommend it?*
**Answer.** Because I do not trust the comparison enough. SPRT had by far the largest
candidate grid — a three-dimensional grid against one or two dimensions for the others
— so it had the most opportunities to find a setting that suits each participant. That
is selection optimism, not necessarily a better mechanism. It is a genuinely
interesting secondary result and I report it as such, but confirming it would need a
design that equalises grid size across families.

**Panel question.** *Isn't a trade-off curve the expected result? What is surprising?*
**Answer.** The trade-off itself is not surprising. Two things are. First, how cheap the
first intervention is — a two-frame dwell captures most of the available stabilisation
— and second, that the margin, which is the distinctive part of the handover analogy,
sits on the wrong side of the curve rather than shifting it. If the margin worked as
the analogy suggests, it should have bought stability more cheaply than dwell. It did
not.

---

## Slide 10 — Threats to validity

**≈ 55 s — do not rush or skip this**

**Purpose.** Bound the claim before making it. Presenting limitations before the
contribution is a deliberate choice and panels reward it.

**What to say.**
> I put the limitations before the contribution because they bound it.
>
> The left panel explains the tied participants. Under instantaneous thresholding,
> seventy-two per cent of sequences never flip at all, and five participants of thirty
> carry two thirds of the instability. For most people a dwell has already removed
> everything there was to remove, so there is nothing left for a margin to improve.
> That is a power limitation, and it is the honest reading of my null.
>
> The right panel is more serious. Strip out location and device state, keep only which
> sensors were missing, and mean AUC still sits at nought point seven six.
>
> So, explicitly: evidence not established in the project materials for any claim that
> this score is behavioural identity independent of context or device.

**Key point.** The study can say what a decision rule does to a score stream. It cannot
say the stream is biometric identity.

**Panel question.** *If missingness alone gives AUC 0.758, is this authentication at
all?*
**Answer.** That is the right question and my honest answer is that I cannot rule it
out. The probe does not show that missingness drove the primary scores — the full
feature set reaches 0.990, so there is discrimination beyond it — but it does show the
score is not a clean behavioural-identity construct. It could be behaviour, handset,
logging process or context regularity, and this design cannot separate them. What it
does not undermine is the decision-layer result: the comparison holds the score stream
fixed, so whatever the score represents, all policies read the same one. The
conclusions are about decision rules, not about biometric identity.

**Panel question.** *Why use ExtraSensory if it isn't an authentication dataset?*
**Answer.** Because it gives real, continuous, in-the-wild sensor streams from many
participants over weeks, which is what a temporal decision-layer study needs and what
purpose-built authentication datasets rarely have. The cost is construct validity, and
I report it rather than hiding it. Stragapede and colleagues make the same point about
mobile behavioural biometrics generally — models can identify the device rather than
the user.

**Panel question.** *What would you do differently?*
**Answer.** Three things. First, recruit or select for instability — the participants
who actually flicker — because the concentration on the left panel is what cost me
power. Second, use a dataset with the same device across users, or the same user across
devices, so device identity can be separated from user identity. Third, equalise the
tuning grids across mechanism families so the secondary comparison is not confounded by
selection opportunity.

---

## Slide 11 — Contribution and answer

**≈ 57 s**

**Purpose.** Separate evidence, interpretation and recommendation, and close on a
bounded claim.

**What to say.**
> To close, let me separate the finding from what I think it means.
>
> The evidence is a preregistered null plus a directional failure: no stability gain
> against either component, and a false-rejection penalty against dwell that breaks the
> bound I set in advance.
>
> My interpretation is that persistence is the part of the analogy that transfers.
> Requiring evidence to hold works; the margin, here, mostly converts instability into
> lockout.
>
> The recommendation is the part I would defend hardest: evaluate the decision layer
> separately from the classifier, and never report a stability number alone — report it
> with false accepts, false rejects and recovery, or a policy that has simply stopped
> responding will look like your best one.
>
> So, bounded to this dataset and protocol: the margin did not earn its place. Thank
> you.

**Key point.** The contribution is the framework and the protocol; the null is the
demonstration that both work.

**Panel question.** *What is the practical implication for a system designer?*
**Answer.** If you have a reasonably clean score stream and you see state flicker, add
a short dwell first. It is simpler, easier to calibrate, and on this benchmark it
captured most of the available stabilisation at about a percentage point of extra false
rejection. Do not reach for a composed margin-plus-dwell policy on the assumption that
more machinery means more stability — on this evidence it mostly buys lockout.

**Panel question.** *What remains unanswered?*
**Answer.** Whether the margin helps on a score stream that is noisier than this one.
My cohort is unusually stable — seventy-two per cent of sequences never flicker — so I
have tested the margin where there was little to fix. A dataset with genuinely unstable
scores might give it room to work. Also whether any of this survives on naturally
observed takeovers rather than composed sequences, and whether the SPRT result holds
once grid sizes are equalised.

**Panel question.** *If you had to state your contribution in one sentence?*
**Answer.** A leakage-aware, calibration-frozen decomposition that isolates one
decision-layer component at a matched operating point, and shows that the component
borrowed from cellular handover does not earn its place on this benchmark.

---

## Timing at a glance

| Slide | Content | Words | ≈ Time |
|---:|---|---:|---:|
| 1 | Title and answer | 77 | 0:33 |
| 2 | Scores are not states | 99 | 0:42 |
| 3 | Gap and question | 122 | 0:52 |
| 4 | What transfers from handover | 112 | 0:48 |
| 5 | Evaluation contract | 129 | 0:55 |
| 6 | Design and preregistered test | 126 | 0:54 |
| 7 | **Primary result** | 148 | 1:03 |
| 8 | Reading the surface | 136 | 0:58 |
| 9 | No mechanism escapes it | 124 | 0:53 |
| 10 | Threats to validity | 129 | 0:55 |
| 11 | Contribution and answer | 133 | 0:57 |
| | **Total** | **1,335** | **9:30** |

At 140 words per minute, which is an unhurried academic pace. At 130 wpm it is 10 min
20 s, so if you are running long the place to save time is slides 3 and 4 — compress
the three literature sentences into one and drop the second half of the analogy. Never
compress slide 7 or slide 10.

## If you are cut to five minutes

Slides 1, 5, 7, 10, 11. That is problem-free: the contract, the result, the bound on
it, and the claim. Say on slide 5 that the score stream is frozen, and on slide 7 that
the conclusion rests on the FRR interval rather than the p-value.

## Rehearsal checklist

- [ ] Replace `[Name]` and `[Supervisor]` on slide 1
- [ ] Confirm the projector aspect ratio with the department (deck is 4:3)
- [ ] Rehearse slide 7 aloud three times — it is the slide the viva turns on
- [ ] Be ready to say "I cannot rule that out" about the F7 probe without becoming
      defensive; it is a limitation you identified yourself, not one the panel found
- [ ] Have `docs/Stage2/tables/tables.md` open on a second screen for the full tables
- [ ] Know these four numbers cold: **p = 0.69**, **FRR +0.074 [0.032, 0.119]**,
      **bound +0.02**, **2.012 → 0.466 for a dwell of two**
