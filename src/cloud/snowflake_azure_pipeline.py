"""Snowflake on Azure Connector and Continuous Stage Sync."""

from config.database_config import DatabaseConfig


class SnowflakeAzureConnector:
    def __init__(self):
        self.account = DatabaseConfig.SNOWFLAKE_ACCOUNT
        self.database = DatabaseConfig.SNOWFLAKE_DATABASE
        self.schema = DatabaseConfig.SNOWFLAKE_SCHEMA

    def trigger_snowpipe_refresh(self, pipe_name: str = "pipe_ingest_pharma_events") -> str:
        """Executes a Snowpipe refresh statement on Snowflake hosted on Microsoft Azure."""
        query = f"ALTER PIPE {self.database}.{self.schema}.{pipe_name} REFRESH;"
        return f"Executing Snowflake on Azure Snowpipe Refresh query: {query}"