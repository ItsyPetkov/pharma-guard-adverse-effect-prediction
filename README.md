# PharmaGuard: Pharmacovigilance Prediction of Serious Adverse Drug Events
 
## Table of Contents
 
- [Project Background and Overview](#project-background-and-overview)
- [Repository Structure](#repository-structure)
- [Data Structure Overview](#data-structure-overview)
- [Results and Evaluation Overview](#results-and-evaluation-overview)
  * [Scenario 1 - Candidate Comparison: Random Forest vs. Logistic Regression](#scenario-1---candidate-comparison-random-forest-vs-logistic-regression)
  * [Scenario 2 - Champion Diagnostics and Reading the Signal Honestly](#scenario-2---champion-diagnostics-and-reading-the-signal-honestly)
- [EDA-based Insights and Predictive Features](#eda-based-insights-and-predictive-features)
  * [Initial Exploratory Data Analysis](#initial-exploratory-data-analysis)
  * [Data Cleaning and Transformation](#data-cleaning-and-transformation)
  * [Pharmacovigilance Signal Detection (ROR / PRR)](#pharmacovigilance-signal-detection-ror--prr)
  * [Feature Engineering](#feature-engineering)
  * [Feature Selection](#feature-selection)
- [Cloud Data Platform and SQL Layer](#cloud-data-platform-and-sql-layer)
- [Business Intelligence Dashboard Specification](#business-intelligence-dashboard-specification)
- [Recommendations](#recommendations)
- [Limitations](#limitations)
- [Future Work and Considerations](#future-work-and-considerations)
## Project Background and Overview
 
PharmaGuard (package name `pharma_guard`) is an end-to-end pharmacovigilance prototype: it takes spontaneous adverse-event reports for drugs, cleans them, engineers clinically motivated risk features, and trains a classifier that estimates whether a given report describes a **serious adverse event**. Around the Python/scikit-learn core, the repository also contains the SQL, cloud-connector and dashboard-specification layers that a production safety-analytics team would build on Microsoft Azure (Azure Synapse, Snowflake on Azure, and Azure Databricks), surfaced through Power BI.
 
**Project goal**: given a single adverse-event report (patient demographics, drug class and route, dose, treatment duration, concomitant medications, organ impairment flags, and time to onset), predict the probability that the event is serious (`serious_adverse_event = 1`), so that high-risk reports can be prioritised for safety review.
 
This project can be divided into the following workflow stages:
 
- **Data Ingestion**: 1,000 adverse-event reports are read from a local CSV (`data/raw/pharma_adverse_events.csv`); the config and SQL are laid out for the same data to live in Azure Blob / ADLS Gen2.
- **Data Cleaning**: `PharmaDataCleaner` performs median/mode imputation, 1st–99th percentile winsorisation of numeric columns, and clinical bounds checks on age (0–115) and weight (1–300 kg).
- **Feature Engineering**: `PharmaFeatureEngineer` derives five domain features (dose intensity per kg, cumulative dose, polypharmacy burden, organ dysfunction score, onset-to-duration ratio).
- **Exploratory Analysis and Feature Selection**: two notebooks cover EDA, disproportionality analysis (Reporting Odds Ratio / Proportional Reporting Ratio), mutual information, and RFECV.
- **Modelling and Evaluation**: a Random Forest and a Logistic Regression are tuned with `GridSearchCV` over stratified 3-fold cross-validation (scored on ROC-AUC); the better one is persisted as the "champion" and evaluated on a stratified 80/20 hold-out with ROC-AUC, PR-AUC, Brier score, and a confusion matrix.
- **Cloud SQL and BI Specification**: Snowflake-on-Azure and Azure Databricks DDL, advanced EDA SQL (ROR/PRR, window functions), a curated KPI view, and a Power BI specification with DAX measures.
Quick links:
 
- Configuration (paths, features, model and cloud settings): [`config/`](config)
- Python source (ingestion, preprocessing, features, models, cloud): [`src/`](src)
- Notebooks (EDA, feature engineering and selection): [`notebooks/`](notebooks)
- SQL (cloud DDL, EDA queries, KPI view): [`sql/`](sql)
- Dashboard schema and Power BI specification: [`dashboards/`](dashboards)
- Automated tests: [`tests/`](tests)
- End-to-end orchestration script: [`run_pipeline.py`](run_pipeline.py)
  
## Repository Structure
 
```text
pharma_prediction_platform/
├── config/
│   ├── config.yaml                                   # Paths, target, feature lists, model + cloud settings
│   └── database_config.py                            # Azure / Snowflake / Databricks settings (env-var driven)
├── dashboards/
│   ├── dashboard_schema.json                         # JSON Schema (draft-07) of the dashboard record structure
│   └── power_bi_spec.md                              # Power BI connection, DAX measures and layout specification
├── data/
│   ├── raw/
│   │   └── pharma_adverse_events.csv                 # 1,000 reports x 16 columns
│   └── processed/
│       └── pharma_features_selected.csv              # 1,000 rows x 23 columns (RFECV output)
├── models/
│   └── artifacts/
│       └── champion_pharma_pipeline.joblib           # Persisted champion scikit-learn pipeline
├── notebooks/
│   ├── exploratory_data_analysis.ipynb               # EDA, target analysis, ROR / PRR, correlations
│   └── feature_engineering_and_selection.ipynb       # Feature engineering, mutual information, RFECV
├── sql/
│   ├── aggregation_views.sql                         # Curated KPI view (vw_power_bi_adr_kpis)
│   ├── eda_queries.sql                               # Age cohorts, ROR / PRR, window-function ranking
│   └── snowflake_databricks_azure.sql                # Storage integration, stage, Snowpipe, Delta table DDL
├── src/
│   ├── __init__.py
│   ├── cloud/
│   │   ├── __init__.py
│   │   ├── databricks_azure_pipeline.py              # run_databricks_azure_delta_sync (stub)
│   │   └── snowflake_azure_pipeline.py               # SnowflakeAzureConnector (stub)
│   ├── data/
│   │   ├── __init__.py
│   │   ├── ingestion.py                              # load_dataset()
│   │   └── preprocessing.py                          # PharmaDataCleaner
│   ├── features/
│   │   ├── __init__.py
│   │   ├── build_features.py                         # PharmaFeatureEngineer
│   │   └── select_features.py                        # ClinicalFeatureSelector (variance filter + RFECV)
│   └── models/
│       ├── __init__.py
│       ├── evaluate.py                               # evaluate_clinical_model()
│       ├── predict.py                                # PharmaInferenceEngine
│       └── train.py                                  # build_pipeline(), train_and_tune_models()
├── tests/
│   ├── __init__.py
│   ├── test_cloud_pipeline.py                        # Static checks on the SQL files
│   ├── test_features.py                              # Dose intensity and polypharmacy arithmetic
│   ├── test_models.py                                # Evaluation metrics
│   └── test_preprocessing.py                         # Imputation and clipping
├── requirements.txt
├── run_pipeline.py                                   # Master end-to-end orchestration script
└── setup.py
```

## Data Structure Overview
 
The primary data set is `data/raw/pharma_adverse_events.csv`: **1,000 adverse-event reports and 16 columns**, one row per report, with no missing values, no duplicate rows and no duplicate `report_id`s. The `FDA-AER-*` report identifiers mimic FDA adverse-event-reporting style, but the value distributions (e.g. weight 50–109.9 kg, dose 21.1–600 mg, onset 1–30 days, and a single `report_date` for every row) indicate the data set is **synthetic / simulated** rather than an extract of real reports, and it should be treated as a demonstration data set.
 
The target is balanced-ish: **519 serious events (51.9%)** and **481 non-serious (48.1%)**.
 
| Column                    | Type   | Description                                                                          | Used in model?                                          |
| ------------------------- | ------ | ------------------------------------------------------------------------------------ | ------------------------------------------------------- |
| report\_id                | string | Unique report identifier (`FDA-AER-1000001` …).                                      | No — identifier                                         |
| report\_date              | date   | Report date (all rows are `2024-03-01`).                                             | No                                                      |
| patient\_age              | int    | Patient age in years (18–85).                                                        | Yes                                                     |
| patient\_sex              | string | Male (532) or Female (468).                                                          | Yes — one-hot encoded                                   |
| patient\_weight\_kg       | float  | Patient weight in kg (50–109.9).                                                     | Yes                                                     |
| drug\_class               | string | Analgesic, Antibiotic, Cardiovascular, CNS / Neurological, Immunosuppressant, Oncology. | Yes — one-hot encoded                                |
| route\_of\_administration | string | Oral, Intravenous or Subcutaneous.                                                   | Yes — one-hot encoded                                   |
| daily\_dose\_mg           | float  | Daily dose in mg (21.1–600).                                                         | Yes                                                     |
| treatment\_duration\_days | int    | Days on treatment (5–120).                                                           | Yes                                                     |
| concomitant\_drug\_count  | int    | Number of concomitant medications (0–8).                                             | Yes                                                     |
| interaction\_risk\_index  | float  | Drug–drug interaction risk score (0–1).                                              | Yes                                                     |
| renal\_impairment\_flag   | int    | 1 if renal impairment (161 patients).                                                | Yes — treated as categorical                            |
| hepatic\_impairment\_flag | int    | 1 if hepatic impairment (93 patients).                                               | Yes — treated as categorical                            |
| reporting\_source         | string | Pharmacist, Physician or Consumer.                                                   | Yes — one-hot encoded                                   |
| time\_to\_onset\_days     | int    | Days from treatment start to event onset (1–30).                                     | Yes                                                     |
| serious\_adverse\_event   | int    | Binary target: 1 = serious adverse event.                                            | Target variable                                         |
 
Engineered features (created by `PharmaFeatureEngineer`, see [Feature Engineering](#feature-engineering)) bring the modelling matrix to 17 input columns (11 numeric and 6 categorical), which expand to **29 features** after scaling and one-hot encoding inside the model pipeline.
 
## Results and Evaluation Overview
 
Two classifiers were tuned with `GridSearchCV` (3-fold stratified CV, ROC-AUC scoring) on an 80/20 stratified split (**800 training rows, 200 test rows**, `random_state=42`) and then evaluated on the same held-out test set:
 
| Model                                  | Best CV ROC-AUC | Test Accuracy | Precision | Recall | F1    | Test ROC-AUC | Test PR-AUC | Brier Score |
| -------------------------------------- | --------------- | ------------- | --------- | ------ | ----- | ------------ | ----------- | ----------- |
| Random Forest (**champion**, 50 trees, depth 5) | 0.709   | 63.5%         | 0.612     | 0.817  | 0.700 | 0.657        | 0.606       | 0.220       |
| Logistic Regression (C = 0.1)          | 0.678           | 65.0%         | 0.655     | 0.692  | 0.673 | 0.663        | 0.622       | 0.231       |
 
Precision, recall and F1 are reported for the positive class (`serious_adverse_event = 1`). The test set contains 104 serious and 96 non-serious reports, so a majority-class guess would score 52.0% accuracy and a constant-probability predictor would have a Brier score of about 0.25. Both models beat those baselines, but only modestly.
 
> **Reproducibility note**: these figures were reproduced by running `run_pipeline.py` on Python 3.12 with scikit-learn 1.8.0, pandas 3.0.2 and NumPy 2.4.4. Exact values can shift slightly across library versions.
 
### Scenario 1 - Candidate Comparison: Random Forest vs. Logistic Regression
 
Both candidates use the same preprocessing (standard scaling of numeric columns, one-hot encoding of categorical columns) and `class_weight="balanced"`.
 
**Key findings**:
 
- The Random Forest wins the model-selection step (CV ROC-AUC 0.709 vs. 0.678) and is therefore saved as the champion.
- On the 200-row hold-out the two models are effectively tied on ranking quality (ROC-AUC 0.657 vs. 0.663), and Logistic Regression is marginally ahead on accuracy, precision and Brier score. With only 200 test rows, these differences are well within sampling noise, so the choice of champion should not be read as a decisive win.
- The Random Forest trades precision for recall: it flags 81.7% of true serious events versus 69.2% for Logistic Regression, which is arguably the preferable behaviour for a safety-screening tool.
### Scenario 2 - Champion Diagnostics and Reading the Signal Honestly
 
The champion's confusion matrix on the test set is:
 
|                        | Predicted non-serious | Predicted serious |
| ---------------------- | --------------------- | ----------------- |
| **Actual non-serious** | 42                    | 54                |
| **Actual serious**     | 19                    | 85                |
 
**Key findings**:
 
- The model catches 85 of 104 serious events (recall 0.817) but at the cost of 54 false alarms; recall on the non-serious class is only 0.438.
- Overall ROC-AUC of 0.657 indicates a real but **weak** signal. This is consistent with the EDA, where no single feature correlates with the target by more than r ≈ 0.22.
- The largest Random Forest feature importances are `daily_dose_mg` (0.149), `polypharmacy_burden` (0.126), `patient_age` (0.119), `dose_intensity_mg_per_kg` (0.113) and `concomitant_drug_count` (0.110). Two of the top five are engineered features, which supports the value of the domain feature engineering.
- The Brier score of 0.220 is only slightly better than the ≈0.25 achievable by always predicting the base rate, so predicted probabilities should not yet be treated as well-calibrated risk estimates.
## EDA-based Insights and Predictive Features
 
This section summarises the exploratory work in [`notebooks/`](notebooks) and re-verified against the raw data.
 
### Initial Exploratory Data Analysis
 
Descriptive statistics for the numeric raw columns:
 
| Feature                    | Mean   | Std    | Min  | Median | Max   |
| -------------------------- | ------ | ------ | ---- | ------ | ----- |
| patient\_age               | 52.25  | 19.80  | 18   | 53.0   | 85    |
| patient\_weight\_kg        | 80.27  | 17.15  | 50   | 81.0   | 109.9 |
| daily\_dose\_mg            | 304.54 | 165.45 | 21.1 | 305.1  | 600   |
| treatment\_duration\_days  | 62.59  | 33.50  | 5    | 62.0   | 120   |
| concomitant\_drug\_count   | 3.85   | 2.58   | 0    | 4.0    | 8     |
| interaction\_risk\_index   | 0.50   | 0.29   | 0    | 0.49   | 1.0   |
| time\_to\_onset\_days      | 16.05  | 8.73   | 1    | 16.0   | 30    |
 
Pearson correlation with the target (`serious_adverse_event`):
 
| Feature                    | r       |
| -------------------------- | ------- |
| daily\_dose\_mg            | +0.221  |
| concomitant\_drug\_count   | +0.203  |
| patient\_age               | +0.156  |
| patient\_weight\_kg        | +0.014  |
| interaction\_risk\_index   | +0.007  |
| hepatic\_impairment\_flag  | +0.005  |
| treatment\_duration\_days  | −0.001  |
| time\_to\_onset\_days      | −0.018  |
| renal\_impairment\_flag    | −0.025  |
 
Patients with serious events are older on average (55.2 vs. 49.0 years). Higher dose, more concomitant drugs and older age are the only features with a meaningful univariate relationship to severity; notably, the raw `interaction_risk_index` is essentially uncorrelated with the outcome (r = 0.007).
 
### Data Cleaning and Transformation
 
`PharmaDataCleaner` (a scikit-learn `BaseEstimator`/`TransformerMixin`) is fitted to learn per-column medians, modes and 1st/99th percentile bounds, then:
 
- **Imputes** missing numeric values with the median and missing categoricals with the mode (fallback `"UNKNOWN"`).
- **Winsorises** numeric columns to their learned 1st–99th percentile range (optional via `clip_outliers`).
- **Enforces clinical bounds**: age clipped to 0–115 years, weight to 1–300 kg.
The supplied raw file is already complete (no missing values), so on this data the cleaner mainly acts as a validated safeguard for future, messier extracts; the unit test exercises it with injected NaNs and impossible values (age 150 / −5, weight 500 kg).
 
### Pharmacovigilance Signal Detection (ROR / PRR)
 
Disproportionality analysis compares the share of serious outcomes for each drug class against all other classes. Recomputed from the raw data (and matching the notebook's ROR/PRR table and the logic in [`sql/eda_queries.sql`](sql/eda_queries.sql)):
 
| Drug class         | Serious | Non-serious | Total | ROR  | PRR  |
| ------------------ | ------- | ----------- | ----- | ---- | ---- |
| Immunosuppressant  | 90      | 64          | 154   | 1.37 | 1.15 |
| CNS / Neurological | 104     | 81          | 185   | 1.24 | 1.10 |
| Antibiotic         | 74      | 67          | 141   | 1.03 | 1.01 |
| Analgesic          | 86      | 81          | 167   | 0.98 | 0.99 |
| Oncology           | 91      | 88          | 179   | 0.95 | 0.98 |
| Cardiovascular     | 74      | 100         | 174   | 0.63 | 0.79 |
 
Immunosuppressants and CNS/neurological drugs show the highest disproportionality, and cardiovascular drugs the lowest. These are point estimates only — no confidence intervals or minimum-case thresholds are computed — so none of these should be interpreted as a confirmed safety signal.
 
### Feature Engineering
 
Five features are derived in `PharmaFeatureEngineer`:
 
- `dose_intensity_mg_per_kg` = daily\_dose\_mg ÷ patient\_weight\_kg (weights ≤ 0 fall back to 70 kg)
- `cumulative_dose_mg` = daily\_dose\_mg × max(treatment\_duration\_days, 1)
- `polypharmacy_burden` = concomitant\_drug\_count × (1 + interaction\_risk\_index)
- `organ_dysfunction_score` = renal\_impairment\_flag + hepatic\_impairment\_flag + (age ≥ 65)
- `onset_to_duration_ratio` = time\_to\_onset\_days ÷ max(treatment\_duration\_days, 1), clipped to 0–5
The exact arithmetic of dose intensity and polypharmacy burden is covered by unit tests. Note that `run_pipeline.py` uses the first four features for modelling; `onset_to_duration_ratio` is computed but is not included in the model's feature lists.
 
### Feature Selection
 
The `feature_engineering_and_selection.ipynb` notebook one-hot encodes the feature set (24 columns), ranks features by **mutual information**, and then runs **RFECV** (Random Forest, 5-fold stratified CV, ROC-AUC scoring). RFECV retained **22 of 24** features, dropping `hepatic_impairment_flag` and `drug_class_Oncology`, and the result is exported to `data/processed/pharma_features_selected.csv` (1,000 rows × 23 columns including the target).
 
The top mutual-information scores were:
 
| Feature                                | Mutual information |
| -------------------------------------- | ------------------ |
| organ\_dysfunction\_score              | 0.0423             |
| daily\_dose\_mg                        | 0.0371             |
| drug\_class\_Immunosuppressant         | 0.0318             |
| drug\_class\_Cardiovascular            | 0.0303             |
| route\_of\_administration\_Subcutaneous | 0.0290            |
| concomitant\_drug\_count               | 0.0263             |
 
All scores are small in absolute terms, again pointing to a weak-signal problem. `src/features/select_features.py` (`ClinicalFeatureSelector`) packages the variance-threshold + RFECV logic as a reusable class, but it is not yet called by `run_pipeline.py`.
 
## Cloud Data Platform and SQL Layer
 
The [`sql/`](sql) folder and [`src/cloud/`](src/cloud) show the intended Azure deployment topology:
 
- **Snowflake on Azure** (`snowflake_databricks_azure.sql`): a storage integration and external stage over Azure Blob / ADLS Gen2, plus an auto-ingest Snowpipe (`pipe_ingest_pharma_events`) driven by Azure Event Grid.
- **Azure Databricks** (`snowflake_databricks_azure.sql`): a Delta Lake table (`pharma_safety.adverse_events_delta`) located on ADLS Gen2 (`abfss://…`).
- **Advanced EDA queries** (`eda_queries.sql`): age-cohort severity rates, ROR/PRR by drug class using a CTE, and a `DENSE_RANK()` window function ranking administration routes by severity within each drug class.
- **Curated KPI view** (`aggregation_views.sql`): `vw_power_bi_adr_kpis`, adding `polypharmacy_tier`, `clinical_vulnerability_profile` and `dose_intensity_per_kg` for BI consumption.
- **Python connectors** (`src/cloud/`): `SnowflakeAzureConnector.trigger_snowpipe_refresh()` and `run_databricks_azure_delta_sync()`. These are currently **stubs** that build and return a descriptive string; they do not open real connections.
## Business Intelligence Dashboard Specification
 
[`dashboards/power_bi_spec.md`](dashboards/power_bi_spec.md) specifies a Power BI report over `vw_power_bi_adr_kpis` (DirectQuery or scheduled refresh, every 4 hours), with DAX measures for total reports, serious-ADR rate, an acute-onset grouping (≤ 3 days, 4–14 days, > 14 days) and a high-risk patient flag. The planned layout contains:
 
1. **Executive KPI cards**: surveillance cohort size, serious-reaction prevalence, geriatric/renal high-risk patient count, and median onset latency.
2. **Temporal chart** of ADR occurrence by drug class.
3. **Disproportionality bar chart** (ROR / PRR) by drug family.
4. **Scatter matrix** of dose intensity vs. cumulative exposure, segmented by severity.
[`dashboards/dashboard_schema.json`](dashboards/dashboard_schema.json) is a JSON Schema (draft-07) describing the record structure that the dashboard consumes. The repository contains the specification only — there is no `.pbix` file.
 
## Recommendations
 
Based on the results above, the **Random Forest champion (test ROC-AUC 0.657, recall 0.817)** should be regarded as a proof-of-concept triage model, not a validated clinical decision tool. Given how close the Logistic Regression baseline is on the hold-out set, it is worth retaining as an interpretable comparator, and model comparison should rest on repeated cross-validation rather than a single 200-row split. Threshold selection (currently a fixed 0.5 in `PharmaInferenceEngine`) should be driven by the relative clinical cost of missed serious events versus false alarms, and probability calibration should be checked before scores are shown to reviewers.
 
## Limitations
 
Despite the pipeline being complete end to end, this project is still prone to the following limitations:
 
- **Synthetic, small data set**: 1,000 reports that appear simulated (identical `report_date`, uniform-looking ranges); results cannot be generalised to real spontaneous-reporting systems such as FAERS, which have missing data, duplicates, and strong reporting biases.
- **Weak predictive signal**: no feature correlates with the outcome above r ≈ 0.22, and the champion reaches only ROC-AUC ≈ 0.66 on a 200-row test set, so metrics carry wide uncertainty.
- **No time dimension**: because all reports share a single date, temporal trend analysis (and the planned temporal dashboard visual) is not meaningful with this data.
- **Signal detection without uncertainty**: ROR and PRR are point estimates with no confidence intervals or minimum case counts, and are calculated per drug class rather than per drug–event pair.
- **Association, not causation**: the model identifies correlates of reported severity; it does not establish that a drug or dose *caused* an event.
- **Cloud layer is illustrative**: the Azure, Snowflake and Databricks components are DDL, configuration and stubs that have not been exercised against live services.
## Future Work and Considerations
 
To build upon this work, the following steps could be considered:
 
- **Pin and package the environment**: pin exact dependency versions (or ship a lockfile), retrain and re-commit the model artifact, and record the training library versions alongside it (e.g. a model card or metadata JSON).
- **Fix the fit-before-split leakage**: place `PharmaDataCleaner` and `PharmaFeatureEngineer` inside the cross-validated `Pipeline`, and wire `ClinicalFeatureSelector` in so feature selection is also evaluated without leakage.
- **Make the config the source of truth**: read folds, algorithm choice and `models_dir` from `config.yaml`, and add a CLI or `python -m` entry point that does not depend on the working directory.
- **Strengthen evaluation**: use repeated stratified CV, report confidence intervals, add calibration curves and threshold/PR-curve analysis, and test gradient-boosted models and SHAP explanations.
- **Correct the notebooks and SQL/DAX**: fix the mislabelled target table and narrative findings, unify the SQL dialect for the target platform, and align the DAX vulnerability categories with the view.
- **Make the cloud layer real**: implement actual Snowflake / Databricks / Azure Blob I/O behind the connector classes, and add integration tests.
- **Add real-world data and validation**: evaluate on de-identified public reports (e.g. FAERS) with proper MedDRA coding, deduplication, and time-based train/test splits, and add confidence intervals to the disproportionality statistics.
- **Ship the dashboard**: build the Power BI report from the specification and connect the model's risk score to the KPI view so reviewers can prioritise high-risk cases.
 
