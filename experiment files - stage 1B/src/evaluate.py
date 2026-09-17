"""Stage 2 authentication metrics. All thresholds come from CALIBRATION data only;
final FAR/FRR are computed on held-out test data with unseen impostors."""
import numpy as np
from sklearn.metrics import roc_curve, roc_auc_score, average_precision_score

def true_eer(y, s):
    fpr, tpr, thr = roc_curve(y, s)
    fnr = 1 - tpr
    i = int(np.nanargmin(np.abs(fnr - fpr)))
    return float((fpr[i] + fnr[i]) / 2), float(thr[i])

def threshold_at_far(y, s, target_far):
    """Lowest threshold on calibration data whose impostor acceptance <= target_far."""
    imp = np.sort(s[y == 0])[::-1]
    if len(imp) == 0:
        return 0.5
    k = int(np.floor(target_far * len(imp)))
    return float(imp[k]) if k < len(imp) else float(imp[-1])

def rates(y, s, thr):
    acc = s >= thr
    gen, imp = y == 1, y == 0
    far = float(acc[imp].mean()) if imp.any() else np.nan
    frr = float(1 - acc[gen].mean()) if gen.any() else np.nan
    return dict(threshold=float(thr), FAR=far, FRR=frr, HTER=float((far + frr) / 2) if gen.any() and imp.any() else np.nan,
                n_genuine=int(gen.sum()), n_impostor=int(imp.sum()))

def roc_points(y, s, n=200):
    fpr, tpr, thr = roc_curve(y, s)
    k = np.linspace(0, len(fpr) - 1, min(n, len(fpr))).astype(int)
    return dict(fpr=fpr[k].tolist(), tpr=tpr[k].tolist(), threshold=np.where(np.isfinite(thr[k]), thr[k], 1.0).tolist())

def evaluate(y_test, s_test, y_cal, s_cal, far_targets=(0.01, 0.001)):
    out = {}
    out['AUC'] = float(roc_auc_score(y_test, s_test)) if len(np.unique(y_test)) > 1 else np.nan
    out['AP_genuine_positive'] = float(average_precision_score(y_test, s_test))
    eer, eer_thr_test = true_eer(y_test, s_test)
    out['EER_test_oracle'] = eer
    out['eer_threshold_test_oracle'] = eer_thr_test   # reported for reference ONLY; never used to set an operating point
    eer_cal, thr_cal = true_eer(y_cal, s_cal)
    out['EER_calibration'] = eer_cal
    ops = {'cal_EER_threshold': rates(y_test, s_test, thr_cal),
           'fixed_0.5': rates(y_test, s_test, 0.5)}
    for tf in far_targets:
        ops[f'cal_FAR{tf}'] = rates(y_test, s_test, threshold_at_far(y_cal, s_cal, tf))
    out['operating_points'] = ops
    out['roc'] = roc_points(y_test, s_test)
    out['score_summary'] = dict(
        genuine=dict(n=int((y_test == 1).sum()), median=float(np.median(s_test[y_test == 1])),
                     p05=float(np.percentile(s_test[y_test == 1], 5))),
        impostor=dict(n=int((y_test == 0).sum()), median=float(np.median(s_test[y_test == 0])),
                      p95=float(np.percentile(s_test[y_test == 0], 95))))
    return out

def bootstrap_ci(values, n_boot=2000, seed=0, alpha=0.05):
    v = np.asarray([x for x in values if np.isfinite(x)], float)
    if len(v) < 2:
        return dict(mean=float(v.mean()) if len(v) else np.nan, lo=np.nan, hi=np.nan, n=int(len(v)))
    rng = np.random.default_rng(seed)
    m = rng.choice(v, size=(n_boot, len(v)), replace=True).mean(1)
    return dict(mean=float(v.mean()), median=float(np.median(v)), lo=float(np.quantile(m, alpha / 2)),
                hi=float(np.quantile(m, 1 - alpha / 2)), n=int(len(v)))
