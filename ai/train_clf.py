import pandas as pd
import joblib
import xgboost as xgb
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import TimeSeriesSplit

def train_xgb(X, y, n_splits=5):
“””
Time-series CV to avoid lookahead bias.
Returns best model by ROC-AUC on validation folds.
“””
tscv = TimeSeriesSplit(n_splits=n_splits)
best_auc, best = -1.0, None
for tr, va in tscv.split(X):
model = xgb.XGBClassifier(
max_depth=4,
n_estimators=300,
learning_rate=0.05,
subsample=0.8,
colsample_bytree=0.8,
eval_metric=‘logloss’,
n_jobs=-1,
tree_method=“hist”
)
model.fit(X.iloc[tr], y.iloc[tr])
p = model.predict_proba(X.iloc[va])[:, 1]
auc = roc_auc_score(y.iloc[va], p)
if auc > best_auc:
best_auc, best = auc, model
return best, best_auc

if name == “main”:
“””
Example (uncomment and provide your dataset):
df = pd.read_csv(“data/merged_with_labels.csv”)
X = df[[“v_delta”,“vrr”,“vt”,“rsi”,“macd_hist”,“ret1”,“ret2”,“vret1”]]
y = df[“label”]
model, auc = train_xgb(X, y)
print(“CV ROC-AUC:”, auc)
joblib.dump({‘model’: model, ‘cols’: X.columns.tolist()}, “models/surf_xgb.pkl”)
“””
print(“Training script ready. Prepare X,y and uncomment example to run.”)
