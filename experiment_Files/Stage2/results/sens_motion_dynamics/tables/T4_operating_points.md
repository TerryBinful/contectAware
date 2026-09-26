| target_name | target_false_locks_per_hour | mechanism | params_str | in_band | n_in_band_cells | n_excluded_absorbing | val_false_locks_per_hour | val_lockout_mean_frames | val_ania_median | val_far_frame | val_miss_rate | best_smoother |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| primary | 0.125 | threshold | theta=0.05732 | True | 3 | 0 | 0.1399 | 1.14 | 3 | 0.5384 | 0.4091 | debounce |
| primary | 0.125 | moving_average | k=3, theta=0.1978 | True | 7 | 0 | 0.1427 | 2.363 | 2.5 | 0.5515 | 0.2424 | debounce |
| primary | 0.125 | ewma | alpha=0.7, theta=0.1419 | True | 6 | 8 | 0.1134 | 1.926 | 3 | 0.5415 | 0.3144 | debounce |
| primary | 0.125 | majority_vote | k=3, theta=0.1545 | True | 6 | 0 | 0.1316 | 2.777 | 2 | 0.4943 | 0.2311 | debounce |
| primary | 0.125 | debounce | T=3, theta=0.31 | True | 6 | 3 | 0.1385 | 8.061 | 2 | 0.4592 | 0.1875 | debounce |
| primary | 0.125 | margin | m=0.2, theta=0.1545 | True | 5 | 177 | 0.126 | 1.844 | 2 | 0.4901 | 0.3163 | debounce |
| primary | 0.125 | hysteresis | m=0.3, T=2, theta=0.3543 | True | 17 | 613 | 0.1357 | 9.134 | 2 | 0.3847 | 0.1894 | debounce |
| primary | 0.125 | trust | r=0.5, tau=0.5, theta=0.4013 | True | 5 | 380 | 0.1092 | 12.46 | 3 | 0.4485 | 0.2443 | debounce |
| primary | 0.125 | sprt | alpha=0.001, beta=0.01804 | True | 29 | 0 | 0.1427 | 24.16 | 1.5 | 0.2854 | 0.1591 | debounce |
| primary | 0.125 | hmm | rho=0.0001, theta=0.4013 | True | 49 | 1 | 0.1427 | 18.2 | 2.5 | 0.3514 | 0.2045 | debounce |
| sensitivity_1 | 0.5 | threshold | theta=0.1301 | True | 2 | 0 | 0.5248 | 1.229 | 2 | 0.4409 | 0.2633 | debounce |
| sensitivity_1 | 0.5 | moving_average | k=2, theta=0.2689 | True | 11 | 34 | 0.5542 | 1.965 | 1 | 0.4019 | 0.1667 | debounce |
| sensitivity_1 | 0.5 | ewma | alpha=0.7, theta=0.2497 | True | 8 | 37 | 0.522 | 1.732 | 1.5 | 0.4091 | 0.1761 | debounce |
| sensitivity_1 | 0.5 | majority_vote | k=3, theta=0.2891 | True | 6 | 22 | 0.5248 | 2.837 | 1 | 0.375 | 0.1458 | debounce |
| sensitivity_1 | 0.5 | debounce | T=2, theta=0.3543 | True | 5 | 19 | 0.557 | 4.369 | 1 | 0.33 | 0.1174 | debounce |
| sensitivity_1 | 0.5 | margin | m=0.3, theta=0.2891 | True | 4 | 0 | 0.5206 | 2.253 | 1 | 0.3332 | 0.1553 | debounce |
| sensitivity_1 | 0.5 | hysteresis | m=0.3, T=2, theta=0.5498 | True | 17 | 21 | 0.5262 | 14.02 | 1 | 0.2248 | 0.0928 | debounce |
| sensitivity_1 | 0.5 | trust | r=0.5, tau=0.5, theta=0.6225 | True | 8 | 15 | 0.5556 | 19.46 | 1 | 0.2037 | 0.08902 | debounce |
| sensitivity_1 | 0.5 | sprt | alpha=0.01, beta=0.2687 | True | 8 | 0 | 0.501 | 11.41 | 0 | 0.1624 | 0.09659 | debounce |
| sensitivity_1 | 0.5 | hmm | rho=0.001, theta=0.9802 | True | 38 | 0 | 0.5724 | 10.02 | 0 | 0.1666 | 0.08902 | debounce |
| sensitivity_2 | 0.04167 | threshold | theta=0.02931 | True | 3 | 0 | 0.04618 | 1.03 | 3.5 | 0.5982 | 0.4697 | debounce |
| sensitivity_2 | 0.04167 | moving_average | k=2, theta=0.07586 | True | 6 | 0 | 0.04618 | 1.515 | 3 | 0.6158 | 0.3939 | debounce |
| sensitivity_2 | 0.04167 | ewma | alpha=0.7, theta=0.09112 | True | 8 | 0 | 0.04758 | 1.588 | 3 | 0.6301 | 0.3977 | debounce |
| sensitivity_2 | 0.04167 | majority_vote | k=3, theta=0.09112 | True | 7 | 0 | 0.04618 | 2.455 | 2.5 | 0.5604 | 0.3258 | debounce |
| sensitivity_2 | 0.04167 | debounce | T=2, theta=0.09975 | True | 4 | 1 | 0.03779 | 3.222 | 3 | 0.5549 | 0.3314 | debounce |
| sensitivity_2 | 0.04167 | margin | m=0.2, theta=0.1301 | True | 3 | 0 | 0.04618 | 1.818 | 2.5 | 0.5365 | 0.3674 | debounce |
| sensitivity_2 | 0.04167 | hysteresis | m=0.3, T=2, theta=0.2689 | True | 12 | 6 | 0.04758 | 8.118 | 2.5 | 0.4727 | 0.2746 | debounce |
| sensitivity_2 | 0.04167 | trust | r=0.5, tau=0.5, theta=0.3318 | True | 6 | 7 | 0.04478 | 8.594 | 3 | 0.5615 | 0.3883 | debounce |
| sensitivity_2 | 0.04167 | sprt | alpha=0.1, beta=1.343e-05 | False | 0 | 60 | 0.06578 | 29.79 | 3 | 0.4282 | 0.2367 | debounce |
| sensitivity_2 | 0.04167 | hmm | rho=0.05, theta=0.001007 | True | 8 | 0 | 0.04758 | 1.147 | 3.5 | 0.6226 | 0.4413 | debounce |
