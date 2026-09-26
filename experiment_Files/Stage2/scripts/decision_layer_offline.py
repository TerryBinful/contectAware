#!/usr/bin/env python3
"""Stage 2 v2 offline decision-layer analysis (PREREGISTRATION_v2, frozen 2026-09-26).

Consumes ONLY the per-frame score dump written by run_mechanism_comparison.py with
configs/v2_scoredump_f3.json (and, for the score-validity probe, v2_scoredump_f7.json).
Fits nothing. Every rule below is fixed in docs/Stage2/PREREGISTRATION_v2.md and
docs/Stage2/V2_ANALYSIS_IMPLEMENTATION_NOTES.md.

  python scripts/decision_layer_offline.py \
      --config configs/v2_scoredump_f3.json \
      --scores results/mechanism_comparison_v2/f3/scores \
      --f7-scores results/mechanism_comparison_v2/f7/scores \
      --out results/mechanism_comparison_v2/analysis

  python scripts/decision_layer_offline.py --self-test --out /tmp/v2_selftest   # synthetic data only

Outputs (all under --out):
  experiment_metadata.json            code commit, dirty flag, SHA-256 of analysis code, inputs
  factorial/operating_points.csv       per user x target x cell: C1/C2 selection record
  factorial/sequence_metrics.csv       test metrics for every selected cell
  factorial/participant_metrics.csv    user-level means
  factorial/response_surface.csv       cell-level summary (margin x dwell)
  primary/cell_selection.csv           cell_H / cell_D / cell_M per user (calibration only)
  primary/primary_tests.csv            §3.1 criteria 1-3
  primary/PRIMARY_DECISION.md          mechanical verdict with the preregistered wording
  primary/frr_difference_curve.csv     full CI curve for alternative margins
  families/operating_points.csv, sequence_metrics.csv, participant_metrics.csv,
  families/mechanism_metrics.csv, families/statistical_tests.csv, families/far_drift.csv
  families/reachability_rejections.csv
  secondary/no_sprt_subset_*.csv       §4.3
  secondary/score_validity_f3_f7.csv   §4.4 (only if --f7-scores given)
"""
import argparse, glob, hashlib, json, os, subprocess, sys, time
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from src import decision_v2 as D

PRIMARY_TARGET = 0.05
SENSITIVITY_TARGETS = (0.03, 0.07)
NI_MARGIN = 0.02                                  # §3.1 non-inferiority margins (FRR, detection failure)
N_BOOT = 2000
SEQ_METRICS = ['FAR', 'FRR', 'n_transitions', 'excess_transitions', 'fewer_than_2_transitions',
               'transition_rate_per_100', 'n_flip_events', 'detection_failure', 'recovery_failure',
               'detection_latency_frames', 'recovery_latency_frames',
               'detection_latency_censored', 'recovery_latency_censored', 'lockout_fraction_during_genuine']
CODE_FILES = ['src/decision_v2.py', 'src/metrics.py', 'scripts/decision_layer_offline.py']

# ------------------------------------------------------------------------------------------
def provenance(args):
    def git(*a):
        try:
            return subprocess.check_output(['git', *a], cwd=HERE, stderr=subprocess.DEVNULL).decode().strip()
        except Exception:
            return 'NOT AVAILABLE'
    dirty = git('status', '--porcelain', '--', 'src', 'scripts', 'configs')
    return dict(git_commit=git('rev-parse', 'HEAD'), analysis_code_dirty=bool(dirty and dirty != 'NOT AVAILABLE'),
                dirty_files=dirty.splitlines() if dirty and dirty != 'NOT AVAILABLE' else [],
                code_sha256={f: hashlib.sha256(open(os.path.join(HERE, f), 'rb').read()).hexdigest() for f in CODE_FILES},
                preregistration='docs/Stage2/PREREGISTRATION_v2.md',
                implementation_notes='docs/Stage2/V2_ANALYSIS_IMPLEMENTATION_NOTES.md',
                args=vars(args), started=time.strftime('%Y-%m-%dT%H:%M:%S'))

def load_user(path):
    df = pd.read_parquet(path) if path.endswith('.parquet') else pd.read_csv(path)
    out = {}
    for split in ('calib', 'test'):
        d = df[df.split == split].sort_values(['sequence_id', 'frame'])
        seqs = []
        for sid, g in d.groupby('sequence_id', sort=True):
            seqs.append(dict(sequence_id=sid, impostor_user=g.impostor_user.iloc[0], score=g.score.to_numpy(float),
                             raw_score=g.raw_score.to_numpy(float), truth=g.truth.to_numpy(int),
                             transition_idx=int(g.transition_idx.iloc[0]), recovery_idx=int(g.recovery_idx.iloc[0])))
        lengths = {len(s['score']) for s in seqs}
        if len(lengths) > 1:
            raise ValueError(f'{path}: unequal sequence lengths in {split}: {lengths}')
        out[split] = seqs
    out['enrolled_user'] = df.enrolled_user.iloc[0]
    return out

def stack(seqs, key='score'):
    return np.vstack([s[key] for s in seqs]), np.vstack([s['truth'] for s in seqs])

def evaluate_test(states_1cand, seqs, cfg):
    rows = []
    for j, s in enumerate(seqs):
        r = D.sequence_metrics_v2(states_1cand[j].astype(int), s['truth'], s['transition_idx'], s['recovery_idx'],
                                  cfg['flip_window'], cfg['stable_frames'])
        rows.append(dict(sequence_id=s['sequence_id'], impostor_user=s['impostor_user'], **r))
    return rows

# ------------------------------------------------------------------------------------------
def analyse_user(U, cfg, targets):
    user = U['enrolled_user']
    Sc, Yc = stack(U['calib']); St, Yt = stack(U['test'])
    sm = D.estimate_score_models(Sc, Yc)
    fac_ops, fac_seq, fam_ops, fam_seq, rej = [], [], [], [], []
    distinct_cal_imp = len({s['impostor_user'] for s in U['calib']})
    for target in targets:
        thetas = D.theta_grid(Sc, Yc, cfg, target)
        # ---------------- primary factorial: only theta tuned in every cell ----------------
        for m in D.FACTORIAL_MARGINS:
            for k in D.FACTORIAL_DWELLS:
                grid = D.factorial_grid(thetas, m, k)
                st = D.simulate('margin_dwell', grid, Sc)
                far, frr = D.pooled_far_frr(st, Yc)
                reach = np.array([D.reachable('margin_dwell', g)[0] for g in grid])
                i, rec = D.select_one_sided(grid, far, frr, reach, target, cfg['far_tolerance'])
                cell = D.cell_name(m, k)
                fac_ops.append(dict(enrolled_user=user, target=target, cell=cell, margin=m, dwell=k,
                                    cell_class=D.cell_class(m, k), distinct_calib_impostors=distinct_cal_imp,
                                    **{kk: (json.dumps(v) if kk == 'chosen_params' else v) for kk, v in rec.items()
                                       if kk != 'eligible_interval'}))
                if i is None:
                    continue
                ts = D.simulate('margin_dwell', [grid[i]], St)[0]
                for r in evaluate_test(ts, U['test'], cfg):
                    fac_seq.append(dict(enrolled_user=user, target=target, cell=cell, margin=m, dwell=k,
                                        cell_class=D.cell_class(m, k), theta=grid[i]['theta'], **r))
        # ---------------- secondary: tuned families ----------------
        for name in D.FAMILY_ORDER:
            grid = D.family_grid(name, thetas)
            st = D.simulate(name, grid, Sc, sm)
            far, frr = D.pooled_far_frr(st, Yc)
            rr = [D.reachable(name, g, sm) for g in grid]
            reach = np.array([r[0] for r in rr])
            for g, (ok, why) in zip(grid, rr):
                if not ok:
                    rej.append(dict(enrolled_user=user, target=target, mechanism=name, params=json.dumps(g), reason=why))
            i, rec = D.select_one_sided(grid, far, frr, reach, target, cfg['far_tolerance'])
            fam_ops.append(dict(enrolled_user=user, target=target, mechanism=name, distinct_calib_impostors=distinct_cal_imp,
                                **{kk: (json.dumps(v) if kk == 'chosen_params' else v) for kk, v in rec.items()
                                   if kk != 'eligible_interval'}))
            if i is None:
                continue
            ts = D.simulate(name, [grid[i]], St, sm)[0]
            for r in evaluate_test(ts, U['test'], cfg):
                fam_seq.append(dict(enrolled_user=user, target=target, mechanism=name, params=json.dumps(grid[i]), **r))
    return fac_ops, fac_seq, fam_ops, fam_seq, rej

# ------------------------------------------------------------------------------------------
def user_means(seq, keys):
    return seq.groupby(keys)[SEQ_METRICS].mean().reset_index()

def paired_boot_diff(a, b, seed=0):
    d = np.asarray(a, float) - np.asarray(b, float)
    return D.bootstrap_mean_ci(d, n_boot=N_BOOT, seed=seed)

def primary_analysis(fac_ops, fac_pu, out):
    """§3.1. Cell selection on CALIBRATION FRR only; tests on TEST data."""
    os.makedirs(out, exist_ok=True)
    ops = fac_ops[(fac_ops.target == PRIMARY_TARGET) & fac_ops.feasible.astype(bool)]
    sel = []
    for u, g in ops.groupby('enrolled_user'):
        row = dict(enrolled_user=u)
        for lab, cls in (('H', 'hysteresis'), ('D', 'dwell_only'), ('M', 'margin_only')):
            c = g[g.cell_class == cls].copy()
            if len(c):
                c['_cx'] = c.margin + c.dwell
                best = c.sort_values(['calib_FRR', '_cx', 'calib_FAR', 'cell']).iloc[0]
                row[f'cell_{lab}'] = best.cell; row[f'cell_{lab}_calib_FRR'] = best.calib_FRR
            else:
                row[f'cell_{lab}'] = None; row[f'cell_{lab}_calib_FRR'] = np.nan
        sel.append(row)
    sel = pd.DataFrame(sel); sel.to_csv(os.path.join(out, 'cell_selection.csv'), index=False)
    pu = fac_pu[fac_pu.target == PRIMARY_TARGET].set_index(['enrolled_user', 'cell'])
    def val(u, c, k):
        return pu.loc[(u, c), k] if c is not None and (u, c) in pu.index else np.nan
    tests, curve = [], []
    ps = []
    for comp in ('D', 'M'):
        pair = sel.dropna(subset=['cell_H', f'cell_{comp}'])
        users = pair.enrolled_user.tolist()
        get = lambda lab, k: np.array([val(u, c, k) for u, c in zip(users, pair[f'cell_{lab}'])])
        xH, xC = get('H', 'excess_transitions'), get(comp, 'excess_transitions')
        W, p = D.wilcoxon_paired(xH, xC)
        frr = paired_boot_diff(get('H', 'FRR'), get(comp, 'FRR'), seed=1)
        dfl = paired_boot_diff(get('H', 'detection_failure'), get(comp, 'detection_failure'), seed=2)
        ps.append(p)
        tests.append(dict(comparison=f'cell_H vs cell_{comp}', n_users_paired=len(users),
                          n_users_without_H=int(sel.cell_H.isna().sum()),
                          n_users_without_comparator=int(sel[f'cell_{comp}'].isna().sum()),
                          excess_H_mean=float(np.nanmean(xH)) if len(xH) else np.nan,
                          excess_comp_mean=float(np.nanmean(xC)) if len(xC) else np.nan,
                          excess_diff_mean=float(np.nanmean(xH - xC)) if len(xH) else np.nan,
                          excess_diff_median=float(np.nanmedian(xH - xC)) if len(xH) else np.nan,
                          wilcoxon_W=W, p_value=p,
                          FRR_diff_mean=frr['mean'], FRR_diff_lo=frr['lo'], FRR_diff_hi=frr['hi'],
                          detfail_diff_mean=dfl['mean'], detfail_diff_lo=dfl['lo'], detfail_diff_hi=dfl['hi']))
        for lvl in (0.80, 0.90, 0.95, 0.99):
            for metric, a, b, sd in (('FRR', get('H', 'FRR'), get(comp, 'FRR'), 1),
                                     ('detection_failure', get('H', 'detection_failure'), get(comp, 'detection_failure'), 2)):
                ci = D.bootstrap_mean_ci(a - b, n_boot=N_BOOT, seed=sd, alpha=1 - lvl)
                curve.append(dict(comparison=f'cell_H vs cell_{comp}', metric=metric, ci_level=lvl,
                                  diff_mean=ci['mean'], lo=ci['lo'], hi=ci['hi']))
    ph = D.holm(ps)
    for t, p in zip(tests, ph):
        t['p_holm'] = p
        t['c1_fewer_excess_significant'] = bool(np.isfinite(p) and p < 0.05 and t['excess_diff_mean'] < 0)
        t['c2_FRR_noninferior'] = bool(np.isfinite(t['FRR_diff_hi']) and t['FRR_diff_hi'] < NI_MARGIN)
        t['c3_detfail_noninferior'] = bool(np.isfinite(t['detfail_diff_hi']) and t['detfail_diff_hi'] < NI_MARGIN)
    T = pd.DataFrame(tests); T.to_csv(os.path.join(out, 'primary_tests.csv'), index=False)
    pd.DataFrame(curve).to_csv(os.path.join(out, 'frr_difference_curve.csv'), index=False)
    met = bool(len(T) == 2 and T.c1_fewer_excess_significant.all() and T.c2_FRR_noninferior.all()
               and T.c3_detfail_noninferior.all())
    verdict = ('Hysteresis earns its place on this benchmark: all three preregistered criteria are met against '
               'both dwell-only and margin-only.' if met else
               'Hysteresis offers no measurable advantage over its components on this benchmark.')
    with open(os.path.join(out, 'PRIMARY_DECISION.md'), 'w') as f:
        f.write('# Primary decision (PREREGISTRATION_v2 §3.1)\n\n')
        f.write('Generated mechanically by scripts/decision_layer_offline.py. Target FAR 0.05, one-sided band '
                '[0.04, 0.05], selection C1 with reachability filter C2, only theta tuned per cell.\n\n')
        f.write(f'**Verdict: {verdict}**\n\n')
        f.write('```\n' + T.T.to_string() + '\n```')
        f.write('\n\nCriteria: (1) fewer excess transitions, paired two-sided Wilcoxon, Holm-adjusted p < 0.05 across '
                'the two comparisons, mean difference < 0; (2) upper 95% bootstrap bound of paired FRR difference '
                f'< +{NI_MARGIN}; (3) same for detection-failure rate. Users lacking an eligible cell for either member '
                'of a pair are excluded from that pair and counted above.\n')
    return met, T

def family_analysis(fam_ops, fam_seq, out, target):
    os.makedirs(out, exist_ok=True)
    seq = fam_seq[fam_seq.target == target]
    if seq.empty:
        return
    pu = user_means(seq, ['enrolled_user', 'mechanism'])
    pu.to_csv(os.path.join(out, 'participant_metrics.csv'), index=False)
    rows = []
    ops = fam_ops[fam_ops.target == target]
    for mname in D.FAMILY_ORDER:
        g = pu[pu.mechanism == mname]; o = ops[ops.mechanism == mname]
        r = dict(mechanism=mname, n_users_feasible=len(g), n_users_infeasible=int((~o.feasible.astype(bool)).sum()),
                 n_sequences=int((seq.mechanism == mname).sum()))
        for k in SEQ_METRICS:
            ci = D.bootstrap_mean_ci(g[k], n_boot=N_BOOT, seed=0)
            r[f'{k}_mean'], r[f'{k}_lo'], r[f'{k}_hi'] = ci['mean'], ci['lo'], ci['hi']
        lo, hi = target - 0.01, target
        r['test_FAR_matched'] = bool(np.isfinite(r['FAR_lo']) and r['FAR_lo'] <= hi and r['FAR_hi'] >= lo)
        rows.append(r)
    pd.DataFrame(rows).to_csv(os.path.join(out, 'mechanism_metrics.csv'), index=False)
    # calibration-to-test FAR drift, per user then averaged
    cal = ops[ops.feasible.astype(bool)][['enrolled_user', 'mechanism', 'calib_FAR']]
    dr = pu[['enrolled_user', 'mechanism', 'FAR']].merge(cal, on=['enrolled_user', 'mechanism'])
    dr['drift'] = dr.FAR - dr.calib_FAR
    dr.groupby('mechanism').drift.agg(['mean', 'median', 'count']).reset_index().to_csv(os.path.join(out, 'far_drift.csv'), index=False)
    tests = []
    for k in ['excess_transitions', 'FRR', 'FAR', 'detection_failure', 'recovery_failure',
              'detection_latency_censored', 'recovery_latency_censored']:
        piv = pu.pivot_table(index='enrolled_user', columns='mechanism', values=k)
        raw = []
        for mname in D.FAMILY_ORDER[1:]:
            if mname not in piv or 'instantaneous' not in piv:
                continue
            d = piv[['instantaneous', mname]].dropna()
            W, p = D.wilcoxon_paired(d[mname], d['instantaneous'])
            raw.append(dict(metric=k, mechanism=mname, baseline='instantaneous', n_users=len(d),
                            mean_difference=float((d[mname] - d['instantaneous']).mean()) if len(d) else np.nan,
                            wilcoxon_W=W, p_value=p))
        for r, p in zip(raw, D.holm([r['p_value'] for r in raw])):
            r['p_holm'] = p; r['significant_holm_005'] = bool(np.isfinite(p) and p < 0.05)
        tests += raw
    pd.DataFrame(tests).to_csv(os.path.join(out, 'statistical_tests.csv'), index=False)

def no_sprt_subset(fam_ops, fam_seq, out):
    ops = fam_ops[(fam_ops.target == PRIMARY_TARGET) & (fam_ops.mechanism != 'sprt')]
    ok = ops.groupby('enrolled_user').feasible.apply(lambda x: bool(x.astype(bool).all()))
    users = ok[ok].index.tolist()
    sub_ops = fam_ops[fam_ops.enrolled_user.isin(users) & (fam_ops.mechanism != 'sprt')]
    sub_seq = fam_seq[fam_seq.enrolled_user.isin(users) & (fam_seq.mechanism != 'sprt')]
    d = os.path.join(out, 'no_sprt_subset'); os.makedirs(d, exist_ok=True)
    json.dump(dict(n_users=len(users), users=users, rule='all mechanisms except SPRT have an eligible '
                   'calibration operating point at FAR 0.05 (calibration data only)'),
              open(os.path.join(d, 'subset.json'), 'w'), indent=2)
    family_analysis(sub_ops, sub_seq, d, PRIMARY_TARGET)

def score_validity(f3_users, f7_dir, out):
    rows = []
    for U3 in f3_users:
        u = U3['enrolled_user']
        c = glob.glob(os.path.join(f7_dir, u[:8] + '.parquet')) + glob.glob(os.path.join(f7_dir, u[:8] + '.csv.gz'))
        if not c:
            rows.append(dict(enrolled_user=u, AUC_F3=np.nan, AUC_F7=np.nan, note='F7 dump missing')); continue
        U7 = load_user(c[0])
        a3 = [(s['sequence_id'], s['impostor_user'], tuple(s['truth'])) for s in U3['test']]
        a7 = [(s['sequence_id'], s['impostor_user'], tuple(s['truth'])) for s in U7['test']]
        same = a3 == a7
        s3, y3 = stack(U3['test'], 'raw_score'); s7, y7 = stack(U7['test'], 'raw_score')
        rows.append(dict(enrolled_user=u, identical_sequences=same, AUC_F3=D.auc(y3.ravel(), s3.ravel()),
                         AUC_F7=D.auc(y7.ravel(), s7.ravel()), note='' if same else 'SEQUENCES DIFFER: not comparable'))
    R = pd.DataFrame(rows); R['diff_F3_minus_F7'] = R.AUC_F3 - R.AUC_F7
    R.to_csv(os.path.join(out, 'score_validity_f3_f7.csv'), index=False)
    ok = R[R.get('identical_sequences', False) == True]
    ci = D.bootstrap_mean_ci(ok.diff_F3_minus_F7, n_boot=N_BOOT, seed=3)
    json.dump(dict(n_users=int(len(ok)), mean_AUC_F3=float(ok.AUC_F3.mean()) if len(ok) else None,
                   mean_AUC_F7=float(ok.AUC_F7.mean()) if len(ok) else None, diff=ci,
                   note='Descriptive construct-validity probe (§4.4). No decision layer is run on F7.'),
              open(os.path.join(out, 'score_validity_summary.json'), 'w'), indent=2, default=float)

# ------------------------------------------------------------------------------------------
def synthetic_dump(d, n_users=8, seed=0):
    """Synthetic score files in the dump schema, for --self-test only. Never real data."""
    rng = np.random.default_rng(seed); os.makedirs(d, exist_ok=True)
    for u in range(n_users):
        rows = []
        for split, n in (('calib', 24), ('test', 6)):
            for k in range(n):
                truth = np.r_[np.ones(60), np.zeros(60), np.ones(60)].astype(int)
                raw = np.where(truth == 1, rng.normal(1.5, 1.2, 180), rng.normal(-1.5, 1.2, 180))
                raw += np.convolve(rng.normal(0, 0.8, 184), np.ones(5) / 5, 'valid')
                score = 1 / (1 + np.exp(-raw))
                rows.append(pd.DataFrame(dict(enrolled_user=f'{u:08X}-SYNTH', split=split,
                                              sequence_id=f'{u:08X}_{split[:3]}s{k}', impostor_user=f'IMP{k % 12}',
                                              frame=np.arange(180), score=score, raw_score=raw, truth=truth,
                                              transition_idx=60, recovery_idx=120)))
        pd.concat(rows).to_csv(os.path.join(d, f'{u:08X}.csv.gz'), index=False)
    return d

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', default=os.path.join(HERE, 'configs', 'v2_scoredump_f3.json'))
    ap.add_argument('--scores'); ap.add_argument('--f7-scores'); ap.add_argument('--out', required=True)
    ap.add_argument('--self-test', action='store_true', help='run end-to-end on synthetic scores only')
    ap.add_argument('--allow-dirty', action='store_true',
                    help='permit uncommitted analysis code (the run is then flagged NOT CONFIRMATORY)')
    ap.add_argument('--max-users', type=int)
    a = ap.parse_args(); cfg = json.load(open(a.config))
    os.makedirs(a.out, exist_ok=True)
    prov = provenance(a)
    if a.self_test:
        a.scores = synthetic_dump(os.path.join(a.out, '_synthetic_scores')); prov['self_test'] = True
    elif prov['analysis_code_dirty'] and not a.allow_dirty:
        sys.exit('REFUSING TO RUN: analysis code has uncommitted changes. Commit first so the v2 analysis is '
                 'tied to a frozen commit, or pass --allow-dirty (run is then labelled NOT CONFIRMATORY).')
    prov['confirmatory'] = bool(not a.self_test and not prov['analysis_code_dirty'])
    json.dump(prov, open(os.path.join(a.out, 'experiment_metadata.json'), 'w'), indent=2)
    files = sorted(glob.glob(os.path.join(a.scores, '*.parquet')) + glob.glob(os.path.join(a.scores, '*.csv.gz')))
    files = files[:a.max_users] if a.max_users else files
    targets = (PRIMARY_TARGET,) + SENSITIVITY_TARGETS
    acc = [[], [], [], [], []]; users = []
    for i, f in enumerate(files, 1):
        t0 = time.time(); U = load_user(f); users.append(U)
        for store, part in zip(acc, analyse_user(U, cfg, targets)):
            store += part
        print(f'[{i}/{len(files)}] {U["enrolled_user"][:8]} ({time.time() - t0:.1f}s)', flush=True)
    fac_ops, fac_seq, fam_ops, fam_seq, rej = (pd.DataFrame(x) for x in acc)
    for sub in ('factorial', 'primary', 'families', 'secondary'):
        os.makedirs(os.path.join(a.out, sub), exist_ok=True)
    fac_ops.to_csv(os.path.join(a.out, 'factorial', 'operating_points.csv'), index=False)
    fac_seq.to_csv(os.path.join(a.out, 'factorial', 'sequence_metrics.csv'), index=False)
    fac_pu = user_means(fac_seq, ['enrolled_user', 'target', 'cell', 'margin', 'dwell', 'cell_class'])
    fac_pu.to_csv(os.path.join(a.out, 'factorial', 'participant_metrics.csv'), index=False)
    surf = fac_pu.groupby(['target', 'margin', 'dwell', 'cell_class'])[SEQ_METRICS].mean().reset_index()
    feas = fac_ops.groupby(['target', 'margin', 'dwell']).feasible.apply(lambda x: int(x.astype(bool).sum())).rename('n_users_feasible')
    surf.merge(feas.reset_index(), on=['target', 'margin', 'dwell']).to_csv(
        os.path.join(a.out, 'factorial', 'response_surface.csv'), index=False)
    met, T = primary_analysis(fac_ops, fac_pu, os.path.join(a.out, 'primary'))
    fam_ops.to_csv(os.path.join(a.out, 'families', 'operating_points.csv'), index=False)
    fam_seq.to_csv(os.path.join(a.out, 'families', 'sequence_metrics.csv'), index=False)
    rej.to_csv(os.path.join(a.out, 'families', 'reachability_rejections.csv'), index=False)
    family_analysis(fam_ops, fam_seq, os.path.join(a.out, 'families'), PRIMARY_TARGET)
    for t in SENSITIVITY_TARGETS:
        family_analysis(fam_ops, fam_seq, os.path.join(a.out, 'secondary', f'far_{t:.2f}'), t)
    no_sprt_subset(fam_ops, fam_seq, os.path.join(a.out, 'secondary'))
    if a.f7_scores:
        score_validity(users, a.f7_scores, os.path.join(a.out, 'secondary'))
    prov.update(finished=time.strftime('%Y-%m-%dT%H:%M:%S'), n_users=len(users), primary_criterion_met=met)
    json.dump(prov, open(os.path.join(a.out, 'experiment_metadata.json'), 'w'), indent=2)
    print('PRIMARY CRITERION MET' if met else 'PRIMARY CRITERION NOT MET')

if __name__ == '__main__':
    main()
