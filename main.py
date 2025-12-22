"""
Test-Driven Development (TDD) Test Suite for Public Health Dashboard
Version 2: Added data cleaning tests
"""

import pandas as pd
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any


def load_data(csv_path: str) -> pd.DataFrame:
    """Load vaccination data from CSV file"""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"File not found: {csv_path}")
    
    df = pd.read_csv(csv_path)
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean vaccination data"""
    cleaned = df.copy()
    
    # Remove rows with missing location
    cleaned = cleaned.dropna(subset=['location'])
    
    # Convert date to datetime
    if 'date' in cleaned.columns:
        cleaned['date'] = pd.to_datetime(cleaned['date'], errors='coerce')
        cleaned = cleaned.dropna(subset=['date'])
    
    # Convert numeric columns
    numeric_columns = ['total_vaccinations', 'people_vaccinated', 
                      'people_fully_vaccinated', 'daily_vaccinations',
                      'total_vaccinations_per_hundred']
    
    for col in numeric_columns:
        if col in cleaned.columns:
            cleaned[col] = pd.to_numeric(cleaned[col], errors='coerce')
            cleaned[col] = cleaned[col].fillna(0)
    
    return cleaned


def create_database(df: pd.DataFrame, db_path: str = "vaccinations.db") -> None:
    """Create SQLite database with vaccination data"""
    conn = sqlite3.connect(db_path)
    df.to_sql('vaccinations', conn, if_exists='replace', index=False)
    conn.commit()
    conn.close()


def filter_by_location(df: pd.DataFrame, location: str) -> pd.DataFrame:
    """Filter data by country/location"""
    return df[df['location'].str.lower() == location.lower()].copy()


def filter_by_date_range(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Filter data by date range
    
    Args:
        df: DataFrame to filter
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        
    Returns:
        Filtered DataFrame
    """
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'])
    
    return df[(df['date'] >= start) & (df['date'] <= end)].copy()


def calculate_summary(df: pd.DataFrame, column: str) -> Dict[str, float]:
    """
    Calculate summary statistics for a column
    
    Args:
        df: DataFrame
        column: Column name to analyze
        
    Returns:
        Dictionary with summary statistics
    """
    if column not in df.columns or len(df) == 0:
        return {}
    
    return {
        'mean': float(df[column].mean()),
        'min': float(df[column].min()),
        'max': float(df[column].max()),
        'count': int(df[column].count()),
        'std': float(df[column].std())
    }


def group_by_location(df: pd.DataFrame) -> pd.DataFrame:
    """
    Group data by location
    
    Args:
        df: DataFrame
        
    Returns:
        Grouped DataFrame
    """
    if 'location' not in df.columns:
        return pd.DataFrame()
    
    # Get numeric columns for aggregation
    numeric_cols = [col for col in df.columns if col != 'location' and pd.api.types.is_numeric_dtype(df[col])]
    
    if numeric_cols:
        grouped = df.groupby('location')[numeric_cols].sum()
    else:
        grouped = pd.DataFrame(index=df['location'].unique())
    
    return grouped


def create_record(db_path: str, record: Dict[str, Any]) -> bool:
    """
    Create a new record in the database
    
    Args:
        db_path: Path to database
        record: Dictionary with record data
        
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        columns = ', '.join(record.keys())
        placeholders = ', '.join(['?' for _ in record])
        query = f"INSERT INTO vaccinations ({columns}) VALUES ({placeholders})"
        
        cursor.execute(query, list(record.values()))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating record: {e}")
        return False


def read_records(db_path: str, limit: int = 100) -> List[tuple]:
    """
    Read records from database
    
    Args:
        db_path: Path to database
        limit: Maximum number of records to return
        
    Returns:
        List of records
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM vaccinations LIMIT {limit}")
        records = cursor.fetchall()
        conn.close()
        return records
    except Exception as e:
        print(f"Error reading records: {e}")
        return []


def update_record(db_path: str, location: str, date: str, field: str, value: Any) -> bool:
    """
    Update a record in the database
    
    Args:
        db_path: Path to database
        location: Location to update
        date: Date of record to update
        field: Field to update
        value: New value
        
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        query = f"UPDATE vaccinations SET {field} = ? WHERE location = ? AND date = ?"
        cursor.execute(query, (value, location, date))
        
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        
        return affected > 0
    except Exception as e:
        print(f"Error updating record: {e}")
        return False