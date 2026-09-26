# Data

Raw ExtraSensory files are **not** committed. They are downloaded automatically by the pipeline
(or by `python scripts/download_data.py`) into `data/raw/` (or `$CA_DATA_DIR`) and verified:

- Source: http://extrasensory.ucsd.edu/data/primary_data_files/ExtraSensory.per_uuid_features_labels.zip
- MD5: `9e44b3484b74cd8a370ff22894e0899b` (identical to the Stage 1 fingerprint)
- Contents: 60 files `<UUID>.features_labels.csv.gz`
- Licence: CC BY-NC-SA 4.0 (Vaizman, Ellis & Lanckriet, 2017/2018)

If the archive cannot be downloaded or its MD5 differs, the pipeline stops with a `DATA` failure.
It never substitutes synthetic data; synthetic files are used only by the test-suite.
