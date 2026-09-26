"""Controlled identity-transition benchmark.

A sequence is  [ genuine block | impostor block | genuine recovery block ]  where every block is a
CONTIGUOUS run of real observations (consecutive gaps <= max_gap_s) taken from one participant.
Blocks are spliced; the splice is recorded explicitly and no timestamps, scores or observations are
interpolated, resampled or synthesised. The frame index is the time base (1 frame ~ 1 minute,
established by the dataset audit); original timestamps travel with every frame for audit.

Determinism: given dataset, participant split, seed and config, the same sequences are produced.

Leakage control:
  * genuine frames come from the enrolled user's chronologically LATER partition
    (calibration partition for calibration sequences, test partition for test sequences);
  * impostor frames come from participants in the calibration or test impostor pool, which are
    disjoint from each other and from the pool used to fit the score generator.
"""
import numpy as np
from . import protocol

def contiguous_blocks(ts, idx, min_len, max_gap_s):
    """All maximal contiguous runs (within the given index subset) of at least min_len frames."""
    seg = protocol.segments(ts[idx], max_gap_s)
    out = []
    for s in np.unique(seg):
        w = idx[seg == s]
        if len(w) >= min_len:
            out.append(w)
    return out

def _take(blocks, need, rng, exclude=None):
    """Pick a random contiguous window of `need` frames, disjoint from `exclude` (row ids).
    Valid starts are found with a cumulative sum over an exclusion mask (O(n) per block).
    Returns None if no such window exists; frames are never reused across blocks."""
    ex = exclude or set()
    cand = []
    for b in blocks:
        if len(b) < need:
            continue
        bad = np.fromiter((int(r) in ex for r in b), dtype=np.int8, count=len(b))
        c = np.concatenate([[0], np.cumsum(bad)])
        starts = np.flatnonzero((c[need:] - c[:-need]) == 0)
        cand += [(b, int(st)) for st in starts]
    if not cand:
        return None
    b, st = cand[int(rng.integers(len(cand)))]
    return b[st:st + need]


def build_sequences(enrolled, ts_user, idx_partition, impostor_sources, cfg, rng,
                    n_sequences=None, round_robin=False, tag=''):
    """impostor_sources: {uuid: (ts, row_index_array)} -> list of sequence dicts.

    round_robin: cycle deterministically through the impostor pool instead of sampling with
    replacement, so every pool member is represented. Used for CALIBRATION sequences, where v1
    covered at most 6 of the 12 calibration impostors and calibration-to-test FAR drift followed.
    n_sequences overrides cfg['sequences_per_user'] (calibration uses more sequences than test).
    tag distinguishes calibration from test sequence ids, which would otherwise both start at _s0
    and collide when the two splits are concatenated in the score dump.
    """
    Lg, Li, Lr = cfg['block_genuine'], cfg['block_impostor'], cfg['block_recovery']
    gb = contiguous_blocks(ts_user, idx_partition, max(Lg, Lr), cfg['max_gap_s'])
    seqs = []
    imp_ids = sorted(impostor_sources)
    if not gb or not imp_ids:
        return seqs
    n_seq = n_sequences if n_sequences is not None else cfg['sequences_per_user']
    for k in range(n_seq):
        g1 = _take(gb, Lg, rng)
        if g1 is None:
            continue
        g2 = _take(gb, Lr, rng, exclude=set(map(int, g1)))
        iu = imp_ids[k % len(imp_ids)] if round_robin else imp_ids[int(rng.integers(len(imp_ids)))]
        its, iidx = impostor_sources[iu]
        ib = _take(contiguous_blocks(its, iidx, Li, cfg['max_gap_s']), Li, rng)
        if g1 is None or g2 is None or ib is None:
            continue
        seqs.append(dict(
            sequence_id=f'{enrolled[:8]}_{tag}s{k}' if tag else f'{enrolled[:8]}_s{k}', enrolled_user=enrolled, impostor_user=iu,
            genuine_rows=g1, impostor_rows=ib, recovery_rows=g2,
            transition_idx=len(g1), recovery_idx=len(g1) + len(ib), length=len(g1) + len(ib) + len(g2),
            truth=np.r_[np.ones(len(g1)), np.zeros(len(ib)), np.ones(len(g2))].astype(int),
            splice_points=[len(g1), len(g1) + len(ib)],
            genuine_ts=ts_user[g1], impostor_ts=its[ib], recovery_ts=ts_user[g2]))
    return seqs

def sequence_scores(seq, score_user_rows, score_impostor_rows):
    """Assemble the score stream for one sequence from the fixed score generator."""
    return np.r_[score_user_rows(seq['genuine_rows']), score_impostor_rows(seq['impostor_user'], seq['impostor_rows']),
                 score_user_rows(seq['recovery_rows'])]

def audit(seqs):
    """Checks that must hold for every constructed sequence (used by the leakage tests)."""
    rep = []
    for s in seqs:
        gen = np.r_[s['genuine_ts'], s['recovery_ts']]
        rep.append(dict(sequence_id=s['sequence_id'], enrolled_user=s['enrolled_user'], impostor_user=s['impostor_user'],
                        length=s['length'], transition_idx=s['transition_idx'], recovery_idx=s['recovery_idx'],
                        genuine_blocks_contiguous=bool(np.all(np.diff(s['genuine_ts']) <= 90) and np.all(np.diff(s['recovery_ts']) <= 90)),
                        impostor_block_contiguous=bool(np.all(np.diff(s['impostor_ts']) <= 90)),
                        genuine_recovery_row_overlap=int(len(set(map(int, s['genuine_rows'])) & set(map(int, s['recovery_rows'])))),
                        duplicate_genuine_timestamps=int(len(gen) - len(np.unique(gen))),
                        enrolled_is_impostor=bool(s['enrolled_user'] == s['impostor_user']),
                        genuine_span_hours=float((gen.max() - gen.min()) / 3600)))
    return rep
