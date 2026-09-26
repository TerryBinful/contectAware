| family | outcome | comparison | n_users | median_a | median_b | median_diff | ci_lo | ci_hi | p_value | p_holm | rank_biserial | significant |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| primary | ania | hysteresis - margin (best smoother on validation) | 33 | 1 | 0 | 1 | 1 | 1 | 0.002877 | 0.002877 | 0.601 | True |
| primary_secondary_outcomes | first_lock | hysteresis - margin (best smoother on validation) | 33 | 1 | 0 | 1 | 1 | 1 | 0.002314 | 0.006942 | 0.601 | True |
| primary_secondary_outcomes | recovery | hysteresis - margin (best smoother on validation) | 33 | 1 | 0 | 1 | 1 | 1 | 3.649e-08 | 3.285e-07 | 1 | True |
| primary_secondary_outcomes | miss_rate | hysteresis - margin (best smoother on validation) | 33 | 0.0625 | 0.0625 | 0 | 0 | 0 | 0.006944 | 0.01389 | -0.9091 | True |
| primary_secondary_outcomes | far_frame | hysteresis - margin (best smoother on validation) | 33 | 0.2021 | 0.1854 | 0.01979 | -0.02083 | 0.04375 | 0.2718 | 0.2718 | 0.2193 | False |
| primary_secondary_outcomes | frr_time | hysteresis - margin (best smoother on validation) | 33 | 0.01329 | 0.007761 | 0.001561 | 0 | 0.01645 | 0.0006973 | 0.003948 | 0.7607 | True |
| primary_secondary_outcomes | false_locks_per_hour | hysteresis - margin (best smoother on validation) | 33 | 0.1075 | 0.1837 | -0.03494 | -0.09266 | 0 | 0.001264 | 0.005057 | -0.7681 | True |
| primary_secondary_outcomes | transitions_per_hour | hysteresis - margin (best smoother on validation) | 33 | 0.1944 | 0.3674 | -0.06989 | -0.2004 | 0 | 0.0006581 | 0.003948 | -0.8116 | True |
| primary_secondary_outcomes | pingpong_per_hour | hysteresis - margin (best smoother on validation) | 33 | 0.04633 | 0.09901 | -0.08863 | -0.1257 | -0.03448 | 4.968e-05 | 0.0003477 | -0.9467 | True |
| primary_secondary_outcomes | lockout_mean_frames | hysteresis - margin (best smoother on validation) | 22 | 12.67 | 3.85 | 5.598 | 4 | 9.476 | 4.005e-05 | 0.0003204 | 1 | True |
| H3_component_ablation | ania | hysteresis - margin | 33 | 1 | 0 | 1 | 1 | 1 | 0.002877 | 0.005754 | 0.601 | True |
| H3_component_ablation | ania | hysteresis - debounce | 33 | 1 | 1 | 0 | 0 | 0 | 0.06332 | 0.06332 | -1 | False |
| H4_context_matching | ania | threshold: M - X | 33 | 0.5 | 0 | 0 | 0 | 0 | 0.2281 | 1 | 0.3216 | False |
| H4_context_matching | ania | moving_average: M - X | 33 | 1 | 1 | 0 | 0 | 0 | 0.1784 | 1 | 0.4359 | False |
| H4_context_matching | ania | ewma: M - X | 33 | 2 | 2 | 0 | 0 | 0 | 0.3168 | 1 | 0.2632 | False |
| H4_context_matching | ania | majority_vote: M - X | 33 | 1 | 1 | 0 | 0 | 0 | 0.2579 | 1 | 0.4222 | False |
| H4_context_matching | ania | debounce: M - X | 33 | 1 | 1 | 0 | 0 | 0 | 0.4951 | 1 | 0.2857 | False |
| H4_context_matching | ania | margin: M - X | 33 | 0 | 0 | 0 | 0 | 0 | 0.8933 | 1 | -0.04545 | False |
| H4_context_matching | ania | hysteresis: M - X | 33 | 1 | 1 | 0 | 0 | 0 | 0.5176 | 1 | 0.2857 | False |
| H4_context_matching | ania | trust: M - X | 33 | 2 | 2 | 0 | 0 | 0 | 0.3805 | 1 | 0.3571 | False |
| H4_context_matching | ania | sprt: M - X | 33 | 1 | 1 | 0 | 0 | 0 | 0.4932 | 1 | 0.183 | False |
