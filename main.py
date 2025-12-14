"""
Public Health Data Insights Dashboard
Task 1: Data access, cleaning, filtering, summary, and CRUD operations
Developed using Test-Driven Development (TDD) approach
"""

import os
from datetime import datetime
import pandas as pd


def log_activity(message: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{timestamp} - INFO - {message}\n"
    try:
        with open("activity.log", "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass


def load_data(csv_path: str) -> pd.DataFrame:
    """
    Load vaccination data from CSV file
    """
    log_activity(f"Loading data from {csv_path}")

    if not os.path.exists(csv_path):
        log_activity(f"ERROR: File not found - {csv_path}")
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path)
    log_activity(f"Successfully loaded {len(df)} records")
    return df
