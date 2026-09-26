# SECONDARY SENSITIVITY at target FAR 0.03 (PREREGISTRATION_v2 §4.2)

**This is NOT the preregistered primary result.** It re-evaluates the identical §3.1 criterion at a declared sensitivity target. The confirmatory primary is at FAR 0.05 in `primary/`.

Generated mechanically by scripts/decision_layer_offline.py. Target FAR 0.03, one-sided band [0.02, 0.03], selection C1 with reachability filter C2, only theta tuned per cell.

**Verdict: Hysteresis offers no measurable advantage over its components on this benchmark.**

```
                                            0                 1
comparison                   cell_H vs cell_D  cell_H vs cell_M
n_users_paired                             30                18
n_users_without_H                           1                 1
n_users_without_comparator                  0                13
excess_H_mean                        0.296667               0.3
excess_comp_mean                     0.547222          0.577778
excess_diff_mean                    -0.250556         -0.277778
excess_diff_median                        0.0               0.0
wilcoxon_W                              133.0              55.0
p_value                              0.037678          0.179162
FRR_diff_mean                        0.066847          0.030818
FRR_diff_lo                          0.029528          0.002468
FRR_diff_hi                          0.107957          0.060573
detfail_diff_mean                         0.0         -0.009259
detfail_diff_lo                           0.0         -0.027778
detfail_diff_hi                           0.0               0.0
p_holm                               0.075357          0.179162
c1_fewer_excess_significant             False             False
c2_FRR_noninferior                      False             False
c3_detfail_noninferior                   True              True
```

Criteria: (1) fewer excess transitions, paired two-sided Wilcoxon, Holm-adjusted p < 0.05 across the two comparisons, mean difference < 0; (2) upper 95% bootstrap bound of paired FRR difference < +0.02; (3) same for detection-failure rate. Users lacking an eligible cell for either member of a pair are excluded from that pair and counted above.
