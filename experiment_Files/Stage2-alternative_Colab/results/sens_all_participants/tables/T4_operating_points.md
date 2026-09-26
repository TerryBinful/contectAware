| target_name | target_false_locks_per_hour | mechanism | params_str | in_band | n_in_band_cells | n_excluded_absorbing | val_false_locks_per_hour | val_lockout_mean_frames | val_ania_median | val_far_frame | val_miss_rate | best_smoother |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| primary | 0.125 | threshold | theta=0.04743 | True | 3 | 0 | 0.1426 | 1.309 | 0 | 0.2763 | 0.1652 | margin |
| primary | 0.125 | moving_average | k=2, theta=0.1192 | True | 17 | 0 | 0.1382 | 2.413 | 1 | 0.3025 | 0.1261 | margin |
| primary | 0.125 | ewma | alpha=0.7, theta=0.1301 | True | 18 | 0 | 0.1365 | 2.367 | 1 | 0.3056 | 0.1161 | margin |
| primary | 0.125 | majority_vote | k=3, theta=0.1545 | True | 16 | 0 | 0.1426 | 3.915 | 1 | 0.2643 | 0.0971 | margin |
| primary | 0.125 | debounce | T=2, theta=0.1824 | True | 10 | 6 | 0.1331 | 4.903 | 1 | 0.2526 | 0.09152 | margin |
| primary | 0.125 | margin | m=0.3, theta=0.1978 | True | 7 | 0 | 0.1175 | 3.316 | 0 | 0.2063 | 0.1194 | margin |
| primary | 0.125 | hysteresis | m=0.3, T=2, theta=0.4013 | True | 34 | 196 | 0.1417 | 9.854 | 1 | 0.203 | 0.06138 | margin |
| primary | 0.125 | trust | r=0.5, tau=0.5, theta=0.5 | True | 8 | 148 | 0.1305 | 13.69 | 2 | 0.2883 | 0.06585 | margin |
| primary | 0.125 | sprt | alpha=0.05, beta=0.005431 | True | 19 | 0 | 0.1391 | 11.46 | 0 | 0.128 | 0.05692 | margin |
| primary | 0.125 | hmm | rho=0.0001, theta=0.9608 | True | 86 | 0 | 0.1417 | 13.12 | 1 | 0.1925 | 0.0625 | margin |
| sensitivity_1 | 0.5 | threshold | theta=0.168 | True | 3 | 0 | 0.5409 | 1.674 | 0 | 0.157 | 0.08482 | margin |
| sensitivity_1 | 0.5 | moving_average | k=3, theta=0.475 | True | 20 | 2 | 0.527 | 4.487 | 1 | 0.1711 | 0.03237 | margin |
| sensitivity_1 | 0.5 | ewma | alpha=0.7, theta=0.3318 | True | 14 | 53 | 0.5521 | 2.714 | 0 | 0.1234 | 0.05804 | margin |
| sensitivity_1 | 0.5 | majority_vote | k=3, theta=0.4502 | True | 24 | 0 | 0.5314 | 4.512 | 1 | 0.1787 | 0.03683 | margin |
| sensitivity_1 | 0.5 | debounce | T=2, theta=0.5498 | True | 11 | 23 | 0.5478 | 6.049 | 1 | 0.1637 | 0.02902 | margin |
| sensitivity_1 | 0.5 | margin | m=0.3, theta=0.3543 | True | 9 | 0 | 0.5348 | 3.105 | 0 | 0.1024 | 0.05915 | margin |
| sensitivity_1 | 0.5 | hysteresis | m=0.2, T=2, theta=0.8699 | True | 30 | 12 | 0.4778 | 28.03 | 1 | 0.1073 | 0.01116 | margin |
| sensitivity_1 | 0.5 | trust | r=0.5, tau=0.5, theta=0.8176 | False | 0 | 0 | 0.394 | 27.05 | 1 | 0.1164 | 0.01562 | margin |
| sensitivity_1 | 0.5 | sprt | alpha=0.01, beta=0.4898 | True | 6 | 0 | 0.4683 | 6.546 | 0 | 0.06423 | 0.03571 | margin |
| sensitivity_1 | 0.5 | hmm | rho=0.001, theta=0.995 | True | 30 | 1 | 0.5737 | 5.941 | 0 | 0.05508 | 0.02679 | margin |
| sensitivity_2 | 0.04167 | threshold | theta=0.02413 | True | 4 | 0 | 0.04666 | 1.278 | 0.25 | 0.3568 | 0.2422 | margin |
| sensitivity_2 | 0.04167 | moving_average | k=2, theta=0.05215 | True | 13 | 0 | 0.04406 | 1.98 | 1 | 0.3775 | 0.1864 | margin |
| sensitivity_2 | 0.04167 | ewma | alpha=0.7, theta=0.06914 | True | 14 | 0 | 0.04752 | 2.055 | 2 | 0.4388 | 0.1763 | margin |
| sensitivity_2 | 0.04167 | majority_vote | k=3, theta=0.05732 | True | 11 | 0 | 0.04406 | 2.804 | 1 | 0.348 | 0.154 | margin |
| sensitivity_2 | 0.04167 | debounce | T=2, theta=0.07586 | True | 10 | 1 | 0.04493 | 4.058 | 1 | 0.3259 | 0.1395 | margin |
| sensitivity_2 | 0.04167 | margin | m=0.1, theta=0.07586 | True | 4 | 0 | 0.04579 | 2.264 | 0 | 0.2855 | 0.1741 | margin |
| sensitivity_2 | 0.04167 | hysteresis | m=0.3, T=2, theta=0.2315 | True | 38 | 13 | 0.04147 | 9.125 | 1 | 0.2821 | 0.1261 | margin |
| sensitivity_2 | 0.04167 | trust | r=0.5, tau=0.5, theta=0.2891 | True | 19 | 17 | 0.04147 | 11.94 | 3 | 0.4561 | 0.3103 | margin |
| sensitivity_2 | 0.04167 | sprt | alpha=0.01, beta=1.217e-06 | True | 74 | 0 | 0.04752 | 21.78 | 2 | 0.349 | 0.1429 | margin |
| sensitivity_2 | 0.04167 | hmm | rho=0.1, theta=0.0009111 | False | 0 | 0 | 0.05962 | 1.58 | 1 | 0.3753 | 0.1842 | margin |
