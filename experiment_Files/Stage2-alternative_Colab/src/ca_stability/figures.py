"""Stage I — figures (PNG, 150 dpi). Every figure is drawn from files in results/<label>/."""
from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from .mechanisms.registry import LABEL, ORDER, build_specs  # noqa: E402
from .provenance import LOG  # noqa: E402

COL = dict(zip(ORDER, plt.get_cmap("tab10").colors))


def _save(fig, r, name):
    out = r.res / "figures"
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / f"{name}.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def _status(r):
    return "" if r.cfg["experiment"]["status"] == "primary" else f"  [{r.cfg['experiment']['status'].upper()}]"


def fig_cadence(r):
    c = pd.read_csv(r.res / "dataset_audit" / "cadence_summary.csv")
    fig, ax = plt.subplots(figsize=(6, 3.2))
    ax.hist(c.frac_gap_59_61, bins=np.linspace(0, 1, 41), color="0.4")
    ax.axvline(r.cfg["cadence"]["regular_min_fraction"], color="C3", ls="--", label="cohort rule")
    ax.set_xlabel("share of a participant's inter-frame gaps within 59-61 s")
    ax.set_ylabel("participants")
    ax.set_title("Sampling cadence per participant" + _status(r))
    ax.legend()
    _save(fig, r, "fig01_cadence")


def fig_exp1(r):
    pu = pd.read_csv(r.res / "baseline" / "exp1_per_user_classifier_metrics.csv")
    rel = pd.read_csv(r.res / "baseline" / "exp1_reliability_test.csv")
    fig, ax = plt.subplots(1, 3, figsize=(12, 3.4))
    ax[0].scatter(np.arange(len(pu)), pu.sort_values("test_auc").test_auc, s=14, color="C0", label="test")
    ax[0].axhline(r.cfg["gate"]["min_median_test_auc"], color="C3", ls="--", label="gate (median)")
    ax[0].set_ylim(0.4, 1.0); ax[0].set_xlabel("genuine user (sorted)"); ax[0].set_ylabel("AUC")
    ax[0].set_title("Exp 1: per-user test AUC"); ax[0].legend(fontsize=8)
    ax[1].scatter(pu.test_eer, pu.val_eer, s=14)
    lim = [0, max(pu.test_eer.max(), pu.val_eer.max()) * 1.1]
    ax[1].plot(lim, lim, "k:", lw=1); ax[1].set_xlabel("test EER"); ax[1].set_ylabel("validation EER")
    ax[1].set_title("EER: validation vs test")
    ax[2].plot([0, 1], [0, 1], "k:", lw=1)
    ax[2].plot(rel.mean_predicted, rel.observed_genuine_rate, "o-")
    ax[2].set_xlabel("mean calibrated score"); ax[2].set_ylabel("genuine share (class-balanced)")
    ax[2].set_title("Reliability (test)")
    fig.suptitle("Fixed score generator" + _status(r), y=1.02)
    _save(fig, r, "fig02_exp1_classifier")


def _frontier(cells, sel, cap):
    """Lower envelope of ANIA over the false-lock rate, per mechanism (admissible cells only)."""
    out = {}
    for m, d in cells.groupby("mechanism"):
        d = d[~(d.lockout_mean_frames > cap)].dropna(subset=["false_locks_per_hour", f"{sel}_ania_median"])
        d = d[d.false_locks_per_hour > 0].sort_values("false_locks_per_hour")
        if d.empty:
            continue
        env = np.minimum.accumulate(d[f"{sel}_ania_median"].values)
        out[m] = (d.false_locks_per_hour.values, env, d)
    return out


def fig_frontiers(r):
    ops = pd.read_csv(r.res / "operating_points.csv")
    sel = ops.selection_condition.iloc[0]
    cap = r.cfg["operating_point"]["max_lockout_frames"]
    tgt = r.cfg["operating_point"]["primary_target"]
    tol = r.cfg["operating_point"]["tolerance"]
    for part in ("val", "test"):
        p = r.res / "sweeps" / f"sweep_{part}.csv"
        if not p.exists():
            continue
        cells = pd.read_csv(p)
        fr = _frontier(cells, sel, cap)
        fig, ax = plt.subplots(1, 2, figsize=(12, 4.2))
        for m in ORDER:
            if m not in fr:
                continue
            x, env, d = fr[m]
            ax[0].step(x, env, where="post", color=COL[m], label=LABEL[m], lw=1.4)
            env_far = np.minimum.accumulate(d[f"{sel}_far_frame"].values)
            ax[1].step(x, env_far, where="post", color=COL[m], lw=1.4)
            o = ops[(ops.mechanism == m) & (ops.target_name == "primary")]
            if len(o):
                row = cells[cells.cell_id == o.cell_id.iloc[0]]
                if len(row):
                    ax[0].plot(row.false_locks_per_hour, row[f"{sel}_ania_median"], "o", color=COL[m], ms=6, mec="k")
                    ax[1].plot(row.false_locks_per_hour, row[f"{sel}_far_frame"], "o", color=COL[m], ms=6, mec="k")
        for a in ax:
            a.set_xscale("log"); a.axvspan(tgt * (1 - tol), tgt * (1 + tol), color="0.85", zorder=0)
            a.set_xlabel("genuine false locks per hour (pooled)")
        ax[0].set_ylabel(f"sustained detection delay, condition {sel}\n(median over users, frames)")
        ax[1].set_ylabel(f"FAR_frame, condition {sel} (mean over users)")
        ax[0].legend(fontsize=7, ncol=2)
        ax[0].set_title(f"Trade-off frontier ({part}); dots = selected cells")
        ax[1].set_title(f"Security frontier ({part})")
        fig.suptitle(("Validation: operating points chosen here" if part == "val" else
                      "Test: descriptive only (points were frozen on validation)") + _status(r), y=1.02)
        _save(fig, r, f"fig03_frontier_{part}")


def fig_outcome_boxes(r, target="primary"):
    pu = pd.read_csv(r.res / "participant_metrics.csv")
    ops = pd.read_csv(r.res / "operating_points.csv")
    sel = ops.selection_condition.iloc[0]
    d = pu[(pu.partition == "test") & (pu.target_name == target)]
    panels = [(f"{sel}_far_frame", f"FAR_frame ({sel})", "security"), (f"{sel}_miss_rate", f"missed blocks ({sel})", "security"),
              ("frr_time", "FRR_time", "security"), ("false_locks_per_hour", "false locks / h", "stability"),
              ("pingpong_per_hour", "ping-pong events / h", "stability"), ("transitions_per_hour", "transitions / h", "stability"),
              (f"{sel}_ania_median", f"sustained detection ({sel}, frames)", "responsiveness"),
              (f"{sel}_recovery_median", f"recovery after return ({sel}, frames)", "responsiveness"),
              ("lockout_mean_frames", "mean false-lock duration (frames)", "responsiveness")]
    mechs = [m for m in ORDER if m in set(d.mechanism)]
    fig, axs = plt.subplots(3, 3, figsize=(14, 10))
    for ax, (col, lab, fam) in zip(axs.flat, panels):
        data = [d[d.mechanism == m][col].dropna().values for m in mechs]
        bp = ax.boxplot(data, patch_artist=True, widths=0.6, showfliers=False)
        for patch, m in zip(bp["boxes"], mechs):
            patch.set_facecolor(COL[m]); patch.set_alpha(0.55)
        for i, x in enumerate(data):
            ax.plot(np.full(len(x), i + 1) + np.random.default_rng(i).uniform(-0.15, 0.15, len(x)), x, ".", color="k", ms=3, alpha=0.6)
        ax.set_xticks(range(1, len(mechs) + 1)); ax.set_xticklabels([LABEL[m] for m in mechs], rotation=45, ha="right", fontsize=8)
        ax.set_title(f"{lab}  [{fam}]", fontsize=10)
    fig.suptitle(f"Test partition, target '{target}': one dot per genuine user" + _status(r))
    fig.tight_layout()
    _save(fig, r, f"fig04_outcomes_{target}")


def fig_tradeoff(r):
    mm = pd.read_csv(r.res / "mechanism_metrics.csv")
    ops = pd.read_csv(r.res / "operating_points.csv")
    sel = ops.selection_condition.iloc[0]
    m = mm[(mm.partition == "test") & (mm.target_name == "primary")]
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.4))
    for _, row in m.iterrows():
        c = COL[row.mechanism]
        for a, (xc, yc) in zip(ax, [(f"{sel}_far_frame", "pingpong_per_hour"), (f"{sel}_far_frame", f"{sel}_ania_median")]):
            x, y = row[f"{xc}__median"], row[f"{yc}__median"]
            a.errorbar(x, y, xerr=[[x - row[f"{xc}__ci_lo"]], [row[f"{xc}__ci_hi"] - x]],
                       yerr=[[y - row[f"{yc}__ci_lo"]], [row[f"{yc}__ci_hi"] - y]], fmt="o", color=c, capsize=2)
            a.annotate(LABEL[row.mechanism], (x, y), fontsize=7, xytext=(4, 3), textcoords="offset points")
    ax[0].set_xlabel(f"FAR_frame ({sel})"); ax[0].set_ylabel("ping-pong events / h")
    ax[1].set_xlabel(f"FAR_frame ({sel})"); ax[1].set_ylabel(f"sustained detection ({sel}, frames)")
    ax[0].set_title("Security vs stability (median over users, 95% CI)")
    ax[1].set_title("Security vs responsiveness")
    fig.suptitle("Test partition at the matched primary operating point" + _status(r), y=1.02)
    _save(fig, r, "fig05_tradeoffs")


def fig_example_trace(r):
    from .evaluate import decision_trace
    ops = pd.read_csv(r.res / "operating_points.csv")
    sel = ops.selection_condition.iloc[0]
    man = pd.read_csv(r.res / "benchmark" / "manifest.csv")
    seq = pd.read_parquet(r.res / "benchmark" / "sequence_scores.parquet")
    cand = man[(man.partition == "test") & (man.condition == sel) & (man.L_frames == 10)]
    if cand.empty:
        return
    m = cand.iloc[len(cand) // 2]          # deterministic pick (middle of the manifest order)
    s = seq[seq.seq_id == m.seq_id].sort_values("t")
    p = s.p_cal.values
    specs = build_specs(r.cfg)
    dens = r.density()
    o = ops[ops.target_name == "primary"]
    lo = max(0, m.splice_idx - 30)
    x = np.arange(len(p))[lo:]
    fig, ax = plt.subplots(2, 1, figsize=(12, 6), gridspec_kw={"height_ratios": [1, 1.6]}, sharex=True)
    ax[0].plot(x, p[lo:], "k.-", lw=0.8, ms=3)
    for a in ax:
        a.axvspan(m.splice_idx - 0.5, m.return_idx - 0.5, color="C3", alpha=0.12)
    ax[0].set_ylabel("calibrated score p"); ax[0].set_ylim(-0.02, 1.02)
    ax[0].set_title(f"Example test sequence {m.seq_id} (condition {m.condition}, impostor block shaded)" + _status(r))
    for i, row in enumerate(o.itertuples()):
        stt = decision_trace(specs[row.mechanism], json.loads(row.params), row.sweep_value, p, {"density": dens})[lo:]
        ax[1].fill_between(x, i, i + 0.8 * (~stt), step="mid", color=COL[row.mechanism], alpha=0.8)
    ax[1].set_yticks(np.arange(len(o)) + 0.4); ax[1].set_yticklabels([LABEL[mm] for mm in o.mechanism], fontsize=8)
    ax[1].set_xlabel("frame (~1 min)"); ax[1].set_title("LOCKED periods (filled) per mechanism at its matched operating point")
    _save(fig, r, "fig06_example_trace")


def fig_hysteresis_heatmap(r):
    cells = pd.read_csv(r.res / "sweeps" / "sweep_val.csv")
    ops = pd.read_csv(r.res / "operating_points.csv")
    sel = ops.selection_condition.iloc[0]
    tgt, tol = r.cfg["operating_point"]["primary_target"], r.cfg["operating_point"]["tolerance"]
    cap = r.cfg["operating_point"]["max_lockout_frames"]
    h = cells[cells.mechanism == "hysteresis"].copy()
    h["m"] = h.params.map(lambda s: json.loads(s)["m"]); h["T"] = h.params.map(lambda s: json.loads(s)["T"])
    ok = h[(h.false_locks_per_hour.between(tgt * (1 - tol), tgt * (1 + tol))) & ~(h.lockout_mean_frames > cap)]
    ms, Ts = sorted(h.m.unique()), sorted(h["T"].unique())
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.6))
    for ax, col, lab in zip(axs, [f"{sel}_ania_median", f"{sel}_far_frame"], ["sustained detection (frames)", "FAR_frame"]):
        Z = np.full((len(ms), len(Ts)), np.nan)
        for i, mv in enumerate(ms):
            for j, Tv in enumerate(Ts):
                d = ok[(ok.m == mv) & (ok["T"] == Tv)].sort_values([f"{sel}_ania_median", f"{sel}_far_frame"])
                if len(d):
                    Z[i, j] = d[col].iloc[0]
        im = ax.imshow(Z, cmap="viridis_r", aspect="auto")
        for i in range(len(ms)):
            for j in range(len(Ts)):
                ax.text(j, i, "—" if np.isnan(Z[i, j]) else f"{Z[i, j]:.2f}", ha="center", va="center", fontsize=8, color="w")
        ax.set_xticks(range(len(Ts))); ax.set_xticklabels(Ts); ax.set_xlabel("dwell T (frames)")
        ax.set_yticks(range(len(ms))); ax.set_yticklabels(ms); ax.set_ylabel("margin m")
        ax.set_title(f"Hysteresis, validation, best matched cell: {lab}", fontsize=9)
        fig.colorbar(im, ax=ax)
    fig.suptitle("Component grid ('—' = no admissible cell at the primary target)" + _status(r), y=1.03)
    _save(fig, r, "fig07_hysteresis_grid")


def fig_by_L(r):
    t = pd.read_csv(r.res / "tables" / "T10_by_block_length.csv")
    ops = pd.read_csv(r.res / "operating_points.csv")
    sel = ops.selection_condition.iloc[0]
    t = t[t.condition == sel]
    fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
    for m in ORDER:
        d = t[t.mechanism == m]
        if d.empty:
            continue
        ax[0].plot(d.L_frames, d.ania_median, "o-", color=COL[m], label=LABEL[m])
        ax[1].plot(d.L_frames, d.miss_rate, "o-", color=COL[m])
    for a in ax:
        a.set_xscale("log"); a.set_xticks(sorted(t.L_frames.unique())); a.set_xticklabels(sorted(t.L_frames.unique()))
        a.set_xlabel("impostor block length L (frames)")
    ax[0].set_ylabel("median sustained detection (frames)"); ax[1].set_ylabel("missed blocks (fraction)")
    ax[0].legend(fontsize=7, ncol=2)
    fig.suptitle(f"Test, condition {sel}, primary target" + _status(r), y=1.02)
    _save(fig, r, "fig08_by_block_length")


def fig_cd(r):
    rk = pd.read_csv(r.res / "friedman_ranks.csv")
    rk = rk[(rk.target_name == "primary")]
    outs = ["ania", "far_frame", "frr_time", "pingpong_per_hour"]
    fig, axs = plt.subplots(len(outs), 1, figsize=(9, 1.5 * len(outs)))
    for ax, o in zip(axs, outs):
        d = rk[rk.outcome == o].sort_values("avg_rank")
        if d.empty:
            continue
        cd, p = d.nemenyi_cd.iloc[0], d.friedman_p.iloc[0]
        k = len(d)
        ax.set_xlim(0.5, k + 0.5); ax.set_ylim(-1, 1); ax.set_yticks([])
        ax.hlines(0, 1, k, color="k", lw=0.8)
        for i, row in enumerate(d.itertuples()):
            y = 0.35 if i % 2 else -0.45
            ax.plot(row.avg_rank, 0, "o", color=COL[row.mechanism])
            ax.annotate(LABEL[row.mechanism], (row.avg_rank, 0), (row.avg_rank, y), fontsize=7, ha="center",
                        arrowprops=dict(arrowstyle="-", lw=0.4))
        if not np.isnan(cd):
            ax.plot([1, 1 + cd], [0.8, 0.8], "k-", lw=2); ax.text(1 + cd / 2, 0.55, f"CD={cd:.2f}", ha="center", fontsize=7)
        ax.set_title(f"{o}: average rank (1 = best), Friedman p = {p:.3g}", fontsize=9)
    fig.suptitle("Nemenyi critical-difference view, test, primary target" + _status(r), y=1.01)
    fig.tight_layout()
    _save(fig, r, "fig09_critical_difference")


def fig_participants(r):
    pu = pd.read_csv(r.res / "participant_metrics.csv")
    ops = pd.read_csv(r.res / "operating_points.csv")
    sel = ops.selection_condition.iloc[0]
    d = pu[(pu.partition == "test") & (pu.target_name == "primary")]
    mechs = [m for m in ORDER if m in set(d.mechanism)]
    fig, axs = plt.subplots(1, 2, figsize=(12, 4))
    for ax, col, lab in zip(axs, [f"{sel}_far_frame", "false_locks_per_hour"], [f"FAR_frame ({sel})", "false locks / h"]):
        W = d.pivot(index="genuine_uuid", columns="mechanism", values=col).reindex(columns=mechs)
        for _, row in W.iterrows():
            ax.plot(range(len(mechs)), row.values, "-", color="0.6", lw=0.6, alpha=0.7)
        ax.plot(range(len(mechs)), W.median().values, "k-o", lw=2, label="median")
        ax.set_xticks(range(len(mechs))); ax.set_xticklabels([LABEL[m] for m in mechs], rotation=45, ha="right", fontsize=8)
        ax.set_ylabel(lab); ax.legend()
    fig.suptitle("Participant variability (one line per genuine user), test, primary target" + _status(r), y=1.02)
    _save(fig, r, "fig10_participant_variability")


def make_figures(r):
    for f in (fig_cadence, fig_exp1, fig_frontiers, fig_outcome_boxes, fig_tradeoff, fig_example_trace,
              fig_hysteresis_heatmap, fig_by_L, fig_cd, fig_participants):
        try:
            f(r)
        except Exception as exc:          # a figure failure must not hide results; it is logged
            LOG.error("figure %s failed: %s", f.__name__, exc)
            raise
