-- ============================================================================
-- SNOWFLAKE ON AZURE & AZURE DATABRICKS CLOUD DDL
-- ============================================================================

-- 1. Snowflake on Azure: Storage Integration with Azure Blob / ADLS Gen2
CREATE OR REPLACE STORAGE INTEGRATION azure_pharma_storage_int
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = 'AZURE'
  ENABLED = TRUE
  AZURE_TENANT_ID = '<your-azure-active-directory-tenant-id>'
  STORAGE_ALLOWED_LOCATIONS = ('azure://pharmasafetylake.blob.core.windows.net/pharma-adverse-events/');

-- 2. Snowflake External Stage using the Azure Storage Integration
CREATE OR REPLACE STAGE pharma_safety_azure_stage
  STORAGE_INTEGRATION = azure_pharma_storage_int
  URL = 'azure://pharmasafetylake.blob.core.windows.net/pharma-adverse-events/raw/'
  FILE_FORMAT = (TYPE = 'CSV' SKIP_HEADER = 1 FIELD_OPTIONALLY_ENCLOSED_BY = '"');

-- 3. Snowflake Continuous Snowpipe with Azure Event Grid notifications
CREATE OR REPLACE PIPE pipe_ingest_pharma_events
  AUTO_INGEST = TRUE
  INTEGRATION = 'AZURE_EVENT_GRID_INT'
  AS
  COPY INTO pharma_safety.adverse_events_raw
  FROM @pharma_safety_azure_stage
  FILE_FORMAT = (TYPE = 'CSV' SKIP_HEADER = 1);

-- 4. Azure Databricks Delta Lake External Table on ADLS Gen2
CREATE TABLE IF NOT EXISTS pharma_safety.adverse_events_delta (
    report_id STRING,
    report_date DATE,
    patient_age INT,
    patient_sex STRING,
    patient_weight_kg DOUBLE,
    drug_class STRING,
    route_of_administration STRING,
    daily_dose_mg DOUBLE,
    treatment_duration_days INT,
    concomitant_drug_count INT,
    interaction_risk_index DOUBLE,
    renal_impairment_flag INT,
    hepatic_impairment_flag INT,
    reporting_source STRING,
    time_to_onset_days INT,
    serious_adverse_event INT
)
USING DELTA
LOCATION 'abfss://pharma-datalake@pharmasafetylake.dfs.core.windows.net/curated/adverse_events/';