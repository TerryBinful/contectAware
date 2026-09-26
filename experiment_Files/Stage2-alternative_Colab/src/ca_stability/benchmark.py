"""Stage D — controlled identity-transition benchmark (implements docs/planning/02_splice_benchmark_spec.md).

For every genuine user g and partition P in {val, test}:

  * PURE GENUINE STREAMS: g's contiguous runs in P with >= `min_stream_frames` frames. These
    carry the genuine-side outcomes (false locks, FRR_time, transitions, ping-pong).
  * SPLICED SEQUENCES (target -> impostor -> target return), per condition c in {X, M} and
    impostor block length L in `L_frames`, `sequences_per_L` sequences:

        seq   = g_run[s-pre : s] ++ i_run[b : b+L] ++ g_run[s : s+suf]
        truth =  1 ... 1           0 ... 0           1 ... 1
        switch column = pre, return column = pre + L

    s ~ Uniform{W, ..., len(g_run) - W} over runs chosen proportional to len - 2W (so both genuine
    flanks have >= W frames); pre = min(s, prefix_cap) (burn-in); suf = min(len - s, suffix_cap).
    The impostor comes from impostor_cal(g) for P = val and impostor_test(g) for P = test, and
    the impostor frames come from that impostor's own P-period, so every impostor is unseen by
    g's model. Impostors are cycled in a seeded order; block starts are uniform over valid
    positions. Condition M additionally requires the impostor's dominant context label over the
    first W frames of its block to equal g's dominant label over the W frames before the splice
    (labels are used ONLY for alignment, never as features).

Construction is SCORE-BLIND: nothing in the selection logic reads a classifier score. Scores are
attached afterwards from the fixed score generator (Stage C). Everything is deterministic given
(dataset, split, seed, config).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .provenance import LOG, write_json
from .splits import user_seed

NO_LABEL = -1
PARTITION_IMPOSTOR_ROLE = {"val": "impostor_cal", "test": "impostor_test"}
PARTITION_SCORE_ROLE = {"val": "imp_cal", "test": "imp_test"}


# ----------------------------------------------------------------------------- context labels
def dominant_label_codes(label_matrix: np.ndarray) -> np.ndarray:
    """Per frame-window dominant label: argmax of positive counts, ties -> earliest in list,
    NO_LABEL if no context label is positive. label_matrix: (n_windows, n_labels) counts."""
    has = label_matrix.max(axis=1) > 0
    return np.where(has, np.argmax(label_matrix, axis=1), NO_LABEL)


def window_counts(labels: np.ndarray, start: int, W: int) -> np.ndarray:
    return labels[start:start + W].sum(axis=0)


# ----------------------------------------------------------------------------- run tables
def runs_of(frames: pd.DataFrame, uuid: str, period: str) -> list[np.ndarray]:
    """Row indices (into `frames`) of each contiguous run of `uuid` in `period`, time-ordered.
    Rows of one run are consecutive integers because frames are sorted by (uuid, timestamp)."""
    m = (frames.uuid.values == uuid) & (frames.period.values == period)
    rows = np.flatnonzero(m)
    if len(rows) == 0:
        return []
    run = frames.run.values[rows]
    cut = np.flatnonzero(np.diff(run) != 0) + 1
    return [r for r in np.split(rows, cut)]


def block_starts(runs: list[np.ndarray], LAB: np.ndarray, W: int) -> pd.DataFrame:
    """Every candidate impostor block start: run index, position, frames remaining in the run,
    and the dominant context label over the first min(W, remaining) frames (score-blind)."""
    out = []
    for ri, rr in enumerate(runs):
        n = len(rr)
        C = np.vstack([np.zeros((1, LAB.shape[1]), dtype=np.int32), np.cumsum(LAB[rr], axis=0, dtype=np.int32)])
        st = np.arange(n)
        end = np.minimum(st + W, n)
        counts = C[end] - C[st]
        out.append(pd.DataFrame({"run_idx": ri, "pos": st, "remaining": n - st, "dom": dominant_label_codes(counts)}))
    if not out:
        return pd.DataFrame(columns=["run_idx", "pos", "remaining", "dom"])
    return pd.concat(out, ignore_index=True)


# ----------------------------------------------------------------------------- builder
def build_benchmark(cfg: dict, frames: pd.DataFrame, split: dict) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Returns (genuine_streams, manifest, coverage). Score-blind."""
    b = cfg["benchmark"]
    W, prefix_cap, suffix_cap = int(b["W"]), int(b["prefix_cap"]), int(b["suffix_cap"])
    min_stream = int(b["min_stream_frames"])
    Ls = [int(x) for x in b["L_frames"]]
    n_per = int(b["sequences_per_L"])
    seed = int(cfg["experiment"]["seed"])
    ctx_cols = [c for c in b["context_labels"] if c in frames.columns]
    missing = sorted(set(b["context_labels"]) - set(ctx_cols))
    if missing:
        raise RuntimeError(f"DATA: context label columns missing from the data: {missing}")
    LAB = frames[ctx_cols].to_numpy(dtype=np.int16)

    gen_rows, man_rows = [], []
    cover = []
    for g in split["genuine_users"]:
        roles = split["roles"][g]
        for part in ("val", "test"):
            g_runs = runs_of(frames, g, part)
            for r in g_runs:
                if len(r) >= min_stream:
                    gen_rows.append({"genuine_uuid": g, "partition": part, "run": int(frames.run.values[r[0]]),
                                     "first_row": int(r[0]), "length": int(len(r))})
            host = [r for r in g_runs if len(r) >= 2 * W + 1]
            if not host:
                raise RuntimeError(f"DATA: {g} has no {part} run long enough to host a splice")
            host_w = np.array([len(r) - 2 * W + 1 for r in host], dtype=float)
            imps = roles[PARTITION_IMPOSTOR_ROLE[part]]
            imp_runs = {u: runs_of(frames, u, part) for u in imps}
            imp_starts = {u: block_starts(imp_runs[u], LAB, W) for u in imps}
            for cond in cfg["benchmark"]["conditions"]:
                for L in Ls:
                    rng = np.random.default_rng(user_seed(seed, "bench", g, part, cond, L))
                    order = [imps[i] for i in rng.permutation(len(imps))]
                    got, attempts, seen = 0, 0, set()
                    while got < n_per and attempts < int(b["max_attempts"]):
                        attempts += 1
                        hr = host[rng.choice(len(host), p=host_w / host_w.sum())]
                        s = int(rng.integers(W, len(hr) - W + 1))
                        g_dom = int(dominant_label_codes(window_counts(LAB, hr[s - W], W)[None])[0])
                        if cond == "M" and g_dom == NO_LABEL:
                            continue
                        chosen = None
                        for k in range(len(order)):          # cycle impostors starting at seq index
                            u = order[(got + k) % len(order)]
                            bs = imp_starts[u]
                            ok = bs.remaining.values >= (max(L, W) if cond == "M" else L)
                            if cond == "M":
                                ok &= bs.dom.values == g_dom
                            cand = np.flatnonzero(ok)
                            if len(cand):
                                j = cand[int(rng.integers(len(cand)))]
                                chosen = (u, int(bs.run_idx.values[j]), int(bs.pos.values[j]))
                                break
                        if chosen is None:
                            continue
                        u, ri, st = chosen
                        key = (int(hr[0]), s, u, ri, st)
                        if key in seen:
                            continue
                        seen.add(key)
                        ir = imp_runs[u][ri]
                        i_dom = int(imp_starts[u].dom.values[(imp_starts[u].run_idx.values == ri) & (imp_starts[u].pos.values == st)][0])
                        pre, suf = min(s, prefix_cap), min(len(hr) - s, suffix_cap)
                        man_rows.append({
                            "genuine_uuid": g, "impostor_uuid": u, "condition": cond,
                            "L_min": L * float(cfg["_meta"].get("frame_period_s", 60.0)) / 60.0, "L_frames": L,
                            "splice_idx": pre, "return_idx": pre + L,
                            "dominant_label_g": ctx_cols[g_dom] if g_dom != NO_LABEL else "",
                            "dominant_label_i": ctx_cols[i_dom] if i_dom != NO_LABEL else "",
                            "seed": user_seed(seed, "bench", g, part, cond, L), "partition": part,
                            "g_run": int(frames.run.values[hr[0]]), "g_run_len": int(len(hr)), "g_splice_pos": s,
                            "prefix_len": pre, "suffix_len": suf,
                            "g_prefix_first_row": int(hr[s - pre]), "g_return_first_row": int(hr[s]),
                            "imp_run": int(frames.run.values[ir[0]]), "imp_block_first_row": int(ir[st]),
                            "t_splice": int(frames.timestamp.values[hr[s - 1]]),
                            "t_imp_block": int(frames.timestamp.values[ir[st]]),
                            "attempt": attempts,
                        })
                        got += 1
                    cover.append({"genuine_uuid": g, "partition": part, "condition": cond, "L_frames": L,
                                  "n_sequences": got, "attempts": attempts})
                    if got < n_per:
                        LOG.info("benchmark: %s %s %s L=%d -> %d/%d sequences", g[:8], part, cond, L, got, n_per)
    streams = pd.DataFrame(gen_rows)
    man = pd.DataFrame(man_rows)
    man.insert(0, "seq_id", [f"{r.partition}-{r.genuine_uuid[:8]}-{r.condition}-L{r.L_frames:02d}-{i:05d}"
                             for i, r in enumerate(man.itertuples())])
    cov = pd.DataFrame(cover)
    coverage = {}
    for part in ("val", "test"):
        for cond in cfg["benchmark"]["conditions"]:
            c = cov[(cov.partition == part) & (cov.condition == cond)]
            coverage[f"{part}_{cond}_frac_g_L_with_any"] = float((c.n_sequences > 0).mean())
            coverage[f"{part}_{cond}_frac_g_L_full"] = float((c.n_sequences >= n_per).mean())
            coverage[f"{part}_{cond}_n_sequences"] = int(c.n_sequences.sum())
    if "M" in cfg["benchmark"]["conditions"]:
        coverage["M_coverage_min"] = min(coverage["val_M_frac_g_L_with_any"], coverage["test_M_frac_g_L_with_any"])
    mode = cfg["operating_point"]["selection_condition"]
    if mode == "auto":
        sel = "M" if coverage.get("M_coverage_min", 0.0) >= cfg["operating_point"]["coverage_threshold"] else "X"
    else:
        sel = mode
    coverage["selection_condition"] = sel
    coverage["per_cell"] = cov.to_dict(orient="records")
    LOG.info("Benchmark: %d genuine streams, %d spliced sequences; M coverage %.3f -> selection condition %s",
             len(streams), len(man), coverage.get("M_coverage_min", float("nan")), sel)
    return streams, man, coverage


# ----------------------------------------------------------------------------- score attachment
def row_scores(scores: dict) -> dict:
    """{g: Series row -> p_cal} for fast lookup (each model's own scores)."""
    return {g: pd.Series(s.p_cal.values, index=s.row.values) for g, s in scores.items()}


def assemble(frames: pd.DataFrame, streams: pd.DataFrame, man: pd.DataFrame, scores: dict):
    """Attach scores. Returns (genuine long table, sequence long table)."""
    rs = row_scores(scores)
    run_rows = {}
    g_long, s_long = [], []
    for st in streams.itertuples():
        rows = np.arange(st.first_row, st.first_row + st.length)
        assert (frames.uuid.values[rows] == st.genuine_uuid).all() and (frames.run.values[rows] == st.run).all()
        g_long.append(pd.DataFrame({"genuine_uuid": st.genuine_uuid, "partition": st.partition, "run": st.run,
                                    "t": np.arange(st.length), "row": rows,
                                    "p_cal": rs[st.genuine_uuid].loc[rows].values}))
    for m in man.itertuples():
        pre_rows = np.arange(m.g_prefix_first_row, m.g_prefix_first_row + m.prefix_len)
        imp_rows = np.arange(m.imp_block_first_row, m.imp_block_first_row + m.L_frames)
        ret_rows = np.arange(m.g_return_first_row, m.g_return_first_row + m.suffix_len)
        rows = np.concatenate([pre_rows, imp_rows, ret_rows])
        truth = np.r_[np.ones(m.prefix_len, np.int8), np.zeros(m.L_frames, np.int8), np.ones(m.suffix_len, np.int8)]
        s_long.append(pd.DataFrame({"seq_id": m.seq_id, "t": np.arange(len(rows)), "row": rows,
                                    "uuid": frames.uuid.values[rows], "truth": truth,
                                    "p_cal": rs[m.genuine_uuid].loc[rows].values}))
    return pd.concat(g_long, ignore_index=True), pd.concat(s_long, ignore_index=True)


# ----------------------------------------------------------------------------- leakage checks
def leakage_checks(cfg: dict, frames: pd.DataFrame, split: dict, streams: pd.DataFrame, man: pd.DataFrame,
                   seq_long: pd.DataFrame, gen_long: pd.DataFrame) -> dict:
    """Explicit checks that FAIL (passed=False) if any leakage path exists. Callers must stop on failure."""
    res = {}
    gap_break = float(cfg["_meta"]["run_break_gap_s"])
    emb = float(cfg["periods"]["embargo_minutes"]) * 60.0

    def add(name, ok, detail=""):
        res[name] = {"passed": bool(ok), "detail": detail}

    # 1. impostor roles
    bad = []
    for m in man.itertuples():
        r = split["roles"][m.genuine_uuid]
        if m.impostor_uuid not in r[PARTITION_IMPOSTOR_ROLE[m.partition]] or m.impostor_uuid in r["impostor_train"] \
                or m.impostor_uuid == m.genuine_uuid:
            bad.append(m.seq_id)
    add("impostor_is_unseen_and_role_correct", not bad, f"{len(bad)} violating sequences" if bad else "all sequences")
    # 2. period purity: every frame of a partition-P object comes from period P
    per = frames.period.values
    sp = seq_long.merge(man[["seq_id", "partition"]], on="seq_id")
    bad_seq = int((per[sp.row.values] != sp.partition.values).sum())
    bad_gen = int((per[gen_long.row.values] != gen_long.partition.values).sum())
    add("period_purity", bad_seq == 0 and bad_gen == 0, f"sequence frames off-period: {bad_seq}; stream frames off-period: {bad_gen}")
    # 3. no evaluation frame is a training frame of the evaluated model
    sp = sp.merge(man[["seq_id", "genuine_uuid", "impostor_uuid", "splice_idx", "return_idx"]], on="seq_id")
    viol = 0
    for g, grp in sp.groupby("genuine_uuid"):
        r = split["roles"][g]
        rows = grp.row.values
        viol += int(((per[rows] == "train") & np.isin(frames.uuid.values[rows], list(set(r["impostor_train"]) | {g}))).sum())
    for g, grp in gen_long.groupby("genuine_uuid"):
        viol += int((per[grp.row.values] == "train").sum())
    add("no_training_frame_in_evaluation", viol == 0, f"{viol} frames")
    # 4. temporal separation: genuine evaluation frames are >= embargo after g's last training frame
    ts, uu = frames.timestamp.values, frames.uuid.values
    worst = np.inf
    for g in split["genuine_users"]:
        tr = ts[(uu == g) & (per == "train")]
        ev = np.r_[gen_long.row.values[gen_long.genuine_uuid.values == g],
                   sp.row.values[(sp.genuine_uuid.values == g) & (sp.truth.values == 1)]]
        if len(tr) and len(ev):
            worst = min(worst, float(ts[ev].min() - tr.max()))
    add("embargo_between_train_and_evaluation", worst >= emb, f"min gap {worst:.0f}s vs embargo {emb:.0f}s")
    # 5. the uuid of every frame is the identity the ground truth says it is
    exp = np.where(sp.truth.values == 1, sp.genuine_uuid.values, sp.impostor_uuid.values)
    add("segment_identity_matches_truth", bool((sp.uuid.values == exp).all()))
    # 6. within-segment continuity: no gap > run-break inside any segment; no duplicated frames
    seg = np.where(sp.t.values < sp.splice_idx.values, 0, np.where(sp.t.values < sp.return_idx.values, 1, 2))
    tmp = pd.DataFrame({"seq_id": sp.seq_id.values, "seg": seg, "ts": ts[sp.row.values]})
    d = tmp.groupby(["seq_id", "seg"]).ts.agg(lambda x: float(np.max(np.diff(x.values))) if len(x) > 1 else 0.0)
    dup = int(sp.duplicated(["seq_id", "row"]).sum())
    add("segment_continuity_no_gap_gt_run_break", bool((d <= gap_break).all()) and dup == 0,
        f"max within-segment gap {d.max():.0f}s (limit {gap_break:.0f}s); duplicated frames {dup}")
    # 7. genuine return frames are later than the prefix frames (the splice does not reverse time)
    rev = int((man.t_splice.values >= frames.timestamp.values[man.g_return_first_row.values]).sum())
    add("genuine_time_order_preserved", rev == 0, f"{rev} sequences")
    # 8. every stream frame is the evaluated user's own frame
    add("streams_are_genuine_only", bool((uu[gen_long.row.values] == gen_long.genuine_uuid.values).all()))
    res["all_passed"] = all(v["passed"] for k, v in res.items() if isinstance(v, dict))
    return res


def run_benchmark(cfg, frames, split, scores, out_dir: Path, work_dir: Path):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    streams, man, coverage = build_benchmark(cfg, frames, split)
    gen_long, seq_long = assemble(frames, streams, man, scores)
    checks = leakage_checks(cfg, frames, split, streams, man, seq_long, gen_long)
    write_json(checks, out_dir / "leakage_checks.json")
    if not checks["all_passed"]:
        failed = [k for k, v in checks.items() if isinstance(v, dict) and not v["passed"]]
        raise RuntimeError(f"CODE/LEAKAGE: benchmark leakage checks failed: {failed}")
    man.to_csv(out_dir / "manifest.csv", index=False)
    streams.to_csv(out_dir / "genuine_streams.csv", index=False)
    cov = dict(coverage)
    per_cell = pd.DataFrame(cov.pop("per_cell"))
    per_cell.to_csv(out_dir / "coverage_per_cell.csv", index=False)
    write_json(cov, out_dir / "coverage.json")
    # score streams: compact, committed (derived, non-identifying beyond the public uuid)
    gen_long[["genuine_uuid", "partition", "run", "t", "row", "p_cal"]].to_parquet(out_dir / "genuine_stream_scores.parquet", index=False)
    seq_long[["seq_id", "t", "row", "uuid", "truth", "p_cal"]].to_parquet(out_dir / "sequence_scores.parquet", index=False)
    Path(work_dir).mkdir(parents=True, exist_ok=True)
    return streams, man, cov, gen_long, seq_long
