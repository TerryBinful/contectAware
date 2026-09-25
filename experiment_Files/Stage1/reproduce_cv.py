"""Re-execution of notebook cell 57 (5-fold CV on the SMOTE-balanced TRAINING set).
Requires cache produced by reproduce_original.py. n_jobs=-1 as in original.
Usage: python reproduce_cv.py <cache_dir>
"""
import sys, os, json, pickle, time, numpy as np
from sklearn.model_selection import StratifiedKFold, cross_val_score
C = sys.argv[1]; OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
m = pickle.load(open(os.path.join(C, 'models.pkl'), 'rb')); d = np.load(os.path.join(C, 'balanced.npz'))
X, y = d['X'], d['y']
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
res = {}
for name in ['lr', 'gb']:
    t = time.time()
    s = cross_val_score(m[name], X, y, cv=cv, scoring='accuracy', n_jobs=-1)
    res[name] = dict(scores=s.tolist(), mean=float(s.mean()), std=float(s.std()), time_s=time.time() - t)
    print(name, res[name], flush=True)
    json.dump(res, open(os.path.join(OUT, 'repro_cv_results.json'), 'w'), indent=2)
