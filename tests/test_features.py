import unittest
import pandas as pd
from src.features.build_features import PharmaFeatureEngineer


class TestPharmaFeatures(unittest.TestCase):
    def setUp(self):
        self.engineer = PharmaFeatureEngineer()
        self.df = pd.DataFrame({
            "daily_dose_mg": [100.0, 200.0],
            "patient_weight_kg": [50.0, 100.0],
            "treatment_duration_days": [10, 20],
            "concomitant_drug_count": [4, 2],
            "interaction_risk_index": [0.5, 0.2],
            "renal_impairment_flag": [1, 0],
            "hepatic_impairment_flag": [0, 0],
            "patient_age": [70, 30],
            "time_to_onset_days": [5, 10]
        })

    def test_dose_intensity_calculation(self):
        res = self.engineer.transform(self.df)
        self.assertAlmostEqual(res["dose_intensity_mg_per_kg"].iloc[0], 2.0)
        self.assertAlmostEqual(res["dose_intensity_mg_per_kg"].iloc[1], 2.0)

    def test_polypharmacy_burden(self):
        res = self.engineer.transform(self.df)
        self.assertAlmostEqual(res["polypharmacy_burden"].iloc[0], 4 * (1.0 + 0.5))


if __name__ == "__main__":
    unittest.main()