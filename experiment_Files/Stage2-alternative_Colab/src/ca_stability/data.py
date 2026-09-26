"""ExtraSensory data access: download/verify, load, chronological periods, contiguous runs.

Nothing in this module looks at classifier scores. Period and run assignment depend only on
timestamps, so they are outcome-blind by construction.
"""
from __future__ import annotations

import glob
import hashlib
import os
import shutil
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from .provenance import LOG

FILE_GLOBS = ("*.features_labels.csv.gz", "*.features_labels.csv")
META_COLS = ("timestamp", "label_source")


# ----------------------------------------------------------------------------- acquisition
def md5sum(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def find_participant_files(data_dir: Path) -> list[Path]:
    data_dir = Path(data_dir)
    found = {}
    for pattern in FILE_GLOBS:
        for p in glob.glob(str(data_dir / "**" / pattern), recursive=True):
            uid = participant_id(p)
            found.setdefault(uid, Path(p))          # prefer .csv.gz (first pattern)
    return [found[k] for k in sorted(found)]


def participant_id(path) -> str:
    return os.path.basename(str(path)).split(".")[0]


def ensure_dataset(cfg: dict, data_dir: Path) -> list[Path]:
    """Return the participant files, downloading + verifying the public archive if needed.

    Raises RuntimeError (DATA failure class) if the data cannot be obtained or verified.
    """
    data_dir = Path(data_dir)
    files = find_participant_files(data_dir)
    expected = int(cfg["data"].get("expected_participants", 60))
    if len(files) == expected:
        LOG.info("Dataset found: %d participant files in %s", len(files), data_dir)
        return files
    if files:
        LOG.warning("Found %d participant files (expected %d) in %s", len(files), expected, data_dir)
    zpath = data_dir / "ExtraSensory.per_uuid_features_labels.zip"
    if not zpath.exists():
        if not cfg["data"].get("auto_download", False):
            raise RuntimeError(f"DATA: ExtraSensory files not found in {data_dir} and auto_download is off")
        data_dir.mkdir(parents=True, exist_ok=True)
        LOG.info("Downloading %s -> %s", cfg["data"]["url"], zpath)
        tmp = zpath.with_suffix(".part")
        with urllib.request.urlopen(cfg["data"]["url"], timeout=120) as r, open(tmp, "wb") as f:
            shutil.copyfileobj(r, f, length=1 << 20)
        tmp.rename(zpath)
    digest = md5sum(zpath)
    if digest != cfg["data"]["md5"]:
        raise RuntimeError(f"DATA: archive MD5 {digest} != expected {cfg['data']['md5']} ({zpath})")
    LOG.info("Archive MD5 verified: %s", digest)
    with zipfile.ZipFile(zpath) as z:
        z.extractall(data_dir)
    files = find_participant_files(data_dir)
    if len(files) != expected:
        raise RuntimeError(f"DATA: after extraction found {len(files)} files, expected {expected}")
    return files


def dataset_fingerprint(files: list[Path]) -> dict:
    """Cheap, stable fingerprint of the participant files actually used."""
    h = hashlib.sha256()
    sizes = {}
    for p in files:
        s = os.path.getsize(p)
        sizes[participant_id(p)] = s
        h.update(participant_id(p).encode())
        h.update(str(s).encode())
    return {"n_files": len(files), "sha256_of_ids_and_sizes": h.hexdigest(), "total_bytes": int(sum(sizes.values()))}


# ----------------------------------------------------------------------------- columns
def all_columns(files: list[Path]) -> list[str]:
    return pd.read_csv(files[0], nrows=0).columns.tolist()


def feature_columns(cols: list[str]) -> list[str]:
    return [c for c in cols if not c.startswith("label:") and c not in META_COLS]


def label_columns(cols: list[str]) -> list[str]:
    return [c for c in cols if c.startswith("label:")]


def columns_for_groups(cols: list[str], prefixes: list[str]) -> list[str]:
    """Feature columns whose name starts with any prefix. NB: 'location' deliberately also
    matches 'location_quick_features' (the Stage 1 behaviour)."""
    feats = feature_columns(cols)
    return [c for c in feats if any(c.startswith(p) for p in prefixes)]


def select_feature_columns(cols: list[str], cfg: dict) -> list[str]:
    """Columns of the configured feature set minus any `features.exclude_patterns` substrings."""
    fs = cfg["features"]
    chosen = columns_for_groups(cols, fs["sets"][fs["set"]])
    excl = fs.get("exclude_patterns") or []
    return [c for c in chosen if not any(x in c for x in excl)]


# ----------------------------------------------------------------------------- loading
def load_frames(files: list[Path], feature_cols: list[str], label_cols: list[str],
                cache_dir: Path | None = None) -> pd.DataFrame:
    """Concatenate participants: uuid, timestamp, features (float32, NaN kept), labels (int8, NaN->0)."""
    key = hashlib.sha256(("|".join(feature_cols) + "#" + "|".join(label_cols) + "#" +
                          "|".join(participant_id(f) for f in files)).encode()).hexdigest()[:12]
    cache = Path(cache_dir) / f"frames_{key}.pkl" if cache_dir else None
    if cache is not None and cache.exists():
        LOG.info("Loading cached frames %s", cache.name)
        return pd.read_pickle(cache)
    parts = []
    for f in files:
        d = pd.read_csv(f, usecols=["timestamp", *feature_cols, *label_cols])
        d[feature_cols] = d[feature_cols].astype(np.float32)
        d[label_cols] = d[label_cols].fillna(0).astype(np.int8)
        d.insert(0, "uuid", participant_id(f))
        parts.append(d)
    df = pd.concat(parts, ignore_index=True)
    df["timestamp"] = df["timestamp"].astype(np.int64)
    df = df.sort_values(["uuid", "timestamp"], kind="mergesort").reset_index(drop=True)
    if cache is not None:
        df.to_pickle(cache)
    LOG.info("Loaded %d participants, %d frames, %d features, %d labels",
             df.uuid.nunique(), len(df), len(feature_cols), len(label_cols))
    return df


# ----------------------------------------------------------------------------- time model
def assign_periods(df: pd.DataFrame, fractions=(0.6, 0.2, 0.2), embargo_minutes: float = 30.0) -> pd.Series:
    """Per-participant chronological split into train / val / test, with embargo.

    Row i (0-based, time-sorted) of a participant with n rows is `train` if i < floor(f0*n),
    `val` if i < floor((f0+f1)*n), else `test`. Frames of `val` (resp. `test`) whose timestamp is
    within `embargo_minutes` of the last frame of the preceding period become `embargo` and are
    never used. Returns a categorical-like string Series aligned with df.
    """
    f0, f1, _ = fractions
    out = np.empty(len(df), dtype=object)
    emb = embargo_minutes * 60.0
    for uid, idx in df.groupby("uuid", sort=False).indices.items():
        idx = np.asarray(idx)
        ts = df["timestamp"].values[idx]
        order = np.argsort(ts, kind="mergesort")
        idx, ts = idx[order], ts[order]
        n = len(idx)
        a, b = int(np.floor(f0 * n)), int(np.floor((f0 + f1) * n))
        lab = np.array(["train"] * a + ["val"] * (b - a) + ["test"] * (n - b), dtype=object)
        if a > 0 and b > a:
            lab[a:b][ts[a:b] < ts[a - 1] + emb] = "embargo"
        if b > a and n > b:
            last_val_ts = ts[b - 1]
            lab[b:][ts[b:] < last_val_ts + emb] = "embargo"
        out[idx] = lab
    return pd.Series(out, index=df.index, name="period")


def assign_runs(df: pd.DataFrame, gap_break_s: float) -> pd.Series:
    """Contiguous-run id per participant: a new run starts where the gap exceeds gap_break_s,
    and (because streams never cross periods) wherever the period changes."""
    run = np.zeros(len(df), dtype=np.int32)
    for uid, idx in df.groupby("uuid", sort=False).indices.items():
        idx = np.asarray(idx)
        ts = df["timestamp"].values[idx]
        per = df["period"].values[idx] if "period" in df else np.array(["x"] * len(idx))
        new = np.ones(len(idx), dtype=bool)
        new[1:] = (np.diff(ts) > gap_break_s) | (per[1:] != per[:-1])
        run[idx] = np.cumsum(new) - 1
    return pd.Series(run, index=df.index, name="run")


def run_table(df: pd.DataFrame) -> pd.DataFrame:
    """One row per (uuid, period, run): start row index, length, time bounds."""
    g = df.reset_index().groupby(["uuid", "period", "run"], sort=True)
    t = g.agg(start=("index", "min"), end=("index", "max"),
              t_first=("timestamp", "min"), t_last=("timestamp", "max"), length=("index", "size")).reset_index()
    t["end"] = t["end"] + 1
    return t
