#!/usr/bin/env python3
"""Stage 2 driver. Fails loudly on missing data, schema problems or protocol violations.

  python scripts/run_stage2.py --config configs/stage2_primary.json --data /path/to/csv --out results/primary
  python scripts/run_stage2.py --config ... --data ... --out ... --dry-run      # audit + cost estimate only
"""
import argparse, json, os, sys, time, traceback
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import data_io, features, protocol, evaluate, experiment

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', required=True); ap.add_argument('--data', required=True)
    ap.add_argument('--out', required=True); ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--max-users', type=int, default=None)
    a = ap.parse_args()
    cfg = json.load(open(a.config)); seed = cfg['seed']
    for d in ['', 'manifests', 'per_impostor', 'score_streams', 'logs']:
        os.makedirs(os.path.join(a.out, d), exist_ok=True)
    log = open(os.path.join(a.out, 'logs', 'run.log'), 'a')
    def say(*m):
        print(*m, flush=True); print(*m, file=log, flush=True)

    say('=== STAGE 2 ===', cfg['name'], '| started', time.strftime('%Y-%m-%d %H:%M:%S'))
    ds = data_io.Dataset(a.data)
    problems = ds.validate_schema(cfg['expect_features'], cfg['expect_users'])
    if problems:
        say('SCHEMA VALIDATION FAILED:'); [say('  -', p) for p in problems]
        sys.exit(2)
    say(f'schema OK: {len(ds.uuids)} participants x {len(ds.feature_cols)} features')
    ds.manifest().to_csv(os.path.join(a.out, 'manifests', 'input_data_manifest.csv'), index=False)

    cls = protocol.classify_participants(ds, cfg)
    cls.to_csv(os.path.join(a.out, 'manifests', 'participant_classification.csv'), index=False)
    primary = cls.loc[cls.eligible_primary, 'uuid'].tolist()
    say(f'participants: {len(primary)} regular (primary), {len(cls) - len(primary)} fragmented (secondary only)')
    if cfg['cohort'] == 'regular':
        enrolled_pool = primary
    elif cfg['cohort'] == 'fragmented':
        enrolled_pool = cls.loc[~cls.eligible_primary, 'uuid'].tolist()
    else:
        enrolled_pool = cls['uuid'].tolist()
    if a.max_users:
        enrolled_pool = enrolled_pool[:a.max_users]
    if not enrolled_pool:
        say('NO ELIGIBLE ENROLLED USERS - stopping'); sys.exit(3)

    pools = protocol.assign_pools(ds.uuids, seed, cfg['n_impostor_fit'], cfg['n_impostor_calib'])
    protocol.check_pools(pools)
    json.dump(dict(pools=pools, enrolled_candidates=enrolled_pool,
                   note='for each enrolled user the user itself is removed from every pool at use time'),
              open(os.path.join(a.out, 'manifests', 'participant_pools.json'), 'w'), indent=2)
    say(f"impostor pools: fit={len(pools['impostor_fit'])} calib={len(pools['impostor_calib'])} test={len(pools['impostor_test'])} (disjoint)")

    runs = [(u, f, m) for u in enrolled_pool for f in cfg['feature_sets'] for m in cfg['models']]
    say(f'planned runs: {len(runs)} = {len(enrolled_pool)} users x {len(cfg["feature_sets"])} feature sets x {len(cfg["models"])} models')
    meta = dict(config=cfg, config_file=os.path.abspath(a.config), data_dir=os.path.abspath(a.data),
                environment=experiment.env_info(), seed=seed, planned_runs=len(runs),
                feature_set_definitions={k: features.FEATURE_SETS[k] for k in cfg['feature_sets']},
                started=time.strftime('%Y-%m-%dT%H:%M:%S'))
    json.dump(meta, open(os.path.join(a.out, 'experiment_metadata.json'), 'w'), indent=2, default=str)
    if a.dry_run:
        say('DRY RUN: audit complete, no models trained.'); return

    rows, failures = [], []
    for i, (u, f, m) in enumerate(runs, 1):
        try:
            r = experiment.run_user(ds, cfg, pools, u, f, m, a.out, seed)
            op = r['operating_points']['cal_EER_threshold']
            say(f"[{i}/{len(runs)}] {u[:8]} {f:22s} {m:19s} AUC={r['AUC']:.4f} EER={r['EER_test_oracle']:.4f} "
                f"FAR={op['FAR']:.4f} FRR={op['FRR']:.4f} ({r['total_seconds']:.0f}s)")
            json.dump(r, open(os.path.join(a.out, f"run__{u[:8]}__{f}__{m}.json"), 'w'), indent=2, default=float)
            rows.append({k: v for k, v in r.items() if k not in ('roc', 'leakage_checks', 'operating_points', 'score_summary')}
                        | {f'{op_name}_{k}': v for op_name, op_d in r['operating_points'].items() for k, v in op_d.items()})
        except Exception as e:
            failures.append(dict(user=u, feature_set=f, model=m, error=repr(e), traceback=traceback.format_exc()))
            say(f'[{i}/{len(runs)}] FAILED {u[:8]} {f} {m}: {e!r}')
        if rows:
            pd.DataFrame(rows).to_csv(os.path.join(a.out, 'per_run_results.csv'), index=False)
        if failures:
            json.dump(failures, open(os.path.join(a.out, 'failures.json'), 'w'), indent=2)

    if rows:
        R = pd.DataFrame(rows)
        agg = []
        for (f, m), g in R.groupby(['feature_set', 'model']):
            a_ci = evaluate.bootstrap_ci(g['AUC'], seed=seed); e_ci = evaluate.bootstrap_ci(g['EER_test_oracle'], seed=seed)
            far = evaluate.bootstrap_ci(g['cal_EER_threshold_FAR'], seed=seed); frr = evaluate.bootstrap_ci(g['cal_EER_threshold_FRR'], seed=seed)
            agg.append(dict(feature_set=f, model=m, n_users=len(g), AUC_mean=a_ci['mean'], AUC_lo=a_ci['lo'], AUC_hi=a_ci['hi'],
                            EER_mean=e_ci['mean'], EER_lo=e_ci['lo'], EER_hi=e_ci['hi'],
                            FAR_mean=far['mean'], FAR_lo=far['lo'], FAR_hi=far['hi'],
                            FRR_mean=frr['mean'], FRR_lo=frr['lo'], FRR_hi=frr['hi'],
                            runtime_median_s=float(g['total_seconds'].median())))
        pd.DataFrame(agg).to_csv(os.path.join(a.out, 'ablation_summary.csv'), index=False)
        say('\n' + pd.DataFrame(agg)[['feature_set', 'model', 'n_users', 'AUC_mean', 'EER_mean', 'FAR_mean', 'FRR_mean']].to_string(index=False))
    say(f'\nEXECUTION SUMMARY: {len(rows)} runs succeeded, {len(failures)} failed. Outputs in {a.out}')

if __name__ == '__main__':
    main()
