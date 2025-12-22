"""
Test-Driven Development (TDD) Test Suite
Tests written BEFORE implementation to guide development
"""

import pytest
import os
import sqlite3
import pandas as pd
from datetime import datetime
import tempfile
import shutil


# Test Data Loading & Database Storage
class TestDataLoading:
    """Test suite for data loading and database operations"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test.db")
        yield db_path
        shutil.rmtree(temp_dir)
    
    def test_load_csv_data(self):
        """Test loading CSV data from dataset folder"""
        from main import load_data
        df = load_data("dataset/vaccinations.csv")
        assert df is not None
        assert len(df) > 0
        assert "location" in df.columns
        assert "date" in df.columns
    
    def test_database_creation(self, temp_db):
        """Test database table creation"""
        from main import create_database, load_data
        df = load_data("dataset/vaccinations.csv")
        create_database(df, temp_db)
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        conn.close()
        
        assert len(tables) > 0
        assert any("vaccinations" in str(t) for t in tables)
    
    def test_empty_csv_handling(self, temp_db):
        """Test handling of empty CSV"""
        from main import load_data
        # Create empty CSV
        empty_csv = "test_empty.csv"
        with open(empty_csv, "w") as f:
            f.write("location,date\n")
        
        df = load_data(empty_csv)
        assert df is not None
        assert len(df) == 0
        
        os.remove(empty_csv)


# Test Data Cleaning & Structuring
class TestDataCleaning:
    """Test suite for data cleaning operations"""
    
    def test_handle_missing_values(self):
        """Test handling of missing/null values"""
        from main import clean_data
        
        test_data = pd.DataFrame({
            "location": ["USA", "UK", None],
            "date": ["2021-01-01", "2021-01-02", "2021-01-03"],
            "total_vaccinations": [100, None, 200]
        })
        
        cleaned = clean_data(test_data)
        assert cleaned is not None
        # Check that missing values are handled (filled or removed)
        assert len(cleaned) <= len(test_data)
    
    def test_date_conversion(self):
        """Test date type conversion"""
        from main import clean_data
        
        test_data = pd.DataFrame({
            "location": ["USA"],
            "date": ["2021-01-01"],
            "total_vaccinations": [100]
        })
        
        cleaned = clean_data(test_data)
        assert pd.api.types.is_datetime64_any_dtype(cleaned["date"])
    
    def test_numeric_conversion(self):
        """Test numeric type conversion"""
        from main import clean_data
        
        test_data = pd.DataFrame({
            "location": ["USA"],
            "date": ["2021-01-01"],
            "total_vaccinations": ["100"]
        })
        
        cleaned = clean_data(test_data)
        assert pd.api.types.is_numeric_dtype(cleaned["total_vaccinations"])


# Test Filtering Operations
class TestFiltering:
    """Test suite for data filtering operations"""
    
    def test_filter_by_country(self):
        """Test filtering data by country/location"""
        from main import filter_by_location
        
        test_data = pd.DataFrame({
            "location": ["USA", "UK", "USA"],
            "date": pd.to_datetime(["2021-01-01", "2021-01-02", "2021-01-03"]),
            "total_vaccinations": [100, 200, 300]
        })
        
        filtered = filter_by_location(test_data, "USA")
        assert len(filtered) == 2
        assert all(filtered["location"] == "USA")
    
    def test_filter_by_date_range(self):
        """Test filtering by date range"""
        from main import filter_by_date_range
        
        test_data = pd.DataFrame({
            "location": ["USA", "USA", "USA"],
            "date": pd.to_datetime(["2021-01-01", "2021-01-15", "2021-02-01"]),
            "total_vaccinations": [100, 200, 300]
        })
        
        filtered = filter_by_date_range(test_data, "2021-01-01", "2021-01-31")
        assert len(filtered) == 2
    
    def test_filter_invalid_location(self):
        """Test filtering with non-existent location"""
        from main import filter_by_location
        
        test_data = pd.DataFrame({
            "location": ["USA", "UK"],
            "date": pd.to_datetime(["2021-01-01", "2021-01-02"]),
            "total_vaccinations": [100, 200]
        })
        
        filtered = filter_by_location(test_data, "InvalidCountry")
        assert len(filtered) == 0


# Test Summary Statistics
class TestSummary:
    """Test suite for summary statistics"""
    
    def test_calculate_mean(self):
        """Test mean calculation"""
        from main import calculate_summary
        
        test_data = pd.DataFrame({
            "location": ["USA", "USA", "USA"],
            "total_vaccinations": [100, 200, 300]
        })
        
        summary = calculate_summary(test_data, "total_vaccinations")
        assert "mean" in summary
        assert summary["mean"] == 200
    
    def test_calculate_min_max(self):
        """Test min and max calculations"""
        from main import calculate_summary
        
        test_data = pd.DataFrame({
            "location": ["USA", "USA", "USA"],
            "total_vaccinations": [100, 200, 300]
        })
        
        summary = calculate_summary(test_data, "total_vaccinations")
        assert "min" in summary
        assert "max" in summary
        assert summary["min"] == 100
        assert summary["max"] == 300
    
    def test_group_by_location(self):
        """Test grouping by location"""
        from main import group_by_location
        
        test_data = pd.DataFrame({
            "location": ["USA", "USA", "UK", "UK"],
            "total_vaccinations": [100, 200, 150, 250]
        })
        
        grouped = group_by_location(test_data)
        assert len(grouped) == 2
        assert "USA" in grouped.index
        assert "UK" in grouped.index


# Test CRUD Operations
class TestCRUD:
    """Test suite for Create, Read, Update, Delete operations"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test.db")
        yield db_path
        shutil.rmtree(temp_dir)
    
    def test_create_record(self, temp_db):
        """Test creating a new record"""
        from main import create_record, create_database, load_data
        
        df = load_data("dataset/vaccinations.csv")
        create_database(df, temp_db)
        
        new_record = {
            "location": "TestCountry",
            "iso_code": "TST",
            "date": "2021-01-01",
            "total_vaccinations": 1000
        }
        
        result = create_record(temp_db, new_record)
        assert result is True
    
    def test_read_records(self, temp_db):
        """Test reading records from database"""
        from main import read_records, create_database, load_data
        
        df = load_data("dataset/vaccinations.csv")
        create_database(df, temp_db)
        
        records = read_records(temp_db, limit=10)
        assert len(records) <= 10
    
    def test_update_record(self, temp_db):
        """Test updating an existing record"""
        from main import update_record, create_database, load_data
        
        df = load_data("dataset/vaccinations.csv")
        create_database(df, temp_db)
        
        result = update_record(temp_db, location="Afghanistan", 
                              date="2021-02-22", 
                              field="total_vaccinations", 
                              value=5000)
        assert result is True
    
    def test_delete_record(self, temp_db):
        """Test deleting a record"""
        from main import delete_record, create_database, load_data
        
        df = load_data("dataset/vaccinations.csv")
        create_database(df, temp_db)
        
        result = delete_record(temp_db, location="Afghanistan", date="2021-02-22")
        assert result is True


# Test Export Functionality
class TestExport:
    """Test suite for data export operations"""
    
    def test_export_to_csv(self):
        """Test exporting filtered data to CSV"""
        from main import export_to_csv
        
        test_data = pd.DataFrame({
            "location": ["USA", "UK"],
            "date": ["2021-01-01", "2021-01-02"],
            "total_vaccinations": [100, 200]
        })
        
        output_file = "test_export.csv"
        result = export_to_csv(test_data, output_file)
        
        assert result is True
        assert os.path.exists(output_file)
        
        # Verify exported data
        exported = pd.read_csv(output_file)
        assert len(exported) == len(test_data)
        
        os.remove(output_file)
    
    def test_export_empty_data(self):
        """Test exporting empty dataframe"""
        from main import export_to_csv
        
        test_data = pd.DataFrame()
        output_file = "test_empty_export.csv"
        
        result = export_to_csv(test_data, output_file)
        assert result is True


# Test Logging
class TestLogging:
    """Test suite for activity logging"""
    
    def test_log_user_activity(self):
        """Test that user activities are logged"""
        from main import log_activity
        
        log_activity("Test action performed")
        
        # Check if log file exists
        assert os.path.exists("activity.log")
        
        # Verify log content
        with open("activity.log", "r") as f:
            content = f.read()
            assert "Test action performed" in content
    
    def test_log_file_creation(self):
        """Test log file is created if not exists"""
        from main import log_activity
        
        # Remove log if exists
        if os.path.exists("activity.log"):
            os.remove("activity.log")
        
        log_activity("First log entry")
        assert os.path.exists("activity.log")


# Test Task 2: Data Structures
class TestDataStructures:
    """Test suite for Task 2 - Data structures and algorithms"""
    
    def test_graph_creation(self):
        """Test creating graph structure for vaccination network"""
        from task2_datastructures import VaccinationGraph
        
        graph = VaccinationGraph()
        assert graph is not None
    
    def test_add_node(self):
        """Test adding nodes to graph"""
        from task2_datastructures import VaccinationGraph
        
        graph = VaccinationGraph()
        graph.add_country("USA", {"population": 330000000})
        
        assert "USA" in graph.get_countries()
    
    def test_add_edge(self):
        """Test adding edges between nodes"""
        from task2_datastructures import VaccinationGraph
        
        graph = VaccinationGraph()
        graph.add_country("USA", {})
        graph.add_country("Canada", {})
        graph.add_connection("USA", "Canada", weight=100)
        
        assert graph.has_connection("USA", "Canada")
    
    def test_shortest_path(self):
        """Test shortest path algorithm"""
        from task2_datastructures import VaccinationGraph
        
        graph = VaccinationGraph()
        graph.add_country("USA", {})
        graph.add_country("Canada", {})
        graph.add_country("Mexico", {})
        
        graph.add_connection("USA", "Canada", weight=1)
        graph.add_connection("USA", "Mexico", weight=1)
        graph.add_connection("Canada", "Mexico", weight=1)
        
        path = graph.shortest_path("USA", "Mexico")
        assert path is not None
        assert len(path) >= 2


# Test Edge Cases
class TestEdgeCases:
    """Test suite for edge cases and error handling"""
    
    def test_invalid_csv_path(self):
        """Test handling of invalid CSV file path"""
        from main import load_data
        
        with pytest.raises(FileNotFoundError):
            load_data("nonexistent_file.csv")
    
    def test_invalid_date_format(self):
        """Test handling of invalid date formats"""
        from main import clean_data
        
        test_data = pd.DataFrame({
            "location": ["USA"],
            "date": ["invalid-date"],
            "total_vaccinations": [100]
        })
        
        cleaned = clean_data(test_data)
        # Should handle gracefully without crashing
        assert cleaned is not None
    
    def test_negative_vaccination_count(self):
        """Test handling of negative vaccination values"""
        from main import clean_data
        
        test_data = pd.DataFrame({
            "location": ["USA"],
            "date": ["2021-01-01"],
            "total_vaccinations": [-100]
        })
        
        cleaned = clean_data(test_data)
        # Negative values should be handled (set to 0 or removed)
        assert cleaned is not None
