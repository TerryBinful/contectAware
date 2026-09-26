"""Stage 2 feature-set definitions and mandatory ablation groups (prefix-based, auditable)."""
import numpy as np

FAMILIES = {
    'phone_motion': ('raw_acc:', 'proc_gyro:', 'raw_magnet:'),
    'watch':        ('watch_acceleration:', 'watch_heading:'),
    'location':     ('location:', 'location_quick_features:'),
    'audio':        ('audio_naive:', 'audio_properties:'),
    'device_state': ('discrete:',),
    'lf_ambient':   ('lf_measurements:',),
}

FEATURE_SETS = {
    'F1_ALL': dict(families=list(FAMILIES), missingness_only=False,
        note='all 225 features; location and device-state INCLUDED per Stage 2 decision'),
    'F2_STAGE1_COMPARABLE': dict(families=['phone_motion_accgyro', 'location', 'device_state'], missingness_only=False,
        note='closest analogue of the Stage 1 pool (acc+gyro+location+discrete), for comparability'),
    'F3_NO_LOC_NO_DEVSTATE': dict(families=['phone_motion', 'audio', 'lf_ambient'], missingness_only=False,
        note='ablation: motion/ambient sensing only; no location, no device state, no watch'),
    'F4_LOCATION_ONLY': dict(families=['location'], missingness_only=False,
        note='diagnostic: identity information carried by location alone'),
    'F5_DEVICE_STATE_ONLY': dict(families=['device_state'], missingness_only=False,
        note='diagnostic: identity information carried by device/OS state alone'),
    'F6_MISSINGNESS_ONLY': dict(families=list(FAMILIES), missingness_only=True,
        note='diagnostic: binary NaN indicators only; tests the Stage 1 data-availability shortcut'),
    'F7_F3_MISSINGNESS_ONLY': dict(families=['phone_motion', 'audio', 'lf_ambient'], missingness_only=True,
        note='construct-validity probe: missingness indicators of the F3 columns ONLY. Bounds how much '
             'of the primary score is data availability rather than behaviour. No decision layer is run on it.'),
}

def resolve(feature_cols, set_name):
    spec = FEATURE_SETS[set_name]
    pref = []
    for fam in spec['families']:
        pref += ['raw_acc:', 'proc_gyro:'] if fam == 'phone_motion_accgyro' else list(FAMILIES[fam])
    idx = [i for i, c in enumerate(feature_cols) if any(c.startswith(p) for p in pref)]
    if not idx:
        raise ValueError(f'feature set {set_name} resolved to 0 columns')
    return np.array(idx, dtype=int), [feature_cols[i] for i in idx]

def materialise(X, idx, missingness_only):
    S = X[:, idx]
    return np.isnan(S).astype(np.float32) if missingness_only else S
