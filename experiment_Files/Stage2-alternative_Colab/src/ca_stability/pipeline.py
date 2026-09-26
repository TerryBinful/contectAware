"""End-to-end Stage 2 pipeline. Every stage is checkpointed (work/<label>/_stages) and can be
resumed after an interruption (e.g. a Colab disconnect) by re-running the same command.

    A audit      dataset download/verification, cadence, feature inventory, eligibility
    B split      participant split (participant_split.json)
    C scoring    Exp 1 fixed score generator + go/no-go gate            -> results/<label>/baseline/
    D benchmark  genuine streams + spliced sequences + leakage checks   -> results/<label>/benchmark/
    E sweep_val  full parameter grids on the VALIDATION partition       -> results/<label>/sweeps/
    F select     matched operating points (written + hashed BEFORE any test computation)
    G evaluate   selected cells on test (and val), sanity checks, test frontier
    H stats      participant-level statistics
    I report     figures, tables, RESULTS_REPORT.md, experiment_metadata.json
"""
from __future__ import annotations

import json
import time
import traceback
from pathlib import Path

import numpy as np
import pandas as pd

from . import __version__
from .config import config_hash, resolve_paths
from .data import (all_columns, assign_periods, assign_runs, dataset_fingerprint, ensure_dataset,
                   participant_id, select_feature_columns)
from .provenance import LOG, Stage, code_fingerprint, environment, git_state, setup_logging, utcnow, write_json

STAGES = ["audit", "split", "scoring", "benchmark", "sweep_val", "select", "evaluate", "stats", "report"]


class Run:
    """Holds config, paths and the in-memory products of the stages."""

    def __init__(self, cfg: dict, force: list | None = None):
        self.cfg = cfg
        self.hash = config_hash(cfg)
        self.paths = resolve_paths(cfg)
        self.res = self.paths["results"]
        # all regenerable caches and stage markers are keyed by the config hash, so a changed
        # config can never silently reuse stale per-user scores or sweep results
        self.work = self.paths["work"] / self.hash[:12]
        self.work.mkdir(parents=True, exist_ok=True)
        self.force = set(force or [])
        self.exp_id = f"{cfg['experiment']['name']}-{cfg['experiment']['label']}-{self.hash[:8]}"
        (self.res / "logs").mkdir(parents=True, exist_ok=True)
        self.log_file = self.res / "logs" / f"run_{time.strftime('%Y%m%dT%H%M%S')}.log"
        setup_logging(self.log_file, cfg["runtime"]["log_level"])
        self._files = self._frames = self._split = self._scores = None
        self._bench = None

    def stage(self, name):
        return Stage(name, self.work, self.hash, force=name in self.force or "all" in self.force)

    # ---------------------------------------------------------------- shared helpers
    @property
    def files(self):
        if self._files is None:
            self._files = ensure_dataset(self.cfg, self.paths["data"])
        return self._files

    def audit_summary(self):
        return json.loads((self.res / "dataset_audit" / "dataset_summary.json").read_text())

    def set_meta(self):
        s = self.audit_summary()
        self.cfg["_meta"]["frame_period_s"] = float(s["frame_period_s_used"])
        self.cfg["_meta"]["run_break_gap_s"] = float(s["run_break_gap_s"])

    @property
    def split(self):
        if self._split is None:
            self._split = json.loads((self.res / "participant_split.json").read_text())
        return self._split

    @property
    def frames(self):
        """Cohort participants: features of the configured set + context labels, periods, runs."""
        if self._frames is None:
            from .data import load_frames
            cohort = set(self.split["cohort"])
            files = [f for f in self.files if participant_id(f) in cohort]
            cols = all_columns(files)
            feats = select_feature_columns(cols, self.cfg)
            labs = [c for c in self.cfg["benchmark"]["context_labels"] if c in cols]
            df = load_frames(files, feats, labs, cache_dir=self.paths["cache"])
            df["period"] = assign_periods(df, self.cfg["periods"]["fractions"], self.cfg["periods"]["embargo_minutes"]).values
            df["run"] = assign_runs(df, self.cfg["_meta"]["run_break_gap_s"]).values
            self._frames, self.feat_cols = df, feats
        return self._frames

    @property
    def scores(self):
        if self._scores is None:
            from .scoring import run_scoring
            self._scores, _, _ = run_scoring(self.cfg, self.frames, self.feat_cols, self.split, self.work,
                                             self.res / "baseline")
        return self._scores

    def bench_tables(self):
        b = self.res / "benchmark"
        man = pd.read_csv(b / "manifest.csv")
        streams = pd.read_csv(b / "genuine_streams.csv")
        gen_long = pd.read_parquet(b / "genuine_stream_scores.parquet")
        seq_long = pd.read_parquet(b / "sequence_scores.parquet")
        cov = json.loads((b / "coverage.json").read_text())
        return streams, man, cov, gen_long, seq_long

    def density(self):
        from .mechanisms.density import ScoreDensity
        return ScoreDensity.from_dict(json.loads((self.res / "benchmark" / "densities.json").read_text()))

    def partitions(self):
        from .evaluate import build_partition
        if self._bench is None:
            streams, man, cov, gen_long, seq_long = self.bench_tables()
            users = self.split["genuine_users"]
            self._bench = {p: build_partition(self.cfg, p, users, gen_long, seq_long, man) for p in ("val", "test")}
            self._cov = cov
        return self._bench

    def record_failure(self, stage, exc):
        path = self.res / "failures.json"
        fails = json.loads(path.read_text()) if path.exists() else []
        msg = str(exc)
        cls = msg.split(":")[0] if msg.split(":")[0] in {"DATA", "CODE", "DEPENDENCY", "METHODOLOGY", "COMPUTATION",
                                                         "REPRODUCIBILITY", "CODE/LEAKAGE"} else "CODE"
        fails.append({"utc": utcnow(), "stage": stage, "class": cls, "message": msg,
                      "traceback": traceback.format_exc(limit=5)})
        write_json(fails, path)


# ----------------------------------------------------------------------------- stages
def stage_audit(r: Run):
    from .audit import run_dataset_audit
    with r.stage("audit") as s:
        if s.done():
            LOG.info("audit: checkpoint found")
        else:
            run_dataset_audit(r.cfg, r.files, r.res / "dataset_audit")
    r.set_meta()


def stage_split(r: Run):
    from .splits import build_split
    with r.stage("split") as s:
        if not s.done():
            elig = pd.read_csv(r.res / "dataset_audit" / "eligibility.csv")
            build_split(r.cfg, elig, r.res / "participant_split.json")


def stage_scoring(r: Run):
    with r.stage("scoring") as s:
        if not s.done() or not (r.res / "baseline" / "exp1_summary.json").exists():
            _ = r.scores
    summ = json.loads((r.res / "baseline" / "exp1_summary.json").read_text())
    if not summ["gate"]["passed"]:
        raise RuntimeError(f"METHODOLOGY: Exp 1 gate failed ({summ['gate']['criterion']}; value "
                           f"{summ['gate']['value']:.3f}). The score stream is not a valid authentication signal; "
                           "mechanism comparison is not run (execution spec: hard gate).")


def stage_benchmark(r: Run):
    from .benchmark import run_benchmark
    from .mechanisms.density import ScoreDensity
    with r.stage("benchmark") as s:
        if not s.done():
            streams, man, cov, gen_long, seq_long = run_benchmark(r.cfg, r.frames, r.split, r.scores,
                                                                  r.res / "benchmark", r.work)
            # SPRT / HMM densities: pooled VALIDATION scores only (genuine val streams vs impostor_cal frames)
            gv = gen_long.p_cal[gen_long.partition == "val"].values
            iv = np.concatenate([sc.p_cal[sc.role == "imp_cal"].values for sc in r.scores.values()])
            d = ScoreDensity.fit(gv, iv, int(r.cfg["mechanisms"]["density_bins"]))
            write_json({**d.to_dict(), "fitted_on": "validation partition only",
                        "n_genuine": int(len(gv)), "n_impostor": int(len(iv))}, r.res / "benchmark" / "densities.json")


def stage_sweep_val(r: Run):
    from .evaluate import sweep_partition
    from .mechanisms.registry import build_specs
    out = r.res / "sweeps"
    out.mkdir(parents=True, exist_ok=True)
    with r.stage("sweep_val") as s:
        if not s.done():
            specs = build_specs(r.cfg)
            P = r.partitions()
            cells, cu = sweep_partition(r.cfg, specs, P["val"], {"density": r.density()},
                                        r.cfg["_meta"]["frame_period_s"], r.work)
            cells.to_csv(out / "sweep_val.csv", index=False)
            cu.to_parquet(r.work / "sweep_val_cell_user.parquet", index=False)


def stage_select(r: Run):
    from .evaluate import file_sha256, select_operating_points
    with r.stage("select") as s:
        if not s.done():
            cells = pd.read_csv(r.res / "sweeps" / "sweep_val.csv")
            sel = json.loads((r.res / "benchmark" / "coverage.json").read_text())["selection_condition"]
            ops = select_operating_points(r.cfg, cells, sel)
            p = r.res / "operating_points.csv"
            ops.to_csv(p, index=False)
            digest = file_sha256(p)
            write_json({"file": "operating_points.csv", "sha256": digest, "frozen_utc": utcnow(),
                        "selection_condition": sel, "note": "written before any test-partition computation"},
                       r.res / "operating_points.frozen.json")
            LOG.info("Operating points frozen (sha256 %s). Best smoother on validation: %s", digest[:12],
                     ops.best_smoother.iloc[0])


def stage_evaluate(r: Run):
    from .evaluate import evaluate_selected, file_sha256, sweep_partition
    from .mechanisms.registry import build_specs
    from .stats import mechanism_summary
    with r.stage("evaluate") as s:
        if s.done():
            return
        frozen = json.loads((r.res / "operating_points.frozen.json").read_text())
        if file_sha256(r.res / "operating_points.csv") != frozen["sha256"]:
            raise RuntimeError("REPRODUCIBILITY: operating_points.csv changed after it was frozen; refusing to evaluate test")
        ops = pd.read_csv(r.res / "operating_points.csv")
        specs = build_specs(r.cfg)
        P = r.partitions()
        ctx = {"density": r.density()}
        fp = r.cfg["_meta"]["frame_period_s"]
        st, sq, pu = [], [], []
        for part in ("test", "val"):
            a, b, c = evaluate_selected(r.cfg, specs, ops, P[part], ctx, fp)
            st.append(a); sq.append(b); pu.append(c)
        st, sq, pu = (pd.concat(x, ignore_index=True) for x in (st, sq, pu))
        st.to_csv(r.res / "sequence_metrics.csv", index=False)
        sq.to_csv(r.res / "transition_metrics.csv", index=False)
        pu.to_csv(r.res / "participant_metrics.csv", index=False)
        mm = mechanism_summary(r.cfg, pu, r.cfg["benchmark"]["conditions"])
        mm.to_csv(r.res / "mechanism_metrics.csv", index=False)
        sanity_checks(r, pu, ops)
        if r.cfg.get("evaluation", {}).get("test_frontier", True):
            cells, _ = sweep_partition(r.cfg, specs, P["test"], ctx, fp, None)
            cells.to_csv(r.res / "sweeps" / "sweep_test.csv", index=False)


def sanity_checks(r: Run, pu: pd.DataFrame, ops: pd.DataFrame):
    """Splice-spec §9 checks 2-4 (check 1 is part of the benchmark leakage checks)."""
    t = pu[(pu.partition == "test") & (pu.target_name == "primary") & (pu.mechanism == "threshold")]
    Lmax = max(r.cfg["benchmark"]["L_frames"])
    cov = json.loads((r.res / "benchmark" / "coverage.json").read_text())
    out = {
        "check2_threshold_X_ania_median_frames": float(t.X_ania_median.median()),
        "check2_threshold_X_miss_rate_mean": float(t.X_miss_rate.mean()),
        "check2_passed": bool(t.X_ania_median.median() < Lmax and t.X_miss_rate.mean() < 0.5),
        "check2_rule": f"median over users of threshold X ANIA < {Lmax} frames and mean X miss rate < 0.5",
        "check3_threshold_M_ania_median_frames": float(t.M_ania_median.median()) if "M_ania_median" in t else None,
        "check3_passed": bool(t.M_ania_median.median() >= t.X_ania_median.median()) if "M_ania_median" in t else None,
        "check3_rule": "M ANIA >= X ANIA for the instantaneous threshold (context matching makes detection harder)",
        "check4_M_coverage_min": cov.get("M_coverage_min"),
        "selection_condition": cov.get("selection_condition"),
    }
    write_json(out, r.res / "benchmark" / "sanity_checks.json")
    for k in ("check2_passed", "check3_passed"):
        if out[k] is False:
            LOG.warning("Sanity %s FAILED — see benchmark/sanity_checks.json (reported, not silently ignored)", k)


def stage_stats(r: Run):
    from .stats import run_stats
    with r.stage("stats") as s:
        if s.done():
            return
        pu = pd.read_csv(r.res / "participant_metrics.csv")
        ops = pd.read_csv(r.res / "operating_points.csv")
        sel = ops.selection_condition.iloc[0]
        tests, ranks = [], []
        for tname in ops.target_name.unique():
            d = pu[(pu.partition == "test") & (pu.target_name == tname)]
            t, rk = run_stats(r.cfg, d, ops[ops.target_name == tname], sel, r.cfg["benchmark"]["conditions"])
            t.insert(0, "target_name", tname)
            rk.insert(0, "target_name", tname)
            tests.append(t); ranks.append(rk)
        pd.concat(tests, ignore_index=True).to_csv(r.res / "statistical_tests.csv", index=False)
        pd.concat(ranks, ignore_index=True).to_csv(r.res / "friedman_ranks.csv", index=False)


def stage_report(r: Run):
    from .figures import make_figures
    from .report import write_report
    from .tables import make_tables
    with r.stage("report") as s:
        make_tables(r)
        make_figures(r)
        write_metadata(r)
        write_report(r)


def write_metadata(r: Run):
    cfg = r.cfg
    ops = pd.read_csv(r.res / "operating_points.csv") if (r.res / "operating_points.csv").exists() else None
    meta = {
        "experiment_id": r.exp_id,
        "experiment_name": cfg["experiment"]["name"],
        "label": cfg["experiment"]["label"],
        "status": cfg["experiment"]["status"],
        "package_version": __version__,
        "generated_utc": utcnow(),
        **git_state(),
        "code_fingerprint_sha256": code_fingerprint(),
        "config_path": cfg["_meta"].get("config_path"),
        "config_hash": r.hash,
        "config": {k: v for k, v in cfg.items() if not k.startswith("_")},
        "derived": {k: v for k, v in cfg["_meta"].items() if k != "config_path"},
        "master_seed": cfg["experiment"]["seed"],
        "dataset": {"name": "ExtraSensory (per-uuid features+labels)", "url": cfg["data"]["url"],
                    "archive_md5_expected": cfg["data"]["md5"], **dataset_fingerprint(r.files)},
        "participant_split": "participant_split.json",
        "n_cohort": len(r.split["cohort"]), "n_genuine_users": len(r.split["genuine_users"]),
        "feature_set": {"name": cfg["features"]["set"], "groups": cfg["features"]["sets"][cfg["features"]["set"]]},
        "classifier": cfg["classifier"],
        "mechanisms": {"primary": cfg["mechanisms"]["primary_set"], "supplementary": cfg["mechanisms"]["supplementary_set"],
                       "grids": cfg["mechanisms"]["grids"]},
        "operating_points": ops.to_dict(orient="records") if ops is not None else None,
        "operating_points_frozen": json.loads((r.res / "operating_points.frozen.json").read_text())
        if (r.res / "operating_points.frozen.json").exists() else None,
        "environment": environment(),
        "reproduction_command": f"python -m ca_stability.cli --config {Path(cfg['_meta']['config_path']).relative_to(Path(cfg['_meta']['config_path']).parents[1])}",
        "stage_timings": {p.stem.replace(".done", ""): json.loads(p.read_text()).get("wall_s")
                          for p in sorted((r.work / "_stages").glob("*.done.json"))},
    }
    write_json(meta, r.res / "experiment_metadata.json")


RUNNERS = {"audit": stage_audit, "split": stage_split, "scoring": stage_scoring, "benchmark": stage_benchmark,
           "sweep_val": stage_sweep_val, "select": stage_select, "evaluate": stage_evaluate,
           "stats": stage_stats, "report": stage_report}


def run_pipeline(cfg: dict, until: str | None = None, force: list | None = None) -> Run:
    r = Run(cfg, force)
    LOG.info("Experiment %s | config %s | results %s | work %s", r.exp_id, cfg["_meta"].get("config_path"), r.res, r.work)
    for name in STAGES:
        try:
            if name != "audit" and "frame_period_s" not in r.cfg["_meta"]:
                r.set_meta()
            RUNNERS[name](r)
        except Exception as exc:
            r.record_failure(name, exc)
            LOG.error("Pipeline stopped at stage '%s': %s", name, exc)
            raise
        if until and name == until:
            LOG.info("Stopping after stage %s (--until)", until)
            break
    return r
