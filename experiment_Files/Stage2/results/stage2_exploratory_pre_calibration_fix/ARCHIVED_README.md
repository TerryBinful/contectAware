# ARCHIVED — exploratory Stage 2 mechanism comparison (pre-correction)

These outputs come from the FIRST mechanism-comparison run (31 users, 179 sequences) and are
**exploratory evidence only. They are not the final Stage 2 results.**

Two defects were identified by methodological review after this run:

1. **Operating-point matching was one-sided.** Candidates were feasible if calibration FAR
   <= target + tolerance, which admitted FAR ≈ 0 (not matched to the 0.05 ± 0.01 operating point).
2. **Detection latency was unbounded.** A stable rejection occurring during the genuine RECOVERY
   block could be counted as successful impostor detection.

Both are corrected in `results/mechanism_comparison/`. Do not mix these numbers with the corrected
results, and do not cite them as final.
