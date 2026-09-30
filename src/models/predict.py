"""Model inference and prediction serving module."""

import joblib
import pandas as pd


class PharmaInferenceEngine:
    def __init__(self, model_path="models/artifacts/champion_pharma_pipeline.joblib"):
        self.model = joblib.load(model_path)

    def predict_risk(self, df: pd.DataFrame) -> pd.DataFrame:
        probabilities = self.model.predict_proba(df)[:, 1]
        decisions = (probabilities >= 0.5).astype(int)
        return pd.DataFrame({
            "adverse_event_risk_score": probabilities,
            "predicted_serious_event": decisions
        })