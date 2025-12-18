"""
Utility functions for accounting calculations and operations.
"""
from sqlalchemy.orm import Session
from database import Account, JournalEntry
import pandas as pd

def get_account_balance(session: Session, account_id: int) -> float:
    """Calculate the balance of a specific account."""
    account = session.query(Account).filter(Account.id == account_id).first()
    if not account:
        return 0.0
    
    # Get all debit entries for this account
    debit_total = session.query(JournalEntry).filter(
        JournalEntry.debit_account_id == account_id
    ).with_entities(JournalEntry.amount).all()
    debit_sum = sum([entry[0] for entry in debit_total])
    
    # Get all credit entries for this account
    credit_total = session.query(JournalEntry).filter(
        JournalEntry.credit_account_id == account_id
    ).with_entities(JournalEntry.amount).all()
    credit_sum = sum([entry[0] for entry in credit_total])
    
    # Calculate balance based on account type
    if account.account_type in ['Asset', 'Expense']:
        # Normal debit balance
        return debit_sum - credit_sum
    else:
        # Normal credit balance (Liability, Equity, Revenue)
        return credit_sum - debit_sum

def get_trial_balance(session: Session) -> pd.DataFrame:
    """Generate trial balance for all accounts."""
    accounts = session.query(Account).filter(Account.is_active == True).all()
    
    trial_balance_data = []
    for account in accounts:
        balance = get_account_balance(session, account.id)
        trial_balance_data.append({
            'Account Code': account.account_code,
            'Account Name': account.account_name,
            'Account Type': account.account_type,
            'Category': account.category,
            'Balance': balance
        })
    
    return pd.DataFrame(trial_balance_data)

def get_balance_sheet_data(session: Session) -> dict:
    """Generate balance sheet data using categories."""
    accounts = session.query(Account).filter(Account.is_active == True).all()
    
    active = []
    passive = []
    
    for account in accounts:
        balance = get_account_balance(session, account.id)
        account_data = {
            'code': account.account_code,
            'name': account.account_name,
            'balance': balance
        }
        
        if account.category == 'Active':
            active.append(account_data)
        elif account.category == 'Passive':
            passive.append(account_data)
    
    total_active = sum([acc['balance'] for acc in active])
    total_passive = sum([acc['balance'] for acc in passive])
    
    return {
        'active': active,
        'passive': passive,
        'total_active': total_active,
        'total_passive': total_passive
    }

def get_income_statement_data(session: Session) -> dict:
    """Generate income statement data using categories."""
    accounts = session.query(Account).filter(Account.is_active == True).all()
    
    products = []
    expenses = []
    
    for account in accounts:
        balance = get_account_balance(session, account.id)
        account_data = {
            'code': account.account_code,
            'name': account.account_name,
            'balance': balance
        }
        
        if account.category == 'Products':
            products.append(account_data)
        elif account.category == 'Expenses':
            expenses.append(account_data)
    
    total_products = sum([acc['balance'] for acc in products])
    total_expenses = sum([acc['balance'] for acc in expenses])
    net_income = total_products - total_expenses
    
    return {
        'products': products,
        'expenses': expenses,
        'total_products': total_products,
        'total_expenses': total_expenses,
        'net_income': net_income
    }

def validate_journal_entry(debit_account_id: int, credit_account_id: int, amount: float) -> tuple:
    """Validate journal entry data."""
    errors = []
    
    if debit_account_id == credit_account_id:
        errors.append("Debit and credit accounts cannot be the same")
    
    if amount <= 0:
        errors.append("Amount must be greater than zero")
    
    return len(errors) == 0, errors