| target_name | target_false_locks_per_hour | mechanism | params_str | in_band | n_in_band_cells | n_excluded_absorbing | val_false_locks_per_hour | val_lockout_mean_frames | val_ania_median | val_far_frame | val_miss_rate | best_smoother |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| primary | 0.125 | threshold | theta=0.04311 | True | 2 | 0 | 0.1204 | 1.419 | 0 | 0.3532 | 0.2595 | margin |
| primary | 0.125 | moving_average | k=2, theta=0.07586 | True | 11 | 0 | 0.119 | 2.153 | 1 | 0.3815 | 0.2121 | margin |
| primary | 0.125 | ewma | alpha=0.7, theta=0.09112 | True | 15 | 0 | 0.1288 | 2.304 | 2 | 0.4214 | 0.2102 | margin |
| primary | 0.125 | majority_vote | k=3, theta=0.09975 | True | 11 | 0 | 0.1316 | 3.617 | 1 | 0.3439 | 0.1761 | margin |
| primary | 0.125 | debounce | T=2, theta=0.1301 | True | 14 | 11 | 0.1427 | 4.735 | 1 | 0.3199 | 0.161 | margin |
| primary | 0.125 | margin | m=0.3, theta=0.1978 | True | 2 | 177 | 0.1204 | 3.965 | 0 | 0.2401 | 0.1648 | margin |
| primary | 0.125 | hysteresis | m=0.3, T=2, theta=0.31 | True | 27 | 304 | 0.133 | 10.72 | 1 | 0.2648 | 0.1193 | margin |
| primary | 0.125 | trust | r=0.5, tau=0.5, theta=0.4013 | True | 10 | 216 | 0.1385 | 15.85 | 2 | 0.3416 | 0.1193 | margin |
| primary | 0.125 | sprt | alpha=0.001, beta=0.02436 | True | 55 | 0 | 0.1357 | 26.61 | 1 | 0.1491 | 0.06629 | margin |
| primary | 0.125 | hmm | rho=0.0001, theta=0.5744 | True | 101 | 0 | 0.1385 | 22.83 | 1 | 0.2336 | 0.09659 | margin |
| sensitivity_1 | 0.5 | threshold | theta=0.1301 | True | 3 | 0 | 0.543 | 1.74 | 0 | 0.2259 | 0.1553 | margin |
| sensitivity_1 | 0.5 | moving_average | k=10, theta=0.8699 | True | 22 | 33 | 0.5542 | 24.28 | 1 | 0.08226 | 0 | margin |
| sensitivity_1 | 0.5 | ewma | alpha=0.1, theta=0.8699 | True | 24 | 36 | 0.4968 | 28.8 | 1 | 0.07711 | 0 | margin |
| sensitivity_1 | 0.5 | majority_vote | k=3, theta=0.4256 | True | 43 | 20 | 0.5668 | 6.057 | 1 | 0.1835 | 0.03409 | margin |
| sensitivity_1 | 0.5 | debounce | T=2, theta=0.5498 | True | 18 | 2 | 0.5654 | 8.502 | 1 | 0.1581 | 0.0303 | margin |
| sensitivity_1 | 0.5 | margin | m=0.3, theta=0.3543 | True | 12 | 1 | 0.55 | 4.527 | 0 | 0.1162 | 0.05492 | margin |
| sensitivity_1 | 0.5 | hysteresis | m=0.1, T=2, theta=0.9241 | True | 36 | 5 | 0.5122 | 28.69 | 1 | 0.09328 | 0.003788 | margin |
| sensitivity_1 | 0.5 | trust | r=0.5, tau=0.2, theta=0.8808 | False | 0 | 0 | 0.3807 | 29.95 | 1 | 0.1205 | 0.01515 | margin |
| sensitivity_1 | 0.5 | sprt | alpha=0.05, beta=0.4898 | True | 4 | 0 | 0.5206 | 9.495 | 0 | 0.06307 | 0.02462 | margin |
| sensitivity_1 | 0.5 | hmm | rho=0.001, theta=0.9955 | True | 44 | 0 | 0.564 | 10.41 | 0 | 0.04435 | 0.02273 | margin |
| sensitivity_2 | 0.04167 | threshold | theta=0.02188 | True | 3 | 0 | 0.04758 | 1.353 | 0 | 0.4505 | 0.3561 | margin |
| sensitivity_2 | 0.04167 | moving_average | k=2, theta=0.04311 | True | 8 | 0 | 0.03919 | 1.964 | 1 | 0.454 | 0.2727 | margin |
| sensitivity_2 | 0.04167 | ewma | alpha=0.7, theta=0.05732 | True | 13 | 0 | 0.04478 | 2.312 | 2 | 0.5039 | 0.25 | margin |
| sensitivity_2 | 0.04167 | majority_vote | k=3, theta=0.05215 | True | 8 | 0 | 0.04338 | 2.968 | 1 | 0.4075 | 0.214 | margin |
| sensitivity_2 | 0.04167 | debounce | T=2, theta=0.05732 | True | 8 | 1 | 0.03779 | 4.074 | 1 | 0.4015 | 0.2216 | margin |
| sensitivity_2 | 0.04167 | margin | m=0.05, theta=0.04743 | True | 3 | 0 | 0.04618 | 1.848 | 0 | 0.3798 | 0.2765 | margin |
| sensitivity_2 | 0.04167 | hysteresis | m=0.3, T=2, theta=0.2142 | True | 21 | 15 | 0.04478 | 8.469 | 1 | 0.3384 | 0.2027 | margin |
| sensitivity_2 | 0.04167 | trust | r=0.5, tau=0.5, theta=0.2497 | True | 9 | 11 | 0.03919 | 13.14 | 4 | 0.5267 | 0.3598 | margin |
| sensitivity_2 | 0.04167 | sprt | alpha=0.05, beta=7.37e-06 | False | 0 | 0 | 0.08257 | 29.92 | 2 | 0.3355 | 0.1288 | margin |
| sensitivity_2 | 0.04167 | hmm | rho=0.1, theta=0.0009111 | False | 0 | 0 | 0.07277 | 1.635 | 2 | 0.4982 | 0.2576 | margin |
