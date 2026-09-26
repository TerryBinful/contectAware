Stage 2 is substantially improved and methodologically credible, but I would not freeze it as thesis evidence quite yet.

I do **not** think you need another research pivot. The current refined research question, architecture, and primary mechanism-comparison experiment are coherent. The remaining work is mainly about demonstrating that the conclusions are not artifacts of calibration feasibility or a single operating point.

### What I would do before freezing Stage 2

#### 1. Complete-feasibility sensitivity analysis

The current calibration results show that the target FAR interval of **0.04–0.06** is not attainable for every user–mechanism combination:

- Instantaneous: 1/31 infeasible
- Moving average: 0/31 infeasible
- EWMA: 0/31 infeasible
- Majority vote: 0/31 infeasible
- Debounce: 0/31 infeasible
- Margin/dual-threshold: 8/31 infeasible
- Hysteresis: 0/31 infeasible
- Trust model: 0/31 infeasible
- SPRT: 23/31 infeasible
- Overall: 32/279 combinations infeasible

That does **not** invalidate the experiment, because the infeasible cases are retained and explicitly reported. However, it means the phrase “all mechanisms were compared at FAR = 5%” would be too strong.

The primary analysis should remain unchanged. Add a **secondary analysis restricted to enrolled users for whom all nine mechanisms have feasible calibration operating points**.

Important constraints:

- Determine eligibility **only from calibration feasibility fields**.
- Never use final-test performance to decide who enters the sensitivity subset.
- Do not alter the primary 31-user analysis.
- Re-run the same participant-level comparisons on that subset.
- State whether the substantive pattern of security/stability/responsiveness trade-offs is materially changed.

This is a sensitivity analysis, not a replacement for the primary analysis.

#### 2. Operating-point sensitivity analysis

The primary operating point is a calibration-defined target FAR of **0.05 ± 0.01**.

Add a secondary analysis using predetermined target FAR values such as:

- 0.03, with feasibility interval 0.02–0.04
- 0.05, with feasibility interval 0.04–0.06
- 0.07, with feasibility interval 0.06–0.08

Use the same calibration-only selection procedure and the same tolerance rule at every target.

Do **not** choose these values after looking at final-test results.

The purpose is to address the robustness question in RQ3: whether the observed security–stability–responsiveness trade-offs depend materially on the selected operating point.

#### 3. Correct the ECDF terminology

One minor documentation issue should be corrected.

An empirical CDF is **monotone non-decreasing**; it is not necessarily strictly monotone because ties can occur.

Where the repository currently says “strictly monotone” in relation to ECDF score normalization, change this to wording such as:

> “monotone non-decreasing empirical CDF transformation”

This is a terminology correction, not an experimental redesign.

#### 4. Make the dependence limitation explicit

The final statistical analysis is appropriately based on participant-level paired comparisons, Wilcoxon signed-rank tests, Holm correction, and bootstrap confidence intervals.

However, the interpretation should explicitly acknowledge that:

- the final-test impostor pool is shared across enrolled users;
- therefore participant-level observations are not perfectly independent with respect to impostor composition;
- underlying participant observations may also be reused across multiple controlled sequences;
- the analysis does not treat sequences as independent subjects, but aggregates them at the enrolled-user level.

This should be documented as a limitation rather than treated as a reason to discard the experiment.

### What should remain frozen

Keep the current primary experiment design:

- regular-cadence primary cohort;
- 31 participants in the intended primary cohort;
- chronological genuine-user separation;
- separate fitting, calibration, and test impostor pools;
- unseen test impostors;
- training-only imputation and scaling;
- no SMOTE;
- per-user authentication models;
- common authentication-score stream;
- nine temporal decision-layer mechanisms;
- controlled identity-transition sequences constructed from real participant observations;
- frame-based timing;
- event-based security, stability, and responsiveness metrics;
- participant-level paired statistical analysis;
- calibration-defined operating points;
- primary feature set `F3_NO_LOC_NO_DEVSTATE`;
- `F1_ALL` as a sensitivity/ablation condition where supported.

Do not replace the primary experiment with either sensitivity analysis.

### Important wording for the thesis

Do not describe the benchmark sequences as naturally observed real-world identity switches. They are:

> “controlled identity-transition sequences constructed from real participant observations.”

Likewise, do not claim that all mechanisms were exactly matched at FAR = 0.05. The defensible formulation is:

> “Nine temporal decision-layer mechanisms were evaluated using a calibration-defined target FAR of 5% with a ±1 percentage-point feasibility interval. The target interval was attainable for most mechanism–participant combinations, but not for all, particularly for SPRT and margin-based mechanisms; infeasible cases were retained and explicitly reported.”

The current experiment therefore provides a credible basis for the study, but the two sensitivity analyses above should be completed before the Stage 2 evidence is frozen.

After those analyses and documentation corrections are committed, freeze Stage 2 and build the research argument from the actual evidence. Do not start thesis writing before that point.
