### Table 1. Primary confirmatory test (target FAR 0.05; participant-level; Holm within family)

| Quantity | cell_H vs cell_D | cell_H vs cell_M |
|---|---|---|
| Participants paired | 30 | 24 |
| Excluded: no feasible H / comparator cell | 1 / 0 | 1 / 6 |
| Excess transitions per sequence, H vs comparator | 0.203 vs 0.332 | 0.237 vs 0.436 |
| Paired difference, mean (median) | -0.129 (0.000) | -0.199 (0.000) |
| Wilcoxon W; p; Holm p | 199.0; 0.475; 0.688 | 117.5; 0.344; 0.688 |
| C1 fewer excess transitions | **not met** | **not met** |
| FRR difference [95% CI] | +0.074 [0.032, 0.119] | +0.030 [-0.008, 0.069] |
| C2 FRR non-inferior (upper bound < +0.02) | **not met** | **not met** |
| Detection-failure difference [95% CI] | +0.000 [0.000, 0.000] | -0.007 [-0.021, 0.000] |
| C3 detection failure non-inferior | met | met |

Source: `primary/primary_tests.csv`. Criterion requires C1–C3 against both comparators.

Sensitivity, target FAR 0.03: cell_H vs cell_D: n=30, excess diff -0.251, Holm p 0.075, FRR diff +0.067 [0.030, 0.108], C1/C2/C3 = N/N/Y; cell_H vs cell_M: n=18, excess diff -0.278, Holm p 0.179, FRR diff +0.031 [0.002, 0.061], C1/C2/C3 = N/N/Y (`secondary/factorial_far_0.03/primary_tests.csv`).

Sensitivity, target FAR 0.07: cell_H vs cell_D: n=31, excess diff -0.351, Holm p 0.008, FRR diff +0.029 [0.008, 0.056], C1/C2/C3 = Y/N/Y; cell_H vs cell_M: n=23, excess diff -0.688, Holm p 0.008, FRR diff +0.026 [-0.004, 0.060], C1/C2/C3 = Y/N/Y (`secondary/factorial_far_0.07/primary_tests.csv`).

### Table 2. Calibration-selected cells per participant (target FAR 0.05)

- **cell_H**: m0.05_k2 (12), m0.05_k3 (8), m0.05_k5 (6), m0.1_k2 (3), m0.1_k3 (1), infeasible (1)
- **cell_D**: m0_k2 (26), m0_k3 (3), m0_k5 (1), m0_k10 (1)
- **cell_M**: m0.05_k1 (15), infeasible (6), m0.2_k1 (5), m0.1_k1 (5)

Source: `primary/cell_selection.csv`. Cell label `m<margin>_k<dwell>`.

### Table 3. Factorial response surface at target FAR 0.05 (θ-only tuning; cells are not paired — feasible participant sets differ)

| m | k | Class | n feasible | Excess / seq | FRR | Test FAR | Recovery failure | Recovery latency (censored, frames) |
|---|---|---|---|---|---|---|---|---|
| 0 | 1 | instantaneous | 30 | 2.012 | 0.042 | 0.043 | 0.042 | 2.7 |
| 0 | 2 | dwell_only | 29 | 0.466 | 0.052 | 0.049 | 0.044 | 3.7 |
| 0 | 3 | dwell_only | 22 | 0.194 | 0.059 | 0.062 | 0.035 | 4.4 |
| 0 | 5 | dwell_only | 31 | 0.676 | 0.238 | 0.063 | 0.147 | 15.4 |
| 0 | 10 | dwell_only | 19 | 0.135 | 0.505 | 0.078 | 0.475 | 38.4 |
| 0.05 | 1 | margin_only | 20 | 0.913 | 0.061 | 0.035 | 0.063 | 4.1 |
| 0.05 | 2 | hysteresis | 14 | 0.288 | 0.079 | 0.053 | 0.055 | 4.8 |
| 0.05 | 3 | hysteresis | 20 | 0.187 | 0.140 | 0.063 | 0.155 | 14.7 |
| 0.05 | 5 | hysteresis | 27 | 0.260 | 0.339 | 0.062 | 0.424 | 31.5 |
| 0.05 | 10 | hysteresis | 9 | 0.000 | 0.588 | 0.087 | 0.870 | 54.1 |
| 0.1 | 1 | margin_only | 22 | 0.521 | 0.068 | 0.033 | 0.073 | 5.4 |
| 0.1 | 2 | hysteresis | 11 | 0.206 | 0.121 | 0.068 | 0.106 | 11.0 |
| 0.1 | 3 | hysteresis | 17 | 0.059 | 0.210 | 0.062 | 0.320 | 23.6 |
| 0.1 | 5 | hysteresis | 18 | 0.081 | 0.487 | 0.059 | 0.720 | 47.3 |
| 0.2 | 1 | margin_only | 13 | 0.149 | 0.132 | 0.054 | 0.167 | 12.3 |
| 0.2 | 2 | hysteresis | 8 | 0.000 | 0.356 | 0.073 | 0.604 | 39.8 |
| 0.2 | 3 | hysteresis | 6 | 0.000 | 0.374 | 0.100 | 0.650 | 43.0 |

Source: `factorial/response_surface.csv`.

### Table 4. Tuned stabiliser families at target FAR 0.05 (participant-level means [95% bootstrap CI])

| Mechanism | n | Excess / seq | FRR | Test FAR | Recovery failure | Detection failure | Recovery latency (censored) | Detection latency (censored) |
|---|---|---|---|---|---|---|---|---|
| Instantaneous | 30 | 2.01 [0.97, 3.31] | 0.042 [0.013, 0.079] | 0.043 | 0.042 | 0.018 | 2.7 | 1.4 |
| Moving average | 31 | 0.53 [0.26, 0.87] | 0.060 [0.032, 0.095] | 0.047 | 0.041 | 0.012 | 5.3 | 1.8 |
| EWMA | 31 | 0.52 [0.23, 0.91] | 0.067 [0.038, 0.102] | 0.045 | 0.041 | 0.024 | 6.1 | 2.1 |
| Majority vote | 31 | 0.43 [0.21, 0.68] | 0.048 [0.021, 0.084] | 0.052 | 0.041 | 0.012 | 3.8 | 2.4 |
| Debounce (dwell) | 31 | 0.32 [0.12, 0.56] | 0.049 [0.021, 0.085] | 0.056 | 0.041 | 0.012 | 3.9 | 2.5 |
| Margin (dual threshold) | 26 | 0.40 [0.14, 0.74] | 0.083 [0.034, 0.141] | 0.038 | 0.103 | 0.021 | 7.5 | 1.7 |
| Margin + dwell | 30 | 0.20 [0.10, 0.31] | 0.124 [0.073, 0.178] | 0.059 | 0.145 | 0.012 | 12.0 | 3.1 |
| Trust model (dual τ) | 31 | 0.04 [0.00, 0.09] | 0.172 [0.130, 0.217] | 0.059 | 0.138 | 0.018 | 19.1 | 3.2 |
| Trust model (single τ) | 31 | 0.17 [0.08, 0.29] | 0.080 [0.053, 0.114] | 0.049 | 0.041 | 0.017 | 7.8 | 2.5 |
| SPRT | 31 | 0.32 [0.15, 0.55] | 0.036 [0.012, 0.071] | 0.047 | 0.035 | 0.024 | 2.7 | 2.2 |

Source: `families/mechanism_metrics.csv`.

### Table 5. Paired tests against instantaneous thresholding (target FAR 0.05; Holm within metric family)

| Mechanism | Δ excess (Holm p) | Δ FRR (Holm p) | Δ test FAR (Holm p) |
|---|---|---|---|
| Moving average | -1.460 (0.0004)* | +0.016 (0.0002)* | +0.005 (0.0615) |
| EWMA | -1.474 (0.0004)* | +0.021 (0.0002)* | +0.003 (1.0000) |
| Majority vote | -1.572 (0.0004)* | +0.006 (0.0002)* | +0.009 (0.0162)* |
| Debounce (dwell) | -1.680 (0.0004)* | +0.007 (0.0002)* | +0.012 (0.0021)* |
| Margin (dual threshold) | -1.688 (0.0004)* | +0.035 (0.8577) | -0.004 (1.0000) |
| Margin + dwell | -1.872 (0.0004)* | +0.071 (0.0002)* | +0.014 (0.0108)* |
| Trust model (dual τ) | -1.973 (0.0002)* | +0.126 (0.0001)* | +0.017 (0.0010)* |
| Trust model (single τ) | -1.834 (0.0002)* | +0.037 (0.0002)* | +0.007 (0.0007)* |
| SPRT | -1.680 (0.0004)* | -0.005 (0.8577) | +0.005 (0.4563) |

\* Holm-adjusted p < 0.05. Source: `families/statistical_tests.csv`.

### Table 6. FAR drift, test minus calibration (target 0.05)

| Mechanism | Mean | Median | n |
|---|---|---|---|
| Debounce (dwell) | +0.0110 | -0.0250 | 31 |
| EWMA | -0.0003 | -0.0410 | 31 |
| Margin + dwell | +0.0138 | -0.0083 | 30 |
| Instantaneous | -0.0002 | -0.0403 | 30 |
| Majority vote | +0.0076 | -0.0257 | 31 |
| Margin (dual threshold) | -0.0066 | -0.0420 | 26 |
| Moving average | +0.0020 | -0.0372 | 31 |
| SPRT | +0.0015 | -0.0410 | 31 |
| Trust model (dual τ) | +0.0114 | -0.0201 | 31 |
| Trust model (single τ) | +0.0027 | -0.0319 | 31 |

Source: `families/far_drift.csv`.

### Table 7. Rank of families by mean excess transitions and by FRR across operating points (1 = lowest)

| Mechanism | Excess rank 0.03 / 0.05 / 0.07 | FRR rank 0.03 / 0.05 / 0.07 |
|---|---|---|
| Instantaneous | 10 / 10 / 10 | 2 / 2 / 1 |
| Moving average | 7 / 9 / 7 | 6 / 5 / 7 |
| EWMA | 4 / 8 / 9 | 7 / 6 / 5 |
| Majority vote | 9 / 7 / 5 | 5 / 3 / 4 |
| Debounce (dwell) | 6 / 4 / 4 | 4 / 4 / 3 |
| Margin (dual threshold) | 8 / 6 / 8 | 3 / 8 / 6 |
| Margin + dwell | 3 / 3 / 2 | 9 / 9 / 8 |
| Trust model (dual τ) | 1 / 1 / 1 | 10 / 10 / 10 |
| Trust model (single τ) | 2 / 2 / 3 | 8 / 7 / 9 |
| SPRT | 4 / 4 / 6 | 1 / 1 / 2 |

Spearman ρ of excess ranks: 0.03 vs 0.05 = 0.84; 0.07 vs 0.05 = 0.89. FRR ranks: 0.81; 0.89.

### Table 4a. Tuned stabiliser families at target FAR 0.03 (participant-level means [95% bootstrap CI])

| Mechanism | n | Excess / seq | FRR | Test FAR | Recovery failure | Detection failure | Recovery latency (censored) | Detection latency (censored) |
|---|---|---|---|---|---|---|---|---|
| Instantaneous | 30 | 1.62 [0.77, 2.65] | 0.050 [0.017, 0.094] | 0.034 | 0.049 | 0.012 | 3.1 | 1.2 |
| Moving average | 31 | 0.53 [0.25, 0.86] | 0.064 [0.031, 0.105] | 0.038 | 0.041 | 0.012 | 4.8 | 1.5 |
| EWMA | 31 | 0.41 [0.19, 0.67] | 0.069 [0.038, 0.108] | 0.036 | 0.041 | 0.012 | 5.9 | 1.5 |
| Majority vote | 31 | 0.58 [0.28, 0.93] | 0.057 [0.024, 0.100] | 0.048 | 0.041 | 0.012 | 3.9 | 2.2 |
| Debounce (dwell) | 31 | 0.53 [0.28, 0.83] | 0.057 [0.024, 0.099] | 0.048 | 0.041 | 0.012 | 3.7 | 2.3 |
| Margin (dual threshold) | 18 | 0.58 [0.24, 0.99] | 0.055 [0.007, 0.121] | 0.039 | 0.044 | 0.030 | 3.2 | 1.9 |
| Margin + dwell | 30 | 0.30 [0.12, 0.51] | 0.125 [0.080, 0.172] | 0.043 | 0.138 | 0.012 | 12.1 | 2.3 |
| Trust model (dual τ) | 31 | 0.05 [0.01, 0.10] | 0.211 [0.159, 0.265] | 0.037 | 0.225 | 0.012 | 22.9 | 2.1 |
| Trust model (single τ) | 31 | 0.25 [0.13, 0.40] | 0.086 [0.058, 0.122] | 0.038 | 0.041 | 0.012 | 8.1 | 1.9 |
| SPRT | 31 | 0.41 [0.20, 0.65] | 0.043 [0.016, 0.081] | 0.038 | 0.035 | 0.024 | 3.2 | 1.9 |

Source: `secondary/far_0.03/mechanism_metrics.csv`.

### Table 4b. Tuned stabiliser families at target FAR 0.07 (participant-level means [95% bootstrap CI])

| Mechanism | n | Excess / seq | FRR | Test FAR | Recovery failure | Detection failure | Recovery latency (censored) | Detection latency (censored) |
|---|---|---|---|---|---|---|---|---|
| Instantaneous | 29 | 1.99 [1.01, 3.24] | 0.030 [0.006, 0.064] | 0.053 | 0.026 | 0.025 | 1.8 | 2.1 |
| Moving average | 31 | 0.74 [0.28, 1.35] | 0.056 [0.030, 0.088] | 0.053 | 0.035 | 0.024 | 4.8 | 2.3 |
| EWMA | 29 | 0.83 [0.31, 1.51] | 0.049 [0.023, 0.086] | 0.053 | 0.038 | 0.025 | 4.0 | 2.2 |
| Majority vote | 31 | 0.58 [0.28, 0.96] | 0.046 [0.019, 0.081] | 0.062 | 0.041 | 0.024 | 3.7 | 3.0 |
| Debounce (dwell) | 31 | 0.45 [0.17, 0.80] | 0.046 [0.019, 0.082] | 0.063 | 0.041 | 0.024 | 3.7 | 3.0 |
| Margin (dual threshold) | 23 | 0.79 [0.30, 1.39] | 0.051 [0.015, 0.096] | 0.037 | 0.055 | 0.016 | 4.0 | 1.4 |
| Margin + dwell | 31 | 0.10 [0.04, 0.18] | 0.075 [0.040, 0.119] | 0.067 | 0.081 | 0.017 | 7.2 | 3.6 |
| Trust model (dual τ) | 31 | 0.03 [0.00, 0.06] | 0.160 [0.112, 0.216] | 0.071 | 0.181 | 0.017 | 17.8 | 3.9 |
| Trust model (single τ) | 31 | 0.17 [0.07, 0.29] | 0.078 [0.052, 0.109] | 0.061 | 0.035 | 0.017 | 8.0 | 2.9 |
| SPRT | 29 | 0.63 [0.34, 0.96] | 0.035 [0.009, 0.071] | 0.061 | 0.038 | 0.032 | 2.7 | 2.7 |

Source: `secondary/far_0.07/mechanism_metrics.csv`.

### Table 8. Where instability sits, and what the score encodes

| Quantity | Value |
|---|---|
| Test sequences with zero excess transitions (instantaneous) | 124/173 (71.7%) |
| Share of per-participant mean excess transitions from top 5 of 30 participants | 65.6% |
| Same share on raw sequence sums | 63.7% |
| Participants with any excess transition (per-participant mean > 0) | 20/30 |
| Mean per-participant test AUC, F3 (full features) | 0.990 |
| Mean per-participant test AUC, F7 (missingness only) | 0.758 |
| Paired difference F3 − F7 [95% CI] | 0.232 [0.191, 0.273], n = 31 |

F7 columns available: ['enrolled_user', 'identical_sequences', 'AUC_F3', 'AUC_F7', 'note', 'diff_F3_minus_F7']. Sources: `families/sequence_metrics.csv`, `secondary/score_validity_*`.
