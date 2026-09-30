#!/usr/bin/env python3
"""
Master End-to-End Orchestration Pipeline.
Loads data, applies cleaning, constructs features, trains, and evaluates models.
"""

import yaml
import pandas as pd
from sklearn.model_selection import train_test_split
from src.data.preprocessing import PharmaDataCleaner
from src.features.build_features import PharmaFeatureEngineer
from src.models.train import train_and_tune_models
from src.models.evaluate import evaluate_clinical_model


def run():
    print("=" * 65)
    print("   PHARMAGUARD END-TO-END PREDICTION & SAFETY PIPELINE")
    print("=" * 65)

    # 1. Ingest Config & Data
    with open("config/config.yaml", "r") as f:
        cfg = yaml.safe_load(f)

    raw_path = cfg["data"]["raw_data_path"]
    print(f"\n[1/5] Ingesting adverse event records from: {raw_path}")
    df = pd.read_csv(raw_path)
    print(f"      Loaded {len(df)} patient reports.")

    # 2. Preprocess & Clean
    print("\n[2/5] Cleaning and imputing biomedical values...")
    cleaner = PharmaDataCleaner()
    df_clean = cleaner.fit_transform(df)

    # 3. Domain Feature Engineering
    print("\n[3/5] Engineering clinical features (dose intensity, polypharmacy)...")
    engineer = PharmaFeatureEngineer()
    df_features = engineer.transform(df_clean)

    target_col = cfg["data"]["target_column"]
    X = df_features.drop(columns=[target_col, "report_id", "report_date"])
    y = df_features[target_col]

    numeric_cols = [c for c in cfg["features"]["numerical_cols"] if c in X.columns] + [
        "dose_intensity_mg_per_kg",
        "cumulative_dose_mg",
        "polypharmacy_burden",
        "organ_dysfunction_score",
    ]
    categorical_cols = [c for c in cfg["features"]["categorical_cols"] if c in X.columns]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=cfg["project"]["random_state"]
    )

    # 4. Model Training & Hyperparameter Tuning
    print("\n[4/5] Training candidate models using Stratified K-Fold CV...")
    champion, candidates = train_and_tune_models(X_train, y_train, numeric_cols, categorical_cols)

    # 5. Diagnostic Evaluation
    print("\n[5/5] Evaluating champion model on clinical validation set...")
    metrics = evaluate_clinical_model(champion, X_test, y_test)

    print("\n" + "=" * 65)
    print(f"  Champion Validation ROC-AUC : {metrics['roc_auc']:.4f}")
    print(f"  Champion Validation PR-AUC  : {metrics['pr_auc']:.4f}")
    print(f"  Champion Brier Loss Score   : {metrics['brier_score_loss']:.4f}")
    print("=" * 65)
    print("Pipeline execution completed successfully!\n")


if __name__ == "__main__":
    run()