"""Stage 2 data access. Read-only over the ExtraSensory primary feature files."""
import os, glob, hashlib, numpy as np, pandas as pd

LABEL_PREFIX = 'label:'
DROP_COLS = ('timestamp', 'label_source')

class Dataset:
    def __init__(self, csv_dir):
        self.dir = csv_dir
        self.files = sorted(glob.glob(os.path.join(csv_dir, '*.csv')))
        if not self.files:
            raise FileNotFoundError(f'No *.csv found in {csv_dir}. See README for the download step.')
        cols = pd.read_csv(self.files[0], nrows=1).columns.tolist()
        self.feature_cols = [c for c in cols if not c.startswith(LABEL_PREFIX) and c not in DROP_COLS]
        self.label_cols = [c for c in cols if c.startswith(LABEL_PREFIX)]
        self.uuids = [os.path.basename(f).split('.')[0] for f in self.files]
        self.path = dict(zip(self.uuids, self.files))
        self._cache = {}

    def validate_schema(self, expect_features=225, expect_users=60):
        problems = []
        if len(self.uuids) != expect_users:
            problems.append(f'expected {expect_users} participant files, found {len(self.uuids)}')
        if len(self.feature_cols) != expect_features:
            problems.append(f'expected {expect_features} feature columns, found {len(self.feature_cols)}')
        ref = set(self.feature_cols)
        for f in self.files:
            c = set(pd.read_csv(f, nrows=1).columns)
            if 'timestamp' not in c:
                problems.append(f'{os.path.basename(f)}: no timestamp column')
            if ref - c:
                problems.append(f'{os.path.basename(f)}: missing {len(ref - c)} feature columns')
        return problems

    def load(self, uuid, cache=True):
        """Return (timestamps int64 ascending, X float32 [n,225], NaNs preserved)."""
        if uuid in self._cache:
            return self._cache[uuid]
        df = pd.read_csv(self.path[uuid], usecols=['timestamp'] + self.feature_cols)
        df = df.sort_values('timestamp', kind='mergesort')
        ts = df['timestamp'].to_numpy(np.int64)
        X = df[self.feature_cols].to_numpy(np.float32)
        if cache:
            self._cache[uuid] = (ts, X)
        return ts, X

    def clear_cache(self):
        self._cache = {}

    def manifest(self):
        rows = []
        for u in self.uuids:
            p = self.path[u]
            rows.append(dict(uuid=u, file=os.path.basename(p), bytes=os.path.getsize(p),
                             md5=hashlib.md5(open(p, 'rb').read()).hexdigest()))
        return pd.DataFrame(rows)
