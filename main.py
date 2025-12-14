"""
Test-Driven Development (TDD) Test Suite for Public Health Dashboard
Version 2: Added data cleaning tests
"""

import pandas as pd
import os
import sqlite3
from typing import Dict, List, Optional, Any


def load_data(csv_path: str) -> pd.DataFrame:
    """
    Load vaccination data from CSV file
    
    Args:
        csv_path: Path to CSV file
        
    Returns:
        DataFrame with vaccination data
        
    Raises:
        FileNotFoundError: If CSV file doesn't exist
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"File not found: {csv_path}")
    
    df = pd.read_csv(csv_path)
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean vaccination data
    
    Args:
        df: Raw DataFrame
        
    Returns:
        Cleaned DataFrame
    """
    # Create a copy to avoid modifying original
    cleaned = df.copy()
    
    # Remove rows with missing location
    cleaned = cleaned.dropna(subset=['location'])
    
    # Convert date to datetime
    if 'date' in cleaned.columns:
        cleaned['date'] = pd.to_datetime(cleaned['date'], errors='coerce')
        # Remove rows with invalid dates
        cleaned = cleaned.dropna(subset=['date'])
    
    # Convert numeric columns
    numeric_columns = ['total_vaccinations', 'people_vaccinated', 
                      'people_fully_vaccinated', 'daily_vaccinations']
    
    for col in numeric_columns:
        if col in cleaned.columns:
            cleaned[col] = pd.to_numeric(cleaned[col], errors='coerce')
            cleaned[col] = cleaned[col].fillna(0)
    
    return cleaned


def create_database(df: pd.DataFrame, db_path: str = "vaccinations.db") -> None:
    """
    Create SQLite database with vaccination data
    
    Args:
        df: Cleaned DataFrame
        db_path: Path to database file
    """
    conn = sqlite3.connect(db_path)
    df.to_sql('vaccinations', conn, if_exists='replace', index=False)
    conn.commit()
    conn.close()


def filter_by_location(df: pd.DataFrame, location: str) -> pd.DataFrame:
    """
    Filter data by country/location
    
    Args:
        df: DataFrame to filter
        location: Country name to filter by
        
    Returns:
        Filtered DataFrame
    """
    return df[df['location'].str.lower() == location.lower()].copy()