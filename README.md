# Public Health Data Insights Dashboard

A Python-based data insights tool for analyzing public health vaccination data. Built using Test-Driven Development (TDD) approach.

## Project Structure

```
Project AMW/
├── main.py                    # Main application (Task 1)
├── task2_datastructures.py    # Data structures & algorithms (Task 2)
├── test_main.py              # Test suite (TDD)
├── requirements.txt          # Python dependencies
├── dataset/
│   └── vaccinations.csv      # Vaccination dataset
├── exports/                  # Generated exports and plots
├── activity.log             # User activity logs
└── vaccinations.db          # SQLite database
```

## Features

### Task 1: Data Insights Dashboard
- **Data Loading**: Load CSV data into SQLite database
- **Data Cleaning**: Handle missing values, type conversions
- **Filtering**: Filter by location, date range
- **Summary Statistics**: Calculate mean, min, max, counts
- **CRUD Operations**: Create, Read, Update, Delete records
- **Export**: Export filtered data to CSV
- **Logging**: Track all user activities
- **Visualization**: Plot vaccination trends

### Task 2: Data Structures & Algorithms
- **Graph Structure**: Model vaccination distribution networks
- **Dijkstra's Algorithm**: Find shortest vaccine distribution routes
- **BFS/DFS Traversal**: Explore network connections
- **Priority Queue**: Manage vaccination appointments by priority
- **Network Analysis**: Identify central hubs and communities

## Installation

### 1. Clone Repository
```powershell
git clone https://github.com/awais2317/kai-Adam-Project.git
cd "kai-Adam-Project"
```

### 2. Create Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

## Running the Application

### Main Application (Task 1)
```powershell
python main.py
```

This launches an interactive CLI menu with options for:
1. Loading and setting up database
2. Viewing data summaries
3. Filtering data
4. CRUD operations
5. Generating statistics and visualizations
6. Exporting data

### Data Structures Demo (Task 2)
```powershell
python task2_datastructures.py
```

This runs demonstrations of:
- Graph-based vaccination network
- Shortest path algorithms
- Network analysis
- Priority queue for vaccination scheduling

### Running Tests
```powershell
# Run all tests
pytest test_main.py -v

# Run specific test class
pytest test_main.py::TestDataLoading -v

# Run with coverage
pytest test_main.py --cov=main --cov-report=html
```

## Usage Examples

### Example 1: Load Data and View Summary
1. Run `python main.py`
2. Choose option `1` to load data
3. Choose option `2` to view summary

### Example 2: Filter by Country
1. Choose option `3`
2. Enter country name (e.g., "United States")
3. View filtered results

### Example 3: Plot Vaccination Trend
1. Choose option `11`
2. Enter country name
3. Choose column to plot (or press Enter for default)
4. View and save the plot

### Example 4: Export Filtered Data
1. Choose option `12`
2. Select filter type (all, by location, by date)
3. Enter filter criteria
4. Find exported CSV in `exports/` folder

## Testing Approach

This project follows **Test-Driven Development (TDD)**:
1. Tests written BEFORE implementation
2. Each function has corresponding test cases
3. Tests cover normal cases, edge cases, and error handling

### Test Coverage
- Data loading and database operations
- Data cleaning and type conversions
- Filtering operations
- Summary statistics
- CRUD operations
- Export functionality
- Logging
- Data structures (Task 2)

## Dataset Information

**Source**: COVID-19 Vaccination Data
- **Location**: `dataset/vaccinations.csv`
- **Records**: ~196,000 rows
- **Columns**: location, iso_code, date, total_vaccinations, people_vaccinated, etc.
- **Date Range**: 2021-02-22 onwards
- **Coverage**: Global (multiple countries)

## Key Technologies

- **Python 3.8+**
- **pandas**: Data manipulation and analysis
- **sqlite3**: Database storage
- **matplotlib**: Data visualization
- **pytest**: Testing framework
- **networkx**: Graph visualization
- **tabulate**: Table formatting

## File Descriptions

### main.py
Core application implementing:
- Data loading and cleaning functions
- Database operations (SQLite)
- Filtering and summary functions
- CRUD operations
- Export functionality
- Activity logging
- CLI interface

### task2_datastructures.py
Advanced data structures:
- `VaccinationGraph`: Graph structure with Dijkstra, BFS, DFS algorithms
- `VaccinationQueue`: Priority queue for vaccination scheduling
- Network analysis functions
- Visualization capabilities

### test_main.py
Comprehensive test suite:
- 30+ test cases
- Tests for all core functionality
- Edge case handling
- Fixtures for temporary databases

## Algorithms & Complexity

### Task 2 Algorithms

**Dijkstra's Shortest Path**
- Time: O((V + E) log V)
- Space: O(V)
- Use: Find optimal vaccine distribution routes

**Breadth-First Search (BFS)**
- Time: O(V + E)
- Space: O(V)
- Use: Explore reachable countries

**Depth-First Search (DFS)**
- Time: O(V + E)
- Space: O(V)
- Use: Network traversal

**Priority Queue (Heap)**
- Insert: O(log n)
- Extract: O(log n)
- Use: Vaccination appointment scheduling

## Troubleshooting

### Issue: "Module not found"
**Solution**: Ensure virtual environment is activated and dependencies installed
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Issue: "Database locked"
**Solution**: Close other connections to database or delete `vaccinations.db` and recreate

### Issue: "No data found for location"
**Solution**: Check spelling of location name. Use option 2 to see available locations

### Issue: Tests failing
**Solution**: Ensure you're in the project directory and dataset exists
```powershell
cd kai-Adam-Project
pytest test_main.py -v
```

## Output Files

- `vaccinations.db`: SQLite database
- `activity.log`: User activity log
- `exports/*.csv`: Exported data files
- `exports/*.png`: Generated plots and visualizations

## Requirements

- Python 3.8 or higher
- Windows PowerShell (for provided commands)
- 100MB free disk space (for database)

## Development Notes

- All functions include docstrings with descriptions
- Type hints used throughout for clarity
- Comprehensive error handling
- Activity logging for all operations
- Following PEP 8 style guidelines
