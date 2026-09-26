I’ve completed the adversarial audit of the corrected `main` branch, including the calibration implementation, operating-point artefacts, mechanism implementations, sequence construction, metrics, statistical analysis, and final results.

## Overall assessment

**Stage 2 is now methodologically credible, but I would not yet freeze it as the final thesis experiment.**

The remaining issues are no longer the catastrophic leakage/protocol problems from Stage 1. They are primarily about **what the comparison actually permits us to infer**, particularly the operating-point design and statistical dependence.

I would classify the current state as:

| Area                                                | Assessment                      |
| --------------------------------------------------- | ------------------------------- |
| Chronological enrolment/calibration/test separation | 🟢 Sound                        |
| Unseen final impostors                              | 🟢 Sound                        |
| Training-only preprocessing                         | 🟢 Sound                        |
| Common score stream                                 | 🟢 Sound                        |
| Detection-latency boundary                          | 🟢 Corrected                    |
| Calibration FAR interval                            | 🟢 Corrected                    |
| Explicit infeasible operating points                | 🟢 Correct                      |
| Controlled identity-transition construction         | 🟢 Defensible, with limitations |
| Participant-level analysis                          | 🟢 Appropriate in principle     |
| Statistical dependence structure                    | 🟡 Needs qualification          |
| “Matched operating point” claim                     | 🟡 Needs narrower wording       |
| Comparability of all nine mechanisms                | 🟡 Needs stronger qualification |
| SPRT comparison                                     | 🔴/🟡 Particularly problematic  |
| Thesis-ready final evidence                         | 🟡 Not quite yet                |

The important point is that **I do not recommend another research pivot**.

---

# 1. The good news: the core experimental architecture holds

The corrected experiment really does implement the architecture we wanted:

> data → temporally separated per-user model → common score stream → temporal decision mechanism → authentication state → security/stability/responsiveness metrics.

The final protocol uses 31 regular-cadence participants, chronological 60/20/20 splits, disjoint fitting/calibration/test impostor pools, and a fixed score generator shared across mechanisms.

The leakage tests also check participant-pool separation, test-impostor isolation, sequence consistency, calibration coverage, and parameter freezing.

That means the central methodological problem from the original Stage 1 experiment—random row splitting and same-impostor contamination—is no longer the foundation of the experiment.

---

# 2. The matched-operating-point issue is now exposed rather than hidden

This is actually a strength of the corrected run.

The calibration code correctly implements:

$$
0.04 \leq FAR_{cal} \leq 0.06.
$$

And it records infeasible cases rather than pretending that FAR = 0 is equivalent to FAR = 0.05.

The final run has:

**32/279 user–mechanism combinations with no feasible operating point.**

The concentration is striking:

* margin/dual threshold: **8/31**
* SPRT: **23/31**
* all other mechanisms combined: **1/155**

So **SPRT is not really participating in the same matched-operating-point experiment for most users.**

This is not merely a cosmetic caveat.

For 23 users, SPRT cannot achieve the specified calibration FAR interval with the available decision rule. The nearest achievable values can be substantially away from 0.05.

Therefore, the thesis should **not** say:

> “Nine mechanisms were compared at FAR = 5%.”

That statement is false.

The defensible formulation is closer to:

> “Nine temporal decision-layer mechanisms were evaluated using a calibration-defined target FAR of 5% with a ±1 percentage-point feasibility interval. The target interval was attainable for most mechanism–participant combinations, but not for all, particularly for SPRT and margin-based mechanisms; infeasible cases were retained and explicitly reported.”

That is a much stronger methodological statement because it acknowledges what the experiment actually did.

---

# 3. There is a deeper issue with interpreting the matched FAR

This is the most important conceptual point from the audit.

The experiment is comparing **decision-layer mechanisms**, and the FAR is measured after the mechanism has transformed the score stream into a state sequence.

That is reasonable.

But a stateful mechanism can alter FAR through its memory, persistence, or initial state—not merely through its threshold.

For example, a mechanism beginning in:

> `AUTHENTICATED`

can remain authenticated through a short sequence of low scores because its state-transition rule has persistence.

That is not necessarily a methodological flaw. **It is partly the phenomenon being studied.**

However, it means the operating point should be described as:

> **matched calibration FAR at the decision layer**

rather than implying that all mechanisms have equivalent underlying score-level operating characteristics.

This distinction should become part of the conceptual framing of RQ2.

---

# 4. The controlled identity-transition benchmark is defensible—but synthetic

The 60 genuine → 60 impostor → 60 recovery construction is methodologically useful because it creates an identical transition structure for every mechanism.

But it is not an observed authentication session.

The repository itself correctly calls these:

> “controlled identity-transition sequences constructed from real participant observations.”

That terminology should be preserved.

The consequence is important:

You can make claims about **response to controlled identity transitions**, but not directly about real-world phone handovers, real account takeover episodes, or naturally occurring user replacement.

This is a **scope limitation**, not a reason to discard the experiment.

---

# 5. The statistical unit is substantially better—but there is one dependence issue

The analysis correctly does:

> sequence metrics → average within enrolled user → compare mechanisms across users.

That is much preferable to treating thousands of frames as independent observations.

However, there is still a dependence structure worth explicitly acknowledging.

The experiment uses the same pool of 24 final-test impostor participants across the enrolled users.

Consequently, the 31 enrolled-user observations are **not perfectly independent with respect to impostor composition**.

For example, an impostor participant can appear in sequences associated with multiple enrolled users.

This does not invalidate the paired comparison because the principal contrast is within enrolled user:

$$
D_i = M_{i,m} - M_{i,\mathrm{instantaneous}}.
$$

But the Wilcoxon test's usual interpretation as a test over independent paired units should be described cautiously.

### Recommendation

We don't need to redesign the entire experiment.

Instead, the thesis should explicitly state that:

> participant-level paired analysis was used to avoid frame-level pseudoreplication, while recognising that the shared impostor-pool construction induces some dependence across enrolled-user observations.

That is a defensible limitation.

---

# 6. There is another dependence issue: sequence reuse

I also checked the benchmark construction.

The code prevents genuine/recovery overlap **within a sequence**, but the same underlying participant observations can potentially be selected again in another sequence because there is no global exclusion across sequences.

Therefore:

* sequence-level observations are not independent;
* six sequences per user should not be treated as six independent experimental subjects.

Fortunately, the analysis does **not** do that.

It averages sequences within participant first.

So again:

**not a fatal problem.**

It should simply be documented as part of the benchmark design.

---

# 7. The statistical testing is broadly appropriate

The analysis performs paired Wilcoxon signed-rank comparisons against instantaneous baseline and Holm correction across the eight mechanism comparisons for each metric.

That is coherent with the experimental design.

One thing I would be careful about in the thesis is the word **“significant.”**

For example, the analysis reports statistically detectable differences for many stability metrics.

Those results should be interpreted as:

> evidence of a systematic paired difference under this experimental protocol,

rather than:

> proof that one mechanism is superior.

This matters because your RQ is explicitly about a **security–stability–responsiveness trade-off**, not about identifying a universal winner.

---

# 8. The actual results support a trade-off story

This is where the experiment becomes academically interesting.

The results do **not** show a simple ordering.

For example:

* instantaneous has the lowest persistence-induced FRR cost but much greater state instability;
* moving average and EWMA substantially reduce transitions but increase FRR;
* majority voting reduces transitions while retaining comparatively lower FRR than several stronger persistence mechanisms;
* debounce produces stronger stabilization but a much larger genuine lockout;
* hysteresis substantially reduces transitions but has very high FRR and long recovery;
* trust has very low flip frequency but substantial lockout and recovery delay;
* SPRT has relatively moderate stability effects but cannot attain the target FAR interval for most users.

That is exactly the kind of result that fits the refined research question.

The important contribution is therefore **not**:

> “Mechanism X is the best.”

It is closer to:

> “Temporal decision-layer design materially changes the security–stability–responsiveness profile even when the upstream authentication score stream is held fixed.”

That is a much stronger and more defensible research proposition.

---

# 9. I found an important terminology issue with the ECDF

The audit describes the calibration ECDF transformation as **“strictly monotone.”**

Technically, an empirical CDF is monotone **non-decreasing**, not necessarily strictly increasing, because tied scores can map to the same empirical-CDF value.

This does **not** invalidate the experiment.

It only means the thesis should say:

> “a monotone ECDF transformation fitted on calibration scores”

rather than:

> “a strictly monotone transformation.”

This is a small correction, but worth making in a Master's dissertation.

---

# 10. One particularly important issue: SPRT is structurally different

The repository correctly acknowledges that SPRT is structurally different.

But I think the thesis needs to go further.

The nine mechanisms are not nine variations of one mathematical procedure.

They include:

* temporal smoothing;
* voting;
* persistence;
* dual thresholds;
* hysteresis;
* trust accumulation;
* sequential hypothesis testing.

SPRT is especially different because its state is driven by a cumulative likelihood-ratio statistic.

Therefore the comparison is best described as:

> **a comparative study of alternative temporal decision-layer mechanisms**

rather than:

> **a comparison of equivalent filters.**

That terminology will protect the thesis from an examiner asking why fundamentally different decision rules are being treated as if they were interchangeable.

---

# 11. One concern about SPRT deserves explicit treatment

The SPRT parameters include Gaussian score distributions estimated from calibration data:

$$
\mu_g,\sigma_g,\mu_i,\sigma_i.
$$

That is legitimate under the current design because the estimates come from calibration data.

However, it makes SPRT more dependent on the **distributional assumptions of the score stream** than the simpler mechanisms.

So if SPRT performs differently, we cannot simply attribute that difference to “SPRT being better/worse.”

The result reflects:

1. the sequential decision rule;
2. the Gaussian modelling assumption;
3. the calibration sample;
4. the available \(A,B\) grid;
5. the score distribution produced by the particular gradient-boosting model.

This belongs in the limitations.

---

# 12. I would make one methodological modification before freezing Stage 2

Not another full experiment.

I recommend **one additional analysis**, not a new research design:

### Matched-feasibility sensitivity analysis

Create a secondary analysis containing only the enrolled users for whom **all nine mechanisms** have a feasible FAR operating point.

Why?

Because the main analysis currently compares mechanisms despite 32 mechanism/user combinations being unable to attain the target interval.

The main analysis should remain the full 31-user analysis.

Then add:

> **complete-feasibility sensitivity analysis**

where the comparison is restricted to users with feasible operating points for every mechanism.

This answers an important examiner question:

> “Are your conclusions about mechanism differences driven by the mechanisms that could not actually be matched to the target FAR?”

We don't need to guess the answer. We can test it.

### Importantly

We should **not** choose the subset based on final-test performance.

Eligibility must be determined solely from the calibration feasibility field already stored in `operating_points.csv`.

That keeps the analysis clean.

---

# 13. I would also add one robustness analysis for the operating point

The target of 5% ± 1 percentage point is reasonable, but the conclusions could potentially depend on that particular choice.

A lightweight sensitivity analysis could examine something like:

* target FAR = 0.03
* target FAR = 0.05
* target FAR = 0.07

with the same calibration-only procedure.

This does **not** need to replace the primary experiment.

It would answer RQ3 much more convincingly:

> How sensitive are the observed trade-offs to decision-layer parameter settings?

Again, this should use calibration only for parameter selection and held-out test data for evaluation.

---

# 14. My recommended final Stage 2 structure

I would now freeze the conceptual structure as:

### Primary experiment

**31 participants**

**F3_NO_LOC_NO_DEVSTATE**

**nine mechanisms**

**target FAR = 0.05 ± 0.01**

**unseen final impostors**

**controlled 60–60–60 transitions**

**participant-level paired analysis**

### Secondary analyses

1. **complete-feasibility subset**
2. **F1_ALL feature sensitivity**
3. **operating-point sensitivity**
4. potentially fragmented-participant robustness analysis later, if computationally practical

That gives us a very defensible hierarchy between:

* primary evidence;
* sensitivity evidence;
* exploratory evidence.

---

# 15. What I would ask Claude to do now

I **would not rerun the entire experiment yet**.

I would give Claude a narrower task:

> preserve the corrected primary results and add the two methodological sensitivity analyses, without altering the primary protocol.

Specifically:

1. complete-feasibility subset analysis;
2. operating-point sensitivity analysis;
3. correct “strictly monotone ECDF” wording;
4. update the protocol audit to acknowledge shared impostor-pool and cross-sequence dependence;
5. do **not** alter the primary results;
6. do **not** select anything using final-test performance;
7. do **not** perform thesis writing.

Once those are committed, **then I would consider Stage 2 experimentally frozen**.

At that point we can move to the much more interesting task: **turning the results into the CSCD601/CSCD613 research argument and designing the final thesis/paper around the evidence rather than around an assumed conclusion.**
