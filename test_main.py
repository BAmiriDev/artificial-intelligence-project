"""
Test-Driven Development (TDD) Test Suite
Tests written BEFORE implementation to guide development
"""

import pytest
import pandas as pd
import os
import tempfile
import shutil
import sqlite3


class TestDataLoading:
    """Test suite for data loading operations"""
    
    def test_load_csv_data_exists(self):
        """Test that CSV file exists"""
        assert os.path.exists("dataset/vaccinations.csv")
    
    def test_load_csv_data_columns(self):
        """Test loading CSV data has expected columns"""
        from main import load_data
        df = load_data("dataset/vaccinations.csv")
        assert "location" in df.columns
        assert "date" in df.columns
    
    def test_load_csv_data_not_empty(self):
        """Test loaded data is not empty"""
        from main import load_data
        df = load_data("dataset/vaccinations.csv")
        assert len(df) > 0


class TestDataCleaning:
    """Test suite for data cleaning operations"""
    
    def test_clean_data_removes_nulls(self):
        """Test that clean_data removes null locations"""
        from main import clean_data
        
        test_data = pd.DataFrame({
            "location": ["USA", None, "UK"],
            "date": ["2021-01-01", "2021-01-02", "2021-01-03"],
            "total_vaccinations": [100, 200, 300]
        })
        
        cleaned = clean_data(test_data)
        assert len(cleaned) == 2
    
    def test_clean_data_converts_dates(self):
        """Test that clean_data converts date strings to datetime"""
        from main import clean_data
        
        test_data = pd.DataFrame({
            "location": ["USA"],
            "date": ["2021-01-01"],
            "total_vaccinations": [100]
        })
        
        cleaned = clean_data(test_data)
        assert pd.api.types.is_datetime64_any_dtype(cleaned["date"])


class TestDatabase:
    """Test suite for database operations"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test.db")
        yield db_path
        shutil.rmtree(temp_dir)
    
    def test_create_database(self, temp_db):
        """Test database creation"""
        from main import create_database, load_data, clean_data
        
        raw_data = load_data("dataset/vaccinations.csv")
        cleaned_data = clean_data(raw_data)
        create_database(cleaned_data, temp_db)
        
        # Verify database was created
        assert os.path.exists(temp_db)
        
        # Verify table exists
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        conn.close()
        
        assert len(tables) > 0
        assert any('vaccinations' in str(t[0]) for t in tables)


class TestFiltering:
    """Test suite for filtering operations"""
    
    def test_filter_by_location(self):
        """Test filtering by country/location"""
        from main import filter_by_location
        
        test_data = pd.DataFrame({
            "location": ["USA", "UK", "USA", "Germany"],
            "date": pd.to_datetime(["2021-01-01", "2021-01-02", "2021-01-03", "2021-01-04"]),
            "total_vaccinations": [100, 200, 300, 400]
        })
        
        filtered = filter_by_location(test_data, "USA")
        assert len(filtered) == 2
        assert all(filtered["location"] == "USA")
    
    def test_filter_by_location_nonexistent(self):
        """Test filtering with non-existent location"""
        from main import filter_by_location
        
        test_data = pd.DataFrame({
            "location": ["USA", "UK"],
            "date": pd.to_datetime(["2021-01-01", "2021-01-02"]),
            "total_vaccinations": [100, 200]
        })
        
        filtered = filter_by_location(test_data, "InvalidCountry")
        assert len(filtered) == 0