"""Provenance: git state, code fingerprint, environment, logging, stage checkpoints."""
from __future__ import annotations

import hashlib
import json
import logging
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from .config import REPO_ROOT, STAGE2_ROOT

LOG = logging.getLogger("ca_stability")


def setup_logging(log_file: Path | None = None, level: str = "INFO") -> logging.Logger:
    LOG.setLevel(getattr(logging, level))
    LOG.handlers.clear()
    fmt = logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s", "%Y-%m-%d %H:%M:%S")
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    LOG.addHandler(sh)
    if log_file is not None:
        fh = logging.FileHandler(log_file, mode="a")
        fh.setFormatter(fmt)
        LOG.addHandler(fh)
    LOG.propagate = False
    return LOG


def _git(*args) -> str | None:
    try:
        return subprocess.check_output(["git", "-C", str(REPO_ROOT), *args],
                                       stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return None


def git_state() -> dict:
    sha = _git("rev-parse", "HEAD")
    status = _git("status", "--porcelain", "--", "experiment_Files/Stage2/src",
                  "experiment_Files/Stage2/configs", "experiment_Files/Stage2/scripts")
    return {
        "git_commit": sha or "UNAVAILABLE (not a git checkout)",
        "git_branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
        "code_dirty": bool(status) if status is not None else None,
        "dirty_files": status.splitlines() if status else [],
    }


def code_fingerprint() -> str:
    """SHA-256 over all pipeline source + config files (works without git)."""
    h = hashlib.sha256()
    for sub in ("src", "configs", "scripts"):
        for p in sorted((STAGE2_ROOT / sub).rglob("*")):
            if p.is_file() and p.suffix in {".py", ".yaml", ".yml"} and "__pycache__" not in p.parts:
                h.update(str(p.relative_to(STAGE2_ROOT)).encode())
                h.update(p.read_bytes())
    cc = REPO_ROOT / "experiment_Files" / "05_cadence_check.py"
    if cc.exists():
        h.update(cc.read_bytes())
    return h.hexdigest()


def environment() -> dict:
    mods = {}
    for m in ("numpy", "pandas", "scipy", "sklearn", "matplotlib", "yaml", "pyarrow"):
        try:
            mods[m] = __import__(m).__version__
        except Exception:
            mods[m] = None
    return {"python": sys.version.split()[0], "platform": platform.platform(),
            "machine": platform.machine(), "packages": mods}


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(obj, path: Path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2, default=_json_default)


def _json_default(o):
    import numpy as np
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return None if np.isnan(o) else float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (Path,)):
        return str(o)
    if isinstance(o, (set, frozenset)):
        return sorted(o)
    return str(o)


class Stage:
    """Checkpointed pipeline stage: skipped when its marker exists for the same config hash."""

    def __init__(self, name: str, work_dir: Path, cfg_hash: str, force: bool = False):
        self.name = name
        self.marker = Path(work_dir) / "_stages" / f"{name}.done.json"
        self.cfg_hash = cfg_hash
        self.force = force
        self.t0 = None

    def done(self) -> bool:
        if self.force or not self.marker.exists():
            return False
        try:
            return json.loads(self.marker.read_text()).get("config_hash") == self.cfg_hash
        except Exception:
            return False

    def __enter__(self):
        self.t0 = time.time()
        LOG.info("=== stage %s: start", self.name)
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            write_json({"stage": self.name, "config_hash": self.cfg_hash, "finished_utc": utcnow(),
                        "wall_s": round(time.time() - self.t0, 2)}, self.marker)
            LOG.info("=== stage %s: done in %.1fs", self.name, time.time() - self.t0)
        else:
            LOG.error("=== stage %s: FAILED (%s: %s)", self.name, exc_type.__name__, exc)
        return False
