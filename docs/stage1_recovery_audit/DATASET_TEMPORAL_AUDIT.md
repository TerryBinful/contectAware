# DATASET & TEMPORAL AUDIT (Stage 1 — Phase 4)

**Data:** official ExtraSensory primary feature files (60 × `*.features_labels.csv.gz`), verified to be the same data used in the original notebook (`REPOSITORY_INVENTORY.md` §3).
**Code:** `experiment_Files/stage1_reproduction/dataset_temporal_audit.py`
**Outputs:** `results/dataset_temporal_summary.json`, `results/dataset_per_user_temporal.csv` (one row per participant)
Descriptive only; nothing was filtered or modified.

---

## 1. Headline

> **One ExtraSensory example is a 20-second sensor recording taken roughly once per minute. The median gap between consecutive examples is 60 s — not 20 s. Every statement in the reports that the "sampling interval" or "temporal resolution" is 20 s is wrong, and every time conversion built on it is wrong by a factor of ~3.**

This is now established from the primary data, not only from external documentation. It is also stated inside the repository's own copy of the Vaizman tutorial (`fusion.ipynb`: *"Every example has its timestamp, indicating the minute when the example was recorded"*).

## 2. Structure

| Item | Value |
|---|---|
| Participants | 60 |
| Rows (examples) | 377,346 (min 1,600; median 6,312; max 11,996 per user) |
| Columns | 278 = `timestamp` + 225 features + 51 `label:` + `label_source` |
| Rows sorted by timestamp within file | 60/60 |
| Duplicate timestamps | 0 |
| Sum of per-user spans (first→last example) | 13,505.2 h |
| Recorded time if 1 example = 1 min | 6,289 h |
| Rows with ≥1 positive context label | 86.6% (pooled) |

The reports' "over 300,000 minutes (approximately 5,000 hours)" is inconsistent with both numbers above (377,346 examples ≈ 6,289 h of minute-examples; span 13,505 h). The notebook's "13,505 hours" is **calendar span**, not recorded time.

## 3. Inter-example interval (all 377,286 within-user gaps)

| Gap (s) | Count | Share |
|---|---|---|
| 1–30 | 8,434 | 2.2% |
| 30–59 | 35,437 | 9.4% |
| 59–60 | 10,182 | 2.7% |
| **60–61** | **238,754** | **63.3%** |
| 61–90 | 62,902 | 16.7% |
| 90–300 | 18,706 | 5.0% |
| 300–3,600 | 2,414 | 0.6% |
| 1 h–1 day | 429 | 0.1% |
| > 1 day | 28 | <0.1% |

Median 60 s; 71.0% of gaps within 59–61 s; minimum 1 s. The "1–59 s" tail (11.6%) means that for some participants two consecutive rows can be seconds apart, i.e. "one frame" does not denote a fixed amount of time.

## 4. Two cadence regimes

Defining a *run* as a maximal sequence with every gap ≤ 90 s:

| | Regular participants | Fragmented participants |
|---|---|---|
| Typical profile | ≥95% of gaps in 59–61 s, a handful of long runs (hundreds–thousands of frames) | 25–37% of gaps < 59 s, 10–15% > 90 s, hundreds–1,900 runs, median run 3–7 frames |
| Count | ~30 | ~30 (30 participants have median run length < 10 frames) |
| Example | `78A91A4E` (target): 99.2% of gaps 59–61 s, 10 runs, median run 1,244 frames | `59EEFAE0`: 16.5% of gaps 59–61 s, 1,171 runs, median run 4 |

One participant (`1155FF54`) has a median gap of 300 s. 37 participants have at least one run ≥ 180 frames (~3 h).

**Implication:** a counter such as TTT = *k frames* means ≈ *k* minutes for regular participants and an undefined, variable duration for fragmented ones. Any temporal-decision experiment must state whether TTT is defined in frames or seconds and how gaps are handled (reset state? carry state?). The original code did neither — it treats the sorted row sequence as uniformly spaced.

## 5. The target participant used in the original hysteresis experiment

| Property | `78A91A4E` | Dataset context |
|---|---|---|
| Rows | 11,996 | Largest of all 60 (selected *because* it is largest) |
| Span | 222.3 h (9.3 days) | median 167.9 h |
| Gaps 59–61 s | 99.2% | dataset median participant 95.9%; lower quartile 33.2% |
| Gaps > 90 s | 0.08% (9 gaps) | mean 6.6% |
| Runs | 10 | median 37.5 |
| Watch accelerometer entirely missing | 24.8% of rows | pooled 35.1% |
| Altitude missing | **0.0%** | pooled 42.5% |

The original temporal experiment was run on the **most regular, longest, most complete** stream in the dataset — a best case for stability, and not representative of half of the participants.

Time conversions for this stream: TTT = 3 frames ≈ **180 s** (not 60 s as printed, not 3 s as written in the paper); the 4-frame "ping-pong window" ≈ **4 min**.

## 6. Missingness by sensor group (share of rows where the entire group is missing, mean over participants)

| Group | Rows fully missing | Used by original model? |
|---|---|---|
| raw_acc (phone accelerometer) | 0.1% | Yes |
| proc_gyro | 5.2% | Yes |
| raw_magnet | 9.1% | **No** |
| watch_acceleration | 37.0% | **No** |
| watch_heading | 62.2% | **No** |
| location | 12.4% | Yes |
| audio | 2.6% | **No** |
| discrete | 0.0% | Yes |
| lf_measurements | 0.1% | **No** |

Six participants have watch acceleration missing in >95% of rows. Missingness is participant- and device-specific, which is exactly why it can act as an identity shortcut (see `AUTHENTICATION_VALIDITY_AUDIT.md` §3.2). Individual location features reach 42.5% (altitude) and 72.3% (speed) missingness.

## 7. Labels

`label:` columns are present for 51 contexts; 86.6% of rows carry at least one positive label, but coverage per participant ranges 30.7%–99.9%. Labels were **not** used by the original pipeline (neither as features nor for evaluation).

## 8. Consequences for the reported claims

| Claim in reports | Status |
|---|---|
| "20-second sampling interval", "sub-minute temporal granularity" | **Refuted** by the data |
| "TTT = 3 seconds" | **Refuted**; implemented TTT ≈ 180 s on the target stream |
| "TTT 3 frames (60 s)" (notebook print) | **Refuted**; ≈180 s |
| "Ping-pong within a 1-minute window" | **Refuted**; window ≈ 4 min |
| "~5,000 hours of data" | **Not supported** (6,289 h recorded; 13,505 h span) |
| "Continuous" streams | **Partly**: continuous at minute level for ~half the participants; fragmented for the rest |
| "16.5% missing data rate" | **Confirmed** (mean over participants of cell-level NaN over 225 features) |
| "15.3% of records lacking watch accelerometer" | **Not supported** (35.1% pooled; 37.0% mean over participants) |
| "Inference latency < 1 s required" | Irrelevant at this cadence; decisions arrive once per minute |

## 9. What the dataset *can* and *cannot* support temporally

- **Can:** minute-level decision sequences for ~30 participants with long regular runs; splicing of blocks between participants at run boundaries; experiments where persistence is expressed in minutes.
- **Cannot:** any claim about sub-minute responsiveness, second-level TTT, or intra-minute oscillation. Such claims would need different data.
- **Needs a decision before the next stage:** how to treat gaps (> 90 s) inside a decision stream, and whether fragmented participants are included.
