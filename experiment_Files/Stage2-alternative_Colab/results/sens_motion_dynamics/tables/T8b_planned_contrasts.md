| family | outcome | comparison | n_users | median_a | median_b | median_diff | ci_lo | ci_hi | p_value | p_holm | rank_biserial | significant |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| primary | ania | hysteresis - debounce (best smoother on validation) | 33 | 1.5 | 2.5 | -1 | -1 | 0 | 0.001033 | 0.001033 | -0.7236 | True |
| primary_secondary_outcomes | first_lock | hysteresis - debounce (best smoother on validation) | 33 | 1.5 | 2.5 | -1 | -1 | 0 | 9.141e-05 | 0.0006399 | -0.89 | True |
| primary_secondary_outcomes | recovery | hysteresis - debounce (best smoother on validation) | 33 | 1 | 2 | -1 | -1 | -1 | 2.756e-05 | 0.0002205 | -0.8207 | True |
| primary_secondary_outcomes | miss_rate | hysteresis - debounce (best smoother on validation) | 33 | 0.25 | 0.25 | 0 | -0.0625 | 0 | 0.163 | 0.9779 | -0.3377 | False |
| primary_secondary_outcomes | far_frame | hysteresis - debounce (best smoother on validation) | 33 | 0.4 | 0.4854 | -0.07292 | -0.1 | -0.04271 | 4.049e-07 | 3.644e-06 | -0.8966 | True |
| primary_secondary_outcomes | frr_time | hysteresis - debounce (best smoother on validation) | 33 | 0.01592 | 0.01441 | 0 | -0.0005198 | 0.000969 | 0.3158 | 1 | 0.2251 | False |
| primary_secondary_outcomes | false_locks_per_hour | hysteresis - debounce (best smoother on validation) | 33 | 0.1102 | 0.1349 | 0 | -0.03071 | 0 | 0.7151 | 1 | -0.09091 | False |
| primary_secondary_outcomes | transitions_per_hour | hysteresis - debounce (best smoother on validation) | 33 | 0.1975 | 0.2699 | 0 | -0.09368 | 0 | 0.6849 | 1 | -0.09881 | False |
| primary_secondary_outcomes | pingpong_per_hour | hysteresis - debounce (best smoother on validation) | 33 | 0.04938 | 0.07777 | 0 | -0.03582 | 0 | 0.7843 | 1 | -0.06522 | False |
| primary_secondary_outcomes | lockout_mean_frames | hysteresis - debounce (best smoother on validation) | 26 | 8.896 | 7.05 | 0.2583 | -1.292 | 2.225 | 0.2637 | 1 | 0.2507 | False |
| H3_component_ablation | ania | hysteresis - margin | 33 | 1.5 | 3 | 0 | -2 | 0 | 0.01544 | 0.01544 | -0.5413 | True |
| H3_component_ablation | ania | hysteresis - debounce | 33 | 1.5 | 2.5 | -1 | -1 | 0 | 0.001033 | 0.002065 | -0.7236 | True |
| H4_context_matching | ania | threshold: M - X | 33 | 3 | 3 | 1 | 0 | 2.5 | 0.05406 | 0.4865 | 0.4092 | False |
| H4_context_matching | ania | moving_average: M - X | 33 | 2.5 | 2.5 | 0 | -0.5 | 0.5 | 0.4722 | 1 | 0.1631 | False |
| H4_context_matching | ania | ewma: M - X | 33 | 3 | 2.5 | 0 | -0.5 | 1 | 0.3683 | 1 | 0.1908 | False |
| H4_context_matching | ania | majority_vote: M - X | 33 | 2.5 | 2 | 0.5 | 0 | 0.5 | 0.3139 | 1 | 0.2167 | False |
| H4_context_matching | ania | debounce: M - X | 33 | 2.5 | 2 | 0 | 0 | 0.5 | 0.1045 | 0.6268 | 0.3983 | False |
| H4_context_matching | ania | margin: M - X | 33 | 3 | 1.5 | 0.5 | 0 | 2 | 0.06933 | 0.5547 | 0.3995 | False |
| H4_context_matching | ania | hysteresis: M - X | 33 | 1.5 | 1.5 | 0 | 0 | 1 | 0.2344 | 1 | 0.2767 | False |
| H4_context_matching | ania | trust: M - X | 33 | 3 | 3 | 0 | 0 | 1 | 0.08561 | 0.5992 | 0.3908 | False |
| H4_context_matching | ania | sprt: M - X | 33 | 1.5 | 1.5 | 0.5 | 0 | 1 | 0.236 | 1 | 0.2593 | False |
