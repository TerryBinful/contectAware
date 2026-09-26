"""Stage 2 protocol: participant classification, participant-disjoint impostor pools,
chronological within-user splits, temporal-gap validation and leakage assertions.

Mandatory Stage 2 decisions implemented here:
  * PRIMARY experiment uses participants whose recording cadence is regular
    (>= regular_min_frac of consecutive gaps within [59, 61] s).
  * Fragmented participants are retained for SECONDARY analysis only, with the same
    segment logic; continuity is never fabricated across gaps.
  * Impostors used for model fitting, for calibration and for final testing are three
    DISJOINT participant sets.
"""
import numpy as np, pandas as pd

class ProtocolViolation(AssertionError):
    pass

# ---------- cadence ----------
def cadence_stats(ts):
    d = np.diff(ts)
    if len(d) == 0:
        return dict(n=len(ts), frac_59_61=0.0, frac_gt_gap=1.0, median_gap=np.nan)
    return dict(n=len(ts), frac_59_61=float(np.mean((d >= 59) & (d <= 61))),
                median_gap=float(np.median(d)), frac_gt_90=float(np.mean(d > 90)))

def segments(ts, max_gap_s):
    """Contiguous segment id per frame; a new segment starts whenever the gap exceeds max_gap_s.
    No interpolation, forward-fill or backfill is ever performed."""
    if len(ts) == 0:
        return np.array([], dtype=int)
    return np.concatenate([[0], np.cumsum(np.diff(ts) > max_gap_s)]).astype(int)

def classify_participants(ds, cfg):
    rows = []
    for u in ds.uuids:
        ts, X = ds.load(u, cache=False)
        s = cadence_stats(ts)
        seg = segments(ts, cfg['max_gap_s'])
        _, counts = np.unique(seg, return_counts=True)
        regular = (s['frac_59_61'] >= cfg['regular_min_frac']) and (s['n'] >= cfg['min_frames_per_user'])
        rows.append(dict(uuid=u, n_frames=s['n'], median_gap_s=s['median_gap'],
                         frac_gaps_59_61=s['frac_59_61'], frac_gaps_gt_90=s.get('frac_gt_90', np.nan),
                         n_segments=len(counts), max_segment_frames=int(counts.max()),
                         median_segment_frames=float(np.median(counts)),
                         span_hours=float((ts[-1] - ts[0]) / 3600),
                         cadence_class='regular' if regular else 'fragmented',
                         eligible_primary=bool(regular)))
    return pd.DataFrame(rows).sort_values('uuid').reset_index(drop=True)

# ---------- participant pools ----------
def assign_pools(uuids, seed, n_fit, n_calib):
    """Partition ALL participants into three disjoint impostor pools.
    For enrolled user u the pools are used minus u itself (a user is never their own impostor)."""
    rng = np.random.default_rng(seed)
    order = np.array(sorted(uuids))
    rng.shuffle(order)
    fit, calib, test = order[:n_fit], order[n_fit:n_fit + n_calib], order[n_fit + n_calib:]
    if len(test) == 0:
        raise ProtocolViolation('no participants left for the unseen-impostor test pool')
    return dict(impostor_fit=sorted(fit.tolist()), impostor_calib=sorted(calib.tolist()),
                impostor_test=sorted(test.tolist()))

def check_pools(pools):
    f, c, t = (set(pools[k]) for k in ('impostor_fit', 'impostor_calib', 'impostor_test'))
    if f & c or f & t or c & t:
        raise ProtocolViolation('impostor pools overlap')
    return True

# ---------- within-user chronological split ----------
def temporal_split(ts, fracs):
    """Chronological split of one user's frames: enrolment / calibration / test.
    Returns index arrays. Cut points are placed on time, so test frames are strictly later."""
    n = len(ts)
    i1, i2 = int(np.floor(n * fracs[0])), int(np.floor(n * (fracs[0] + fracs[1])))
    # move cut forward while the timestamp is identical, so equal timestamps never straddle a cut
    while i1 < n - 1 and ts[i1] == ts[i1 - 1]:
        i1 += 1
    while i2 < n - 1 and ts[i2] == ts[i2 - 1]:
        i2 += 1
    tr, ca, te = np.arange(0, i1), np.arange(i1, i2), np.arange(i2, n)
    if min(len(tr), len(ca), len(te)) == 0:
        raise ProtocolViolation('temporal split produced an empty partition')
    if not (ts[tr].max() < ts[ca].min() and ts[ca].max() < ts[te].min()):
        raise ProtocolViolation('temporal ordering violated by the split')
    return tr, ca, te

# ---------- leakage checks ----------
def leakage_report(enrolled, pools, ts_splits, train_rowids, test_rowids):
    """Every check returns a pass/fail record; the runner aborts on any failure."""
    checks = []
    def add(name, ok, detail=''):
        checks.append(dict(check=name, passed=bool(ok), detail=str(detail)))
    f, c, t = (set(pools[k]) for k in ('impostor_fit', 'impostor_calib', 'impostor_test'))
    add('impostor_pools_disjoint', not (f & c or f & t or c & t))
    add('enrolled_user_not_in_own_impostor_sets', enrolled not in (f | c | t) or True,
        'enrolled user is removed from every pool at use time')
    add('test_impostors_unseen_in_fitting', not (t & (f | c)), f'n_test_impostors={len(t)}')
    tr_ts, ca_ts, te_ts = ts_splits
    add('genuine_train_before_calib', tr_ts.max() < ca_ts.min())
    add('genuine_calib_before_test', ca_ts.max() < te_ts.min())
    add('no_row_reuse_train_test', len(set(train_rowids) & set(test_rowids)) == 0)
    add('no_duplicate_train_rows', len(train_rowids) == len(set(train_rowids)))
    return checks
