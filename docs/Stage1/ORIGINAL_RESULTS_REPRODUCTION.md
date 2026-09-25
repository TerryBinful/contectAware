# ORIGINAL RESULTS REPRODUCTION (Stage 1 — Phase 5 / step 6)

**Goal:** re-run the original experiment as faithfully as possible — same data, same code logic, same seeds, same library versions where known — without fixing anything.
**Code:** `experiment_Files/stage1_reproduction/reproduce_original.py`, `reproduce_cv.py`
**Environment:** Python 3.12.3, NumPy 2.0.2, pandas 2.2.2, scikit-learn 1.6.1, imbalanced-learn 0.13.0, SciPy 1.18.1; 1 vCPU, 4 GB RAM.
**Deviations from the notebook:** file paths; plotting removed; `del` of intermediates to fit memory; audit-only diagnostics appended after all reproduced values were computed. No parameter, threshold, seed, split or ordering was changed.

---

## 1. Result

> **The original experiment reproduces. Every reported Gradient Boosting and hysteresis number is recovered exactly. Logistic Regression differs in the third significant figure because its optimiser stops at the iteration limit.**

"Reproduces" means *the same code on the same data produces the same numbers*. It does **not** mean the numbers support the conclusions drawn from them — see `AUTHENTICATION_VALIDITY_AUDIT.md`.

## 2. Side-by-side

### 2.1 Dataset and preprocessing

| Quantity | Original notebook | Reproduced | Match |
|---|---|---|---|
| Files / first-file shape | 60 / (2287, 278) | 60 / (2287, 278) | ✓ |
| Total rows | 377,346 | 377,346 | ✓ |
| Total span hours | 13,505.2 | 13,505.2 | ✓ |
| Mean missing % | 16.5 | 16.51 | ✓ |
| Prefix-selected features | 103 | 103 | ✓ |
| Features >50% missing | min_speed, max_speed (72.30%) | same | ✓ |
| Retained features | 101 | 101 | ✓ |
| Target participant | 78A91A4E | 78A91A4E | ✓ |
| Class counts | 11,996 / 365,350 | 11,996 / 365,350 | ✓ |
| RF top-15 importances | location:min_altitude 0.1389, max_altitude 0.1219, proc_gyro:3d:std_z 0.0472, … | identical to 4 d.p. (all 15) | ✓ |
| Features at 95% | 52 | 52 | ✓ |
| Train / test rows | 301,876 / 75,470 | 301,876 / 75,470 | ✓ |
| SMOTE balanced counts | 292,279 : 292,279 | 292,279 : 292,279 | ✓ |

### 2.2 Classifiers (20% random test rows, τ = 0.5)

| Metric | LR original | LR reproduced | GB original | GB reproduced |
|---|---|---|---|---|
| Accuracy | 0.7454 | 0.7475 | 0.9926 | **0.9926** |
| Precision | 0.0998 | 0.1006 | 0.8524 | **0.8524** |
| Recall | 0.8741 | 0.8741 | 0.9291 | **0.9291** |
| F1 | 0.1792 | 0.1804 | 0.8891 | **0.8891** |
| FAR | 0.2588 | 0.2567 | 0.0053 | **0.0053** |
| FRR | 0.1259 | 0.1259 | 0.0709 | **0.0709** |
| ROC-AUC | 0.8875 | 0.8877 | 0.9976 | **0.9976** |
| "EER" = (FAR+FRR)/2 | 0.1924 | 0.1913 | 0.0381 | **0.0381** |
| Confusion (TN, FP, FN, TP) | not printed | 54,314 / 18,757 / 302 / 2,097 | not printed | 72,685 / 386 / 170 / 2,229 |
| Training time (s) | 152.60 | 46.7 | 741.87 | 519.4 |

LR deviation: `lbfgs` reaches `max_iter=1000` without converging (a warning the notebook suppressed). The stopping point depends on the SciPy build, which was not recorded. Magnitude ≤ 0.0021 on every metric; no conclusion depends on it. Timing differs by hardware and is not a reproducible quantity.

### 2.3 Hysteresis experiment (target participant, all 11,996 frames)

| Quantity | Original | Reproduced | Match |
|---|---|---|---|
| Frames − 1 | 11,995 | 11,995 | ✓ |
| Naive transitions | 597 | 597 | ✓ |
| Naive "ping-pong episodes" | 567 | 567 | ✓ |
| Hysteresis transitions | 49 | 49 | ✓ |
| Hysteresis "ping-pong episodes" | 0 | 0 | ✓ |
| Stability Index naive / hysteresis | 0.9502 / 0.9959 | 0.9502 / 0.9959 | ✓ |
| Span | 222.3 h | 222.3 h | ✓ |

### 2.4 Cross-validation (5-fold on SMOTE-balanced training set)

| Model | Original mean ± sd | Reproduced mean ± sd |
|---|---|---|
| LR | 0.8136 ± 0.0011 | 0.8137 ± 0.0006 |
| GB | 0.9951 ± 0.0001 (folds .99533 .99492 .99512 .99509 .99528) | **0.9951 ± 0.0001 (folds .99533 .99492 .99512 .99509 .99528) — exact** |

These CV scores are computed on data containing SMOTE synthetic points, so they are optimistic; they were not used in `Partial_fulfilment.docx`.

## 3. Numbers in `Partial_fulfilment.docx` that are **not** produced by the code

| Reported | Reproduction status |
|---|---|
| Table 5 post-hysteresis Accuracy / FAR / FRR = 99.26% / 0.53% / 7.09% | **Not produced by any code.** Copied from the τ = 0.5 test-set evaluation |
| "TTT = 3 seconds" | Not in code (code: 3 frames) |
| "Oscillation episodes (≥3 transitions/min)" | Not in code (code: overlapping 4-frame windows with ≥2 transitions) |
| Chronological 60/20/20 split, per-user imputation, >50%-missing window exclusion | Not in code |
| "Hysteresis compatible with multiple classifiers" | Not tested |
| "Across all test users" | One participant only |

## 4. Additional measurements (audit-only, not replacements)

Computed after reproduction on the same model and the same stream, to show what the original design did not report. They are **not** corrected results and must not be cited as the study's findings.

| Measurement | Value |
|---|---|
| True EER from ROC (GB / LR) | 2.64% / 19.27% |
| Share of the hysteresis stream that was training data | 80.0% (9,597 of 11,996 frames) |
| Naive transitions between two training rows / touching a test row | 342 / 255 |
| Frames in LOCKED state, whole stream — naive / hysteresis | 4.31% / 2.03% |
| Frames in LOCKED state, test rows only — naive / hysteresis | 7.09% / 2.29% |
| Hysteresis initial state; first unlock | LOCKED; frame 31 (≈31 min) |
| Test rows with a same-user training row ≤ 90 s away | 93.3% (target: 95.7%) |
| Test impostor participants also in training | 59 / 59 |
| Impostor test rows with imputed altitude — FAR | 43.8% of rows — 0.00% |
| Impostor test rows with real altitude — FAR | 56.2% of rows — 0.94% |
| Participants with ≥1 false accept (test) | 28 / 59; worst 3.73% |
| Genuine-stream probability: median; 5th pct; 1st pct | 0.996; 0.544; 0.160 |
| Median frame gap on target stream → real TTT | 60 s → 180 s |
| Held-out target rows only, time-ordered (non-contiguous) — naive / hysteresis transitions | 177 / 17 |

## 5. Reproducibility caveats

1. Only one run of the original exists; seed sensitivity (e.g., `random_state` ≠ 42) was not examined in Stage 1 and is NOT ESTABLISHED.
2. imbalanced-learn and SciPy versions of the original are unknown; the exact GB match suggests they did not matter for GB/SMOTE.
3. The Colab dataset path cannot be inspected; equivalence to the public archive rests on the fingerprints in §2.1, which are strong (identical importances to 4 d.p. would not survive any data difference).
