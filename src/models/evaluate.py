"""
Model Evaluation and Pharmacovigilance Diagnostics.
Computes ROC-AUC, Average Precision (PR-AUC), Brier Score, and Confusion Matrix.
"""

from typing import Any, Dict
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)


def evaluate_clinical_model(pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Any]:
    y_pred_proba = pipeline.predict_proba(X_test)[:, 1]
    y_pred = pipeline.predict(X_test)

    roc_auc = roc_auc_score(y_test, y_pred_proba)
    pr_auc = average_precision_score(y_test, y_pred_proba)
    brier = brier_score_loss(y_test, y_pred_proba)
    cm = confusion_matrix(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)

    metrics = {
        "roc_auc": float(roc_auc),
        "pr_auc": float(pr_auc),
        "brier_score_loss": float(brier),
        "confusion_matrix": cm.tolist(),
        "classification_report": report,
    }
    return metrics