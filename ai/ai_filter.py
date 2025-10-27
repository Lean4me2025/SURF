import joblib
import numpy as np

def load_model(path=‘models/surf_xgb.pkl’):
“””
Returns (model, feature_columns) previously saved by train_clf.py
“””
pack = joblib.load(path)
return pack[‘model’], pack[‘cols’]

def score_row(model, cols, rowdict):
“””
Given a dictionary of current features (rowdict),
return predicted probability of ‘wave success’.
“””
x = np.array([[rowdict.get(c, np.nan) for c in cols]], dtype=float)
return float(model.predict_proba(x)[0, 1])

def size_from_prob(p, base_cap=0.25, min_cap=0.05, gain=0.4):
“””
Convert probability into position size fraction.
p=0.50 → ~min_cap; higher p increases size up to base_cap.
“””
size = gain * max(0.0, p - 0.5)
return max(min_cap, min(base_cap, size))
