# Stage 1 — Faithful reproduction & audit code

Purpose: reproduce **exactly** what `../COMPLETE_ExtraSensory_Analysis_with_Hysteresis.ipynb` did, and
measure (without changing) properties of that pipeline. **No redesign, tuning, or new mechanism is implemented here.**

## Data (not committed)
```bash
curl -O http://extrasensory.ucsd.edu/data/primary_data_files/ExtraSensory.per_uuid_features_labels.zip
# MD5 9e44b3484b74cd8a370ff22894e0899b, 225,374,973 bytes
unzip ExtraSensory.per_uuid_features_labels.zip -d raw
mkdir csv && for f in raw/*.gz; do gunzip -c "$f" > "csv/$(basename "$f" .gz)"; done
```

## Run
```bash
python -m venv venv && . venv/bin/activate && pip install -r requirements.txt
python dataset_temporal_audit.py  /path/csv                 # ~1 min
python reproduce_original.py      /path/csv  /path/cache    # ~12 min on 1 vCPU
python leakage_shortcut_diagnostics.py /path/csv /path/cache
python reproduce_cv.py            /path/cache               # ~40 min on 1 vCPU
```

| Script | Mirrors notebook cells | Adds |
|---|---|---|
| `dataset_temporal_audit.py` | — | cadence, runs, missingness per participant |
| `reproduce_original.py` | 7–8, 11–12, 18–53 (verbatim logic, seeds, order) | `DIAGNOSTICS` block (clearly separated; read-only) |
| `leakage_shortcut_diagnostics.py` | — | split adjacency, altitude-missingness shortcut, closed-set check |
| `reproduce_cv.py` | 57 | — |

## Results (`results/`)
- `repro_results.json` — every reproduced number + diagnostics
- `repro_cv_results.json` — 5-fold CV
- `repro_leakage_shortcut_diagnostics.json`
- `repro_rf_feature_importance.csv`, `repro_per_impostor_acceptance_test.csv`
- `dataset_temporal_summary.json`, `dataset_per_user_temporal.csv`

Hardware used: 1 vCPU, 4 GB RAM, Python 3.12.3. Deviations from the original are only file paths, removal of plotting,
and `del` of intermediates (no numeric effect).
