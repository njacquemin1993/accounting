# Simple Accounting App

A simple accounting application built with Python, Streamlit, and SQLAlchemy.

## Features

- **Chart of Accounts Management**: Add and manage accounts categorized as Active (Assets), Passive (Liabilities/Equity), Expenses, and Products (Revenue)
- **Journal Entries**: Record double-entry bookkeeping transactions
- **Account Balances**: View balances for all accounts with filtering options
- **Balance Sheet**: Generate and view balance sheet with automatic balance validation

## Technologies Used

- **Frontend**: Streamlit
- **Database**: SQLite with SQLAlchemy ORM
- **Additional Libraries**: Pandas for data manipulation

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

## Application Structure

- `app.py`: Main Streamlit application entry point
- `database.py`: SQLAlchemy models and database configuration
- `accounting_utils.py`: Utility functions for accounting calculations
- `tabs/`: Directory containing tab modules
  - `chart_of_accounts.py`: Chart of Accounts tab functionality
  - `journal_entries.py`: Journal Entries tab functionality
  - `account_balances.py`: Account Balances tab functionality
  - `result_sheet.py`: Result Sheet (Income Statement) tab functionality
  - `balance_sheet.py`: Balance Sheet tab functionality
- `requirements.txt`: Python dependencies

## Default Chart of Accounts

The application comes pre-configured with a basic chart of accounts:

### Assets (Active)
- 1000 - Cash
- 1100 - Accounts Receivable
- 1200 - Inventory
- 1500 - Equipment

### Liabilities (Passive)
- 2000 - Accounts Payable
- 2100 - Short-term Loans
- 2500 - Long-term Debt

### Equity (Passive)
- 3000 - Owner's Equity
- 3100 - Retained Earnings

### Revenue (Products)
- 4000 - Sales Revenue
- 4100 - Service Revenue

### Expenses
- 5000 - Cost of Goods Sold
- 5100 - Rent Expense
- 5200 - Utilities Expense
- 5300 - Marketing Expense

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

## Contributing

This is a simple educational project. Feel free to fork and enhance it with additional features like:
- Income statement generation
- Cash flow statement
- Account reconciliation
- User authentication
- Multi-company support
- Advanced reporting