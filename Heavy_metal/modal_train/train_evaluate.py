
import os
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

DATA_PATH = "pollution_clean.csv"
TARGET = "HMPI"
# ----------------------

os.makedirs("models", exist_ok=True)
os.makedirs("results", exist_ok=True)

df = pd.read_csv(DATA_PATH)
X = df.drop(columns=[TARGET])
y = df[TARGET]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

models = {
    "Ridge": (Ridge(), {"alpha": [0.1, 1, 10]}),
    "RandomForest": (
        RandomForestRegressor(random_state=42),
        {"n_estimators": [100, 200], "max_depth": [None, 10, 20]},
    ),
}

rows, best_name, best_model, best_r2 = [], None, None, -np.inf
for name, (model, grid) in models.items():
    gs = GridSearchCV(model, grid, cv=5, scoring="r2", n_jobs=-1)
    gs.fit(X_train, y_train)
    pred = gs.best_estimator_.predict(X_test)
    r2 = r2_score(y_test, pred)
    rows.append({
        "Model": name,
        "Best Params": gs.best_params_,
        "CV R2": cross_val_score(gs.best_estimator_, X, y, cv=5, scoring="r2").mean(),
        "Test R2": r2,
        "MAE": mean_absolute_error(y_test, pred),
        "RMSE": np.sqrt(mean_squared_error(y_test, pred)),
    })
    if r2 > best_r2:
        best_name, best_model, best_r2, best_pred = name, gs.best_estimator_, r2, pred

results = pd.DataFrame(rows)
results.to_csv("results/metrics.csv", index=False)
print(results)

joblib.dump(best_model, "models/best_model.pkl")
print(f"Best model: {best_name} (R2={best_r2:.3f}) saved to models/best_model.pkl")

# Actual vs predicted plot
plt.figure(figsize=(5, 5))
plt.scatter(y_test, best_pred, alpha=0.7)
lims = [min(y_test.min(), best_pred.min()), max(y_test.max(), best_pred.max())]
plt.plot(lims, lims, "r--")
plt.xlabel("Actual HMPI")
plt.ylabel("Predicted HMPI")
plt.title(f"{best_name}: Actual vs Predicted")
plt.tight_layout()
plt.savefig("results/actual_vs_predicted.png", dpi=150)

if hasattr(best_model, "feature_importances_"):
    imp = pd.Series(best_model.feature_importances_, index=X.columns).sort_values()
    imp.plot(kind="barh", figsize=(6, 4), title="Feature Importance")
    plt.tight_layout()
    plt.savefig("results/feature_importance.png", dpi=150)
