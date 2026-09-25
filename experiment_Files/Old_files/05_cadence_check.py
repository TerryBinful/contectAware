#!/usr/bin/env python3
"""
05_cadence_check.py — verify the ExtraSensory frame period from timestamps.

THE FIRST THING TO RUN. Everything downstream (TTT in frames, meaning of the
baseline transition count, splice block lengths, cadence limitation) depends on
the actual inter-frame interval, which no project document states correctly.

Usage:
    python 05_cadence_check.py <path-to-user>.features_labels.csv [more files...]
    python 05_cadence_check.py /path/to/ExtraSensory/*.features_labels.csv

Expects a 'timestamp' column (unix seconds) as in the public release. If your
files are gzipped (.csv.gz) pandas handles that automatically.

Outputs, per file and pooled:
    - median / IQR / mode of consecutive timestamp differences (seconds)
    - fraction of gaps within 1.5x the median ("contiguous")
    - number of contiguous runs and their length distribution (frames, minutes)
    - total recording span in hours
    - what a 3-second TTT would mean in frames at this cadence

No dependencies beyond pandas and numpy.
"""
import sys
import numpy as np
import pandas as pd


def analyse(path):
    df = pd.read_csv(path)
    if "timestamp" not in df.columns:
        raise SystemExit(f"{path}: no 'timestamp' column. Columns start: {list(df.columns[:5])}")
    ts = np.sort(df["timestamp"].astype(float).values)
    d = np.diff(ts)
    d = d[d > 0]
    if len(d) == 0:
        raise SystemExit(f"{path}: fewer than two frames")

    med = float(np.median(d))
    q1, q3 = np.percentile(d, [25, 75])
    vals, counts = np.unique(np.round(d), return_counts=True)
    mode = float(vals[np.argmax(counts)])
    contiguous = float(np.mean(d <= 1.5 * med))

    # contiguous runs: break where gap > 2 * median
    breaks = np.where(d > 2 * med)[0]
    run_edges = np.concatenate([[0], breaks + 1, [len(ts)]])
    run_lengths = np.diff(run_edges)  # frames per run

    span_h = (ts[-1] - ts[0]) / 3600.0
    return dict(
        file=path,
        n_frames=len(ts),
        median_gap_s=med,
        iqr_s=(float(q1), float(q3)),
        mode_gap_s=mode,
        frac_contiguous=contiguous,
        n_runs=len(run_lengths),
        run_len_frames_median=float(np.median(run_lengths)),
        run_len_frames_p90=float(np.percentile(run_lengths, 90)),
        run_len_min_median=float(np.median(run_lengths) * med / 60.0),
        span_hours=span_h,
        diffs=d,
    )


def report(r):
    med = r["median_gap_s"]
    print(f"\n=== {r['file']} ===")
    print(f"frames                 : {r['n_frames']}")
    print(f"median gap             : {med:.1f} s   (IQR {r['iqr_s'][0]:.1f}–{r['iqr_s'][1]:.1f} s, mode {r['mode_gap_s']:.0f} s)")
    print(f"fraction contiguous    : {r['frac_contiguous']:.3f}  (gap <= 1.5 x median)")
    print(f"contiguous runs        : {r['n_runs']}  (median {r['run_len_frames_median']:.0f} frames ≈ {r['run_len_min_median']:.1f} min; p90 {r['run_len_frames_p90']:.0f} frames)")
    print(f"recording span         : {r['span_hours']:.1f} h")
    print(f"-- implications --")
    print(f"  1 frame              = {med:.0f} s  -> minimum meaningful TTT = 1 frame = {med/60:.2f} min")
    print(f"  TTT = 3 s            = {3/med:.3f} frames  -> {'INERT (sub-frame)' if 3 < med else 'ok'}")
    print(f"  60-s ping-pong window= {60/med:.2f} frames -> '>=3 transitions/min' {'is IMPOSSIBLE at this cadence' if 60/med < 3 else 'is possible'}")
    for L in (3, 10, 30, 60):
        print(f"  splice block L={L:>2} min = {int(np.ceil(L*60/med))} frames")


def main(paths):
    results = [analyse(p) for p in paths]
    for r in results:
        report(r)
    if len(results) > 1:
        pooled = np.concatenate([r["diffs"] for r in results])
        print("\n=== POOLED over", len(results), "files ===")
        print(f"median gap {np.median(pooled):.1f} s; IQR {np.percentile(pooled,25):.1f}–{np.percentile(pooled,75):.1f} s")
        print(f"fraction contiguous {np.mean(pooled <= 1.5*np.median(pooled)):.3f}")
    print("\nRecord the median gap in 01_preregistration_template.md before doing anything else.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1:])
