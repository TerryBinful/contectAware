#!/usr/bin/env bash
# Rebuild every paper artefact -- figures and tables -- from the frozen v2 analysis CSVs.
#
# Read-only with respect to the experiment: this refits no model, regenerates no score
# dump, and writes nothing under experiment_Files/Stage2/results/.../analysis/. It reads
# CSV and JSON from there and writes into figures/{rendered,checks,posthoc}/ and
# tables/tables.md.
#
# Usage:  ./build.sh            rebuild everything
#         ./build.sh fig3       rebuild only the parts whose name contains "fig3"
#         ./build.sh tables     rebuild only the tables
#
# Each figure script aborts rather than writing a figure whose labels would be cut off,
# and fig3 aborts if any of its three annotated numbers stops reproducing.
#
# Requires: python3 with pandas, numpy, matplotlib, pyarrow (fig5 reads a parquet dump)
# and scipy (Table 7's Spearman rho).
set -euo pipefail
cd "$(dirname "$0")"

ANALYSIS="../../experiment_Files/Stage2/results/mechanism_comparison_v2/analysis"
if [[ ! -d "$ANALYSIS" ]]; then
    echo "error: analysis directory not found at $ANALYSIS" >&2
    echo "       run this from a full clone -- the frozen results must be present." >&2
    exit 2
fi

FILTER="${1:-}"
STATUS=0

# ---- figures ---------------------------------------------------------------------
for f in figures/scripts/fig*.py figures/scripts/posthoc_*.py; do
    [[ -n "$FILTER" && "$f" != *"$FILTER"* ]] && continue
    echo "=== $f"
    if python3 "$f"; then :; else echo "    FAILED"; STATUS=1; fi
done

# ---- tables ----------------------------------------------------------------------
# make_tables.py is the reviewer's script, kept byte-for-byte as delivered: it takes the
# analysis directory as its one argument and writes markdown to stdout. The redirect
# lives here rather than in the script so the script stays verbatim and auditable.
if [[ -z "$FILTER" || "tables/make_tables.py" == *"$FILTER"* ]]; then
    echo "=== tables/make_tables.py"
    if python3 tables/make_tables.py "$ANALYSIS" > tables/tables.md; then
        echo "  wrote tables/tables.md ($(grep -c '^### Table' tables/tables.md) tables, $(wc -l < tables/tables.md) lines)"
    else
        echo "    FAILED"; STATUS=1
    fi
fi

rm -rf figures/scripts/__pycache__
exit $STATUS
