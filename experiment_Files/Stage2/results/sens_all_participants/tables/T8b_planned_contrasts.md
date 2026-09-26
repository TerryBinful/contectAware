| family | outcome | comparison | n_users | median_a | median_b | median_diff | ci_lo | ci_hi | p_value | p_holm | rank_biserial | significant |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| primary | ania | hysteresis - margin (best smoother on validation) | 56 | 1 | 0 | 1 | 1 | 1 | 0.003714 | 0.003714 | 0.4208 | True |
| primary_secondary_outcomes | first_lock | hysteresis - margin (best smoother on validation) | 56 | 1 | 0 | 1 | 1 | 1 | 6.195e-05 | 0.0003098 | 0.5777 | True |
| primary_secondary_outcomes | recovery | hysteresis - margin (best smoother on validation) | 56 | 1 | 0 | 1 | 1 | 1 | 1.164e-13 | 1.048e-12 | 1 | True |
| primary_secondary_outcomes | miss_rate | hysteresis - margin (best smoother on validation) | 56 | 0.0625 | 0.125 | -0.0625 | -0.125 | 0 | 6.254e-07 | 4.378e-06 | -0.9786 | True |
| primary_secondary_outcomes | far_frame | hysteresis - margin (best smoother on validation) | 56 | 0.1958 | 0.2208 | -0.008854 | -0.0375 | 0.04583 | 0.6984 | 0.6984 | -0.05952 | False |
| primary_secondary_outcomes | frr_time | hysteresis - margin (best smoother on validation) | 56 | 0.01394 | 0.002996 | 0.00739 | 0.003258 | 0.01493 | 3.085e-08 | 2.468e-07 | 0.9478 | True |
| primary_secondary_outcomes | false_locks_per_hour | hysteresis - margin (best smoother on validation) | 56 | 0.1202 | 0.07297 | 0 | 0 | 0.0631 | 0.05937 | 0.2375 | 0.338 | False |
| primary_secondary_outcomes | transitions_per_hour | hysteresis - margin (best smoother on validation) | 56 | 0.2048 | 0.1459 | 0 | 0 | 0.1277 | 0.1081 | 0.3243 | 0.2846 | False |
| primary_secondary_outcomes | pingpong_per_hour | hysteresis - margin (best smoother on validation) | 56 | 0.04565 | 0.06486 | 0 | -0.03317 | 0 | 0.2646 | 0.5292 | -0.2024 | False |
| primary_secondary_outcomes | lockout_mean_frames | hysteresis - margin (best smoother on validation) | 31 | 8 | 3 | 3.286 | 1.857 | 5.5 | 4.155e-05 | 0.0002493 | 0.8713 | True |
| H3_component_ablation | ania | hysteresis - margin | 56 | 1 | 0 | 1 | 1 | 1 | 0.003714 | 0.007429 | 0.4208 | True |
| H3_component_ablation | ania | hysteresis - debounce | 56 | 1 | 1 | 0 | 0 | 0 | 0.01735 | 0.01735 | -1 | True |
| H4_context_matching | ania | threshold: M - X | 56 | 0.25 | 0 | 0 | 0 | 0 | 0.1439 | 1 | 0.3153 | False |
| H4_context_matching | ania | moving_average: M - X | 56 | 1 | 1 | 0 | 0 | 0 | 0.4765 | 1 | 0.2083 | False |
| H4_context_matching | ania | ewma: M - X | 56 | 1 | 1 | 0 | 0 | 0 | 0.4795 | 1 | 0.1842 | False |
| H4_context_matching | ania | majority_vote: M - X | 56 | 1 | 1 | 0 | 0 | 0 | 0.7891 | 1 | -0.09091 | False |
| H4_context_matching | ania | debounce: M - X | 56 | 1 | 1 | 0 | 0 | 0 | 0.5392 | 1 | -0.2182 | False |
| H4_context_matching | ania | margin: M - X | 56 | 0 | 0 | 0 | 0 | 0 | 0.9544 | 1 | -0.01667 | False |
| H4_context_matching | ania | hysteresis: M - X | 56 | 1 | 1 | 0 | 0 | 0 | 0.07962 | 0.7165 | -0.8667 | False |
| H4_context_matching | ania | trust: M - X | 56 | 2 | 2 | 0 | 0 | 0 | 0.6662 | 1 | 0.1905 | False |
| H4_context_matching | ania | sprt: M - X | 56 | 0 | 0 | 0 | 0 | 0 | 0.3236 | 1 | 0.268 | False |
