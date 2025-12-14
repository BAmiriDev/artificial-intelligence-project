"""
Public Health Data Insights Dashboard
Task 1: Data access, cleaning, filtering, summary, and CRUD operations
Developed using Test-Driven Development (TDD) approach
"""

import os
from datetime import datetime


def log_activity(message: str) -> None:
    """
    Log user activities to `activity.log` by appending a timestamped line.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{timestamp} - INFO - {message}\n"
    try:
        with open("activity.log", "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass
