"""Database and Cloud credentials configuration module for Microsoft Azure and Partners."""

import os


class DatabaseConfig:
    # Microsoft Azure Cloud Platform - Storage & Synapse
    AZURE_SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID", "pharma-safety-subscription")
    AZURE_RESOURCE_GROUP = os.getenv("AZURE_RESOURCE_GROUP", "pharma-safety-rg")
    AZURE_STORAGE_ACCOUNT = os.getenv("AZURE_STORAGE_ACCOUNT", "pharmasafetylake")
    AZURE_CONTAINER = os.getenv("AZURE_CONTAINER", "pharma-adverse-events")
    AZURE_SYNAPSE_WORKSPACE = os.getenv("AZURE_SYNAPSE_WORKSPACE", "pharma-safety-synapse")
    AZURE_SYNAPSE_SQL_POOL = os.getenv("AZURE_SYNAPSE_SQL_POOL", "PharmaSafetyPool")
    AZURE_SYNAPSE_DATASET = "pharma_safety.adverse_events_curated"

    # Snowflake hosted on Microsoft Azure
    SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER", "pharma_admin")
    SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD", "")
    SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT", "azure_eastus2.snowflakecomputing.com")
    SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DB", "PHARMA_SAFETY_DB")
    SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA", "SAFETY_ANALYTICS")
    SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WH", "COMPUTE_WH")

    # Databricks on Microsoft Azure (Azure Databricks)
    DATABRICKS_HOST = os.getenv("DATABRICKS_HOST", "https://adb-1234567890123456.7.azuredatabricks.net")
    DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN", "")
    DATABRICKS_HTTP_PATH = os.getenv("DATABRICKS_HTTP_PATH", "/sql/1.0/endpoints/pharma_endpoint")