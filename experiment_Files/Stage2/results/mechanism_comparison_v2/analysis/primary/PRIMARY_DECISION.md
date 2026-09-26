# Primary decision (PREREGISTRATION_v2 §3.1)

Generated mechanically by scripts/decision_layer_offline.py. Target FAR 0.05, one-sided band [0.04, 0.05], selection C1 with reachability filter C2, only theta tuned per cell.

**Verdict: Hysteresis offers no measurable advantage over its components on this benchmark.**

```
                                            0                 1
comparison                   cell_H vs cell_D  cell_H vs cell_M
n_users_paired                             30                24
n_users_without_H                           1                 1
n_users_without_comparator                  0                 6
excess_H_mean                        0.202778          0.236806
excess_comp_mean                     0.332222          0.436111
excess_diff_mean                    -0.129444         -0.199306
excess_diff_median                        0.0               0.0
wilcoxon_W                              199.0             117.5
p_value                              0.474788          0.343785
FRR_diff_mean                        0.074417          0.030365
FRR_diff_lo                          0.032407         -0.007621
FRR_diff_hi                          0.118676           0.06885
detfail_diff_mean                         0.0         -0.006944
detfail_diff_lo                           0.0         -0.020833
detfail_diff_hi                           0.0               0.0
p_holm                                0.68757           0.68757
c1_fewer_excess_significant             False             False
c2_FRR_noninferior                      False             False
c3_detfail_noninferior                   True              True
```

Criteria: (1) fewer excess transitions, paired two-sided Wilcoxon, Holm-adjusted p < 0.05 across the two comparisons, mean difference < 0; (2) upper 95% bootstrap bound of paired FRR difference < +0.02; (3) same for detection-failure rate. Users lacking an eligible cell for either member of a pair are excluded from that pair and counted above.
