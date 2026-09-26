# Metric definitions (Stage 2)

Code: `experiment_Files/Stage2/src/ca_stability/metrics.py` (unit-tested in `tests/test_metrics.py`).
1 frame ≈ 60 s (verified cadence). ANGA/ANIA-time are the project's time-normalised adaptation of
Bours & Mondal's (2015) action-count ANGA/ANIA.

**Conventions.** A *session* is a contiguous run (gap ≤ 120 s). `S[t]` ∈ {AUTH, LOCKED} is the
mechanism state after frame t. Every session starts from a virtual AUTH state before its first
frame, so a LOCKED first frame counts as a lock. A *transition* at t: `S[t] ≠ S[t−1]`.

## Genuine side (pure genuine test streams)
| Metric | Definition | Family |
|---|---|---|
| False lock | transition AUTH → LOCKED | stability / security |
| False locks per hour | Σ false locks / genuine hours (= 1 / ANGA-time); per user and pooled | stability (matching criterion) |
| FRR_time | locked genuine frames / genuine frames | security (usability cost) |
| FR frames | count of locked genuine frames | security |
| Transitions per hour | Σ transitions / genuine hours | stability |
| Ping-pong event | a state *episode* that starts with a transition at t and ends with the next transition at t′ with t′ − t ≤ W_pp (= 5 frames). Episodes are disjoint, so events do not overlap; unterminated episodes are not counted | stability |
| Ping-pong lock | ping-pong event whose state is LOCKED (a brief false lock undone within W_pp) | stability |
| Mean false-lock duration (lockout) | locked genuine frames / false locks | responsiveness (cost of a lock) |

## Transition side (spliced sequences; switch at column C, impostor block of L frames, return at C+L)
| Metric | Definition | Family |
|---|---|---|
| FAR_frame (access fraction) | impostor-block frames in AUTH / L | security |
| FA frames | count of impostor frames in AUTH | security |
| Locked at switch | `S[C−1]` = LOCKED | context |
| First-lock delay | min{t − C : C ≤ t < C+L, S[t] = LOCKED}; censored at L | responsiveness |
| Sustained detection delay (ANIA, frames) | first t ∈ [C, C+L) with S LOCKED on [t, min(t + n_sustain, C+L)), n_sustain = 3; value t − C | responsiveness (primary outcome) |
| Miss | no sustained detection within the block; delay censored at L | security |
| Recovery latency | min{t − (C+L) : t ≥ C+L, S[t] = AUTH}; censored at the suffix length | responsiveness |
| Locked at return | `S[C+L−1]` = LOCKED | context |

## Aggregation and inference
Per genuine user: sums over streams (genuine side); median / mean over that user's sequences
(transition side). Across users: median with user-level bootstrap 95% CI; pooled counts reported
alongside. Frames and sequences are never treated as independent observations in tests.
