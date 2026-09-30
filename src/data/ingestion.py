"""Data Ingestion Module from Azure Blob / ADLS Gen2 or Local CSV extracts."""

import os
import pandas as pd


def load_dataset(filepath: str = "data/raw/pharma_adverse_events.csv") -> pd.DataFrame:
    """Loads pharmaceutical dataset from local storage or Azure cloud extract."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Adverse event dataset not found at: {filepath}")
    return pd.read_csv(filepath)