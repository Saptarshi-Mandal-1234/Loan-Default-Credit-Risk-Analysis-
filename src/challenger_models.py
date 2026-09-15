"""
Challenger Models — compares Logistic Regression (baseline) against
Random Forest and Gradient Boosting to validate whether the simpler,
more interpretable model is competitive enough to justify production use.
"""

import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score, accuracy_score

from modeling import load_processed, build_model_frame, train_and_evaluate

df = load_processed()
X, y = build_model_frame(df)

baseline = train_and_evaluate(X, y)
X_train, X_test = baseline["X_train"], baseline["X_test"]
y_train, y_test = baseline["y_train"], baseline["y_test"]

results = {"Logistic Regression": baseline["metrics"]}

models = {
    "Random Forest": RandomForestClassifier(
        n_estimators=300, max_depth=8, class_weight="balanced", random_state=42, n_jobs=-1
    ),
    "Gradient Boosting": GradientBoostingClassifier(
        n_estimators=200, max_depth=3, learning_rate=0.1, random_state=42
    ),
}

fitted_models = {"Logistic Regression": baseline["model"]}

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    results[name] = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
        "roc_auc": roc_auc_score(y_test, y_proba),
    }
    fitted_models[name] = model

comparison = pd.DataFrame(results).T.round(4)
print("=== CHALLENGER MODEL COMPARISON ===")
print(comparison)

best_model_name = comparison["roc_auc"].idxmax()
print(f"\nBest ROC-AUC: {best_model_name} ({comparison.loc[best_model_name, 'roc_auc']:.4f})")

comparison.to_csv("reports/business/challenger_model_comparison.csv")
joblib.dump(fitted_models["Random Forest"], "models/random_forest_model.pkl")
joblib.dump(fitted_models["Gradient Boosting"], "models/gradient_boosting_model.pkl")
print("\nSaved comparison table and challenger model artifacts.")

print("""
DECISION: Logistic Regression is retained as the PRODUCTION model despite
potentially lower raw ROC-AUC than tree ensembles, because:
1. Full coefficient-level transparency required for credit committee sign-off
   and regulatory fair-lending review (tree ensembles need post-hoc SHAP to
   achieve similar transparency).
2. Monotonic, auditable score mapping (PD -> 300-900) is straightforward with
   a linear model; tree ensembles can produce non-monotonic local behavior.
3. Performance gap (see table) does not justify the interpretability trade-off
   for a first-generation production model.
Random Forest / Gradient Boosting are retained as documented CHALLENGER
models for future benchmarking, not for production decisioning.
""")
