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


class TestStatistics:
    """Test suite for statistical operations"""
    
    def test_calculate_summary(self):
        """Test summary statistics calculation"""
        from main import calculate_summary
        
        test_data = pd.DataFrame({
            "total_vaccinations": [100, 200, 300, 400, 500]
        })
        
        summary = calculate_summary(test_data, "total_vaccinations")
        
        assert "mean" in summary
        assert "min" in summary
        assert "max" in summary
        assert "count" in summary
        assert summary["mean"] == 300.0
        assert summary["min"] == 100.0
        assert summary["max"] == 500.0
    
    def test_group_by_location(self):
        """Test grouping data by location"""
        from main import group_by_location
        
        test_data = pd.DataFrame({
            "location": ["USA", "USA", "UK", "UK", "Germany"],
            "total_vaccinations": [100, 200, 150, 250, 300]
        })
        
        grouped = group_by_location(test_data)
        assert len(grouped) == 3
        assert "USA" in grouped.index
        assert "UK" in grouped.index


class TestCRUD:
    """Test suite for Create, Read, Update, Delete operations"""
    
    @pytest.fixture
    def temp_db_with_data(self):
        """Create temporary database with test data"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test.db")
        
        test_data = pd.DataFrame({
            "location": ["USA", "UK", "USA"],
            "date": pd.to_datetime(["2021-01-01", "2021-01-02", "2021-01-03"]),
            "total_vaccinations": [1000, 2000, 3000]
        })
        
        conn = sqlite3.connect(db_path)
        test_data.to_sql('vaccinations', conn, if_exists='replace', index=False)
        conn.close()
        
        yield db_path
        shutil.rmtree(temp_dir)
    
    def test_create_record(self, temp_db_with_data):
        """Test creating a new record"""
        from main import create_record
        
        new_record = {
            "location": "TestCountry",
            "date": "2021-01-04",
            "total_vaccinations": 5000
        }
        
        result = create_record(temp_db_with_data, new_record)
        assert result is True
        
        # Verify record was added
        conn = sqlite3.connect(temp_db_with_data)
        df = pd.read_sql("SELECT * FROM vaccinations WHERE location = 'TestCountry'", conn)
        conn.close()
        assert len(df) == 1
    
    def test_read_records(self, temp_db_with_data):
        """Test reading records"""
        from main import read_records
        
        records = read_records(temp_db_with_data, limit=2)
        assert len(records) == 2
    
    def test_update_record(self, temp_db_with_data):
        """Test updating a record"""
        from main import update_record
        
        result = update_record(temp_db_with_data, "USA", "2021-01-01", 
                              "total_vaccinations", 1500)
        assert result is True


class TestEdgeCases:
    """Test suite for edge cases"""
    
    def test_empty_data_handling(self):
        """Test handling empty dataframes"""
        from main import calculate_summary, filter_by_location
        
        empty_df = pd.DataFrame()
        
        # Should handle gracefully
        summary = calculate_summary(empty_df, "total_vaccinations")
        assert summary == {}
        
        filtered = filter_by_location(empty_df, "USA")
        assert len(filtered) == 0