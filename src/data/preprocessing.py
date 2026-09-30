"""
Data Preprocessing Module for Pharmaceutical Adverse Event Records.
Handles missing data imputation, outlier treatment, and boundary validation.
"""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class PharmaDataCleaner(BaseEstimator, TransformerMixin):
    def __init__(self, clip_outliers: bool = True):
        self.clip_outliers = clip_outliers
        self.numeric_medians_ = {}
        self.categorical_modes_ = {}
        self.numeric_bounds_ = {}

    def fit(self, X: pd.DataFrame, y=None):
        X_df = X.copy()
        num_cols = X_df.select_dtypes(include=[np.number]).columns
        for col in num_cols:
            median_val = X_df[col].median()
            self.numeric_medians_[col] = 0.0 if np.isnan(median_val) else median_val
            q_low = X_df[col].quantile(0.01)
            q_high = X_df[col].quantile(0.99)
            self.numeric_bounds_[col] = (q_low, q_high)

        cat_cols = X_df.select_dtypes(include=["object", "category"]).columns
        for col in cat_cols:
            mode_val = X_df[col].mode()
            self.categorical_modes_[col] = mode_val[0] if not mode_val.empty else "UNKNOWN"
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X_df = X.copy()
        for col, median in self.numeric_medians_.items():
            if col in X_df.columns:
                X_df[col] = X_df[col].fillna(median)
                if self.clip_outliers and col in self.numeric_bounds_:
                    low, high = self.numeric_bounds_[col]
                    X_df[col] = np.clip(X_df[col], low, high)

        for col, mode in self.categorical_modes_.items():
            if col in X_df.columns:
                X_df[col] = X_df[col].fillna(mode).astype(str)

        if "patient_age" in X_df.columns:
            X_df["patient_age"] = np.clip(X_df["patient_age"], 0, 115)
        if "patient_weight_kg" in X_df.columns:
            X_df["patient_weight_kg"] = np.clip(X_df["patient_weight_kg"], 1.0, 300.0)
        return X_df