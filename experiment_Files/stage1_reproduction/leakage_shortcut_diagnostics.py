"""Audit-only diagnostics on the reproduced original model. Does NOT retrain or alter it.
Recomputes the (deterministic) original preprocessing, loads the saved GB model and quantifies:
 (1) temporal-neighbour leakage of the random row split,
 (2) whether missingness/imputation of altitude acts as a shortcut,
 (3) closed-set structure (every 'impostor' in test also appears in training),
 (4) distribution of the target user's genuine-stream probabilities.
Usage: python leakage_shortcut_diagnostics.py <csv_dir> <cache_dir>
"""
import sys, os, glob, json, pickle, numpy as np, pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import RobustScaler
D, C = sys.argv[1], sys.argv[2]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
m = pickle.load(open(os.path.join(C, 'models.pkl'), 'rb')); idx_test = np.load(os.path.join(C, 'idx_test.npy'))
files = sorted(glob.glob(os.path.join(D, '*.csv')))
cols = pd.read_csv(files[0], nrows=1).columns
feat = [c for c in cols if not c.startswith('label:') and c not in ['timestamp', 'label_source']]
sel = [c for c in feat if any(c.startswith(s) for s in ['raw_acc', 'proc_gyro', 'location', 'discrete'])]
dfs = []
for f in files:
    df = pd.read_csv(f, usecols=['timestamp'] + sel); df['user_id'] = os.path.basename(f).split('_')[0]; dfs.append(df)
A = pd.concat(dfs, ignore_index=True); del dfs
vf = m['valid_features']
alt_missing = A['location:min_altitude'].isna().values
Xs = RobustScaler().fit_transform(SimpleImputer(strategy='median').fit_transform(A[vf]))
Xf = pd.DataFrame(Xs, columns=vf)[m['selected_final_features']].values; del Xs
y = (A['user_id'] == m['target_user']).astype(int).values
is_test = np.zeros(len(A), bool); is_test[idx_test] = True
p_test = m['gb'].predict_proba(Xf[idx_test])[:, 1]; pred = (p_test >= 0.5).astype(int)
R = {}
yt = y[idx_test]; am = alt_missing[idx_test]
imp = yt == 0
R['impostor_test_rows'] = int(imp.sum())
R['impostor_test_frac_altitude_missing'] = float(am[imp].mean())
R['FAR_impostor_rows_altitude_missing'] = float(pred[imp & am].mean())
R['FAR_impostor_rows_altitude_present'] = float(pred[imp & ~am].mean())
R['share_of_false_accepts_with_altitude_present'] = float((pred[imp] & ~am[imp]).sum() / max(pred[imp].sum(), 1))
R['target_rows_frac_altitude_missing'] = float(alt_missing[y == 1].mean())
# (1) temporal-neighbour leakage: for each test row, is an adjacent frame (<=90 s, same user) in train?
A['is_test'] = is_test
A = A.sort_values(['user_id', 'timestamp'])
same_prev = (A['user_id'].values[1:] == A['user_id'].values[:-1]) & (np.diff(A['timestamp'].values) <= 90)
tr = ~A['is_test'].values
prev_train = np.r_[False, same_prev & tr[:-1]]
next_train = np.r_[same_prev & tr[1:], False]
te = A['is_test'].values
R['test_rows_with_adjacent_train_frame_le90s'] = float((prev_train | next_train)[te].mean())
tgt = (A['user_id'] == m['target_user']).values
R['target_test_rows_with_adjacent_train_frame_le90s'] = float((prev_train | next_train)[te & tgt].mean())
# (3) closed set
R['impostor_users_in_test'] = int(A.loc[te & ~tgt, 'user_id'].nunique())
R['impostor_users_in_test_also_in_train'] = int(len(set(A.loc[te & ~tgt, 'user_id']) & set(A.loc[tr & ~tgt, 'user_id'])))
# (4) genuine stream probabilities
s = np.load(os.path.join(C, 'stream.npz')); p = s['y_proba']
R['genuine_stream_frac_p_in_0.4_0.6'] = float(((p > 0.4) & (p < 0.6)).mean())
R['genuine_stream_frac_p_lt_0.4'] = float((p <= 0.4).mean())
R['genuine_stream_p_quantiles'] = {q: float(np.quantile(p, q)) for q in [0.01, 0.05, 0.1, 0.5]}
tsd = np.diff(s['ts']); R['genuine_stream_gap_median_s'] = float(np.median(tsd))
R['hyst_TTT_3_frames_equals_seconds_median'] = float(3 * np.median(tsd))
json.dump(R, open(os.path.join(OUT, 'repro_leakage_shortcut_diagnostics.json'), 'w'), indent=2)
print(json.dumps(R, indent=2))
