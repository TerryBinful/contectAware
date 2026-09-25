# Mechanism Reference — Decision-Layer Stabilisation Policies

All mechanisms consume the same per-frame calibrated probability stream `p[t] = P(genuine | frame t)` and emit `state[t] ∈ {AUTH, LOCKED}`. Nothing else differs between arms. `Δt` = frame period in seconds; all time-based parameters are **specified in frames** and reported in both frames and minutes.

Initial state for every mechanism: `AUTH` (session begins authenticated).

---

## 0. Instantaneous threshold (null)
```
state[t] = AUTH if p[t] >= θ else LOCKED
```
Params: θ. Grid: {0.3, 0.4, 0.5, 0.6, 0.7}.

## 1. Moving average
```
q[t] = mean(p[t-k+1 .. t]);  state[t] = AUTH if q[t] >= θ else LOCKED
```
Params: k, θ. Grid: k ∈ {2, 3, 5, 10, 20}; θ as above.

## 2. Exponentially weighted moving average
```
q[t] = α·p[t] + (1-α)·q[t-1];  state[t] = AUTH if q[t] >= θ else LOCKED
```
Params: α, θ. Grid: α ∈ {0.05, 0.1, 0.2, 0.3, 0.5, 0.7}.

## 3. Majority vote
```
state[t] = AUTH if #{p[t-k+1..t] >= θ} > k/2 else LOCKED
```
Params: k (odd), θ. Grid: k ∈ {3, 5, 7, 11}.

## 4. Dwell-only (debounce / TTT)
```
raw[t] = AUTH if p[t] >= θ else LOCKED
if raw[t] != state[t-1]: counter += 1 else counter = 0
if counter >= T: state[t] = raw[t]; counter = 0 else state[t] = state[t-1]
```
Params: T (frames), θ. Grid: T ∈ {1, 2, 3, 5, 8}. **This is the TTT component alone.**

## 5. Margin-only (dual threshold / Schmitt trigger)
```
if state[t-1] == AUTH:   state[t] = LOCKED if p[t] <  θ_lock   else AUTH
else:                    state[t] = AUTH   if p[t] >= θ_unlock else LOCKED
with θ_unlock = θ + m/2, θ_lock = θ - m/2
```
Params: θ, m. Grid: m ∈ {0.05, 0.1, 0.2, 0.3}. **This is the margin component alone.**
Optional asymmetric variant: (θ_lock, θ_unlock) independently — report if used.

## 6. Hysteresis (margin + dwell) — the handover-derived candidate
```
if state[t-1] == AUTH:  cond = p[t] <  θ_lock
else:                   cond = p[t] >= θ_unlock
if cond: counter += 1 else counter = 0
if counter >= T: flip state; counter = 0 else hold
```
Params: θ, m, T. Grid: product of §5 and §4 grids. Optionally separate T_lock and T_unlock (asymmetric dwell) — if used, pre-register it.

## 7. Trust model (Bours/Mondal/Kiyani-style additive confidence)
```
trust[0] = 1.0
trust[t] = clip(trust[t-1] + r·(p[t] - θ), 0, 1)     # reward if above θ, penalise if below
state[t] = LOCKED if trust[t] < τ_final else AUTH
(optional alert tier: if trust[t] < τ_alert: increase penalty rate)
```
Params: r (rate), τ_final, θ. Grid: r ∈ {0.05, 0.1, 0.2, 0.5}; τ_final ∈ {0.2, 0.3, 0.5}. Cite Bours et al. 2015; Mondal et al. 2017; Kiyani et al. 2020 for the two-threshold variant.

## 8. Sequential Probability Ratio Test
```
LLR[t] = LLR[t-1] + log( f1(p[t]) / f0(p[t]) )     # f1: genuine score density, f0: impostor score density, both fitted on VALIDATION
if LLR[t] >= A: state = AUTH,   LLR = 0
if LLR[t] <= B: state = LOCKED, LLR = 0
else: hold
A = log((1-β)/α),  B = log(β/(1-α))
```
Params: α, β (target error rates). Grid: α, β ∈ {0.01, 0.05, 0.1}. Score densities may be estimated by histogram/KDE of validation p values per class. Cite Allano et al. 2010 (biometric SPRT fusion) and Wald.

## 9. (Optional) Two-state HMM
Emission: p[t] binned; transition matrix and emissions fitted on validation; Viterbi or forward filtering gives state. Include only if 7 and 8 leave a gap.

---

## Matched-operating-point procedure

For each mechanism:
1. Run the full grid on **validation** sequences.
2. Compute ANGA-time (genuine segments) for every grid cell.
3. Select the cell(s) whose ANGA-time is closest to the pre-registered target; among ties choose the lowest median ANIA-time on validation.
4. Freeze that cell. Report ANIA-time, miss rate, recovery time, ping-pong rate on **test** sequences.
5. Also plot the entire grid as a curve (ANGA-time vs. median ANIA-time) so readers can see the frontier, not just the matched point.

## Component ablation for hysteresis
Report, at the matched point: hysteresis (6) vs. margin-only (5) vs. dwell-only (4). H3 is supported only if (6) beats both (4) and (5).

## Metric definitions (mirror of pre-registration §5)
- ANGA-time = genuine minutes / false locks.
- ANIA-time = minutes from switch to first n-frame sustained LOCKED.
- Miss rate = impostor blocks never locked before return.
- Recovery time = minutes from return to first AUTH.
- Ping-pong rate = sign-alternating transitions within W_pp frames, per genuine hour.
