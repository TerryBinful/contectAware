"""Stage 2 runner: per-enrolled-user authentication models under the mandatory protocol.

Protocol (see configs/*.json and README.md):
  enrolment  = first fracs[0] of the enrolled user's frames, chronologically
  calibration= next fracs[1]  (+ impostor rows from the CALIBRATION impostor pool)
  test       = final fracs[2] (+ impostor rows from the TEST impostor pool, UNSEEN in fitting)
Imputer and scaler are fitted on TRAINING rows only. Thresholds come from calibration only.
"""
import os, json, time, platform, subprocess, numpy as np, pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import RobustScaler
from sklearn.ensemble import GradientBoostingClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from . import data_io, features, protocol, evaluate

def build_model(name, params, seed):
    if name == 'gradient_boosting':
        return GradientBoostingClassifier(random_state=seed, **params)
    if name == 'hist_gradient_boosting':
        return HistGradientBoostingClassifier(random_state=seed, **params)
    if name == 'logistic_regression':
        return LogisticRegression(random_state=seed, **params)
    raise ValueError(f'unknown model {name}')

def env_info():
    try:
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        commit = 'NOT AVAILABLE'
    import sklearn, scipy
    return dict(python=platform.python_version(), platform=platform.platform(), numpy=np.__version__,
                pandas=pd.__version__, sklearn=sklearn.__version__, scipy=scipy.__version__, git_commit=commit)

def sample_pool(ds, uuids, exclude, cap_total, seed, tag):
    """Row-sample from a participant pool. Rows are drawn per participant (seeded, without
    replacement); nothing is synthesised. Returns X, owner-uuid array, timestamps."""
    use = [u for u in uuids if u != exclude]
    if not use:
        raise protocol.ProtocolViolation(f'{tag}: empty impostor pool after removing the enrolled user')
    per = max(1, int(np.ceil(cap_total / len(use)))) if cap_total else None
    rng = np.random.default_rng(seed)
    Xs, who, tss = [], [], []
    for u in use:
        ts, X = ds.load(u)
        if per is not None and len(ts) > per:
            k = np.sort(rng.choice(len(ts), per, replace=False))
            ts, X = ts[k], X[k]
        Xs.append(X); tss.append(ts); who += [u] * len(ts)
    return np.vstack(Xs), np.array(who), np.concatenate(tss)

def run_user(ds, cfg, pools, enrolled, fs_name, model_name, outdir, seed):
    t0 = time.time()
    ts_u, X_u = ds.load(enrolled)
    tr, ca, te = protocol.temporal_split(ts_u, cfg['split_fracs'])
    seg_te = protocol.segments(ts_u[te], cfg['max_gap_s'])

    Xi_tr, who_tr, _ = sample_pool(ds, pools['impostor_fit'], enrolled, cfg['impostor_train_cap'], seed + 1, 'fit')
    Xi_ca, who_ca, _ = sample_pool(ds, pools['impostor_calib'], enrolled, cfg['impostor_calib_cap'], seed + 2, 'calib')
    Xi_te, who_te, _ = sample_pool(ds, pools['impostor_test'], enrolled, cfg['impostor_test_cap'], seed + 3, 'test')

    idx, cols = features.resolve(ds.feature_cols, fs_name)
    mo = features.FEATURE_SETS[fs_name]['missingness_only']
    G = lambda X: features.materialise(X, idx, mo)
    Xtr = np.vstack([G(X_u[tr]), G(Xi_tr)])
    ytr = np.r_[np.ones(len(tr)), np.zeros(len(Xi_tr))]
    imp = SimpleImputer(strategy='median', keep_empty_features=True).fit(Xtr)   # TRAIN ONLY
    sc = RobustScaler().fit(imp.transform(Xtr))                                 # TRAIN ONLY
    P = lambda X: sc.transform(imp.transform(X))
    Xtr_p = P(Xtr)
    w = np.where(ytr == 1, (ytr == 0).sum() / max((ytr == 1).sum(), 1), 1.0)     # class balancing by weights, no SMOTE
    clf = build_model(model_name, cfg['models'][model_name], seed)
    if model_name == 'logistic_regression':
        clf.fit(Xtr_p, ytr)
    else:
        clf.fit(Xtr_p, ytr, sample_weight=w)
    t_fit = time.time() - t0

    s_ca = clf.predict_proba(P(np.vstack([G(X_u[ca]), G(Xi_ca)])))[:, 1]
    y_ca = np.r_[np.ones(len(ca)), np.zeros(len(Xi_ca))]
    s_gen = clf.predict_proba(P(G(X_u[te])))[:, 1]
    s_imp = clf.predict_proba(P(G(Xi_te)))[:, 1]
    s_te = np.r_[s_gen, s_imp]
    y_te = np.r_[np.ones(len(te)), np.zeros(len(s_imp))]

    res = evaluate.evaluate(y_te, s_te, y_ca, s_ca)
    thr = res['operating_points']['cal_EER_threshold']['threshold']
    per_imp = (pd.DataFrame(dict(uuid=who_te, score=s_imp))
               .groupby('uuid')['score'].agg(n='size', mean_score='mean',
                                             far=lambda x: float((x >= thr).mean())).reset_index())
    tag = f'{enrolled[:8]}__{fs_name}__{model_name}'
    per_imp.to_csv(os.path.join(outdir, 'per_impostor', f'{tag}.csv'), index=False)
    np.savez_compressed(os.path.join(outdir, 'score_streams', f'{tag}.npz'),
                        genuine_ts=ts_u[te], genuine_score=s_gen, genuine_segment=seg_te,
                        impostor_score=s_imp, impostor_uuid=who_te)

    checks = protocol.leakage_report(enrolled, pools, (ts_u[tr], ts_u[ca], ts_u[te]),
                                     [f'{enrolled}:{i}' for i in tr], [f'{enrolled}:{i}' for i in te])
    checks.append(dict(check='test_impostor_rows_from_unseen_participants_only',
                       passed=set(who_te).isdisjoint(set(who_tr) | set(who_ca)), detail=f'{len(set(who_te))} participants'))
    checks.append(dict(check='preprocessing_fitted_on_training_rows_only', passed=True,
                       detail=f'imputer/scaler fitted on {len(Xtr)} training rows'))
    if any(not c['passed'] for c in checks):
        raise protocol.ProtocolViolation(f'{tag}: ' + str([c for c in checks if not c['passed']]))

    return dict(enrolled_user=enrolled, feature_set=fs_name, model=model_name, n_features=len(cols),
                n_genuine_train=int(len(tr)), n_genuine_calib=int(len(ca)), n_genuine_test=int(len(te)),
                n_impostor_train=int(len(Xi_tr)), n_impostor_calib=int(len(Xi_ca)), n_impostor_test=int(len(Xi_te)),
                n_test_impostor_participants=int(len(set(who_te))), n_test_segments=int(seg_te.max() + 1),
                genuine_test_span_hours=float((ts_u[te][-1] - ts_u[te][0]) / 3600),
                fit_seconds=float(t_fit), total_seconds=float(time.time() - t0),
                leakage_checks=checks, **{k: v for k, v in res.items() if k != 'roc'}, roc=res['roc'])
