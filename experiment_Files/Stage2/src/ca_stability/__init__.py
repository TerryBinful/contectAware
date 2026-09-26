"""ca_stability — Stage 2 decision-layer stabilisation comparison for continuous authentication.

Pipeline:  ExtraSensory frames -> fixed per-user score generator -> common calibrated score
stream -> identity-transition benchmark -> nine decision-layer mechanisms (+1 supplementary)
-> matched operating point (validation) -> frozen parameters -> test evaluation -> statistics.
"""
__version__ = "2.0.0"
