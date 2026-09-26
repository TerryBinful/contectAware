"""Stages E-G — parameter sweeps, matched operating point, evaluation of the selected cells.

Operating-point procedure (identical for every mechanism; docs/planning/03 §Matched-operating-point):
  1. Sweep every (fixed-parameter combo x sweep value) cell on the VALIDATION partition only.
  2. For each cell compute the pooled genuine false-lock rate  R = sum(false locks) / sum(genuine hours)
     over all genuine users' validation streams (R = 1 / ANGA-time).
  3. Admissible cells: R within target x [1 - tol, 1 + tol] AND mean false-lock duration
     (locked genuine frames / false locks) <= max_lockout_frames. The second condition (amendment
     A1, decided on pilot VALIDATION data) excludes absorbing configurations that meet the rate
     target by never unlocking, e.g. margin with theta + m/2 >= 1.
  4. Among admissible cells choose the lowest validation ANIA statistic = median over users of each
     user's median sustained-detection delay in the selection condition (misses censored at L).
     Tie-breaks: lower mean FAR_frame (access fraction), then smaller |log(R / target)|, then grid order.
  5. If no cell is admissible, choose the cell(s) with the smallest |log(R / target)|, then step 4's
     rule, and flag the mechanism `in_band = False`.
  6. Write operating_points.csv (+ SHA-256) BEFORE any test-partition computation. The test stage
     refuses to run unless the file's hash matches the recorded one.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from .mechanisms.batch import StreamBatch
from .mechanisms.registry import ORDER, params_string
from .metrics import GEN_FIELDS, SEQ_FIELDS, genuine_stream_metrics, rate_per_hour, transition_sequence_metrics
from .provenance import LOG

BUDGET = 12_000_000          # max K*n*T elements per vectorised call (memory bound, ~12 MB per bool array)


# ----------------------------------------------------------------------------- partition container
@dataclass
class PartitionData:
    name: str
    users: list
    gen_batches: list = field(default_factory=list)     # (StreamBatch, stream_index_array)
    stream_meta: pd.DataFrame = None                     # one row per genuine stream, column u (user idx)
    seq_groups: list = field(default_factory=list)       # (L, StreamBatch, seq_index_array)
    seq_meta: pd.DataFrame = None                        # one row per spliced sequence, columns u, cond, L
    C: int = 120

    @property
    def n_streams(self):
        return len(self.stream_meta)

    @property
    def n_seqs(self):
        return len(self.seq_meta)


def _bucket(lengths: np.ndarray, cap: int = 1_500_000, waste: float = 1.25):
    """Group streams (sorted by length) so each padded block wastes <= 25% and has <= cap cells."""
    order = np.argsort(lengths, kind="mergesort")
    buckets, cur = [], []
    for i in order:
        trial = cur + [i]
        T = lengths[trial].max()
        if cur and (len(trial) * T > cap or len(trial) * T > waste * lengths[trial].sum()):
            buckets.append(np.array(cur))
            cur = [i]
        else:
            cur = trial
    if cur:
        buckets.append(np.array(cur))
    return buckets


def build_partition(cfg, part: str, users: list, gen_long: pd.DataFrame, seq_long: pd.DataFrame,
                    man: pd.DataFrame) -> PartitionData:
    uidx = {u: i for i, u in enumerate(users)}
    C = int(cfg["benchmark"]["prefix_cap"])
    g = gen_long[gen_long.partition == part]
    arrays, meta = [], []
    for (uu, run), grp in g.groupby(["genuine_uuid", "run"], sort=True):
        if uu not in uidx:
            continue
        arrays.append(grp.sort_values("t").p_cal.values)
        meta.append({"genuine_uuid": uu, "u": uidx[uu], "run": run, "length": len(grp)})
    smeta = pd.DataFrame(meta)
    pdata = PartitionData(part, users, stream_meta=smeta, C=C)
    for b in _bucket(smeta.length.values):
        pdata.gen_batches.append((StreamBatch.from_arrays([arrays[i] for i in b]), b))
    m = man[(man.partition == part) & man.genuine_uuid.isin(users)].reset_index(drop=True)
    m["u"] = m.genuine_uuid.map(uidx)
    seqs = {sid: grp.sort_values("t").p_cal.values for sid, grp in seq_long[seq_long.seq_id.isin(m.seq_id)].groupby("seq_id")}
    suffix_cap = int(cfg["benchmark"]["suffix_cap"])
    for L in sorted(m.L_frames.unique()):
        idx = np.flatnonzero(m.L_frames.values == L)
        arr = [seqs[m.seq_id.values[i]] for i in idx]
        starts = C - m.prefix_len.values[idx]
        sb = StreamBatch.from_arrays(arr, starts=starts, T=C + int(L) + suffix_cap)
        pdata.seq_groups.append((int(L), sb, idx))
    pdata.seq_meta = m
    return pdata


# ----------------------------------------------------------------------------- core evaluation
def run_cells(spec, combo: dict, values: np.ndarray, pdata: PartitionData, ctx: dict, W_pp: int, n_sustain: int):
    """Evaluate one combo for a vector of sweep values. Returns (gen, seq):
    gen[field] (K, n_streams) and seq[field] (K, n_seqs), in pdata's stream / sequence order."""
    K = len(values)
    gen = {f: np.zeros((K, pdata.n_streams), dtype=np.int64) for f in GEN_FIELDS}
    seq = {f: np.zeros((K, pdata.n_seqs), dtype=np.int64) for f in SEQ_FIELDS}
    for sb, idx in pdata.gen_batches:
        kc = max(1, BUDGET // max(1, sb.n * sb.T))
        for a in range(0, K, kc):
            S = spec.batch(sb, combo, values[a:a + kc], ctx)
            out = genuine_stream_metrics(S, sb.valid[None], W_pp)
            for f in GEN_FIELDS:
                gen[f][a:a + kc, idx] = out[f]
    for L, sb, idx in pdata.seq_groups:
        kc = max(1, BUDGET // max(1, sb.n * sb.T))
        for a in range(0, K, kc):
            S = spec.batch(sb, combo, values[a:a + kc], ctx)
            out = transition_sequence_metrics(S, sb.valid[None], pdata.C, L, n_sustain)
            for f in SEQ_FIELDS:
                seq[f][a:a + kc, idx] = out[f]
    return gen, seq


def user_aggregates(gen: dict, seq: dict, pdata: PartitionData, conditions: list) -> dict:
    """Per (K, user) aggregates: genuine sums and per-condition transition summaries."""
    U = len(pdata.users)
    K = next(iter(gen.values())).shape[0]
    M = np.zeros((pdata.n_streams, U))
    M[np.arange(pdata.n_streams), pdata.stream_meta.u.values] = 1.0
    out = {f: gen[f] @ M for f in GEN_FIELDS}
    sm = pdata.seq_meta
    L = sm.L_frames.values.astype(float)
    far = seq["far_auth_frames"] / L[None]
    for c in conditions:
        for key in ("ania_med", "miss", "far", "rec_med", "first_lock_med", "locked_at_switch", "n"):
            out[f"{c}_{key}"] = np.full((K, U), np.nan)
        for u in range(U):
            msk = (sm.u.values == u) & (sm.condition.values == c)
            if not msk.any():
                continue
            out[f"{c}_ania_med"][:, u] = np.median(seq["ania"][:, msk], axis=1)
            out[f"{c}_miss"][:, u] = seq["miss"][:, msk].mean(axis=1)
            out[f"{c}_far"][:, u] = far[:, msk].mean(axis=1)
            out[f"{c}_rec_med"][:, u] = np.median(seq["recovery"][:, msk], axis=1)
            out[f"{c}_first_lock_med"][:, u] = np.median(seq["first_lock"][:, msk], axis=1)
            out[f"{c}_locked_at_switch"][:, u] = seq["locked_at_switch"][:, msk].mean(axis=1)
            out[f"{c}_n"][:, u] = msk.sum()
    return out


def cell_summary(agg: dict, conditions, frame_period_s: float) -> dict:
    """Pooled / across-user summaries per cell (K,)."""
    fr = agg["frames"].sum(1)
    s = {
        "genuine_hours": fr * frame_period_s / 3600.0,
        "false_locks": agg["locks"].sum(1),
        "false_locks_per_hour": rate_per_hour(agg["locks"].sum(1), fr, frame_period_s),
        "false_locks_per_hour_user_median": np.nanmedian(rate_per_hour(agg["locks"], agg["frames"], frame_period_s), axis=1),
        "frr_time": agg["locked_frames"].sum(1) / np.maximum(fr, 1),
        "transitions_per_hour": rate_per_hour(agg["transitions"].sum(1), fr, frame_period_s),
        "pingpong_per_hour": rate_per_hour(agg["pp_events"].sum(1), fr, frame_period_s),
        "pingpong_locks_per_hour": rate_per_hour(agg["pp_locks"].sum(1), fr, frame_period_s),
        "lockout_mean_frames": np.where(agg["locks"].sum(1) > 0, agg["locked_frames"].sum(1) / np.maximum(agg["locks"].sum(1), 1), np.nan),
    }
    with np.errstate(all="ignore"):
        for c in conditions:
            s[f"{c}_ania_median"] = np.nanmedian(agg[f"{c}_ania_med"], axis=1)
            s[f"{c}_miss_rate"] = np.nanmean(agg[f"{c}_miss"], axis=1)
            s[f"{c}_far_frame"] = np.nanmean(agg[f"{c}_far"], axis=1)
            s[f"{c}_recovery_median"] = np.nanmedian(agg[f"{c}_rec_med"], axis=1)
            s[f"{c}_first_lock_median"] = np.nanmedian(agg[f"{c}_first_lock_med"], axis=1)
    return s


def sweep_partition(cfg, specs: dict, pdata: PartitionData, ctx: dict, frame_period_s: float,
                    work_dir: Path | None = None):
    """Full grid on one partition. Returns (cells DataFrame, per-(cell,user) DataFrame)."""
    conds = cfg["benchmark"]["conditions"]
    W_pp, n_sus = int(cfg["metrics"]["W_pp"]), int(cfg["metrics"]["n_sustain"])
    cells, cu = [], []
    for name in [n for n in ORDER if n in specs]:
        spec = specs[name]
        cache = Path(work_dir) / f"sweep_{pdata.name}_{name}.pkl" if work_dir else None
        if cache is not None and cache.exists():
            c_df, cu_df = pd.read_pickle(cache)
            cells.append(c_df)
            cu.append(cu_df)
            LOG.info("sweep %s/%s: cached (%d cells)", pdata.name, name, len(c_df))
            continue
        import time
        t0 = time.time()
        c_rows, cu_rows = [], []
        for ci, combo in enumerate(spec.combos):
            gen, seq = run_cells(spec, combo, spec.sweep_values, pdata, ctx, W_pp, n_sus)
            agg = user_aggregates(gen, seq, pdata, conds)
            summ = cell_summary(agg, conds, frame_period_s)
            for k, v in enumerate(spec.sweep_values):
                cid = f"{name}|{ci}|{k}"
                row = {"cell_id": cid, "mechanism": name, "combo_idx": ci, "params": json.dumps(combo, sort_keys=True),
                       "sweep_name": spec.sweep_name, "sweep_value": float(v), "sweep_idx": k,
                       "params_str": params_string(name, combo, spec.sweep_name, float(v))}
                row.update({key: float(val[k]) for key, val in summ.items()})
                c_rows.append(row)
            keys = [key for key in agg if agg[key].ndim == 2]
            for u, uu in enumerate(pdata.users):
                block = {"cell_id": [f"{name}|{ci}|{k}" for k in range(len(spec.sweep_values))],
                         "genuine_uuid": uu}
                for key in keys:
                    block[key] = agg[key][:, u]
                cu_rows.append(pd.DataFrame(block))
        c_df, cu_df = pd.DataFrame(c_rows), pd.concat(cu_rows, ignore_index=True)
        if cache is not None:
            pd.to_pickle((c_df, cu_df), cache)
        cells.append(c_df)
        cu.append(cu_df)
        LOG.info("sweep %s/%s: %d cells in %.1fs", pdata.name, name, len(c_df), time.time() - t0)
    return pd.concat(cells, ignore_index=True), pd.concat(cu, ignore_index=True)


# ----------------------------------------------------------------------------- selection
def select_operating_points(cfg, cells: pd.DataFrame, sel_cond: str) -> pd.DataFrame:
    op = cfg["operating_point"]
    tol = float(op["tolerance"])
    cap = float(op["max_lockout_frames"])
    targets = [("primary", float(op["primary_target"]))] + [(f"sensitivity_{i+1}", float(t)) for i, t in enumerate(op["sensitivity_targets"])]
    rows = []
    for tname, tgt in targets:
        for name in [n for n in ORDER if n in set(cells.mechanism)]:
            c = cells[cells.mechanism == name].copy()
            r = c.false_locks_per_hour.values
            with np.errstate(divide="ignore"):
                c["log_dev"] = np.abs(np.log(np.where(r > 0, r, 1e-12) / tgt))
            c["admissible"] = ~(c.lockout_mean_frames.values > cap)          # NaN (no locks) is admissible
            c["in_band"] = (r >= tgt * (1 - tol)) & (r <= tgt * (1 + tol)) & c.admissible
            pool = c[c.in_band]
            in_band = len(pool) > 0
            if not in_band:
                base = c[c.admissible] if c.admissible.any() else c
                pool = base[np.isclose(base.log_dev, base.log_dev.min())]
            pool = pool.assign(_ania=pool[f"{sel_cond}_ania_median"].fillna(np.inf),
                               _far=pool[f"{sel_cond}_far_frame"].fillna(np.inf))
            best = pool.sort_values(["_ania", "_far", "log_dev", "combo_idx", "sweep_idx"], kind="mergesort").iloc[0]
            rows.append({
                "target_name": tname, "target_false_locks_per_hour": tgt, "tolerance": tol,
                "selection_condition": sel_cond, "mechanism": name, "cell_id": best.cell_id,
                "params": best.params, "sweep_name": best.sweep_name, "sweep_value": best.sweep_value,
                "params_str": best.params_str, "in_band": bool(in_band), "n_in_band_cells": int(c.in_band.sum()),
                "n_rate_band_cells": int(((r >= tgt * (1 - tol)) & (r <= tgt * (1 + tol))).sum()),
                "n_excluded_absorbing": int((((r >= tgt * (1 - tol)) & (r <= tgt * (1 + tol))) & ~c.admissible).sum()),
                "max_lockout_frames": cap, "val_lockout_mean_frames": best.lockout_mean_frames,
                "val_frr_time": best.frr_time,
                "n_cells": int(len(c)), "val_false_locks_per_hour": best.false_locks_per_hour,
                "val_ania_median": best[f"{sel_cond}_ania_median"], "val_far_frame": best[f"{sel_cond}_far_frame"],
                "val_miss_rate": best[f"{sel_cond}_miss_rate"], "val_transitions_per_hour": best.transitions_per_hour,
            })
    ops = pd.DataFrame(rows)
    # pre-registered primary comparator: best smoother by the same validation statistic at the primary target
    cand = cfg["stats"]["smoother_candidates"]
    p = ops[(ops.target_name == "primary") & ops.mechanism.isin(cand)]
    p = p.assign(_band=~p.in_band).sort_values(["_band", "val_ania_median", "val_far_frame"], kind="mergesort")
    ops["best_smoother"] = p.mechanism.iloc[0] if len(p) else ""
    return ops


def file_sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ----------------------------------------------------------------------------- selected-cell detail
def evaluate_selected(cfg, specs, ops: pd.DataFrame, pdata: PartitionData, ctx: dict, frame_period_s: float):
    """Full per-stream / per-sequence / per-user detail for each selected cell on one partition."""
    conds = cfg["benchmark"]["conditions"]
    W_pp, n_sus = int(cfg["metrics"]["W_pp"]), int(cfg["metrics"]["n_sustain"])
    st_rows, sq_rows, pu_rows = [], [], []
    for op in ops.itertuples():
        spec = specs[op.mechanism]
        combo = json.loads(op.params)
        gen, seq = run_cells(spec, combo, np.array([op.sweep_value]), pdata, ctx, W_pp, n_sus)
        base = {"target_name": op.target_name, "mechanism": op.mechanism, "params_str": op.params_str,
                "partition": pdata.name}
        sm = pdata.stream_meta
        st = pd.DataFrame({**base, "genuine_uuid": sm.genuine_uuid.values, "run": sm.run.values,
                           **{f: gen[f][0] for f in GEN_FIELDS}})
        st_rows.append(st)
        q = pdata.seq_meta
        sq = pd.DataFrame({**base, "seq_id": q.seq_id.values, "genuine_uuid": q.genuine_uuid.values,
                           "impostor_uuid": q.impostor_uuid.values, "condition": q.condition.values,
                           "L_frames": q.L_frames.values, **{f: seq[f][0] for f in SEQ_FIELDS}})
        sq["far_frame"] = sq.far_auth_frames / sq.L_frames
        sq_rows.append(sq)
        # participant level
        g = st.groupby("genuine_uuid")[list(GEN_FIELDS)].sum()
        pu = pd.DataFrame(index=pd.Index(pdata.users, name="genuine_uuid"))
        pu = pu.join(g)
        pu["genuine_hours"] = pu.frames * frame_period_s / 3600.0
        pu["false_locks_per_hour"] = rate_per_hour(pu.locks, pu.frames, frame_period_s)
        pu["frr_time"] = pu.locked_frames / pu.frames
        pu["transitions_per_hour"] = rate_per_hour(pu.transitions, pu.frames, frame_period_s)
        pu["pingpong_per_hour"] = rate_per_hour(pu.pp_events, pu.frames, frame_period_s)
        pu["pingpong_locks_per_hour"] = rate_per_hour(pu.pp_locks, pu.frames, frame_period_s)
        pu["lockout_mean_frames"] = np.where(pu.locks > 0, pu.locked_frames / pu.locks.clip(lower=1), np.nan)
        for c in conds:
            d = sq[sq.condition == c].groupby("genuine_uuid")
            pu[f"{c}_n_sequences"] = d.size()
            pu[f"{c}_ania_median"] = d.ania.median()
            pu[f"{c}_ania_mean"] = d.ania.mean()
            pu[f"{c}_first_lock_median"] = d.first_lock.median()
            pu[f"{c}_miss_rate"] = d.miss.mean()
            pu[f"{c}_far_frame"] = d.far_frame.mean()
            pu[f"{c}_fa_frames"] = d.far_auth_frames.sum()
            pu[f"{c}_impostor_frames"] = d.L_frames.sum()
            pu[f"{c}_recovery_median"] = d.recovery.median()
            pu[f"{c}_recovery_censored_rate"] = d.recovery_censored.mean()
            pu[f"{c}_locked_at_switch_rate"] = d.locked_at_switch.mean()
            pu[f"{c}_locked_at_return_rate"] = d.locked_at_return.mean()
        pu = pu.reset_index()
        for k, v in base.items():
            pu.insert(0, k, v)
        pu_rows.append(pu)
    return (pd.concat(st_rows, ignore_index=True), pd.concat(sq_rows, ignore_index=True),
            pd.concat(pu_rows, ignore_index=True))


def decision_trace(spec, combo, value, p: np.ndarray, ctx) -> np.ndarray:
    """States of one mechanism on one sequence (for figures)."""
    sb = StreamBatch.from_arrays([p])
    return spec.batch(sb, combo, np.array([value]), ctx)[0, 0]
