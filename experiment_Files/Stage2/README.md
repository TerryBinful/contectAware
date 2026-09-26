# Stage 2 — experiment package (code, configs, tests, results)

Narrative documentation for this stage lives in **`docs/Stage2/`**:

| Document | Contents |
|---|---|
| `README_STAGE2_PROTOCOL.md` | Stage 2 protocol rebuild (per-user models, chronological splits, unseen impostors, feature ablation) |
| `README_MECHANISM_COMPARISON.md` | the post-pivot mechanism-comparison experiment: question, hypothesis, design, execution |
| `FINAL_PROTOCOL_AUDIT.md` | the 24-section protocol audit of the corrected final run |
| `STAGE2_FINAL_CORRECTED_EXECUTION_REPORT.md` | corrected final run (31/31 users) |
| `STAGE2_SENSITIVITY_ANALYSIS_REPORT.md` | complete-feasibility subset and FAR 0.03/0.05/0.07 sensitivity |
| `STAGE2_RESOURCE_AUDIT.md`, `STAGE2_EXECUTION_REPORT.md` | earlier Stage 2 audit and partial-run report |

## This folder

```
experiment_Files/Stage2/
├── src/        data_io, features, protocol, experiment, evaluate, benchmark, calibrate,
│               mechanisms, metrics
├── scripts/    run_dataset_audit, run_stage2, run_mechanism_comparison,
│               analyse_mechanism_comparison, sensitivity_complete_feasibility,
│               make_sensitivity_report, make_report
├── configs/    mechanism_comparison, sensitivity_far_003/007, stage2_primary, pilot, ...
├── tests/      test_mechanisms.py (18), test_leakage.py (16)
├── colab/      Stage2_ExtraSensory_Colab.ipynb
├── results/    dataset_audit/, mechanism_comparison/ (PRIMARY + sensitivity/),
│               stage2_exploratory_pre_calibration_fix/ (ARCHIVED, superseded),
│               primary/, pilot/, pilot_mechanism/, costprobe/ (Stage 2 ablation + pilots)
└── figures/, logs/
```

## Which results are which

- **Primary:** `results/mechanism_comparison/` — corrected final run, 31 users, FAR 0.05 ± 0.01.
- **Sensitivity:** `results/mechanism_comparison/sensitivity/` — complete-feasibility subset (6 users) and FAR 0.03 / 0.07.
- **Archived/exploratory:** `results/stage2_exploratory_pre_calibration_fix/` — superseded, do not cite.

## Running

Data is not committed (≈748 MB); download instructions are in `docs/Stage2/README_STAGE2_PROTOCOL.md` §4.

```bash
pip install numpy==2.0.2 pandas==2.2.2 scikit-learn==1.6.1 scipy matplotlib tabulate
cd experiment_Files/Stage2

python scripts/run_dataset_audit.py --data <csv_dir> --out results/dataset_audit
python scripts/run_mechanism_comparison.py --config configs/mechanism_comparison.json \
       --data <csv_dir> --out results/mechanism_comparison [--resume]
python scripts/analyse_mechanism_comparison.py --out results/mechanism_comparison
python scripts/sensitivity_complete_feasibility.py --primary results/mechanism_comparison \
       --out results/mechanism_comparison/sensitivity/complete_feasibility
python scripts/make_sensitivity_report.py --primary results/mechanism_comparison \
       --sens results/mechanism_comparison/sensitivity \
       --report ../../docs/Stage2/STAGE2_SENSITIVITY_ANALYSIS_REPORT.md

python tests/test_mechanisms.py && python tests/test_leakage.py results/mechanism_comparison
```

`experiment_metadata.json` inside each results directory records the folder path as it was at execution
time; those files are run provenance and are intentionally not rewritten by later reorganisation.
