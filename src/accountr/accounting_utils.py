"""
Utility functions for accounting calculations and operations.
"""

from sqlalchemy.orm import Session
from accountr.database import Account, JournalEntry
import pandas as pd
from accountr.constants import (
    CATEGORY_ACTIVE,
    CATEGORY_PASSIVE,
    CATEGORY_EXPENSES,
    CATEGORY_PRODUCTS,
    DEBIT_BALANCE_CATEGORIES,
)


def get_account_balance(session: Session, account_id: int) -> float:
    """Calculate the balance of a specific account."""
    account = session.query(Account).filter(Account.id == account_id).first()
    if not account:
        return 0.0

    # Start with the base balance (for Active/Passive accounts)
    base_balance = account.balance if hasattr(account, "balance") else 0.0

    # Get all debit entries for this account
    debit_total = (
        session.query(JournalEntry)
        .filter(JournalEntry.debit_account_id == account_id)
        .with_entities(JournalEntry.amount)
        .all()
    )
    debit_sum = sum([entry[0] for entry in debit_total])

    # Get all credit entries for this account
    credit_total = (
        session.query(JournalEntry)
        .filter(JournalEntry.credit_account_id == account_id)
        .with_entities(JournalEntry.amount)
        .all()
    )
    credit_sum = sum([entry[0] for entry in credit_total])

    # Calculate balance based on category
    if account.category in DEBIT_BALANCE_CATEGORIES:
        # Normal debit balance (Active = Assets, Expenses = Expenses)
        # For Active accounts, add base balance; for Expenses, base balance is always 0
        balance_from_entries = debit_sum - credit_sum
        if account.category == CATEGORY_ACTIVE:
            return base_balance + balance_from_entries
        else:
            return balance_from_entries
    else:
        # Normal credit balance (Passive = Liabilities + Equity, Products = Revenue)
        # For Passive accounts, add base balance; for Products, base balance is always 0
        balance_from_entries = credit_sum - debit_sum
        if account.category == CATEGORY_PASSIVE:
            return base_balance + balance_from_entries
        else:
            return balance_from_entries


def get_trial_balance(session: Session) -> pd.DataFrame:
    """Generate trial balance for all accounts."""
    accounts = session.query(Account).filter(Account.is_active).all()

    trial_balance_data = []
    for account in accounts:
        balance = get_account_balance(session, account.id)
        trial_balance_data.append(
            {
                "Account ID": account.id,
                "Account Code": account.account_code,
                "Account Name": account.account_name,
                "Category": account.category,
                "Balance": balance,
            }
        )

    return pd.DataFrame(trial_balance_data)


def get_balance_sheet_data(session: Session) -> dict:
    """Generate balance sheet data using categories."""
    accounts = session.query(Account).filter(Account.is_active).all()

    active = []
    passive = []

    for account in accounts:
        balance = get_account_balance(session, account.id)
        account_data = {
            "code": account.account_code,
            "name": account.account_name,
            "balance": balance,
        }

        if account.category == CATEGORY_ACTIVE:
            active.append(account_data)
        elif account.category == CATEGORY_PASSIVE:
            passive.append(account_data)

    total_active = sum([acc["balance"] for acc in active])
    total_passive = sum([acc["balance"] for acc in passive])

    return {
        "active": active,
        "passive": passive,
        "total_active": total_active,
        "total_passive": total_passive,
    }


def get_income_statement_data(session: Session) -> dict:
    """Generate income statement data using categories."""
    accounts = session.query(Account).filter(Account.is_active).all()

    products = []
    expenses = []

    for account in accounts:
        balance = get_account_balance(session, account.id)
        account_data = {
            "code": account.account_code,
            "name": account.account_name,
            "balance": balance,
        }

        if account.category == CATEGORY_PRODUCTS:
            products.append(account_data)
        elif account.category == CATEGORY_EXPENSES:
            expenses.append(account_data)

    total_products = sum([acc["balance"] for acc in products])
    total_expenses = sum([acc["balance"] for acc in expenses])
    net_income = total_products - total_expenses

    return {
        "products": products,
        "expenses": expenses,
        "total_products": total_products,
        "total_expenses": total_expenses,
        "net_income": net_income,
    }


def get_account_entries(session: Session, account_id: int) -> pd.DataFrame:
    """Get all journal entries for a specific account."""
    account = session.query(Account).filter(Account.id == account_id).first()
    if not account:
        return pd.DataFrame()

    entries_data = []

    # Get all entries where this account is debited
    debit_entries = (
        session.query(JournalEntry)
        .filter(JournalEntry.debit_account_id == account_id)
        .order_by(JournalEntry.date.desc())
        .all()
    )

    for entry in debit_entries:
        entries_data.append(
            {
                "Date": entry.date,
                "Description": entry.description,
                "Counterparty": f"{entry.credit_account.account_code} - {entry.credit_account.account_name}",
                "Debit": entry.amount,
                "Credit": 0.0,
            }
        )

    # Get all entries where this account is credited
    credit_entries = (
        session.query(JournalEntry)
        .filter(JournalEntry.credit_account_id == account_id)
        .order_by(JournalEntry.date.desc())
        .all()
    )

    for entry in credit_entries:
        entries_data.append(
            {
                "Date": entry.date,
                "Description": entry.description,
                "Counterparty": f"{entry.debit_account.account_code} - {entry.debit_account.account_name}",
                "Debit": 0.0,
                "Credit": entry.amount,
            }
        )

    df = pd.DataFrame(entries_data)
    if not df.empty:
        # Sort by date (most recent first)
        df = df.sort_values("Date", ascending=False)

    return df


def validate_journal_entry(debit_account_id: int, credit_account_id: int, amount: float) -> tuple:
    """Validate journal entry data."""
    errors = []

    if debit_account_id == credit_account_id:
        errors.append("Debit and credit accounts cannot be the same")

    if amount <= 0:
        errors.append("Amount must be greater than zero")

    return len(errors) == 0, errors
