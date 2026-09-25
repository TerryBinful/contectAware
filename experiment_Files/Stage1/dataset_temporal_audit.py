"""Stage-1 dataset & temporal audit of the ExtraSensory primary feature files.
Read-only descriptive analysis. No modelling. Usage:
    python dataset_temporal_audit.py <dir_with_60_features_labels.csv>
"""
import sys, glob, os, json
import numpy as np, pandas as pd

D = sys.argv[1]; OUT = os.path.join(os.path.dirname(__file__), 'results')
files = sorted(glob.glob(os.path.join(D, '*.csv')))
rows = []; allgaps = []
groups = {'raw_acc':'raw_acc:', 'proc_gyro':'proc_gyro:', 'raw_magnet':'raw_magnet:',
          'watch_acceleration':'watch_acceleration:', 'watch_heading':'watch_heading:',
          'location':'location', 'audio':'audio_', 'discrete':'discrete:', 'lf_measurements':'lf_measurements:'}
grp_missing = {g: [] for g in groups}
for f in files:
    df = pd.read_csv(f)
    uid = os.path.basename(f).split('.')[0]
    ts = df['timestamp'].values
    feat = [c for c in df.columns if not c.startswith('label') and c != 'timestamp']
    lab = [c for c in df.columns if c.startswith('label:')]
    sorted_in_file = bool(np.all(np.diff(ts) > 0))
    t = np.sort(ts); d = np.diff(t)
    allgaps.append(d)
    labelled = (df[lab].fillna(0).sum(axis=1) > 0).mean()
    # contiguous runs where consecutive gap <= 90 s
    breaks = np.where(d > 90)[0]
    run_lengths = np.diff(np.concatenate([[-1], breaks, [len(t)-1]]))
    for g, p in groups.items():
        cols = [c for c in feat if c.startswith(p)]
        grp_missing[g].append(df[cols].isna().all(axis=1).mean())
    rows.append(dict(uuid=uid, n_rows=len(df), span_hours=(t[-1]-t[0])/3600,
        recorded_hours_if_1min=len(df)/60, sorted_in_file=sorted_in_file,
        duplicate_ts=int(len(t)-len(np.unique(t))),
        dt_median_s=float(np.median(d)), dt_p05=float(np.percentile(d,5)), dt_p95=float(np.percentile(d,95)),
        frac_dt_eq_60=float(np.mean(d==60)), frac_dt_59_61=float(np.mean((d>=59)&(d<=61))),
        frac_dt_lt_59=float(np.mean(d<59)), frac_gaps_gt_90=float(np.mean(d>90)),
        n_runs=len(run_lengths), median_run_len=float(np.median(run_lengths)), max_run_len=int(run_lengths.max()),
        frac_rows_any_label=float(labelled),
        watch_acc_absent=float(df[[c for c in feat if c.startswith('watch_acceleration:')]].isna().all(axis=1).mean()),
        audio_absent=float(df[[c for c in feat if c.startswith('audio_')]].isna().all(axis=1).mean()),
        n_feature_cols=len(feat), n_label_cols=len(lab), n_cols=df.shape[1]))
T = pd.DataFrame(rows)
T.to_csv(os.path.join(OUT, 'dataset_per_user_temporal.csv'), index=False)
g = np.concatenate(allgaps)
bins = [0,1,30,59,60,61,90,300,3600,86400,1e12]
hist = pd.cut(pd.Series(g), bins=bins, right=False).value_counts().sort_index()
summary = dict(n_users=len(T), total_rows=int(T.n_rows.sum()), total_span_hours=float(T.span_hours.sum()),
    total_recorded_hours_if_1min=float(T.n_rows.sum()/60),
    all_gaps=len(g), gap_median=float(np.median(g)), gap_frac_eq_60=float(np.mean(g==60)),
    gap_frac_59_61=float(np.mean((g>=59)&(g<=61))), gap_frac_lt_59=float(np.mean(g<59)),
    gap_frac_gt_90=float(np.mean(g>90)), min_gap=float(g.min()),
    gap_histogram={str(k): int(v) for k, v in hist.items()},
    users_not_sorted=int((~T.sorted_in_file).sum()), total_duplicate_ts=int(T.duplicate_ts.sum()),
    group_all_missing_mean_over_users={k: float(np.mean(v)) for k, v in grp_missing.items()},
    users_with_watch_acc_absent_gt_95pct=int((T.watch_acc_absent>0.95).sum()),
    rows_min=int(T.n_rows.min()), rows_max=int(T.n_rows.max()), rows_median=float(T.n_rows.median()))
json.dump(summary, open(os.path.join(OUT, 'dataset_temporal_summary.json'), 'w'), indent=2)
print(json.dumps(summary, indent=2))
print(T.sort_values('n_rows', ascending=False).head(5).to_string())
print(T[T.uuid.str.startswith('78A91A4E')].T.to_string())
