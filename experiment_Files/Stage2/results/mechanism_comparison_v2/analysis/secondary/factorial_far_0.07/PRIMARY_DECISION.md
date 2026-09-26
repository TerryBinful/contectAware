# SECONDARY SENSITIVITY at target FAR 0.07 (PREREGISTRATION_v2 §4.2)

**This is NOT the preregistered primary result.** It re-evaluates the identical §3.1 criterion at a declared sensitivity target. The confirmatory primary is at FAR 0.05 in `primary/`.

Generated mechanically by scripts/decision_layer_offline.py. Target FAR 0.07, one-sided band [0.06, 0.07], selection C1 with reachability filter C2, only theta tuned per cell.

**Verdict: Hysteresis offers no measurable advantage over its components on this benchmark.**

```
                                            0                 1
comparison                   cell_H vs cell_D  cell_H vs cell_M
n_users_paired                             31                23
n_users_without_H                           0                 0
n_users_without_comparator                  0                 8
excess_H_mean                        0.101613          0.100725
excess_comp_mean                     0.452151          0.788406
excess_diff_mean                    -0.350538         -0.687681
excess_diff_median                        0.0               0.0
wilcoxon_W                              105.0              52.0
p_value                              0.003758          0.007769
FRR_diff_mean                        0.029265          0.025978
FRR_diff_lo                          0.008091         -0.003902
FRR_diff_hi                          0.055651          0.060208
detfail_diff_mean                   -0.006452               0.0
detfail_diff_lo                     -0.019355               0.0
detfail_diff_hi                           0.0               0.0
p_holm                               0.007516          0.007769
c1_fewer_excess_significant              True              True
c2_FRR_noninferior                      False             False
c3_detfail_noninferior                   True              True
```

Criteria: (1) fewer excess transitions, paired two-sided Wilcoxon, Holm-adjusted p < 0.05 across the two comparisons, mean difference < 0; (2) upper 95% bootstrap bound of paired FRR difference < +0.02; (3) same for detection-failure rate. Users lacking an eligible cell for either member of a pair are excluded from that pair and counted above.
