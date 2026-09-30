import unittest
import numpy as np
import pandas as pd
from src.data.preprocessing import PharmaDataCleaner


class TestPharmaPreprocessing(unittest.TestCase):
    def setUp(self):
        self.mock_data = pd.DataFrame({
            "patient_age": [25, 45, np.nan, 150, -5],
            "patient_weight_kg": [70.0, np.nan, 80.0, 500.0, 10.0],
            "daily_dose_mg": [100.0, 200.0, np.nan, 300.0, 50.0],
            "patient_sex": ["Male", "Female", np.nan, "Male", "Female"],
            "drug_class": ["Cardiovascular", "Oncology", "CNS", np.nan, "Cardiovascular"]
        })
        self.cleaner = PharmaDataCleaner(clip_outliers=True)

    def test_imputation_and_clipping(self):
        cleaned_df = self.cleaner.fit_transform(self.mock_data)
        self.assertEqual(cleaned_df.isna().sum().sum(), 0)
        self.assertTrue((cleaned_df["patient_age"] >= 0).all())
        self.assertTrue((cleaned_df["patient_age"] <= 115).all())


if __name__ == "__main__":
    unittest.main()