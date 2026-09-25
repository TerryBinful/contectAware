"""
Exp 4 - Feature-group ablation: is the authentication signal behavioural, or is it
place, device and data-availability?

WHY THIS EXISTS
---------------
`AUTHENTICATION_VALIDITY_AUDIT.md` section 3 established that in the original pipeline
location-prefixed features carried ~40% of Gini importance, that `location:min_altitude`
and `location:max_altitude` alone carried 26.1%, and that the target participant's 0%
altitude-missingness acted as a shortcut which rejected 43.8% of impostor rows for free
(FAR 0.00% on altitude-missing rows vs 0.94% where altitude was present; 100% of false
accepts fell on altitude-present rows). Section 3.4 of that audit names the question
"how much performance survives without location and missingness cues" as the single most
important unresolved item for criterion C4, and did not run it. This script runs it.

WHY IT DOES NOT REUSE THE ORIGINAL PROTOCOL
-------------------------------------------
Running this ablation under the original evaluation protocol would be worse than not
running it, because it would produce a falsely reassuring answer. The original used a
random row-level split on series sampled at ~60 s, so 93.3% of target test rows had a
same-user training row within 90 s. Adjacent frames are near-duplicates, so under that
protocol *any* sufficiently expressive feature set - motion included - can score well by
memorising near-neighbours. A motion-only arm would then look strong for reasons that
have nothing to do with behavioural discriminability, and the ablation would appear to
exonerate the pipeline.

This script therefore evaluates every arm under a protocol that removes the three
confounds the audit identified, so that differences between arms are attributable to
feature content:

  1. Chronological genuine split (train on the participant's earlier data, test on their
     later data) with a temporal embargo across the boundary - addresses C1.
  2. Subject-disjoint impostors: impostor users appearing in test never appear in
     training - addresses C2.
  3. More than one genuine user: the ablation is repeated per target participant and
     analysed with the user as the unit of analysis - addresses C3.
  4. Imputer and scaler fitted on the training partition only - addresses the C11 leak
     recorded in the audit (the original fitted both on all 377,346 rows before
     splitting).

Consequently the absolute numbers here are NOT comparable to the original's 0.9926
accuracy or 0.53% FAR, and are not intended to be. They will be worse, and that is the
point: they are the first numbers in this project measured under a protocol where being
worse is meaningful. Only the *relative* comparison between feature sets is the result.

ARMS
----
  all              raw_acc + proc_gyro + location(+_quick_features) + discrete (original set)
  no_location      all minus every location-prefixed feature
  motion_only      raw_acc + proc_gyro only (the strongest claim to being behavioural)
  location_only    location-prefixed features only
  discrete_only    discrete phone-state features only (battery, wifi, call state)
  missingness_only binary "was this feature NaN" indicators, values discarded entirely

`missingness_only` is the direct probe for the shortcut channel. It contains no sensor
readings at all - only which sensors reported. If it authenticates well above chance, the
model can identify a participant purely from their device's data-availability pattern,
which is a property of hardware and app behaviour rather than of the person.
`location_only` is the complementary probe: if it approaches `all`, the pipeline is a
place detector.

READING THE RESULT
------------------
Primary metric is subject-independent EER computed threshold-free from the ROC, reported
per target participant, compared across arms by paired Wilcoxon signed-rank with the user
as the unit of analysis (never the frame - frames are autocorrelated).

  - `motion_only` EER stays reasonable and near `all`  -> the signal is substantially
    behavioural; the pivot proceeds on this dataset as planned.
  - `motion_only` degrades markedly but stays well below chance -> a motion-only score
    stream is still usable, but the thesis must narrow its scope accordingly and say so.
  - `motion_only` approaches chance (EER ~0.5) while `location_only` or
    `missingness_only` do not -> there is no behavioural authentication signal here to
    stabilise, and the decision-layer comparison needs a different dataset. This is the
    outcome that must be known before further work, not after.

No threshold in this script decides which of those holds. It reports the numbers; the
interpretation belongs in the write-up.

USAGE
    python exp4_feature_ablation.py <csv_dir> [--targets N] [--model hgb|gb|lr]
                                    [--train-frac F] [--embargo-min M] [--out DIR]
                                    [--rf-select] [--max-impostor-rows N] [--seed S]
    python exp4_feature_ablation.py --self-test     # synthetic data, no real dataset needed

Outputs <out>/exp4_ablation_results.json and <out>/exp4_ablation_per_user.csv.
"""
import argparse
import glob
import json
import os
import sys
import time

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.preprocessing import RobustScaler

# Prefixes as matched by the original pipeline. Note that 'location' also captures
# 'location_quick_features', which is how the original arrived at 13 location-prefixed
# features among its 52 selected (9 + 4).
SENSOR_PREFIXES = ['raw_acc', 'proc_gyro', 'location', 'discrete']
LOCATION_PREFIXES = ('location',)          # covers location: and location_quick_features:
MOTION_PREFIXES = ('raw_acc', 'proc_gyro')
DISCRETE_PREFIXES = ('discrete',)

ARMS = ['all', 'no_location', 'motion_only', 'location_only', 'discrete_only',
        'missingness_only']


def log(*a):
    print(*a, flush=True)


# ----------------------------------------------------------------------------- metrics
def eer_from_roc(y_true, scores):
    """Threshold-free EER. Returns (eer, threshold_at_eer)."""
    if len(np.unique(y_true)) < 2:
        return float('nan'), float('nan')
    fpr, tpr, thr = roc_curve(y_true, scores)
    fnr = 1.0 - tpr
    i = int(np.nanargmin(np.abs(fnr - fpr)))
    return float((fpr[i] + fnr[i]) / 2.0), float(thr[i])


def far_frr_at(y_true, scores, threshold):
    pred = (scores >= threshold).astype(int)
    imp = y_true == 0
    gen = y_true == 1
    far = float(pred[imp].mean()) if imp.any() else float('nan')
    frr = float(1.0 - pred[gen].mean()) if gen.any() else float('nan')
    return far, frr


# ------------------------------------------------------------------------ data loading
def load_dataset(csv_dir):
    """Load the sensor columns the original pipeline used, preserving NaNs.

    NaNs are deliberately NOT imputed here: the missingness pattern is itself one of the
    signals under test, so it must survive until each arm decides what to do with it.
    """
    files = sorted(glob.glob(os.path.join(csv_dir, '*.csv')))
    if not files:
        sys.exit(f'No CSV files found in {csv_dir}')
    cols = pd.read_csv(files[0], nrows=0).columns.tolist()
    feature_cols = [c for c in cols
                    if not c.startswith('label:') and c not in ('timestamp', 'label_source')]
    selected = [c for c in feature_cols if any(c.startswith(p) for p in SENSOR_PREFIXES)]
    frames = []
    for f in files:
        d = pd.read_csv(f, usecols=['timestamp'] + selected)
        d[selected] = d[selected].astype(np.float32)
        d['user_id'] = os.path.basename(f).split('_')[0]
        frames.append(d)
    df = pd.concat(frames, ignore_index=True)
    del frames
    log(f'Loaded {len(files)} users, {len(df):,} rows, {len(selected)} sensor features')
    return df, selected


def arm_columns(arm, selected):
    if arm == 'all':
        return list(selected)
    if arm == 'no_location':
        return [c for c in selected if not c.startswith(LOCATION_PREFIXES)]
    if arm == 'motion_only':
        return [c for c in selected if c.startswith(MOTION_PREFIXES)]
    if arm == 'location_only':
        return [c for c in selected if c.startswith(LOCATION_PREFIXES)]
    if arm == 'discrete_only':
        return [c for c in selected if c.startswith(DISCRETE_PREFIXES)]
    if arm == 'missingness_only':
        return list(selected)          # values replaced by NaN-indicators downstream
    raise ValueError(arm)


# -------------------------------------------------------------------------------- model
def build_model(kind, seed):
    if kind == 'hgb':
        from sklearn.ensemble import HistGradientBoostingClassifier
        # Chosen for tractability: 6 arms x N target users means many fits. Comparable in
        # capacity to the original's GradientBoostingClassifier but far faster.
        return HistGradientBoostingClassifier(
            max_iter=200, learning_rate=0.1, max_depth=6, min_samples_leaf=50,
            l2_regularization=1.0, class_weight='balanced', random_state=seed)
    if kind == 'gb':
        from sklearn.ensemble import GradientBoostingClassifier
        # Original Stage 1 hyperparameters, for continuity. No class_weight support, so
        # imbalance is handled by sample weights below.
        return GradientBoostingClassifier(
            n_estimators=200, learning_rate=0.1, max_depth=6, min_samples_split=100,
            min_samples_leaf=50, subsample=0.8, max_features='sqrt', random_state=seed)
    if kind == 'lr':
        return LogisticRegression(C=1.0, penalty='l2', solver='lbfgs', max_iter=1000,
                                  class_weight='balanced', random_state=seed)
    raise ValueError(kind)


def fit_predict(kind, seed, Xtr, ytr, Xte):
    m = build_model(kind, seed)
    if kind == 'gb':
        # Emulate class_weight='balanced' for the estimator that lacks it.
        n = len(ytr)
        pos = max(int(ytr.sum()), 1)
        neg = max(n - pos, 1)
        w = np.where(ytr == 1, n / (2.0 * pos), n / (2.0 * neg))
        m.fit(Xtr, ytr, sample_weight=w)
    else:
        m.fit(Xtr, ytr)
    return m.predict_proba(Xte)[:, 1]


# ------------------------------------------------------------------------------ one run
def run_one(df, selected, target, arm, args, rng):
    """One (target participant, arm) evaluation under the corrected protocol."""
    tgt = df[df.user_id == target].sort_values('timestamp')
    others = sorted(df.user_id.unique().tolist())
    others.remove(target)

    # --- subject-disjoint impostor partition (C2) -----------------------------------
    perm = rng.permutation(len(others))
    shuffled = [others[i] for i in perm]
    half = len(shuffled) // 2
    imp_train_users, imp_test_users = set(shuffled[:half]), set(shuffled[half:])

    # --- chronological genuine split with embargo (C1) -------------------------------
    ts = tgt.timestamp.values
    cut = np.quantile(ts, args.train_frac)
    embargo = args.embargo_min * 60.0
    g_tr = tgt[tgt.timestamp <= cut]
    g_te = tgt[tgt.timestamp > cut + embargo]
    if len(g_tr) < 200 or len(g_te) < 200:
        return None

    imp_tr = df[df.user_id.isin(imp_train_users)]
    imp_te = df[df.user_id.isin(imp_test_users)]
    if args.max_impostor_rows:
        # Subsample impostors for tractability only; genuine rows are never subsampled.
        for name, frame in (('tr', imp_tr), ('te', imp_te)):
            if len(frame) > args.max_impostor_rows:
                idx = rng.choice(len(frame), args.max_impostor_rows, replace=False)
                if name == 'tr':
                    imp_tr = frame.iloc[np.sort(idx)]
                else:
                    imp_te = frame.iloc[np.sort(idx)]

    cols = arm_columns(arm, selected)
    if not cols:
        return None

    def matrix(frame):
        block = frame[cols]
        if arm == 'missingness_only':
            # Discard every sensor value; keep only whether it was reported.
            return block.isna().to_numpy(dtype=np.float32)
        return block.to_numpy(dtype=np.float32)

    Xtr = np.vstack([matrix(g_tr), matrix(imp_tr)])
    ytr = np.concatenate([np.ones(len(g_tr), int), np.zeros(len(imp_tr), int)])
    Xte = np.vstack([matrix(g_te), matrix(imp_te)])
    yte = np.concatenate([np.ones(len(g_te), int), np.zeros(len(imp_te), int)])

    # --- preprocessing fitted on train only (C11) ------------------------------------
    if arm != 'missingness_only':
        keep = ~np.all(np.isnan(Xtr), axis=0)      # columns entirely NaN in train
        Xtr, Xte = Xtr[:, keep], Xte[:, keep]
        if Xtr.shape[1] == 0:
            return None
        imp = SimpleImputer(strategy='median').fit(Xtr)
        sc = RobustScaler().fit(imp.transform(Xtr))
        Xtr = sc.transform(imp.transform(Xtr))
        Xte = sc.transform(imp.transform(Xte))

    if args.rf_select:
        from sklearn.ensemble import RandomForestClassifier
        rf = RandomForestClassifier(n_estimators=100, max_depth=10, n_jobs=-1,
                                    random_state=args.seed).fit(Xtr, ytr)
        order = np.argsort(rf.feature_importances_)[::-1]
        k = int((np.cumsum(rf.feature_importances_[order]) >= 0.95).argmax() + 1)
        sel = order[:k]
        Xtr, Xte = Xtr[:, sel], Xte[:, sel]

    scores = fit_predict(args.model, args.seed, Xtr, ytr, Xte)
    eer, thr = eer_from_roc(yte, scores)
    auc = float(roc_auc_score(yte, scores)) if len(np.unique(yte)) > 1 else float('nan')
    far05, frr05 = far_frr_at(yte, scores, 0.5)

    # --- protocol diagnostics: confirm the confounds are actually gone ---------------
    tr_ts = g_tr.timestamp.values
    te_ts = g_te.timestamp.values
    pos = np.searchsorted(tr_ts, te_ts)
    prev_gap = np.where(pos > 0, te_ts - tr_ts[np.clip(pos - 1, 0, len(tr_ts) - 1)], np.inf)
    adjacent = float(np.mean(prev_gap <= 90.0))

    return {
        'target_user': target,
        'arm': arm,
        'n_features_used': int(Xtr.shape[1]),
        'eer': eer,
        'eer_threshold': thr,
        'auc': auc,
        'far_at_0.5': far05,
        'frr_at_0.5': frr05,
        'n_genuine_train': int(len(g_tr)),
        'n_genuine_test': int(len(g_te)),
        'n_impostor_train': int(len(imp_tr)),
        'n_impostor_test': int(len(imp_te)),
        'n_impostor_users_train': len(imp_train_users),
        'n_impostor_users_test': len(imp_test_users),
        'impostor_users_overlap': len(imp_train_users & imp_test_users),   # must be 0
        'genuine_test_rows_within_90s_of_train': adjacent,                 # want ~0
        'mean_missing_frac_train': (float(np.isnan(matrix(g_tr)).mean())
                                    if arm != 'missingness_only' else None),
    }


# --------------------------------------------------------------------------- statistics
def paired_stats(per_user, baseline='all'):
    """Paired comparison across target participants. Unit of analysis is the user."""
    from scipy.stats import wilcoxon
    tbl = per_user.pivot_table(index='target_user', columns='arm', values='eer')
    out = {}
    if baseline not in tbl:
        return out
    for arm in tbl.columns:
        if arm == baseline:
            continue
        pair = tbl[[baseline, arm]].dropna()
        if len(pair) < 3:
            out[arm] = {'n_users': int(len(pair)), 'note': 'too few users for a test'}
            continue
        d = pair[arm] - pair[baseline]
        rec = {
            'n_users': int(len(pair)),
            f'median_eer_{baseline}': float(pair[baseline].median()),
            f'median_eer_{arm}': float(pair[arm].median()),
            'median_eer_delta': float(d.median()),
            'users_worse_without': int((d > 0).sum()),
        }
        if np.any(d != 0):
            try:
                st, p = wilcoxon(pair[arm], pair[baseline])
                rec['wilcoxon_stat'], rec['wilcoxon_p'] = float(st), float(p)
            except ValueError as e:
                rec['wilcoxon_error'] = str(e)
        else:
            rec['wilcoxon_note'] = 'all differences zero'
        out[arm] = rec
    return out


# --------------------------------------------------------------------------- self-test
def make_synthetic(path, n_users=12, n_rows=1500, seed=0):
    """Synthetic ExtraSensory-shaped data, for validating the script without the dataset.

    Built so the arms are distinguishable by construction: location features separate
    users strongly, motion features weakly, and altitude missingness is user-specific -
    which is the pattern the real audit reported. A correct implementation should show
    location_only close to all, motion_only clearly worse but better than chance, and
    missingness_only informative. This validates the code path, not the real dataset.
    """
    rng = np.random.default_rng(seed)
    os.makedirs(path, exist_ok=True)
    cols = ([f'raw_acc:magnitude_stats:f{i}' for i in range(15)]
            + [f'proc_gyro:magnitude_stats:f{i}' for i in range(19)]
            + ['location:min_altitude', 'location:max_altitude']
            + [f'location:f{i}' for i in range(7)]
            + [f'location_quick_features:f{i}' for i in range(4)]
            + [f'discrete:battery:f{i}' for i in range(5)])
    for u in range(n_users):
        uid = f'USER{u:03d}'
        t0 = 1400000000 + u * 10_000_000
        ts = t0 + np.arange(n_rows) * 60
        d = {'timestamp': ts}
        for c in cols:
            if c.startswith(('location', 'location_quick')):
                centre = rng.normal(u * 3.0, 0.3)      # strong per-user separation
                v = rng.normal(centre, 1.0, n_rows)
            elif c.startswith(('raw_acc', 'proc_gyro')):
                centre = rng.normal(u * 0.25, 0.1)     # weak per-user separation
                v = rng.normal(centre, 1.0, n_rows)
            else:
                v = rng.normal(0, 1, n_rows)
            miss = 0.0 if u % 3 == 0 else rng.uniform(0.2, 0.7)
            if c.startswith('location') and miss > 0:
                v[rng.random(n_rows) < miss] = np.nan
            d[c] = v.astype(np.float32)
        d['label:SITTING'] = rng.integers(0, 2, n_rows)
        d['label_source'] = 2
        pd.DataFrame(d).to_csv(os.path.join(path, f'{uid}.features_labels.csv'), index=False)
    log(f'Synthetic dataset written to {path}: {n_users} users x {n_rows} rows')
    return path


# -------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('csv_dir', nargs='?', help='directory of ExtraSensory per-user CSVs')
    ap.add_argument('--self-test', action='store_true',
                    help='run on synthetic data to validate the pipeline')
    ap.add_argument('--targets', type=int, default=10,
                    help='number of target participants, by row count (default 10)')
    ap.add_argument('--model', default='hgb', choices=['hgb', 'gb', 'lr'])
    ap.add_argument('--train-frac', type=float, default=0.6,
                    help='earlier fraction of each target timeline used for training')
    ap.add_argument('--embargo-min', type=float, default=30.0,
                    help='minutes dropped after the split boundary')
    ap.add_argument('--max-impostor-rows', type=int, default=60000,
                    help='cap on impostor rows per partition; 0 disables')
    ap.add_argument('--rf-select', action='store_true',
                    help='apply the original 95%%-cumulative RF selection inside each arm '
                         '(off by default: selecting separately per arm confounds the '
                         'comparison this script exists to make)')
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--out', default=None)
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    out_dir = args.out or os.path.join(here, 'results')
    os.makedirs(out_dir, exist_ok=True)

    if args.self_test:
        import tempfile
        args.csv_dir = make_synthetic(os.path.join(tempfile.mkdtemp(), 'synth'))
        args.targets = min(args.targets, 6)
        args.max_impostor_rows = 8000
    if not args.csv_dir:
        ap.error('csv_dir is required unless --self-test is given')

    t0 = time.time()
    df, selected = load_dataset(args.csv_dir)
    counts = df.user_id.value_counts()
    targets = counts.index[:args.targets].tolist()
    log(f'Target participants ({len(targets)}): '
        + ', '.join(f'{u}({counts[u]})' for u in targets))

    rows = []
    for ti, target in enumerate(targets, 1):
        for arm in ARMS:
            rng = np.random.default_rng(args.seed)   # identical impostor partition per arm
            r = run_one(df, selected, target, arm, args, rng)
            if r is None:
                log(f'[{ti}/{len(targets)}] {target} {arm}: skipped (insufficient data)')
                continue
            rows.append(r)
            log(f'[{ti}/{len(targets)}] {target:<10} {arm:<17} '
                f'EER={r["eer"]:.4f} AUC={r["auc"]:.4f} feats={r["n_features_used"]}')

    if not rows:
        sys.exit('No results produced.')

    per_user = pd.DataFrame(rows)
    per_user.to_csv(os.path.join(out_dir, 'exp4_ablation_per_user.csv'), index=False)

    summary = (per_user.groupby('arm')
               .agg(n_users=('eer', 'size'), eer_median=('eer', 'median'),
                    eer_mean=('eer', 'mean'), eer_std=('eer', 'std'),
                    auc_median=('auc', 'median'),
                    features=('n_features_used', 'median'))
               .reindex([a for a in ARMS if a in set(per_user.arm)]).round(4))

    # Protocol assertions: if these are violated the numbers above are not trustworthy.
    checks = {
        'impostor_partitions_disjoint': bool((per_user.impostor_users_overlap == 0).all()),
        'max_genuine_test_rows_within_90s_of_train':
            float(per_user.genuine_test_rows_within_90s_of_train.max()),
        'preprocessing_fitted_on_train_only': True,
        'unit_of_analysis': 'target participant',
    }

    results = {
        'config': {k: v for k, v in vars(args).items()},
        'dataset': {'n_users': int(df.user_id.nunique()), 'n_rows': int(len(df)),
                    'n_sensor_features': len(selected)},
        'protocol_checks': checks,
        'summary_by_arm': summary.reset_index().to_dict(orient='records'),
        'paired_vs_all': paired_stats(per_user, baseline='all'),
        'wall_time_s': time.time() - t0,
    }
    with open(os.path.join(out_dir, 'exp4_ablation_results.json'), 'w') as f:
        json.dump(results, f, indent=2, default=float)

    log('\n' + '=' * 78)
    log('EER by arm (lower is better; 0.5 is chance). Unit of analysis: participant.')
    log('=' * 78)
    log(summary.to_string())
    log('\nPaired vs "all" (Wilcoxon signed-rank across participants):')
    log(json.dumps(results['paired_vs_all'], indent=2, default=float))
    log('\nProtocol checks: ' + json.dumps(checks, default=float))
    log(f'\nWrote {out_dir}/exp4_ablation_results.json and exp4_ablation_per_user.csv')
    log(f'Wall time {time.time() - t0:.1f}s')
    log('\nNOTE: absolute values here are not comparable to the original Stage 1 numbers '
        '(0.9926 accuracy, 0.53% FAR), which were produced under a random row-level '
        'split with closed-set impostors. Compare arms to each other, not to those.')


if __name__ == '__main__':
    main()
