| target_name | target_false_locks_per_hour | mechanism | params_str | in_band | n_in_band_cells | n_excluded_absorbing | val_false_locks_per_hour | val_lockout_mean_frames | val_ania_median | val_far_frame | val_miss_rate | best_smoother |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| primary | 0.125 | threshold | theta=0.04743 | True | 2 | 0 | 0.1338 | 1.087 | 0 | 0.3814 | 0.25 | margin |
| primary | 0.125 | moving_average | k=2, theta=0.1091 | True | 7 | 0 | 0.1396 | 1.875 | 1 | 0.4051 | 0.1641 | margin |
| primary | 0.125 | ewma | alpha=0.7, theta=0.1192 | True | 16 | 0 | 0.128 | 1.955 | 1 | 0.4125 | 0.1562 | margin |
| primary | 0.125 | majority_vote | k=3, theta=0.1192 | True | 10 | 0 | 0.1338 | 2.696 | 1 | 0.3663 | 0.125 | margin |
| primary | 0.125 | debounce | T=2, theta=0.1419 | True | 8 | 1 | 0.1396 | 4 | 1 | 0.3517 | 0.1328 | margin |
| primary | 0.125 | margin | m=0.3, theta=0.1978 | True | 4 | 177 | 0.1106 | 3.421 | 0 | 0.281 | 0.1562 | margin |
| primary | 0.125 | hysteresis | m=0.3, T=2, theta=0.3318 | True | 33 | 520 | 0.1338 | 11.09 | 1 | 0.2799 | 0.1016 | margin |
| primary | 0.125 | trust | r=0.5, tau=0.5, theta=0.4256 | True | 13 | 255 | 0.1338 | 11.3 | 2 | 0.3447 | 0.1016 | margin |
| primary | 0.125 | sprt | alpha=0.05, beta=0.009899 | True | 41 | 0 | 0.1396 | 12.83 | 0 | 0.1434 | 0.04688 | margin |
| primary | 0.125 | hmm | rho=0.0001, theta=0.9427 | True | 101 | 1 | 0.1396 | 14.67 | 1 | 0.215 | 0.04688 | margin |
| sensitivity_1 | 0.5 | threshold | theta=0.1301 | True | 3 | 0 | 0.5178 | 1.449 | 0 | 0.269 | 0.125 | margin |
| sensitivity_1 | 0.5 | moving_average | k=3, theta=0.3775 | True | 16 | 29 | 0.5353 | 3.978 | 1 | 0.2288 | 0.02344 | margin |
| sensitivity_1 | 0.5 | ewma | alpha=0.1, theta=0.7858 | True | 17 | 37 | 0.5702 | 23.99 | 1 | 0.1568 | 0.03906 | margin |
| sensitivity_1 | 0.5 | majority_vote | k=3, theta=0.3543 | True | 20 | 7 | 0.5702 | 4.327 | 1 | 0.2354 | 0.03906 | margin |
| sensitivity_1 | 0.5 | debounce | T=2, theta=0.4013 | True | 7 | 29 | 0.5528 | 5.116 | 1 | 0.2262 | 0.04688 | margin |
| sensitivity_1 | 0.5 | margin | m=0.3, theta=0.31 | True | 9 | 0 | 0.5237 | 3.744 | 0 | 0.1659 | 0.05469 | margin |
| sensitivity_1 | 0.5 | hysteresis | m=0.3, T=2, theta=0.8176 | True | 35 | 14 | 0.5702 | 28.96 | 1 | 0.1089 | 0.007812 | margin |
| sensitivity_1 | 0.5 | trust | r=0.5, tau=0.5, theta=0.7858 | True | 25 | 24 | 0.448 | 29.58 | 1 | 0.1138 | 0.01562 | margin |
| sensitivity_1 | 0.5 | sprt | alpha=0.05, beta=0.3628 | True | 8 | 0 | 0.5644 | 7.021 | 0 | 0.08789 | 0.02344 | margin |
| sensitivity_1 | 0.5 | hmm | rho=0.0001, theta=0.999 | True | 41 | 0 | 0.5353 | 8.011 | 0 | 0.08516 | 0.02344 | margin |
| sensitivity_2 | 0.04167 | threshold | theta=0.0266 | True | 2 | 0 | 0.04655 | 1 | 1.5 | 0.4583 | 0.3516 | margin |
| sensitivity_2 | 0.04167 | moving_average | k=2, theta=0.05215 | True | 6 | 0 | 0.04655 | 1.25 | 1 | 0.4786 | 0.2656 | margin |
| sensitivity_2 | 0.04167 | ewma | alpha=0.7, theta=0.06914 | True | 4 | 0 | 0.04655 | 1.625 | 2 | 0.5385 | 0.25 | margin |
| sensitivity_2 | 0.04167 | majority_vote | k=3, theta=0.06297 | True | 6 | 0 | 0.04655 | 2.375 | 1 | 0.4288 | 0.1641 | margin |
| sensitivity_2 | 0.04167 | debounce | T=2, theta=0.06914 | True | 9 | 5 | 0.04073 | 2.857 | 1 | 0.4241 | 0.1875 | margin |
| sensitivity_2 | 0.04167 | margin | m=0.2, theta=0.1301 | True | 3 | 0 | 0.04655 | 2.875 | 0 | 0.3583 | 0.2188 | margin |
| sensitivity_2 | 0.04167 | hysteresis | m=0.3, T=2, theta=0.2142 | True | 16 | 31 | 0.04073 | 5.714 | 1 | 0.3642 | 0.1719 | margin |
| sensitivity_2 | 0.04167 | trust | r=0.5, tau=0.2, theta=0.31 | True | 6 | 5 | 0.04073 | 11.57 | 5 | 0.6021 | 0.3594 | margin |
| sensitivity_2 | 0.04167 | sprt | alpha=0.01, beta=1.823e-08 | True | 5 | 0 | 0.04655 | 19.25 | 3 | 0.4845 | 0.3203 | margin |
| sensitivity_2 | 0.04167 | hmm | rho=0.0001, theta=0.1545 | False | 0 | 0 | 0.07564 | 17.85 | 2 | 0.3452 | 0.1016 | margin |
