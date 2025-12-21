# Simple Accounting App

A simple accounting application built with Python, Streamlit, and SQLAlchemy.

## Features

- **Multi-language Support**: Available in English, French, and German
- **Chart of Accounts Management**: Add, edit, and manage accounts categorized as Active (Assets), Passive (Liabilities/Equity), Expenses, and Products (Revenue)
- **Journal Entries**: Record double-entry bookkeeping transactions with validation
- **Account Balances**: View balances for all accounts with filtering and detailed transaction history
- **Balance Sheet**: Generate and view balance sheet with automatic balance validation
- **Result Sheet (Income Statement)**: View revenue and expenses with net income calculation
- **Excel Export**: Export all accounting data to formatted Excel workbooks
- **Database Management**: Backup, restore, and manage database files
- **Year-End Closing**: Automated year-end closing with comprehensive backup packages

## Technologies Used

- **Frontend**: Streamlit for web interface
- **Database**: SQLite with SQLAlchemy ORM
- **Data Processing**: Pandas for data manipulation and analysis
- **Export**: XlsxWriter for Excel report generation
- **Visualization**: Plotly for charts (if needed)

## Installation

1. Clone or download this repository
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   streamlit run app.py
   ```

2. Open your web browser and navigate to the URL shown in the terminal (usually `http://localhost:8501`)

3. Select your preferred language from the dropdown (English, French, or German)

## Application Structure

The application follows a modular architecture with clear separation of concerns:

### Core Modules
- `app.py`: Main Streamlit application entry point with navigation
- `database.py`: SQLAlchemy models (Account, JournalEntry) and database configuration
- `constants.py`: Centralized configuration values and magic numbers
- `helpers.py`: Common helper functions for validation and formatting
- `accounting_utils.py`: Business logic for accounting calculations (balance, trial balance, etc.)
- `translation_utils.py`: Multi-language support utilities (English, French, German)
- `translations.py`: Translation strings for all supported languages

### Page Modules (`pages/`)
- `chart_of_accounts_page.py`: Chart of Accounts management
- `journal_entries_page.py`: Journal entry recording and editing
- `account_balances_page.py`: Account balance viewing with filtering
- `result_sheet_page.py`: Income Statement (Result Sheet) generation
- `balance_sheet_page.py`: Balance Sheet generation with validation

### File Management
- `file_manager.py`: Database backup, restore, and file operations
- `file_management_ui.py`: UI components for file management and year-end closing
- `excel_utils.py`: Excel formatting utilities and configuration
- `excel_export.py`: Excel export logic for all accounting reports

### Database
- `accounting.db`: SQLite database (auto-created on first run)
- `requirements.txt`: Python package dependencies

## Database

The application uses SQLite for data storage. The database file (`accounting.db`) will be created automatically in the same directory as the application.

## Features Overview

### Chart of Accounts Tab
- View all active accounts in a table format
- Add new accounts with account codes, names, types, and categories
- Deactivate accounts (soft delete)

### Journal Entries Tab
- View recent journal entries
- Add new journal entries with double-entry validation
- Select debit and credit accounts from dropdown menus

### Account Balances Tab
- View balances for all accounts
- Filter by category or account type
- Summary metrics showing totals by account type

### Balance Sheet Tab
- Traditional balance sheet format
- Shows Assets on the left, Liabilities and Equity on the right
- Automatic balance validation (Assets = Liabilities + Equity)

## Code Quality

This project follows professional coding standards:
- **No Magic Numbers**: All configuration values centralized in `constants.py`
- **DRY Principle**: Common functionality extracted into helper modules
- **Separation of Concerns**: Clear boundaries between UI, business logic, and data layers
- **Modular Architecture**: Focused modules with single responsibilities
- **Type Hints**: Function signatures include type information where appropriate
- **Documentation**: Functions include docstrings explaining purpose and parameters
