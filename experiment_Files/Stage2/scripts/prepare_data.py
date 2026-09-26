#!/usr/bin/env python3
"""Download, verify and decompress the ExtraSensory primary feature files.

Pure Python: no shell loops. The previous Colab cell used
    !for f in /content/es_raw/*.gz; do gunzip -c "$f" > "$DATA_DIR/$(basename $f .gz)"; done
inside an IPython `!` line, where `$f` is substituted from the *Python* namespace rather than
left for the shell. `f` does not exist there, so the loop wrote nothing and the CSV count was 0.

  python scripts/prepare_data.py --data-dir /content/extrasensory_csv
"""
import argparse, gzip, hashlib, os, shutil, sys, tempfile, time, urllib.request, zipfile

URL = 'http://extrasensory.ucsd.edu/data/primary_data_files/ExtraSensory.per_uuid_features_labels.zip'
ZIP_MD5 = '9e44b3484b74cd8a370ff22894e0899b'
ZIP_BYTES = 225374973
N_EXPECTED = 60

def _progress(done, total, t0):
    if not total:
        return
    pct = 100.0 * done / total
    mb, tmb = done / 1e6, total / 1e6
    el = max(time.time() - t0, 1e-6)
    sys.stdout.write(f'\r  {pct:5.1f}%  {mb:6.1f}/{tmb:.1f} MB  ({mb/el:.1f} MB/s)')
    sys.stdout.flush()

def download(dest, url=URL, chunk=1 << 20):
    if os.path.exists(dest) and os.path.getsize(dest) == ZIP_BYTES:
        print(f'archive already present: {dest}')
        return dest
    print(f'downloading {url}')
    t0 = time.time()
    with urllib.request.urlopen(url) as r, open(dest, 'wb') as out:
        total = int(r.headers.get('Content-Length') or 0)
        done = 0
        while True:
            buf = r.read(chunk)
            if not buf:
                break
            out.write(buf); done += len(buf); _progress(done, total, t0)
    print()
    return dest

def verify(path, strict=False):
    size = os.path.getsize(path)
    md5 = hashlib.md5()
    with open(path, 'rb') as fh:
        for b in iter(lambda: fh.read(1 << 20), b''):
            md5.update(b)
    d = md5.hexdigest()
    ok = (d == ZIP_MD5 and size == ZIP_BYTES)
    print(f'archive: {size:,} bytes (expected {ZIP_BYTES:,}); md5 {d} (expected {ZIP_MD5}) -> {"OK" if ok else "MISMATCH"}')
    if not ok and strict:
        raise SystemExit('archive verification failed; delete it and re-download')
    return ok

def extract(zip_path, data_dir):
    """Unzip and gunzip every member into data_dir as plain .csv. Idempotent."""
    os.makedirs(data_dir, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix='es_raw_')
    try:
        with zipfile.ZipFile(zip_path) as z:
            members = [m for m in z.namelist() if m.endswith('.gz')]
            print(f'archive contains {len(members)} .gz members; decompressing')
            for i, m in enumerate(members, 1):
                out_name = os.path.basename(m)[:-3]           # strip .gz
                out_path = os.path.join(data_dir, out_name)
                if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
                    continue
                z.extract(m, tmp)
                with gzip.open(os.path.join(tmp, m), 'rb') as src, open(out_path, 'wb') as dst:
                    shutil.copyfileobj(src, dst)
                if i % 10 == 0 or i == len(members):
                    print(f'  {i}/{len(members)}')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def check(data_dir):
    csvs = sorted(f for f in os.listdir(data_dir) if f.endswith('.csv'))
    empty = [f for f in csvs if os.path.getsize(os.path.join(data_dir, f)) == 0]
    return csvs, empty

def prepare(data_dir, work_dir='/content', strict=True):
    csvs, empty = ([], []) if not os.path.isdir(data_dir) else check(data_dir)
    if len(csvs) == N_EXPECTED and not empty:
        print(f'{len(csvs)} participant CSVs already present in {data_dir}')
        return data_dir
    zip_path = os.path.join(work_dir, 'extrasensory.zip')
    download(zip_path)
    verify(zip_path, strict=strict)
    extract(zip_path, data_dir)
    csvs, empty = check(data_dir)
    if empty:
        raise SystemExit(f'{len(empty)} CSV files are empty, e.g. {empty[:3]} - delete {data_dir} and retry')
    if len(csvs) != N_EXPECTED:
        raise SystemExit(f'expected {N_EXPECTED} participant CSVs, found {len(csvs)} in {data_dir}')
    total_mb = sum(os.path.getsize(os.path.join(data_dir, f)) for f in csvs) / 1e6
    print(f'{len(csvs)} participant CSVs ready in {data_dir} ({total_mb:.0f} MB)')
    return data_dir

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--data-dir', required=True); ap.add_argument('--work-dir', default='/content')
    ap.add_argument('--no-strict', action='store_true')
    a = ap.parse_args()
    prepare(a.data_dir, a.work_dir, strict=not a.no_strict)
