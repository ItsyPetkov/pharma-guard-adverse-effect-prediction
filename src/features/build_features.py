"""
Biomedical Feature Engineering Module.
Creates domain ratios, polypharmacy indices, and organ dysfunction metrics.
"""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class PharmaFeatureEngineer(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X: pd.DataFrame, y=None):
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        df = X.copy()

        # 1. Weight-adjusted dose intensity
        if "daily_dose_mg" in df.columns and "patient_weight_kg" in df.columns:
            safe_weight = np.where(df["patient_weight_kg"] <= 0, 70.0, df["patient_weight_kg"])
            df["dose_intensity_mg_per_kg"] = df["daily_dose_mg"] / safe_weight
        else:
            df["dose_intensity_mg_per_kg"] = 0.0

        # 2. Cumulative drug exposure estimate
        if "daily_dose_mg" in df.columns and "treatment_duration_days" in df.columns:
            df["cumulative_dose_mg"] = df["daily_dose_mg"] * np.maximum(df["treatment_duration_days"], 1)
        else:
            df["cumulative_dose_mg"] = 0.0

        # 3. Polypharmacy interaction burden
        if "concomitant_drug_count" in df.columns and "interaction_risk_index" in df.columns:
            df["polypharmacy_burden"] = df["concomitant_drug_count"] * (1.0 + df["interaction_risk_index"])
        else:
            df["polypharmacy_burden"] = 0.0

        # 4. Vulnerable Patient Risk Multiplier
        renal = df["renal_impairment_flag"].astype(int) if "renal_impairment_flag" in df.columns else 0
        hepatic = df["hepatic_impairment_flag"].astype(int) if "hepatic_impairment_flag" in df.columns else 0
        elderly = (df["patient_age"] >= 65).astype(int) if "patient_age" in df.columns else 0
        df["organ_dysfunction_score"] = renal + hepatic + elderly

        # 5. Acute vs Chronic Latency Ratio
        if "time_to_onset_days" in df.columns and "treatment_duration_days" in df.columns:
            duration = np.maximum(df["treatment_duration_days"], 1.0)
            df["onset_to_duration_ratio"] = np.clip(df["time_to_onset_days"] / duration, 0.0, 5.0)
        else:
            df["onset_to_duration_ratio"] = 1.0

        return df