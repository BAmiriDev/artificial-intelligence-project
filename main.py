"""
Public Health Data Insights Dashboard
Task 1: Data access, cleaning, filtering, summary, and CRUD operations
Developed using Test-Driven Development (TDD) approach
"""

import pandas as pd
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import matplotlib.pyplot as plt
from tabulate import tabulate


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
        # If logging fails, silently ignore to avoid breaking functionality
        pass


def load_data(csv_path: str) -> pd.DataFrame:
    """
    Load vaccination data from CSV file
    """
    log_activity(f"Loading data from {csv_path}")
    
    if not os.path.exists(csv_path):
        log_activity(f"ERROR: File not found - {csv_path}")
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    # Read CSV with date parsing
    df = pd.read_csv(csv_path)
    log_activity(f"Successfully loaded {len(df)} records")
    
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and structure vaccination data
    - Handle missing values
    - Convert date types
    - Convert numeric types
    - Remove invalid entries
    """
    log_activity("Starting data cleaning process")
    
    # Create a copy to avoid modifying original
    cleaned = df.copy()
    
    # Remove rows where location is missing
    cleaned = cleaned.dropna(subset=['location'])
    
    # Convert date column to datetime, handling errors
    try:
        cleaned['date'] = pd.to_datetime(cleaned['date'], errors='coerce')
        # Remove rows with invalid dates
        cleaned = cleaned.dropna(subset=['date'])
    except Exception as e:
        log_activity(f"Warning: Date conversion issue - {str(e)}")
    
    # Convert numeric columns
    numeric_columns = [
        'total_vaccinations', 'people_vaccinated', 'people_fully_vaccinated',
        'total_boosters', 'daily_vaccinations', 'total_vaccinations_per_hundred',
        'people_vaccinated_per_hundred', 'people_fully_vaccinated_per_hundred'
    ]
    
    for col in numeric_columns:
        if col in cleaned.columns:
            cleaned[col] = pd.to_numeric(cleaned[col], errors='coerce')
            # Replace negative values with 0
            cleaned.loc[cleaned[col] < 0, col] = 0
            # Fill NaN with 0 for numeric columns
            cleaned[col] = cleaned[col].fillna(0)
    
    # Remove duplicate entries
    cleaned = cleaned.drop_duplicates()
    
    log_activity(f"Data cleaning complete. {len(cleaned)} valid records")
    
    return cleaned


def create_database(df: pd.DataFrame, db_path: str = "vaccinations.db") -> None:
    """
    Create SQLite database and store vaccination data
    """
    log_activity(f"Creating database at {db_path}")
    
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    
    # Store DataFrame in database
    df.to_sql('vaccinations', conn, if_exists='replace', index=False)
    
    conn.commit()
    conn.close()
    
    log_activity(f"Database created successfully with {len(df)} records")


def filter_by_location(df: pd.DataFrame, location: str) -> pd.DataFrame:
    """
    Filter data by country/location
    """
    log_activity(f"Filtering data by location: {location}")
    
    filtered = df[df['location'].str.lower() == location.lower()].copy()
    
    log_activity(f"Found {len(filtered)} records for {location}")
    
    return filtered


def filter_by_date_range(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Filter data by date range
    """
    log_activity(f"Filtering data by date range: {start_date} to {end_date}")
    
    # Convert dates
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    
    # Ensure date column is datetime
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'])
    
    filtered = df[(df['date'] >= start) & (df['date'] <= end)].copy()
    
    log_activity(f"Found {len(filtered)} records in date range")
    
    return filtered


def calculate_summary(df: pd.DataFrame, column: str) -> Dict[str, float]:
    """
    Calculate summary statistics for a column
    """
    log_activity(f"Calculating summary statistics for {column}")
    
    if column not in df.columns:
        log_activity(f"ERROR: Column {column} not found")
        return {}
    
    summary = {
        'mean': float(df[column].mean()),
        'min': float(df[column].min()),
        'max': float(df[column].max()),
        'count': int(df[column].count()),
        'sum': float(df[column].sum())
    }
    
    log_activity(f"Summary calculated: mean={summary['mean']:.2f}")
    
    return summary


def group_by_location(df: pd.DataFrame) -> pd.DataFrame:
    """
    Group data by location and calculate aggregates
    """    
    log_activity("Grouping data by location")

    # Collect max aggregates for available numeric columns
    agg_cols = {}
    for col in ['total_vaccinations', 'people_vaccinated', 'people_fully_vaccinated']:
        if col in df.columns:
            agg_cols[col] = 'max'

    # Compute grouped maxima
    if agg_cols:
        grouped_max = df.groupby('location').agg(agg_cols)
    else:
        # Empty frame with locations only -> create empty DataFrame
        grouped_max = pd.DataFrame(index=df['location'].unique())

    # Record counts per location
    counts = df.groupby('location').size().rename('record_count')

    # Combine results
    grouped = pd.concat([grouped_max, counts], axis=1).fillna(0)

    log_activity(f"Grouped into {len(grouped)} locations")

    return grouped


def create_record(db_path: str, record: Dict[str, Any]) -> bool:
    """
    Create a new record in the database
    """
    log_activity(f"Creating new record for {record.get('location', 'Unknown')}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Build INSERT query
        columns = ', '.join(record.keys())
        placeholders = ', '.join(['?' for _ in record])
        query = f"INSERT INTO vaccinations ({columns}) VALUES ({placeholders})"
        
        cursor.execute(query, list(record.values()))
        conn.commit()
        conn.close()
        
        log_activity("Record created successfully")
        return True
    except Exception as e:
        log_activity(f"ERROR creating record: {str(e)}")
        return False


def read_records(db_path: str, limit: int = 100, where: str = None) -> List[tuple]:
    """
    Read records from database
    """
    log_activity(f"Reading records from database (limit: {limit})")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        query = f"SELECT * FROM vaccinations"
        if where:
            query += f" WHERE {where}"
        query += f" LIMIT {limit}"
        
        cursor.execute(query)
        records = cursor.fetchall()
        conn.close()
        
        log_activity(f"Retrieved {len(records)} records")
        return records
    except Exception as e:
        log_activity(f"ERROR reading records: {str(e)}")
        return []


def update_record(db_path: str, location: str, date: str, field: str, value: Any) -> bool:
    """
    Update an existing record in the database
    """
    log_activity(f"Updating record: {location} - {date} - {field}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        query = f"UPDATE vaccinations SET {field} = ? WHERE location = ? AND date = ?"
        cursor.execute(query, (value, location, date))
        
        conn.commit()
        affected_rows = cursor.rowcount
        conn.close()
        
        log_activity(f"Updated {affected_rows} record(s)")
        return affected_rows > 0
    except Exception as e:
        log_activity(f"ERROR updating record: {str(e)}")
        return False


def delete_record(db_path: str, location: str, date: str) -> bool:
    """
    Delete a record from the database
    """
    log_activity(f"Deleting record: {location} - {date}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        query = "DELETE FROM vaccinations WHERE location = ? AND date = ?"
        cursor.execute(query, (location, date))
        
        conn.commit()
        affected_rows = cursor.rowcount
        conn.close()
        
        log_activity(f"Deleted {affected_rows} record(s)")
        return affected_rows > 0
    except Exception as e:
        log_activity(f"ERROR deleting record: {str(e)}")
        return False


def export_to_csv(df: pd.DataFrame, output_path: str) -> bool:
    """
    Export DataFrame to CSV file
    """
    log_activity(f"Exporting {len(df)} records to {output_path}")
    
    try:
        # If the output path includes a directory, ensure it exists
        out_dir = os.path.dirname(output_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        # Write to the exact path requested by the caller
        df.to_csv(output_path, index=False)
        log_activity(f"Export successful: {output_path}")
        return True
    except Exception as e:
        log_activity(f"ERROR exporting to CSV: {str(e)}")
        return False


def plot_trend(df: pd.DataFrame, location: str, column: str = 'total_vaccinations') -> None:
    """
    Plot vaccination trend over time for a location
    """
    log_activity(f"Generating trend plot for {location}")
    
    # Filter by location
    data = filter_by_location(df, location)
    
    if len(data) == 0:
        print(f"No data found for {location}")
        return
    
    # Sort by date
    data = data.sort_values('date')
    
    # Remove zeros for better visualization
    data = data[data[column] > 0]
    
    # Create plot
    plt.figure(figsize=(12, 6))
    plt.plot(data['date'], data[column], marker='o', linestyle='-', linewidth=2)
    plt.title(f'{column.replace("_", " ").title()} Trend - {location}')
    plt.xlabel('Date')
    plt.ylabel(column.replace("_", " ").title())
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save plot
    os.makedirs("exports", exist_ok=True)
    plot_path = f"exports/{location}_{column}_trend.png"
    plt.savefig(plot_path)
    print(f"\nPlot saved to: {plot_path}")
    
    plt.show()
    
    log_activity(f"Trend plot generated: {plot_path}")


def display_menu() -> None:
    """Display main menu options"""
    print("\n" + "="*60)
    print("  PUBLIC HEALTH DATA INSIGHTS DASHBOARD")
    print("="*60)
    print("\n[DATA OPERATIONS]")
    print("1. Load and Setup Database")
    print("2. View Data Summary")
    print("3. Filter Data by Location")
    print("4. Filter Data by Date Range")
    print("5. View Top Locations by Vaccinations")
    print("\n[CRUD OPERATIONS]")
    print("6. Create New Record")
    print("7. Read Records")
    print("8. Update Record")
    print("9. Delete Record")
    print("\n[ANALYSIS & EXPORT]")
    print("10. View Statistics for a Location")
    print("11. Plot Vaccination Trend")
    print("12. Export Filtered Data to CSV")
    print("\n[OTHER]")
    print("13. View Activity Log")
    print("0. Exit")
    print("\n" + "="*60)


def main():
    """Main CLI application"""
    print("Initializing Public Health Data Insights Dashboard...")
    log_activity("Application started")
    
    # Global variables
    db_path = "vaccinations.db"
    csv_path = "dataset/vaccinations.csv"
    data = None
    
    while True:
        display_menu()
        choice = input("\nEnter your choice (0-13): ").strip()
        
        try:
            if choice == '0':
                print("\nThank you for using the dashboard!")
                log_activity("Application closed")
                break
            
            elif choice == '1':
                print("\n[Loading and Setting Up Database...]")
                raw_data = load_data(csv_path)
                data = clean_data(raw_data)
                create_database(data, db_path)
                print(f"\n✓ Database created successfully!")
                print(f"  Total records: {len(data)}")
                print(f"  Locations: {data['location'].nunique()}")
                print(f"  Date range: {data['date'].min()} to {data['date'].max()}")
            
            elif choice == '2':
                if data is None:
                    print("\n⚠ Please load data first (Option 1)")
                    continue
                
                print("\n[DATA SUMMARY]")
                print(f"Total Records: {len(data)}")
                print(f"Unique Locations: {data['location'].nunique()}")
                print(f"Date Range: {data['date'].min().date()} to {data['date'].max().date()}")
                print(f"\nColumns: {', '.join(data.columns[:8])}...")
            
            elif choice == '3':
                if data is None:
                    print("\n⚠ Please load data first (Option 1)")
                    continue
                
                location = input("\nEnter location name (e.g., United States, India): ").strip()
                filtered = filter_by_location(data, location)
                
                if len(filtered) == 0:
                    print(f"\n⚠ No data found for '{location}'")
                    print("\nSuggestions:", ', '.join(data['location'].unique()[:10]))
                else:
                    print(f"\n✓ Found {len(filtered)} records for {location}")
                    print("\nSample data:")
                    print(tabulate(filtered.head(10), headers='keys', tablefmt='grid'))
            
            elif choice == '4':
                if data is None:
                    print("\n⚠ Please load data first (Option 1)")
                    continue
                
                start = input("Enter start date (YYYY-MM-DD): ").strip()
                end = input("Enter end date (YYYY-MM-DD): ").strip()
                
                filtered = filter_by_date_range(data, start, end)
                print(f"\n✓ Found {len(filtered)} records between {start} and {end}")
                print(f"Locations in range: {filtered['location'].nunique()}")
            
            elif choice == '5':
                if data is None:
                    print("\n⚠ Please load data first (Option 1)")
                    continue
                
                grouped = group_by_location(data)
                top_10 = grouped.sort_values('total_vaccinations', ascending=False).head(10)
                
                print("\n[TOP 10 LOCATIONS BY TOTAL VACCINATIONS]")
                print(tabulate(top_10, headers='keys', tablefmt='grid'))
            
            elif choice == '6':
                location = input("Location: ").strip()
                iso_code = input("ISO Code: ").strip()
                date = input("Date (YYYY-MM-DD): ").strip()
                total_vax = input("Total Vaccinations: ").strip()
                
                record = {
                    'location': location,
                    'iso_code': iso_code,
                    'date': date,
                    'total_vaccinations': int(total_vax) if total_vax else 0
                }
                
                if create_record(db_path, record):
                    print("\n✓ Record created successfully!")
                else:
                    print("\n✗ Failed to create record")
            
            elif choice == '7':
                limit = input("Number of records to display (default 10): ").strip()
                limit = int(limit) if limit else 10
                
                records = read_records(db_path, limit=limit)
                print(f"\n[SHOWING {len(records)} RECORDS]")
                
                # Convert to DataFrame for better display
                conn = sqlite3.connect(db_path)
                df_records = pd.read_sql(f"SELECT * FROM vaccinations LIMIT {limit}", conn)
                conn.close()
                
                print(tabulate(df_records, headers='keys', tablefmt='grid'))
            
            elif choice == '8':
                location = input("Location to update: ").strip()
                date = input("Date (YYYY-MM-DD): ").strip()
                field = input("Field to update (e.g., total_vaccinations): ").strip()
                value = input("New value: ").strip()
                
                if update_record(db_path, location, date, field, value):
                    print("\n✓ Record updated successfully!")
                else:
                    print("\n✗ Failed to update record")
            
            elif choice == '9':
                location = input("Location to delete: ").strip()
                date = input("Date (YYYY-MM-DD): ").strip()
                confirm = input(f"Delete record for {location} on {date}? (yes/no): ").strip()
                
                if confirm.lower() == 'yes':
                    if delete_record(db_path, location, date):
                        print("\n✓ Record deleted successfully!")
                    else:
                        print("\n✗ Failed to delete record")
                else:
                    print("\n✗ Deletion cancelled")
            
            elif choice == '10':
                if data is None:
                    print("\n⚠ Please load data first (Option 1)")
                    continue
                
                location = input("Enter location name: ").strip()
                filtered = filter_by_location(data, location)
                
                if len(filtered) == 0:
                    print(f"\n⚠ No data found for '{location}'")
                else:
                    print(f"\n[STATISTICS FOR {location.upper()}]")
                    
                    for col in ['total_vaccinations', 'people_vaccinated', 'people_fully_vaccinated']:
                        if col in filtered.columns:
                            summary = calculate_summary(filtered, col)
                            print(f"\n{col.replace('_', ' ').title()}:")
                            print(f"  Mean: {summary['mean']:,.0f}")
                            print(f"  Min: {summary['min']:,.0f}")
                            print(f"  Max: {summary['max']:,.0f}")
                            print(f"  Total: {summary['sum']:,.0f}")
            
            elif choice == '11':
                if data is None:
                    print("\n⚠ Please load data first (Option 1)")
                    continue
                
                location = input("Enter location name: ").strip()
                column = input("Column to plot (default: total_vaccinations): ").strip()
                column = column if column else 'total_vaccinations'
                
                plot_trend(data, location, column)
            
            elif choice == '12':
                if data is None:
                    print("\n⚠ Please load data first (Option 1)")
                    continue
                
                print("\nFilter options:")
                print("1. Export all data")
                print("2. Export by location")
                print("3. Export by date range")
                
                filter_choice = input("Choose filter: ").strip()
                
                export_data = data
                filename = "export.csv"
                
                if filter_choice == '2':
                    location = input("Enter location: ").strip()
                    export_data = filter_by_location(data, location)
                    filename = f"export_{location.replace(' ', '_')}.csv"
                elif filter_choice == '3':
                    start = input("Start date (YYYY-MM-DD): ").strip()
                    end = input("End date (YYYY-MM-DD): ").strip()
                    export_data = filter_by_date_range(data, start, end)
                    filename = f"export_{start}_to_{end}.csv"
                
                if export_to_csv(export_data, filename):
                    print(f"\n✓ Exported {len(export_data)} records to exports/{filename}")
                else:
                    print("\n✗ Export failed")
            
            elif choice == '13':
                if os.path.exists('activity.log'):
                    print("\n[RECENT ACTIVITY LOG]")
                    with open('activity.log', 'r') as f:
                        lines = f.readlines()
                        for line in lines[-20:]:  # Show last 20 entries
                            print(line.strip())
                else:
                    print("\n⚠ No activity log found")
            
            else:
                print("\n⚠ Invalid choice. Please try again.")
        
        except Exception as e:
            print(f"\n✗ Error: {str(e)}")
            log_activity(f"ERROR: {str(e)}")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
