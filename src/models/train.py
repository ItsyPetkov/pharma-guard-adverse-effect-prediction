"""
Scikit-Learn Model Training & Hyperparameter Tuning Pipeline.
Trains and compares Random Forest and Logistic Regression models.
"""

import os
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def build_pipeline(numeric_features, categorical_features, model):
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features),
        ]
    )
    return Pipeline(steps=[("preprocessor", preprocessor), ("classifier", model)])


def train_and_tune_models(X_train: pd.DataFrame, y_train: pd.Series, numeric_cols, categorical_cols):
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    candidate_configs = {
        "random_forest": {
            "model": RandomForestClassifier(class_weight="balanced", random_state=42),
            "params": {"classifier__n_estimators": [50, 100], "classifier__max_depth": [5, 10]},
        },
        "logistic_regression": {
            "model": LogisticRegression(max_iter=500, class_weight="balanced", random_state=42),
            "params": {"classifier__C": [0.1, 1.0]},
        },
    }

    best_models = {}
    for name, config in candidate_configs.items():
        pipeline = build_pipeline(numeric_cols, categorical_cols, config["model"])
        grid = GridSearchCV(pipeline, param_grid=config["params"], cv=cv, scoring="roc_auc", n_jobs=-1)
        grid.fit(X_train, y_train)
        best_models[name] = {
            "best_estimator": grid.best_estimator_,
            "best_cv_roc_auc": grid.best_score_,
        }

    champion_name = max(best_models, key=lambda k: best_models[k]["best_cv_roc_auc"])
    champion_pipeline = best_models[champion_name]["best_estimator"]

    os.makedirs("models/artifacts", exist_ok=True)
    joblib.dump(champion_pipeline, "models/artifacts/champion_pharma_pipeline.joblib")
    return champion_pipeline, best_models