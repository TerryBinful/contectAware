# Decision mechanisms (Stage 2)

All mechanisms consume the same calibrated score stream `p[t]` = P(genuine | frame t) and expose
`reset()`, `update(score, timestamp)`, `state()`, `diagnostics()` (reference classes:
`src/ca_stability/mechanisms/reference.py`; vectorised twins in `batch.py`, bit-identical by test).
All temporal parameters are in frames. Every session starts AUTH; state resets at session start.

| # | Mechanism | Rule | Swept | Fixed grid |
|---|---|---|---|---|
| 1 | Threshold (baseline) | AUTH ⇔ p ≥ θ | θ | — |
| 2 | Moving average | q = mean of last min(k, t+1) scores; AUTH ⇔ q ≥ θ | θ | k ∈ {2,3,5,10,20} |
| 3 | EWMA | q₀ = p₀; q = αp + (1−α)q; AUTH ⇔ q ≥ θ | θ | α ∈ {.05,.1,.2,.3,.5,.7} |
| 4 | Majority vote | votes v = [p ≥ θ] over last min(k, t+1) frames; AUTH if more AUTH votes, LOCKED if more LOCKED, tie keeps state | θ | k ∈ {3,5,7,11} |
| 5 | Debounce (dwell only) | switch to the raw decision [p ≥ θ] only after it has disagreed with the state for T consecutive frames | θ | T ∈ {2,3,5,8} |
| 6 | Margin (dual threshold only) | from AUTH lock if p < θ − m/2; from LOCKED unlock if p ≥ θ + m/2 | θ | m ∈ {.05,.1,.2,.3} |
| 7 | Hysteresis (margin + dwell; handover-style) | margin conditions must hold for T consecutive frames (Time-to-Trigger) | θ | m × T, T ∈ {2,3,5,8} |
| 8 | Trust | trust₀ = 1; trust ← clip(trust + r(p − θ), 0, 1); AUTH ⇔ trust ≥ τ | θ | r ∈ {.05,.1,.2,.5}, τ ∈ {.2,.3,.5} |
| 9 | SPRT (Wald, with restart) | Λ ← Λ + log f₁(p)/f₀(p); AUTH if Λ ≥ log((1−β)/α), LOCKED if Λ ≤ log(β/(1−α)); Λ ← 0 after a decision | β (log-grid, 60) | α ∈ {.001,.01,.05,.1,.2} |
| S | HMM filter (supplementary) | 2-state forward filter, switch prob. ρ, prior π₀ = 0.999; AUTH ⇔ posterior ≥ θ | θ | ρ ∈ {1e-4,1e-3,1e-2,.05,.1} |

f₁, f₀: Laplace-smoothed 20-bin histograms of validation genuine and validation (calibration-role)
impostor scores (`results/<label>/benchmark/densities.json`). Test data are never used to fit them.
Mechanism 7 with T = 1 equals mechanism 6, so T = 1 is excluded from the hysteresis grid (H3 needs
non-nested arms). Mechanisms 6–8 can be absorbing (never unlock) at extreme θ; such cells are
inadmissible at the operating point (amendment A1).
