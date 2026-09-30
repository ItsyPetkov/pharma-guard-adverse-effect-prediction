"""
Feature Selection Pipeline.
Executes Variance Thresholding and Recursive Feature Elimination (RFECV).
"""

from typing import List
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import RFECV, VarianceThreshold, mutual_info_classif
from sklearn.model_selection import StratifiedKFold


class ClinicalFeatureSelector:
    def __init__(self, variance_thresh: float = 0.01, cv_folds: int = 3):
        self.variance_thresh = variance_thresh
        self.cv_folds = cv_folds
        self.var_filter = VarianceThreshold(threshold=variance_thresh)
        self.rfecv = None
        self.selected_columns: List[str] = []

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.var_filter.fit(X)
        retained_mask = self.var_filter.get_support()
        retained_cols = X.columns[retained_mask].tolist()
        X_var = X[retained_cols]

        base_estimator = RandomForestClassifier(
            n_estimators=30, max_depth=5, class_weight="balanced", random_state=42, n_jobs=-1
        )
        cv = StratifiedKFold(n_splits=self.cv_folds, shuffle=True, random_state=42)
        self.rfecv = RFECV(
            estimator=base_estimator,
            step=1,
            cv=cv,
            scoring="roc_auc",
            min_features_to_select=3,
            n_jobs=-1,
        )
        self.rfecv.fit(X_var, y)
        self.selected_columns = [
            col for col, sel in zip(retained_cols, self.rfecv.support_) if sel
        ]
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        return X[self.selected_columns]

    def get_mutual_info(self, X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
        mi = mutual_info_classif(X[self.selected_columns], y, random_state=42)
        return pd.DataFrame({
            "feature": self.selected_columns,
            "mutual_info": mi
        }).sort_values(by="mutual_info", ascending=False)