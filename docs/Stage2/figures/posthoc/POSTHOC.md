# Post-hoc paired descriptives for the selected hysteresis cell

> **POST HOC, NOT IN THE FROZEN PLAN.**
>
> These quantities were computed during review. They are **not** part of the
> preregistered confirmatory analysis in `docs/Stage2/PREREGISTRATION_v2.md`, which tests
> excess transitions (C1) plus non-inferiority on FRR (C2) and detection failure (C3),
> and nothing else. No p-value, no Holm correction and no decision rule is attached to
> anything below. The intervals are descriptive bootstrap intervals over participants.

**Script:** `docs/Stage2/figures/scripts/posthoc_cellH_descriptives.py`
**Outputs (this directory):** `posthoc_cellH_descriptives.csv`,
`posthoc_cellH_vs_paper.csv`, `provenance.json`

**Method**, matching the frozen pipeline exactly: participants are paired, so a
participant contributes only when both cells were feasible; the statistic is the mean of
the per-participant paired difference (H minus comparator); the interval is the project's
own routine `src.decision_v2.bootstrap_mean_ci` with `n_boot = 2000` and `seed = 20260918`
— one seed for every metric and both comparisons, so the table is reproducible from the
script alone. Sources: `analysis/primary/cell_selection.csv` for which cell each
participant contributes, `analysis/factorial/participant_metrics.csv` with
`target == 0.05` for the values. Both read only.

**Pairing.** cell_H vs cell_D: **30 of 31** participants (1 has no feasible H cell, 0 lack
a D cell). cell_H vs cell_M: **24 of 31** (1 has no H cell, 6 have no M cell). The two
comparisons therefore rest on different participant sets and are not comparable with each
other.

## cell_H versus cell_D (dwell only), 30 paired participants

| Metric | mean H | mean D | Mean paired diff | 95% CI | Excludes 0 |
|---|---|---|---|---|---|
| `recovery_failure` | 0.1450 | 0.0422 | **+0.103** | [0.028, 0.197] | yes |
| `recovery_latency_censored` (frames) | 11.994 | 4.004 | **+7.99** | [3.45, 13.57] | yes |
| `lockout_fraction_during_genuine` | 0.1244 | 0.0500 | **+0.074** | [0.033, 0.122] | yes |
| `FAR` | 0.0591 | 0.0568 | +0.002 | [−0.011, 0.015] | no |
| `detection_latency_censored` (frames) | 3.086 | 2.586 | +0.50 | [−0.261, 1.228] | no |

### Agreement with the values printed in Section 5.1

| Metric | Reproduced here | Paper | Point estimate gap | Matches to 3 dp |
|---|---|---|---|---|
| `recovery_failure` | +0.103 [0.028, 0.197] | +0.103 [0.033, 0.189] | 0.000222 | **yes** |
| `recovery_latency_censored` | +7.990 [3.452, 13.569] | +7.990 [3.460, 13.370] | 0.000000 | **yes** |
| `lockout_fraction_during_genuine` | +0.074 [0.033, 0.122] | +0.074 [0.034, 0.119] | 0.000417 | **yes** |
| `FAR` | +0.002 [−0.011, 0.015] | +0.002 [−0.012, 0.016] | 0.000315 | **yes** |
| `detection_latency_censored` | +0.500 [−0.261, 1.228] | +0.500 [−0.290, 1.240] | 0.000000 | **yes** |

**All five point estimates reproduce to three decimal places.** Confidence bounds differ
by at most 0.0287 on the proportion and rate metrics and 0.199 frames on
`recovery_latency_censored`. That is ordinary resampling variation: the reported intervals
were produced with a different seed, and 2,000 resamples of 30 participants gives bounds
of roughly this precision. No bound crosses zero in a direction that would change the
reading of any metric.

## cell_H versus cell_M (margin only), 24 paired participants

| Metric | mean H | mean M | Mean paired diff | 95% CI | Excludes 0 |
|---|---|---|---|---|---|
| `recovery_failure` | 0.0910 | 0.0944 | −0.003 | [−0.108, 0.069] | no |
| `recovery_latency_censored` (frames) | 9.253 | 6.510 | +2.74 | [−1.39, 5.85] | no |
| `lockout_fraction_during_genuine` | 0.1077 | 0.0773 | +0.030 | [−0.010, 0.069] | no |
| `FAR` | 0.0458 | 0.0294 | +0.017 | [−0.001, 0.029] | no |
| `detection_latency_censored` (frames) | 2.254 | 1.175 | **+1.08** | [0.025, 1.783] | yes |

The paper does not print a cell_H versus cell_M version of this table, so there is nothing
to compare these against; they are reported here because the prompt asked for the
comparison to be repeated.

## Reading

Against **dwell only**, adding the margin costs recovery: the margin + dwell cell fails to
recover an additional 10.3 percentage points of the time, takes about 8 more frames — on
this dataset's cadence, roughly 8 minutes — to recover when it does, and leaves the
genuine user locked out for 7.4 more percentage points of genuine frames. It buys nothing
measurable in return: the FAR difference is 0.002 with an interval spanning zero, so the
extra lockout is not being exchanged for security, and detection latency is statistically
indistinguishable.

Against **margin only**, the picture is weaker and rests on 24 participants. Only
detection latency separates, and by about one frame.

Both readings are descriptive. They are consistent with the preregistered result — that
the margin + dwell cell offers no measurable advantage over its components — but they are
not what that result was tested on, and they should be reported as post-hoc observations
that motivate future work, not as findings.
