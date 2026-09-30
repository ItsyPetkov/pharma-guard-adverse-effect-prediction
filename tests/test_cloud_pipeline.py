import unittest
import re


class TestCloudSql(unittest.TestCase):
    def test_syntax_checks(self):
        with open("sql/eda_queries.sql", "r") as f:
            eda_sql = f.read()
        self.assertTrue(re.search(r"DENSE_RANK\(\)\s+OVER", eda_sql, re.IGNORECASE))
        self.assertTrue(re.search(r"reporting_odds_ratio_ror", eda_sql, re.IGNORECASE))

    def test_snowflake_azure_ddl(self):
        with open("sql/snowflake_databricks_azure.sql", "r") as f:
            azure_sql = f.read()
        self.assertTrue(re.search(r"STORAGE_PROVIDER\s*=\s*'AZURE'", azure_sql, re.IGNORECASE))
        self.assertTrue(re.search(r"AZURE_TENANT_ID", azure_sql, re.IGNORECASE))
        self.assertTrue(re.search(r"abfss://", azure_sql, re.IGNORECASE))


if __name__ == "__main__":
    unittest.main()