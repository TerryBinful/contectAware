# Dataset & cadence audit

Generated 2026-09-24T19:16:50 from `/home/claude/data/csv`.

## Observed facts

- 60 participant files, 225 feature columns, 51 label columns, 377,346 observations.
- Schema problems: none.
- Inter-observation gap: median 60 s, mean 128.9 s; 71.0% of gaps lie in 59-61 s; 5.5% exceed 90 s.
- Gap histogram: {'0-30s': 8434, '30-59s': 35437, '59-61s': 248936, '61-90s': 62902, '90-300s': 18706, '300-3600s': 2414, '3600-86400s': 429, '86400-1000000000000s': 28}.
- Observations per participant: min 1600, median 6312, max 11996.
- Feature inventory by family: {'phone_motion': 83, 'watch': 55, 'location': 17, 'audio': 28, 'device_state': 34, 'lf_ambient': 8}.

## Derived quantities

- The ~60-second cadence hypothesis **holds** (median gap equals 60 s), so 1 frame is treated as ~1 minute.
- Eligibility rule `frac(59-61s) >= 0.95 and frames >= 1500` yields **31 eligible** and 29 fragmented participants.
- Contiguous segments (gaps <= 90 s): 20654 in total; 37 participants have at least one segment of >= 180 frames.

## Assumptions

- A gap above 90 s breaks temporal continuity; blocks are never joined across such a gap.
- One frame is treated as one decision opportunity; frame-based temporal parameters are used throughout.

## Limitations

- Cadence is irregular for the fragmented participants, so frame-based durations are only approximate for them; they are excluded from the primary experiment.
- No sub-minute analysis is possible with this dataset.
- The 20-second figure in earlier project documents is the sensor recording window, not the sampling interval.
