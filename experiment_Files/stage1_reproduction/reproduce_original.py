"""Faithful re-execution of COMPLETE_ExtraSensory_Analysis_with_Hysteresis.ipynb
(cells 7-50, 53; CV cell 57 is in reproduce_cv.py).
Logic, parameters, ordering and seeds are copied verbatim from the executed notebook.
Only changes: file paths, no plotting, `del` of intermediates to fit 3-4 GB RAM
(does not alter any value), and saving of intermediate arrays for audit.
The DIAGNOSTICS block at the end is ADDITIONAL audit instrumentation; it does not
modify any reproduced quantity.
Usage: python reproduce_original.py <csv_dir>
"""
import sys, os, glob, gc, json, time, pickle
import numpy as np, pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (confusion_matrix, accuracy_score, precision_score,
                             recall_score, f1_score, roc_auc_score, roc_curve)
from sklearn.impute import SimpleImputer
from imblearn.over_sampling import SMOTE

DATASET_PATH = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'results'); os.makedirs(OUT, exist_ok=True)
CACHE = sys.argv[2] if len(sys.argv) > 2 else '/tmp/stage1_cache'; os.makedirs(CACHE, exist_ok=True)
R = {}
def log(*a):
    print(*a, flush=True)
T0 = time.time()

# --- cell 7/8 ---
csv_files = sorted(glob.glob(os.path.join(DATASET_PATH, '*.csv')))
sample_df = pd.read_csv(csv_files[0])
all_columns = sample_df.columns.tolist()
feature_cols = [c for c in all_columns if not c.startswith('label:') and c not in ['timestamp', 'label_source']]
label_cols = [c for c in all_columns if c.startswith('label:')]
R['sample_shape'] = list(sample_df.shape); R['n_feature_cols'] = len(feature_cols); R['n_label_cols'] = len(label_cols)
del sample_df

# --- cell 11/12 (only the reported numbers) ---
tot_rows = 0; tot_hours = 0; miss = []
for f in csv_files:
    df = pd.read_csv(f)
    tot_rows += len(df); tot_hours += (df['timestamp'].max() - df['timestamp'].min()) / 3600
    miss.append(df[feature_cols].isna().sum().sum() / (len(df) * len(feature_cols)) * 100)
    del df
R['total_records'] = int(tot_rows); R['total_hours'] = float(tot_hours); R['avg_missing_pct'] = float(np.mean(miss))
log('A:', R)

# --- cell 18 ---
selected_sensors = ['raw_acc', 'proc_gyro', 'location', 'discrete']
selected_features = [c for c in feature_cols if any(c.startswith(s) for s in selected_sensors)]
dfs = []
for f in csv_files:
    user_id = os.path.basename(f).split('_')[0]
    df = pd.read_csv(f, usecols=['timestamp'] + selected_features)
    df['user_id'] = user_id
    dfs.append(df)
auth_dataset = pd.concat(dfs, ignore_index=True); del dfs; gc.collect()
R['n_selected_features'] = len(selected_features); R['auth_dataset_shape'] = list(auth_dataset.shape)

# --- cell 20/21 ---
missing_stats = auth_dataset[selected_features].isna().sum().sort_values(ascending=False)
missing_pct = (missing_stats / len(auth_dataset)) * 100
R['features_gt50_missing'] = missing_pct[missing_pct > 50].round(2).to_dict()
valid_features = missing_pct[missing_pct <= 50].index.tolist()
R['n_valid_features'] = len(valid_features)
X = auth_dataset[valid_features].copy()
imputer = SimpleImputer(strategy='median')
X_imputed = pd.DataFrame(imputer.fit_transform(X), columns=valid_features); del X; gc.collect()
scaler = RobustScaler()
X_scaled = pd.DataFrame(scaler.fit_transform(X_imputed), columns=valid_features); del X_imputed; gc.collect()

# --- cell 23 ---
user_counts = auth_dataset['user_id'].value_counts()
target_user = user_counts.index[0]
y = (auth_dataset['user_id'] == target_user).astype(int).values
R['target_user'] = target_user; R['n_target'] = int(y.sum()); R['n_other'] = int((1 - y).sum())
log('B:', {k: R[k] for k in ['n_selected_features', 'n_valid_features', 'target_user', 'n_target', 'n_other']})

# --- cell 26 ---
t = time.time()
X_train_temp, X_test_temp, y_train_temp, y_test_temp, idx_tr_tmp, idx_te_tmp = train_test_split(
    X_scaled, y, np.arange(len(y)), test_size=0.2, random_state=42, stratify=y)
rf_importance = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10, n_jobs=-1)
rf_importance.fit(X_train_temp, y_train_temp)
feature_importance = pd.DataFrame({'feature': valid_features, 'importance': rf_importance.feature_importances_}
                                  ).sort_values('importance', ascending=False)
feature_importance.to_csv(os.path.join(OUT, 'repro_rf_feature_importance.csv'), index=False)
R['rf_time_s'] = time.time() - t
del X_train_temp, X_test_temp, y_train_temp, y_test_temp, rf_importance; gc.collect()

# --- cell 28 ---
cumsum = feature_importance['importance'].cumsum()
n_features_95 = int((cumsum >= 0.95).argmax() + 1)
selected_final_features = feature_importance.head(n_features_95)['feature'].tolist()
X_final = X_scaled[selected_final_features].copy()
R['n_features_95'] = n_features_95; R['top15'] = feature_importance.head(15).round(4).values.tolist()
log('C:', n_features_95, R['top15'][:5])

# --- cell 32 ---
X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
    X_final, y, np.arange(len(y)), test_size=0.2, random_state=42, stratify=y)
R['same_split_as_rf'] = bool(np.array_equal(np.sort(idx_train), np.sort(idx_tr_tmp)))
smote = SMOTE(random_state=42, k_neighbors=5)
X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)
R['n_train'] = len(X_train); R['n_test'] = len(X_test); R['balanced_counts'] = np.bincount(y_train_balanced).tolist()
np.save(os.path.join(CACHE, 'idx_test.npy'), idx_test)

# --- cell 34 ---
lr_params = dict(C=1.0, penalty='l2', solver='lbfgs', max_iter=1000, class_weight='balanced', random_state=42)
t = time.time(); lr_model = LogisticRegression(**lr_params).fit(X_train_balanced, y_train_balanced); R['lr_time_s'] = time.time() - t
y_pred_lr = lr_model.predict(X_test); y_pred_proba_lr = lr_model.predict_proba(X_test)[:, 1]
R['lr_acc'] = accuracy_score(y_test, y_pred_lr); log('LR acc', R['lr_acc'])

# --- cell 36 ---
gb_params = dict(n_estimators=200, learning_rate=0.1, max_depth=6, min_samples_split=100, min_samples_leaf=50,
                 subsample=0.8, max_features='sqrt', random_state=42, verbose=0)
t = time.time(); gb_model = GradientBoostingClassifier(**gb_params).fit(X_train_balanced, y_train_balanced); R['gb_time_s'] = time.time() - t
y_pred_gb = gb_model.predict(X_test); y_pred_proba_gb = gb_model.predict_proba(X_test)[:, 1]
R['gb_acc'] = accuracy_score(y_test, y_pred_gb); log('GB acc', R['gb_acc'])
pickle.dump(dict(lr=lr_model, gb=gb_model, selected_final_features=selected_final_features,
                 valid_features=valid_features, target_user=target_user), open(os.path.join(CACHE, 'models.pkl'), 'wb'))
np.savez(os.path.join(CACHE, 'balanced.npz'), X=X_train_balanced.values if hasattr(X_train_balanced, 'values') else X_train_balanced, y=y_train_balanced)
del X_train_balanced; gc.collect()

# --- cell 42 ---
user_data = auth_dataset[auth_dataset['user_id'] == target_user].copy()
orig_index = user_data.index.values  # row ids in auth_dataset (before sort)
user_data = user_data.sort_values('timestamp')
orig_index_sorted = user_data.index.values
user_data = user_data.reset_index(drop=True)
time_span_hours = (user_data['timestamp'].max() - user_data['timestamp'].min()) / 3600
X_user_scaled = scaler.transform(imputer.transform(user_data[valid_features].copy()))
X_user_final = pd.DataFrame(X_user_scaled, columns=valid_features)[selected_final_features].values
R['time_span_hours'] = time_span_hours

# --- cell 44 ---
y_proba = gb_model.predict_proba(X_user_final)[:, 1]
NAIVE_THRESHOLD = 0.5
naive_decisions = (y_proba >= NAIVE_THRESHOLD).astype(int)
naive_transitions = int(np.sum(np.abs(np.diff(naive_decisions))))
total_frames = len(naive_decisions) - 1
PING_PONG_WINDOW = 3
def pingpong(s):
    c = 0
    for i in range(len(s) - PING_PONG_WINDOW):
        if np.sum(np.abs(np.diff(s[i:i + PING_PONG_WINDOW + 1]))) >= 2:
            c += 1
    return c
ping_pong_count = pingpong(naive_decisions)

# --- cell 46 (verbatim state machine) ---
TTT_FRAMES = 3; UNLOCK_THRESHOLD = 0.6; LOCK_THRESHOLD = 0.4
def hysteresis(p):
    st = np.zeros(len(p), dtype=int); uc = 0; lc = 0
    for i in range(1, len(p)):
        cs = st[i - 1]; cp = p[i]
        if cs == 0:
            if cp >= UNLOCK_THRESHOLD:
                uc += 1; st[i] = 1 if uc >= TTT_FRAMES else 0
                if st[i] == 1: uc = 0
            else:
                uc = 0; st[i] = 0
        else:
            if cp <= LOCK_THRESHOLD:
                lc += 1; st[i] = 0 if lc >= TTT_FRAMES else 1
                if st[i] == 0: lc = 0
            else:
                lc = 0; st[i] = 1
    return st
hysteresis_state = hysteresis(y_proba)
hyst_transitions = int(np.sum(np.abs(np.diff(hysteresis_state))))
hyst_ping_pong = pingpong(hysteresis_state)
R.update(total_frames=total_frames, naive_transitions=naive_transitions, ping_pong_count=ping_pong_count,
         hyst_transitions=hyst_transitions, hyst_ping_pong=hyst_ping_pong,
         stability_naive=1 - naive_transitions / total_frames, stability_hyst=1 - hyst_transitions / total_frames)
log('HYST:', naive_transitions, ping_pong_count, hyst_transitions, hyst_ping_pong)

# --- cell 53 (verbatim metric function incl. its 'EER') ---
def calculate_auth_metrics(y_true, y_pred, y_pred_proba):
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    far = fp / (fp + tn) if (fp + tn) > 0 else 0
    frr = fn / (fn + tp) if (fn + tp) > 0 else 0
    return {'Accuracy': accuracy_score(y_true, y_pred), 'Precision': precision_score(y_true, y_pred),
            'Recall': recall_score(y_true, y_pred), 'F1-Score': f1_score(y_true, y_pred),
            'FAR': far, 'FRR': frr, 'ROC-AUC': roc_auc_score(y_true, y_pred_proba), 'EER': (far + frr) / 2,
            'confusion_tn_fp_fn_tp': [int(tn), int(fp), int(fn), int(tp)]}
R['lr_metrics'] = calculate_auth_metrics(y_test, y_pred_lr, y_pred_proba_lr)
R['gb_metrics'] = calculate_auth_metrics(y_test, y_pred_gb, y_pred_proba_gb)
log('GB metrics', R['gb_metrics'])

# ================= DIAGNOSTICS (audit-only; not part of original) =================
Dg = {}
def true_eer(yt, p):
    fpr, tpr, _ = roc_curve(yt, p); fnr = 1 - tpr; i = np.nanargmin(np.abs(fnr - fpr)); return float((fpr[i] + fnr[i]) / 2)
Dg['gb_true_eer_test'] = true_eer(y_test, y_pred_proba_gb)
Dg['lr_true_eer_test'] = true_eer(y_test, y_pred_proba_lr)
# how much of the hysteresis stream was training data?
test_set = set(idx_test.tolist())
in_test = np.array([i in test_set for i in orig_index_sorted])
Dg['target_stream_frames'] = int(len(in_test)); Dg['target_stream_frames_in_test'] = int(in_test.sum())
Dg['target_stream_frac_in_train'] = float(1 - in_test.mean())
# genuine-stream acceptance on the stream actually used
Dg['stream_frac_locked_naive'] = float(1 - naive_decisions.mean())
Dg['stream_frac_locked_hyst'] = float(1 - hysteresis_state.mean())
Dg['stream_frac_locked_naive_trainrows'] = float(1 - naive_decisions[~in_test].mean())
Dg['stream_frac_locked_naive_testrows'] = float(1 - naive_decisions[in_test].mean())
Dg['stream_frac_locked_hyst_testrows'] = float(1 - hysteresis_state[in_test].mean())
Dg['hyst_initial_state'] = int(hysteresis_state[0]); Dg['hyst_first_unlock_frame'] = int(np.argmax(hysteresis_state == 1))
Dg['naive_transitions_within_trainrows_pairs'] = int(np.sum((np.abs(np.diff(naive_decisions)) == 1) & ~in_test[1:] & ~in_test[:-1]))
Dg['naive_transitions_touching_testrow'] = int(np.sum((np.abs(np.diff(naive_decisions)) == 1) & (in_test[1:] | in_test[:-1])))
# test-rows-only subsequence (same model, same thresholds) - diagnostic
p_te = y_proba[in_test]; nd_te = (p_te >= 0.5).astype(int); hs_te = hysteresis(p_te)
Dg['testonly_subseq'] = dict(frames=int(len(p_te)), naive_transitions=int(np.abs(np.diff(nd_te)).sum()),
                             naive_pingpong=pingpong(nd_te), hyst_transitions=int(np.abs(np.diff(hs_te)).sum()),
                             hyst_pingpong=pingpong(hs_te), frac_locked_naive=float(1 - nd_te.mean()),
                             frac_locked_hyst=float(1 - hs_te.mean()))
# ping-pong definition check: overlapping windows
Dg['pingpong_is_overlapping_window_count'] = True
# post-hysteresis frame-level FRR on stream vs reported FRR
Dg['reported_frr_is_test_set_naive_only'] = True
# per-impostor acceptance on held-out test rows (naive 0.5)
te_users = auth_dataset['user_id'].values[idx_test]
per_user = pd.DataFrame({'u': te_users, 'y': y_test, 'pred': y_pred_gb}).query('y==0').groupby('u')['pred'].agg(['mean', 'size'])
per_user = per_user.sort_values('mean', ascending=False)
per_user.to_csv(os.path.join(OUT, 'repro_per_impostor_acceptance_test.csv'))
Dg['impostor_users_with_any_fa'] = int((per_user['mean'] > 0).sum())
Dg['impostor_top5_acceptance'] = per_user.head(5)['mean'].round(4).to_dict()
# importance share by sensor group
fi = feature_importance.copy()
fi['group'] = fi.feature.str.split(':').str[0]
Dg['importance_share_by_group'] = fi.groupby('group')['importance'].sum().round(4).to_dict()
Dg['importance_share_selected52_by_group'] = fi.head(n_features_95).groupby('group')['importance'].sum().round(4).to_dict()
# stationary-location proxy: per-user median altitude
alt = auth_dataset.groupby('user_id')['location:min_altitude'].median()
Dg['target_median_min_altitude'] = float(alt.loc[target_user])
Dg['users_within_5m_altitude_of_target'] = int((np.abs(alt - alt.loc[target_user]) <= 5).sum() - 1)
Dg['target_frac_altitude_missing_imputed'] = float(auth_dataset.loc[auth_dataset.user_id == target_user, 'location:min_altitude'].isna().mean())
Dg['all_frac_altitude_missing_imputed'] = float(auth_dataset['location:min_altitude'].isna().mean())
Dg['imputer_median_min_altitude'] = float(imputer.statistics_[valid_features.index('location:min_altitude')])
R['diagnostics'] = Dg
np.savez(os.path.join(CACHE, 'stream.npz'), y_proba=y_proba, naive=naive_decisions, hyst=hysteresis_state,
         in_test=in_test, ts=user_data['timestamp'].values)
R['wall_time_s'] = time.time() - T0
json.dump(R, open(os.path.join(OUT, 'repro_results.json'), 'w'), indent=2, default=float)
log(json.dumps(Dg, indent=2, default=float))
