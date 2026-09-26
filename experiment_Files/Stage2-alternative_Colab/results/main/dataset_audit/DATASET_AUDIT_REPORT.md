# Dataset audit report (auto-generated — do not edit by hand)

## Observed facts (computed from the participant files in this run)
- Participants: 60; frames: 377,346; feature columns: 225; label columns: 51.
- Pooled median inter-frame gap: 60.0 s (IQR 60.0-60.0 s; mean 128.9 s).
- Share of gaps within 59-61 s: 0.710.
- Participants with >= 80% of gaps in 59-61 s (regular): 34; others (fragmented): 26.
- Lowest regular-participant share: 0.900; highest fragmented-participant share: 0.5660764690787785.
- Participants whose phone reports no gyroscope at all: 61359772, CCAF77F0, F50235E0.
- Mean (over participants) cell-level missingness over all features: 0.165.

## Derived quantities
- Frame period used for all conversions: 60 s (1 frame = 1 decision ~ 1 minute).
- A contiguous run breaks where a gap exceeds 120 s (= 2.0 x frame period).
- Eligible genuine participants for the 'regular' cohort: 33; excluded: 27 (reasons in eligibility.csv).

## Feature groups

| category | n_features | pooled_missing_mean | in_stage1_selected | in_primary |
|---|---|---|---|---|
| audio_ambient | 28 | 0.02501 | 0 | 0 |
| device_state | 26 | 0 | 5 | 0 |
| environment_device | 8 | 0.5779 | 0 | 0 |
| location | 17 | 0.2688 | 13 | 0 |
| magnetometer | 31 | 0.08317 | 0 | 0 |
| phone_motion | 52 | 0.02376 | 34 | 52 |
| time_of_day | 8 | 0 | 0 | 0 |
| watch_heading | 9 | 0.6093 | 0 | 0 |
| watch_motion | 46 | 0.3513 | 0 | 0 |

## Assumptions
- One ExtraSensory example (a 20-s recording, nominally once per minute) is one decision frame.
- Frames inside a run are treated as consecutive decisions; temporal parameters are in frames.
- Gaps above the run-break threshold end a session; every mechanism restarts in AUTH at a new run.

## Limitations
- Decision cadence is ~1/min; nothing here supports claims about sub-minute responsiveness.
- Fragmented-cadence participants have frames that are not 60 s apart; they are excluded from the primary cohort.
- Labels are self-reported and sparse; they are used only to align context-matched impostor blocks, never as features.
