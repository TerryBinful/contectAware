# Review 1 — Key Findings (condensed)

These are the load-bearing findings from the first methodological review. Each must be resolved before any result from the February 2026 documents is reused.

## Arithmetic findings (from the reported numbers themselves)

**Finding A — Post-hysteresis classification metrics were almost certainly not measured.**
Table 5 reports Accuracy 99.26% → 99.26%, FAR 0.53% → 0.53%, FRR 7.09% → 7.09% (all Δ = 0.0%) while the output sequence lost 548 state transitions. Within a user's stream the ground-truth identity is constant, so every removed transition removes an error boundary; accuracy *must* change. The identical values indicate the classification metrics were computed once on the raw classifier output and copied into both columns. **Consequence:** "stability without accuracy cost" is unsupported. **Fix:** recompute all classification metrics on the post-mechanism state sequence.

**Finding B — The oscillation metric is arithmetically impossible as defined.**
"Oscillation episode = ≥3 transitions within 60 s"; 567 episodes reported from 597 total transitions. 567 episodes need ≥1,701 transitions. Only overlapping sliding windows could produce this, in which case episodes are not events and the count has no interpretable magnitude. **Fix:** define window semantics or, better, replace with ANGA-time.

**Finding C — The two stability metrics are algebraically dependent.**
(1 − 0.9502)/(1 − 0.9959) = 12.15; 597/49 = 12.18. Stability Index ≈ 1 − k·(transitions)/N with k ≈ 6.3. Reporting both is reporting one measurement twice. (Solving for N gives ≈72k frames ≈ 19% of 377,346 — consistent with the stated 20% test split, so the stability analysis was probably on held-out data.) **Fix:** drop SI or redefine it independently.

**Finding D — TTT as stated is inoperable at the data's cadence.**
TTT = 3 s (Partial fulfilment) / 2–5 s (PDF); frames are ≥20 s apart (likely ≈60 s — see cadence check). A sub-frame dwell is satisfied by every observation and does nothing. Either TTT was inert and the whole effect is the margin, or TTT was implemented in frames and mis-reported. **Fix:** report TTT in frames; run margin-only / dwell-only / both.

## Consistency and integrity flags

| # | Flag | Severity |
|---|---|---|
| C1 | PDF describes a human-participant within-subjects study; all other documents describe offline secondary analysis | **Critical** |
| C2 | PDF ethics claims (no audio/GPS, on-device processing, no upload) contradict ExtraSensory usage and Google Colab | **Critical** |
| C3 | 225 features − 2 dropped ≠ 101 | High |
| C4 | 103 / 101 / 52 / 53 feature counts in consecutive paragraphs | High |
| C5 | "≈5 transitions per user" ≠ 597/60 ≈ 10 | Medium |
| C6 | "Khan et al. (2020)" cited, absent from all reference lists; later silently deleted | **High — verify or remove** |
| C7 | Vaizman 2017 (Vol 16) vs 2018 (Vol 17, different DOI) for the same title/pages | Medium |
| C8 | Word count ~4,900 vs ~4,100 | Low |
| C9 | Core hysteresis-in-security quote sourced to `aimjournals.com` | High |
| C10 | "SVMs/RF cannot handle missingness" used to argue non-triviality, then RF and GB used after imputation | Medium |
| C11 | Find-replace corruption: "user behavioural", "exhibitss", "he proliferation", "statical" | Medium |
| C12 | `[Your Name]`, `[INDEX NUMBER]` placeholders | Low, fatal if submitted |
| C13 | Generative-AI tools listed in References rather than a declaration | Medium |

## Structural findings

- **Degenerate task:** identity never changes within an ExtraSensory user stream, so the optimal temporal policy is "never switch." Any smoothing is rewarded; the design cannot distinguish hysteresis from any other filter.
- **No mechanism baselines:** comparison is hysteresis vs. nothing.
- **Classification ≠ authentication:** no per-user models, no held-out impostors, no per-user EER, no detection latency, no attack protocol.
- **SMOTE and calibration:** post-SMOTE probabilities are calibrated to a 1:1 prior; hysteresis thresholds sit on an uncalibrated scale. Never discussed.
- **Parameter selection:** validation split defined, never used; margin never reported. Test-set influence cannot be excluded.
- **Mechanism identity:** margin + TTT = Schmitt trigger + debounce. The telecom framing is narrative, not formal content.

## What survived Review 1 at full strength

- The problem statement and motivation.
- The literature review and 16-row gap table in *Partial fulfilment*.
- The dataset justification and Big Data critique.
- The honest LR baseline result (74.54%).
- The internally consistent GB confusion matrix (FAR 0.53%, FRR 7.09%, 1:30.36 → precision 0.852, accuracy 99.25% — verified).
- The research instinct: aggregate accuracy is the wrong target; temporal decision behaviour matters.
