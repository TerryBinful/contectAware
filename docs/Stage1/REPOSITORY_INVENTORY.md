# REPOSITORY INVENTORY (Stage 1 — Phase 0)

**Repository:** `https://github.com/TerryBinful/contectAware.git`
**Inventoried:** 16 September 2026
**State at inventory:** branch `main`, single commit `ef16807` ("file structures and exp files", 16 Sep 2026 04:15 UTC). No other branches or tags.

---

## 1. Important absence

The task brief says the *Experimental Recovery & Research Pivot Execution Protocol* was uploaded to the repository. **It is not in the repository** at commit `ef16807`. The only document present is `docs/Research State Audit — Independent Verification.md`. Stage 1 was therefore executed against the six steps listed in the task message itself (inventory → pipeline → model output → authentication validity → dataset/temporal audit → reproduction). If the Protocol defines additional Phase 0–4 requirements, they have not been checked.

The Research State Audit refers to files `01`–`04`, `05_cadence_check.py`, `06_literature_to_add.md`, `MSc_Pivot_Audit.md`, `Review_1_Key_Findings.md` and `README.md`. **None of these are in the repository.**

No dataset files, saved models, `results/` folders, CSV tables or figures are committed. All original outputs exist only as outputs embedded inside notebooks.

---

## 2. File-by-file inventory (as found)

| Path | Size | Type | Executed? | What it is | Role in original research |
|---|---|---|---|---|---|
| `docs/Research State Audit — Independent Verification.md` | 27 KB | Markdown | — | Prior audit (15 Sep 2026), written **without** access to code or data | Context only |
| `experiment_Files/COMPLETE_ExtraSensory_Analysis_with_Hysteresis.ipynb` | 553 KB | Colab notebook, GPU T4 | **Yes** — cells 1–31 in order, one cell (a re-mount) skipped; outputs saved | CSCD 613 Big-Data exam notebook, Sections A–F, incl. hysteresis | **PRIMARY SOURCE of every number in `Partial_fulfilment.docx`** |
| `experiment_Files/Copy of COMPLETE_…Hysteresis.ipynb` | 553 KB | Colab notebook | Yes (identical outputs) | Duplicate; code differs only by one emoji in one `print` | Duplicate — no independent evidence |
| `experiment_Files/COMPLETE_…Hysteresis (2).ipynb` | 570 KB | Colab notebook | **No** (outputs cleared) | Code-identical to the primary notebook | Duplicate — no evidence |
| `experiment_Files/extrasensory_ml_analysis.ipynb` | 548 KB | Colab notebook, TPU | Partially; execution counters cleared, some outputs kept; hysteresis cell **failed** (`RuntimeError: Missing dependencies … gb_model`) | Earlier draft of the same exam pipeline (imputation comparison, ingestion benchmark, 90%-importance variant) | Precursor; **no model or hysteresis results survive** |
| `experiment_Files/extraSensoryDataset.ipynb` | 255 KB | Colab notebook | Partially | Cell 0: **synthetic** trust-score demo (`np.random.normal(80, 2.5)`), threshold vs hysteresis; cells 1–3: RAM/ingestion stress tests on `.csv.gz` files | Source of the "I/O latency / memory ceiling" Big-Data narrative. Cell 0 is simulated, **not** ExtraSensory |
| `experiment_Files/fusion.ipynb` | 1.3 MB | Notebook, **python2** kernel | Mostly stale outputs | Official *"Introduction to the ExtraSensory Dataset"* tutorial by Y. Vaizman (May 2017), lightly edited | Reference material. Its own output states: *"Every example has its timestamp, indicating the minute when the example was recorded"* |
| `experiment_Files/Section-G.ipynb` | 22 KB | Colab notebook | Yes | Exam Section G: synthetic Weather/Play dataset, entropy & information gain | **Unrelated** to authentication |
| `experiment_Files/Untitled4.ipynb` | 159 KB | Colab notebook | Yes | Section G variant with a synthetic "VPN authentication" dataset | **Unrelated** to ExtraSensory; synthetic |

Both Section-G notebooks set `STUDENT_ID = 12345678` (placeholder) as the seed while printing `22427613`, so their printed seed does not match the seed actually used. Not relevant to the authentication research, but recorded.

---

## 3. Data provenance

| Item | Finding |
|---|---|
| Path used by primary notebook | `/content/drive/MyDrive/ML Data/Heuristics/Files_csv/` (60 decompressed `*.features_labels.csv`) |
| Path used by stress-test notebook | `/content/drive/MyDrive/ML Data/Heuristics/zips/*.csv.gz` |
| Data committed to repo | **None** |
| Data used for Stage 1 | Official public archive `http://extrasensory.ucsd.edu/data/primary_data_files/ExtraSensory.per_uuid_features_labels.zip` (225,374,973 bytes, MD5 `9e44b3484b74cd8a370ff22894e0899b`, server last-modified 23 May 2017) |
| Is it the same data the notebook used? | **Yes, to every fingerprint available**: 60 identical UUID file names; first sorted file shape (2287, 278); 377,346 total rows; 13,505.2 total span-hours; 747.61 MB uncompressed; mean per-user missingness 16.5%; identical target user and row counts; identical RF feature-importance ranking to 4 d.p. (see `ORIGINAL_RESULTS_REPRODUCTION.md`). |

---

## 4. Environment provenance

| Item | Original (from notebook outputs) | Stage-1 reproduction |
|---|---|---|
| Platform | Google Colab, GPU T4 runtime (scikit-learn does not use the GPU) | Ubuntu 24, 1 vCPU, 4 GB RAM |
| Python | NOT ESTABLISHED FROM AVAILABLE EVIDENCE | 3.12.3 |
| NumPy / pandas | 2.0.2 / 2.2.2 (printed) | 2.0.2 / 2.2.2 |
| scikit-learn | 1.6.1 (printed in the precursor notebook only; primary notebook does not print it) | 1.6.1 |
| imbalanced-learn | NOT ESTABLISHED (installed unpinned via `pip install -q`) | 0.13.0 |
| SciPy | NOT ESTABLISHED | venv default |
| `requirements.txt`, lock file, seeds file | **Absent** | Added in `experiment_Files/stage1_reproduction/` |

---

## 5. Items added by Stage 1

```
docs/stage1_recovery_audit/
    REPOSITORY_INVENTORY.md                (this file)
    ORIGINAL_PIPELINE_RECONSTRUCTION.md
    AUTHENTICATION_VALIDITY_AUDIT.md
    DATASET_TEMPORAL_AUDIT.md
    ORIGINAL_RESULTS_REPRODUCTION.md
    STAGE1_EXECUTIVE_REPORT.md
experiment_Files/stage1_reproduction/
    README.md
    requirements.txt
    dataset_temporal_audit.py
    reproduce_original.py
    reproduce_cv.py
    results/   (JSON/CSV outputs only; no raw data)
```

No existing file was modified, renamed or deleted.

---

## 6. Inventory-level conclusions

1. Exactly **one** executed notebook produced the reported results. The other two "COMPLETE" notebooks are duplicates and add no independent replication.
2. Every quantitative claim about hysteresis in `Partial_fulfilment.docx` traces to cells 44, 46 and 50 of that one notebook, run once, on one user.
3. There is **no** code anywhere in the repository for: chronological 60/20/20 splitting, per-user imputation, exclusion of windows with >50% missing data, a 53-feature set, a TTT of 3 seconds, post-hysteresis accuracy/FAR/FRR, or a "ping-pong frequency per 1-minute window". These appear in the written documents only.
4. Some material described in the documents as experimental (the hysteresis "novelty demonstration" figure in `extraSensoryDataset.ipynb`) is **simulated** data.
