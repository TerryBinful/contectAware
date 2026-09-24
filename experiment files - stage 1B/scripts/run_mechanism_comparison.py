#!/usr/bin/env python3
"""POST-PIVOT EXPERIMENT: comparison of decision-layer stabilization mechanisms
under a common score generator and a matched operating point.

  python scripts/run_mechanism_comparison.py --config configs/mechanism_comparison.json \
      --data /path/to/csv --out results/mechanism_comparison [--max-users N] [--resume]
"""
import argparse, json, os, sys, time, traceback
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import data_io, features, protocol, experiment, benchmark, calibrate, metrics
from src import mechanisms as M

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', required=True); ap.add_argument('--data', required=True)
    ap.add_argument('--out', required=True); ap.add_argument('--max-users', type=int, default=None)
    ap.add_argument('--resume', action='store_true')
    a = ap.parse_args(); cfg = json.load(open(a.config)); seed = cfg['seed']
    for d in ['', 'manifests', 'benchmark', 'calibration', 'logs', 'figures', 'tables']:
        os.makedirs(os.path.join(a.out, d), exist_ok=True)
    log = open(os.path.join(a.out, 'logs', 'run.log'), 'a')
    def say(*m): print(*m, flush=True); print(*m, file=log, flush=True)
    exp_id = cfg['experiment_id'] + '_' + time.strftime('%Y%m%dT%H%M%S')
    say(f'=== POST-PIVOT MECHANISM COMPARISON === {exp_id}')

    ds = data_io.Dataset(a.data)
    probs = ds.validate_schema(cfg['expect_features'], cfg['expect_users'])
    if probs:
        say('SCHEMA VALIDATION FAILED:'); [say(' -', p) for p in probs]; sys.exit(2)
    cls = protocol.classify_participants(ds, cfg)
    cls.to_csv(os.path.join(a.out, 'manifests', 'participant_classification.csv'), index=False)
    cohort = cls.loc[cls.eligible_primary, 'uuid'].tolist() if cfg['cohort'] == 'regular' else cls['uuid'].tolist()
    pools = protocol.assign_pools(ds.uuids, seed, cfg['n_impostor_fit'], cfg['n_impostor_calib'])
    protocol.check_pools(pools)
    json.dump(dict(pools=pools, enrolled_candidates=cohort, cohort=cfg['cohort']),
              open(os.path.join(a.out, 'manifests', 'participant_split.json'), 'w'), indent=2)
    users = cohort[:a.max_users] if a.max_users else cohort
    say(f'{len(cohort)} eligible users ({cfg["cohort"]} cohort); running {len(users)}; '
        f'pools fit/calib/test = {len(pools["impostor_fit"])}/{len(pools["impostor_calib"])}/{len(pools["impostor_test"])}')
    json.dump(dict(experiment_id=exp_id, git_commit=experiment.env_info()['git_commit'], config=cfg,
                   config_path=os.path.abspath(a.config), dataset=os.path.abspath(a.data),
                   random_seed=seed, feature_set=cfg['feature_set'], classifier=cfg['score_model'],
                   mechanisms=M.MECHANISM_ORDER, operating_point=dict(target_FAR=cfg['target_far'], tolerance=cfg['far_tolerance']),
                   environment=experiment.env_info(), started=time.strftime('%Y-%m-%dT%H:%M:%S')),
              open(os.path.join(a.out, 'experiment_metadata.json'), 'w'), indent=2, default=str)

    seq_rows, cal_rows, bench_rows, gen_rows, failures = [], [], [], [], []
    done = set()
    seq_path = os.path.join(a.out, 'sequence_metrics.csv')
    if a.resume and os.path.exists(seq_path):
        prev = pd.read_csv(seq_path); seq_rows = prev.to_dict('records'); done = set(prev.enrolled_user)
        say(f'RESUME: {len(done)} users already done')

    for ui, u in enumerate(users, 1):
        if u in done: continue
        try:
            t0 = time.time()
            gen, parts = experiment.fit_score_generator(ds, cfg, pools, u, cfg['feature_set'], cfg['score_model'], seed)
            ts_u, X_u = parts['ts'], parts['X']
            rng = np.random.default_rng(seed + ui)
            src = {}
            for pool_name, pool in [('calib', pools['impostor_calib']), ('test', pools['impostor_test'])]:
                src[pool_name] = {}
                for iu in pool:
                    if iu == u: continue
                    its, _ = ds.load(iu); src[pool_name][iu] = (its, np.arange(len(its)))
            cal_seqs = benchmark.build_sequences(u, ts_u, parts['calib'], src['calib'], cfg, rng)
            test_seqs = benchmark.build_sequences(u, ts_u, parts['test'], src['test'], cfg, rng)
            if not cal_seqs or not test_seqs:
                raise RuntimeError(f'insufficient contiguous blocks (calib={len(cal_seqs)}, test={len(test_seqs)})')
            # fit the score normaliser on CALIBRATION raw scores only (monotone; no test data)
            cal_raw = [gen.raw_score(X_u[parts['calib']])]
            for iu in list(src['calib'])[:cfg.get('normaliser_impostors', 6)]:
                _, Xi = ds.load(iu); cal_raw.append(gen.raw_score(Xi[:cfg.get('normaliser_rows', 1500)]))
            gen.fit_normaliser(np.concatenate(cal_raw))
            score_u = lambda rows: gen.score(X_u[rows])
            def score_imp(uu, rows):
                _, Xi = ds.load(uu); return gen.score(Xi[rows])
            cal_streams = [(benchmark.sequence_scores(s, score_u, score_imp), s['truth']) for s in cal_seqs]
            test_streams = [(benchmark.sequence_scores(s, score_u, score_imp), s['truth']) for s in test_seqs]
            sm = calibrate.estimate_score_models(cal_streams)
            pooled_cal = np.concatenate([s for s, _ in cal_streams])
            thetas = sorted(set(np.quantile(pooled_cal, cfg['theta_quantiles']).tolist()))  # no rounding

            params = {}
            for name in M.MECHANISM_ORDER:
                p, rec = calibrate.calibrate_mechanism(name, cal_streams, cfg['target_far'], cfg['far_tolerance'],
                                                       thetas, sm)
                params[name] = p; rec.update(enrolled_user=u); cal_rows.append(rec)
            for s, (scores, truth) in zip(test_seqs, test_streams):
                for name in M.MECHANISM_ORDER:
                    st = M.build(name, params[name]).run(scores)
                    r = metrics.evaluate_sequence(st, truth, s['transition_idx'], s['recovery_idx'],
                                                 cfg['flip_window'], cfg['stable_frames'])
                    seq_rows.append(dict(enrolled_user=u, sequence_id=s['sequence_id'], impostor_user=s['impostor_user'],
                                         mechanism=name, params=json.dumps(params[name]), length=s['length'],
                                         transition_idx=s['transition_idx'], recovery_idx=s['recovery_idx'], **r))
            bench_rows += benchmark.audit(test_seqs)
            gen_rows.append(dict(**gen.meta, n_calib_sequences=len(cal_seqs), n_test_sequences=len(test_seqs),
                                 score_models=json.dumps(sm), thetas=json.dumps(thetas),
                                 total_seconds=float(time.time() - t0)))
            say(f'[{ui}/{len(users)}] {u[:8]}: {len(test_seqs)} test seq, {len(cal_seqs)} calib seq, '
                f'{len(M.MECHANISM_ORDER)} mechanisms ({time.time() - t0:.0f}s)')
        except Exception as e:
            failures.append(dict(user=u, error=repr(e), traceback=traceback.format_exc()))
            say(f'[{ui}/{len(users)}] FAILED {u[:8]}: {e!r}')
        pd.DataFrame(seq_rows).to_csv(seq_path, index=False)
        if cal_rows: pd.DataFrame(cal_rows).to_csv(os.path.join(a.out, 'operating_points.csv'), index=False)
        if bench_rows: pd.DataFrame(bench_rows).to_csv(os.path.join(a.out, 'benchmark', 'sequence_manifest.csv'), index=False)
        if gen_rows: pd.DataFrame(gen_rows).to_csv(os.path.join(a.out, 'score_generator_manifest.csv'), index=False)
        if failures: json.dump(failures, open(os.path.join(a.out, 'failures.json'), 'w'), indent=2)
    say(f'EXECUTION SUMMARY: users done={len(set(pd.DataFrame(seq_rows).enrolled_user)) if seq_rows else 0}, '
        f'sequence-rows={len(seq_rows)}, failures={len(failures)}')

if __name__ == '__main__':
    main()
