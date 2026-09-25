"""Leakage tests for the post-pivot experiment. These FAIL if any protocol boundary is violated.

They run against generated artefacts (manifests + benchmark audit) so that a completed run can be
re-verified by a reviewer without re-running the experiment:

    python tests/test_leakage.py results/mechanism_comparison
"""
import json, os, re, sys
import pandas as pd

UUID = re.compile(r'[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}', re.I)

def uuids(cell):
    """Participant ids from a manifest cell (stored as a list repr, possibly numpy-quoted)."""
    return set(UUID.findall(str(cell)))

def check(out):
    fails, checks = [], []
    def ok(name, cond, detail=''):
        checks.append((name, bool(cond), detail))
        if not cond:
            fails.append(f'{name}: {detail}')

    split = json.load(open(os.path.join(out, 'manifests', 'participant_split.json')))
    f, c, t = (set(split['pools'][k]) for k in ('impostor_fit', 'impostor_calib', 'impostor_test'))
    ok('impostor_pools_pairwise_disjoint', not (f & c or f & t or c & t),
       f'fit&calib={f & c}, fit&test={f & t}, calib&test={c & t}')

    G = pd.read_csv(os.path.join(out, 'score_generator_manifest.csv'))
    fit_used = set()
    for s in G.fit_impostor_participants:
        fit_used |= uuids(s)
    ok('fitting_never_touched_test_impostors', not (fit_used & t), f'overlap={sorted(fit_used & t)[:5]}')
    ok('enrolled_user_never_in_own_fitting_impostors',
       all(r.enrolled_user not in uuids(r.fit_impostor_participants) for r in G.itertuples()))

    B = pd.read_csv(os.path.join(out, 'benchmark', 'sequence_manifest.csv'))
    ok('test_impostors_are_from_the_unseen_pool', set(B.impostor_user) <= t,
       f'unexpected={sorted(set(B.impostor_user) - t)[:5]}')
    ok('enrolled_user_is_never_the_impostor', not B.enrolled_is_impostor.any())
    ok('genuine_and_recovery_blocks_disjoint', B.genuine_recovery_row_overlap.sum() == 0,
       f'overlapping rows={int(B.genuine_recovery_row_overlap.sum())}')
    ok('no_duplicate_genuine_timestamps', B.duplicate_genuine_timestamps.sum() == 0,
       f'duplicates={int(B.duplicate_genuine_timestamps.sum())}')
    ok('all_genuine_blocks_contiguous', B.genuine_blocks_contiguous.all())
    ok('all_impostor_blocks_contiguous', B.impostor_block_contiguous.all())

    S = pd.read_csv(os.path.join(out, 'sequence_metrics.csv'))
    ok('every_mechanism_evaluated_on_identical_sequences',
       S.groupby('mechanism').sequence_id.nunique().nunique() == 1,
       str(S.groupby('mechanism').sequence_id.nunique().to_dict()))
    ok('no_duplicate_user_sequence_mechanism_rows',
       not S.duplicated(['enrolled_user', 'sequence_id', 'mechanism']).any())

    O = pd.read_csv(os.path.join(out, 'operating_points.csv'))
    ok('calibration_recorded_for_every_mechanism_and_user',
       O.groupby('enrolled_user').mechanism.nunique().min() == S.mechanism.nunique())
    ok('parameters_identical_across_test_sequences_of_a_user',
       S.groupby(['enrolled_user', 'mechanism']).params.nunique().max() == 1,
       'parameters must be fixed at calibration, not per test sequence')
    return checks, fails

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'results/mechanism_comparison'
    checks, fails = check(out)
    for n, p, d in checks:
        print(('PASS ' if p else 'FAIL ') + n + (f'  [{d}]' if not p else ''))
    print(f'\n{sum(p for _, p, _ in checks)}/{len(checks)} leakage checks passed')
    sys.exit(1 if fails else 0)
