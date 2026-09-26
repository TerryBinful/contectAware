#!/usr/bin/env bash
# Rebuild every paper figure and the post-hoc table from the frozen result CSVs.
#
# Read-only with respect to the experiment: this rebuilds nothing under
# experiment_Files/Stage2/results/.../analysis/, refits no model, regenerates no score
# dump. It only reads CSV and JSON from there and writes into rendered/, checks/ and
# posthoc/ beside this script.
#
# Usage:  ./build.sh          rebuild everything
#         ./build.sh fig3     rebuild just the scripts whose name contains "fig3"
#
# Each figure script aborts rather than writing a figure whose labels would be cut off,
# and Figure 3 aborts if any of its three annotated numbers stops reproducing.
set -euo pipefail
cd "$(dirname "$0")"

FILTER="${1:-}"
STATUS=0
for f in scripts/fig*.py scripts/posthoc_*.py; do
    [[ -n "$FILTER" && "$f" != *"$FILTER"* ]] && continue
    echo "=== $f"
    if python3 "$f"; then :; else echo "    FAILED"; STATUS=1; fi
done
rm -rf scripts/__pycache__
exit $STATUS
