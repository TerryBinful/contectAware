#!/usr/bin/env python3
"""Dataset & cadence audit (post-pivot gate). Reuses src/protocol.py rather than adding a second
cadence checker. Outputs machine-readable artefacts plus a human-readable report that separates
observed facts, derived quantities, assumptions and limitations.

  python scripts/run_dataset_audit.py --data /path/csv --out results/dataset_audit
"""
import argparse, json, os, sys, time
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import data_io, protocol, features

ap = argparse.ArgumentParser(); ap.add_argument('--data', required=True); ap.add_argument('--out', required=True)
ap.add_argument('--regular-min-frac', type=float, default=0.95); ap.add_argument('--min-frames', type=int, default=1500)
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
ds = data_io.Dataset(a.data)
probs = ds.validate_schema()
cfg = dict(regular_min_frac=a.regular_min_frac, min_frames_per_user=a.min_frames, max_gap_s=90)
T = protocol.classify_participants(ds, cfg)
T.to_csv(os.path.join(a.out, 'cadence_summary.csv'), index=False)
ds.manifest().to_csv(os.path.join(a.out, 'input_data_manifest.csv'), index=False)

gaps = []
for u in ds.uuids:
    ts, _ = ds.load(u, cache=False); gaps.append(np.diff(ts))
g = np.concatenate(gaps)
bins = [0, 30, 59, 61, 90, 300, 3600, 86400, 1e12]
hist = {f'{int(bins[i])}-{int(bins[i+1])}s': int(((g >= bins[i]) & (g < bins[i+1])).sum()) for i in range(len(bins) - 1)}
inv = {}
for fam, pref in features.FAMILIES.items():
    inv[fam] = len([c for c in ds.feature_cols if any(c.startswith(p) for p in pref)])
S = dict(generated=time.strftime('%Y-%m-%dT%H:%M:%S'), data_dir=os.path.abspath(a.data),
         schema_problems=probs, n_participants=len(ds.uuids), n_feature_columns=len(ds.feature_cols),
         n_label_columns=len(ds.label_cols), total_observations=int(T.n_frames.sum()),
         gap_median_s=float(np.median(g)), gap_mean_s=float(np.mean(g)),
         frac_gaps_59_61=float(np.mean((g >= 59) & (g <= 61))), frac_gaps_gt_90=float(np.mean(g > 90)),
         gap_histogram=hist, cadence_hypothesis_60s_holds=bool(np.median(g) == 60),
         eligibility=dict(rule=f'frac(59-61s) >= {a.regular_min_frac} and frames >= {a.min_frames}',
                          n_eligible=int(T.eligible_primary.sum()), n_fragmented=int((~T.eligible_primary).sum())),
         sequence_structure=dict(total_segments=int(T.n_segments.sum()),
                                 max_segment_frames=int(T.max_segment_frames.max()),
                                 min_segment_frames_max_per_user=int(T.max_segment_frames.min()),
                                 median_segment_frames_median=float(T.median_segment_frames.median()),
                                 users_with_segment_ge_180=int((T.max_segment_frames >= 180).sum())),
         feature_inventory=inv,
         observations_per_user=dict(min=int(T.n_frames.min()), median=float(T.n_frames.median()), max=int(T.n_frames.max())))
json.dump(S, open(os.path.join(a.out, 'cadence_summary.json'), 'w'), indent=2)

with open(os.path.join(a.out, 'DATASET_AUDIT_REPORT.md'), 'w') as fh:
    w = fh.write
    w(f"# Dataset & cadence audit\n\nGenerated {S['generated']} from `{S['data_dir']}`.\n\n## Observed facts\n\n")
    w(f"- {S['n_participants']} participant files, {S['n_feature_columns']} feature columns, "
      f"{S['n_label_columns']} label columns, {S['total_observations']:,} observations.\n")
    w(f"- Schema problems: {S['schema_problems'] or 'none'}.\n")
    w(f"- Inter-observation gap: median {S['gap_median_s']:.0f} s, mean {S['gap_mean_s']:.1f} s; "
      f"{S['frac_gaps_59_61']*100:.1f}% of gaps lie in 59-61 s; {S['frac_gaps_gt_90']*100:.1f}% exceed 90 s.\n")
    w(f"- Gap histogram: {S['gap_histogram']}.\n")
    w(f"- Observations per participant: min {S['observations_per_user']['min']}, "
      f"median {S['observations_per_user']['median']:.0f}, max {S['observations_per_user']['max']}.\n")
    w(f"- Feature inventory by family: {S['feature_inventory']}.\n\n## Derived quantities\n\n")
    w(f"- The ~60-second cadence hypothesis **{'holds' if S['cadence_hypothesis_60s_holds'] else 'does not hold'}** "
      "(median gap equals 60 s), so 1 frame is treated as ~1 minute.\n")
    w(f"- Eligibility rule `{S['eligibility']['rule']}` yields **{S['eligibility']['n_eligible']} eligible** "
      f"and {S['eligibility']['n_fragmented']} fragmented participants.\n")
    w(f"- Contiguous segments (gaps <= 90 s): {S['sequence_structure']['total_segments']} in total; "
      f"{S['sequence_structure']['users_with_segment_ge_180']} participants have at least one segment of >= 180 frames.\n\n")
    w("## Assumptions\n\n- A gap above 90 s breaks temporal continuity; blocks are never joined across such a gap.\n"
      "- One frame is treated as one decision opportunity; frame-based temporal parameters are used throughout.\n\n")
    w("## Limitations\n\n- Cadence is irregular for the fragmented participants, so frame-based durations are only "
      "approximate for them; they are excluded from the primary experiment.\n"
      "- No sub-minute analysis is possible with this dataset.\n"
      "- The 20-second figure in earlier project documents is the sensor recording window, not the sampling interval.\n")
print(json.dumps({k: S[k] for k in ['n_participants', 'total_observations', 'gap_median_s', 'frac_gaps_59_61',
                                    'cadence_hypothesis_60s_holds']}, indent=2))
print('eligible:', S['eligibility'])
