import unittest
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from src.models.evaluate import evaluate_clinical_model


class TestModelTraining(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)
        n = 100
        self.X = pd.DataFrame({
            "dose": np.random.uniform(10, 500, n),
            "age": np.random.randint(18, 90, n)
        })
        self.y = pd.Series(np.random.choice([0, 1], size=n, p=[0.7, 0.3]))
        self.pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(random_state=42))
        ])
        self.pipeline.fit(self.X, self.y)

    def test_metrics(self):
        metrics = evaluate_clinical_model(self.pipeline, self.X, self.y)
        self.assertIn("roc_auc", metrics)
        self.assertTrue(0.0 <= metrics["roc_auc"] <= 1.0)


if __name__ == "__main__":
    unittest.main()