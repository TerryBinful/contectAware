| target_name | target_false_locks_per_hour | mechanism | params_str | in_band | n_in_band_cells | n_excluded_absorbing | val_false_locks_per_hour | val_lockout_mean_frames | val_ania_median | val_far_frame | val_miss_rate | best_smoother |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| primary | 0.125 | threshold | theta=0.04311 | True | 2 | 0 | 0.1413 | 1.386 | 2.5 | 0.4524 | 0.3295 | margin |
| primary | 0.125 | moving_average | k=2, theta=0.09975 | True | 14 | 0 | 0.126 | 2.178 | 1.5 | 0.4616 | 0.2424 | margin |
| primary | 0.125 | ewma | alpha=0.7, theta=0.1091 | True | 11 | 0 | 0.1302 | 2.226 | 2 | 0.4719 | 0.2367 | margin |
| primary | 0.125 | majority_vote | k=3, theta=0.1091 | True | 9 | 0 | 0.1232 | 3.023 | 1 | 0.4206 | 0.1932 | margin |
| primary | 0.125 | debounce | T=2, theta=0.1545 | True | 9 | 4 | 0.1357 | 4.649 | 1 | 0.3783 | 0.1591 | margin |
| primary | 0.125 | margin | m=0.3, theta=0.1978 | True | 4 | 177 | 0.1148 | 4.098 | 0 | 0.3445 | 0.2178 | margin |
| primary | 0.125 | hysteresis | m=0.3, T=2, theta=0.3318 | True | 25 | 535 | 0.1302 | 10.39 | 1 | 0.3115 | 0.1326 | margin |
| primary | 0.125 | trust | r=0.5, tau=0.5, theta=0.4256 | True | 9 | 293 | 0.133 | 12.71 | 2 | 0.3727 | 0.1477 | margin |
| primary | 0.125 | sprt | alpha=0.001, beta=0.01336 | True | 35 | 0 | 0.1427 | 22.2 | 1 | 0.2283 | 0.0928 | margin |
| primary | 0.125 | hmm | rho=0.0001, theta=0.7685 | True | 92 | 0 | 0.1413 | 19.54 | 1 | 0.2732 | 0.1212 | margin |
| sensitivity_1 | 0.5 | threshold | theta=0.1301 | True | 3 | 0 | 0.543 | 1.544 | 0 | 0.3157 | 0.1799 | margin |
| sensitivity_1 | 0.5 | moving_average | k=3, theta=0.3543 | True | 15 | 45 | 0.508 | 3.854 | 1 | 0.2821 | 0.07008 | margin |
| sensitivity_1 | 0.5 | ewma | alpha=0.5, theta=0.3318 | True | 13 | 42 | 0.4814 | 3.387 | 1 | 0.2897 | 0.09848 | margin |
| sensitivity_1 | 0.5 | majority_vote | k=3, theta=0.3318 | True | 19 | 20 | 0.5262 | 4.152 | 1 | 0.2677 | 0.07576 | margin |
| sensitivity_1 | 0.5 | debounce | T=2, theta=0.4013 | True | 7 | 23 | 0.5612 | 5.277 | 1 | 0.2396 | 0.06439 | margin |
| sensitivity_1 | 0.5 | margin | m=0.3, theta=0.31 | True | 10 | 0 | 0.5458 | 3.21 | 0 | 0.2077 | 0.09091 | margin |
| sensitivity_1 | 0.5 | hysteresis | m=0.3, T=2, theta=0.7858 | True | 39 | 22 | 0.5584 | 27.05 | 1 | 0.1099 | 0.01515 | margin |
| sensitivity_1 | 0.5 | trust | r=0.5, tau=0.5, theta=0.7858 | True | 21 | 36 | 0.5374 | 27.92 | 1 | 0.1058 | 0.01515 | margin |
| sensitivity_1 | 0.5 | sprt | alpha=0.01, beta=0.4898 | True | 9 | 0 | 0.5612 | 9.267 | 0 | 0.108 | 0.04167 | margin |
| sensitivity_1 | 0.5 | hmm | rho=0.0001, theta=0.9989 | True | 45 | 0 | 0.5542 | 9.861 | 0 | 0.09618 | 0.04167 | margin |
| sensitivity_2 | 0.04167 | threshold | theta=0.01984 | True | 1 | 0 | 0.04198 | 1.167 | 3.5 | 0.5537 | 0.4394 | margin |
| sensitivity_2 | 0.04167 | moving_average | k=2, theta=0.04743 | True | 11 | 0 | 0.04338 | 2.387 | 2.5 | 0.5419 | 0.3447 | margin |
| sensitivity_2 | 0.04167 | ewma | alpha=0.7, theta=0.06297 | True | 12 | 0 | 0.04338 | 2.774 | 3 | 0.5895 | 0.3333 | margin |
| sensitivity_2 | 0.04167 | majority_vote | k=3, theta=0.06297 | True | 9 | 0 | 0.04758 | 3.618 | 1.5 | 0.4825 | 0.2462 | margin |
| sensitivity_2 | 0.04167 | debounce | T=2, theta=0.07586 | True | 9 | 1 | 0.04338 | 4.581 | 1 | 0.4677 | 0.2386 | margin |
| sensitivity_2 | 0.04167 | margin | m=0.05, theta=0.04743 | True | 1 | 0 | 0.04618 | 2.242 | 2.5 | 0.4806 | 0.3447 | margin |
| sensitivity_2 | 0.04167 | hysteresis | m=0.3, T=2, theta=0.2315 | True | 23 | 14 | 0.04338 | 10.55 | 1 | 0.3998 | 0.214 | margin |
| sensitivity_2 | 0.04167 | trust | r=0.5, tau=0.5, theta=0.2689 | True | 9 | 11 | 0.04478 | 11.28 | 3.5 | 0.5562 | 0.3769 | margin |
| sensitivity_2 | 0.04167 | sprt | alpha=0.001, beta=1.35e-08 | False | 0 | 1 | 0.04898 | 29.86 | 4 | 0.5149 | 0.3409 | margin |
| sensitivity_2 | 0.04167 | hmm | rho=0.1, theta=0.0009111 | False | 0 | 0 | 0.05458 | 1.974 | 3 | 0.5962 | 0.3409 | margin |
