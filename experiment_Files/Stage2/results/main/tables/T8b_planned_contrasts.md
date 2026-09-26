| family | outcome | comparison | n_users | median_a | median_b | median_diff | ci_lo | ci_hi | p_value | p_holm | rank_biserial | significant |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| primary | ania | hysteresis - margin (best smoother on validation) | 33 | 1 | 1 | 0.5 | -0.5 | 1 | 0.921 | 0.921 | 0.02069 | False |
| primary_secondary_outcomes | first_lock | hysteresis - margin (best smoother on validation) | 33 | 1 | 0.5 | 1 | 0.5 | 1 | 0.167 | 0.334 | 0.2727 | False |
| primary_secondary_outcomes | recovery | hysteresis - margin (best smoother on validation) | 33 | 1 | 0 | 1 | 1 | 1 | 3.649e-08 | 3.285e-07 | 1 | True |
| primary_secondary_outcomes | miss_rate | hysteresis - margin (best smoother on validation) | 33 | 0.125 | 0.125 | -0.0625 | -0.125 | 0 | 4.702e-05 | 0.0003291 | -0.9565 | True |
| primary_secondary_outcomes | far_frame | hysteresis - margin (best smoother on validation) | 33 | 0.2615 | 0.3135 | -0.03333 | -0.08958 | -1.11e-16 | 0.005313 | 0.02656 | -0.5561 | True |
| primary_secondary_outcomes | frr_time | hysteresis - margin (best smoother on validation) | 33 | 0.01585 | 0.005764 | 0.009307 | 0.001879 | 0.02712 | 6.281e-06 | 5.025e-05 | 0.9947 | True |
| primary_secondary_outcomes | false_locks_per_hour | hysteresis - margin (best smoother on validation) | 33 | 0.139 | 0.08646 | 0 | 0 | 0.06633 | 0.03085 | 0.1234 | 0.5257 | False |
| primary_secondary_outcomes | transitions_per_hour | hysteresis - margin (best smoother on validation) | 33 | 0.2387 | 0.1729 | 0 | 0 | 0.1327 | 0.05159 | 0.1548 | 0.4638 | False |
| primary_secondary_outcomes | pingpong_per_hour | hysteresis - margin (best smoother on validation) | 33 | 0.08646 | 0.04684 | 0 | -0.03193 | 0 | 0.6148 | 0.6148 | -0.1225 | False |
| primary_secondary_outcomes | lockout_mean_frames | hysteresis - margin (best smoother on validation) | 20 | 10.88 | 4.421 | 4.882 | 2.062 | 7.643 | 0.0002535 | 0.001521 | 0.9825 | True |
| H3_component_ablation | ania | hysteresis - margin | 33 | 1 | 1 | 0.5 | -0.5 | 1 | 0.921 | 0.921 | 0.02069 | False |
| H3_component_ablation | ania | hysteresis - debounce | 33 | 1 | 1 | 0 | 0 | 0 | 0.007058 | 0.01412 | -1 | True |
| H4_context_matching | ania | threshold: M - X | 33 | 2 | 1.5 | 0 | 0 | 1 | 0.7028 | 1 | 0.08547 | False |
| H4_context_matching | ania | moving_average: M - X | 33 | 1 | 1 | 0 | 0 | 0 | 0.8808 | 1 | 0.0381 | False |
| H4_context_matching | ania | ewma: M - X | 33 | 2 | 1.5 | 0 | 0 | 0.5 | 0.5561 | 1 | 0.1367 | False |
| H4_context_matching | ania | majority_vote: M - X | 33 | 1 | 1 | 0 | 0 | 0 | 0.3519 | 1 | 0.2549 | False |
| H4_context_matching | ania | debounce: M - X | 33 | 1 | 1 | 0 | 0 | 0 | 0.5681 | 1 | 0.1569 | False |
| H4_context_matching | ania | margin: M - X | 33 | 1 | 0 | 0 | 0 | 1 | 0.05824 | 0.5242 | 0.4585 | False |
| H4_context_matching | ania | hysteresis: M - X | 33 | 1 | 1 | 0 | 0 | 0 | 0.9644 | 1 | -0.01515 | False |
| H4_context_matching | ania | trust: M - X | 33 | 2 | 2 | 0 | 0 | 0 | 0.7386 | 1 | 0.08772 | False |
| H4_context_matching | ania | sprt: M - X | 33 | 1 | 1 | 0 | 0 | 0.5 | 0.3839 | 1 | 0.2095 | False |
