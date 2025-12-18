"""
Main Streamlit application for the accounting system.
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date
from database import DatabaseManager, Account, JournalEntry
from accounting_utils import get_account_balance, get_trial_balance, get_balance_sheet_data, get_income_statement_data, validate_journal_entry

# Initialize database
@st.cache_resource
def get_database():
    db_manager = DatabaseManager()
    db_manager.initialize_default_accounts()
    return db_manager

def main():
    st.set_page_config(
        page_title="Accounting System",
        page_icon="💰",
        layout="wide"
    )
    
    st.title("💰 Simple Accounting System")
    
    # Initialize database
    db_manager = get_database()
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Chart of Accounts", 
        "📝 Journal Entries", 
        "⚖️ Account Balances", 
        "📈 Result Sheet",
        "📋 Balance Sheet",
    ])
    
    with tab1:
        manage_chart_of_accounts(db_manager)
    
    with tab2:
        manage_journal_entries(db_manager)
    
    with tab3:
        view_account_balances(db_manager)
    
    with tab4:
        view_result_sheet(db_manager)
    
    with tab5:
        view_balance_sheet(db_manager)

def manage_chart_of_accounts(db_manager):
    """Tab for managing chart of accounts."""
    st.header("Chart of Accounts")
    
    session = db_manager.get_session()
    
    # Display existing accounts
    accounts = session.query(Account).filter(Account.is_active == True).order_by(Account.account_code).all()
    
    if accounts:
        account_data = []
        for account in accounts:
            account_data.append({
                'ID': account.id,
                'Code': account.account_code,
                'Name': account.account_name,
                'Category': account.category
            })
        
        df = pd.DataFrame(account_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No accounts found. Add your first account below.")
    
    st.subheader("Add New Account")
    
    col1, col2 = st.columns(2)
    
    with col1:
        account_code = st.text_input("Account Code", help="e.g., 1000, 2000, etc.")
        account_name = st.text_input("Account Name", help="e.g., Cash, Accounts Payable")
        
    with col2:
        category = st.selectbox(
            "Category",
            ["Active", "Passive", "Expenses", "Products"]
        )
    
    if st.button("Add Account"):
        if account_code and account_name:
            # Check if account code already exists
            existing = session.query(Account).filter(Account.account_code == account_code).first()
            if existing:
                st.error("Account code already exists!")
            else:
                new_account = Account(
                    account_code=account_code,
                    account_name=account_name,
                    account_type="General",  # Default type since we only use categories
                    category=category
                )
                session.add(new_account)
                session.commit()
                st.success("Account added successfully!")
                st.rerun()
        else:
            st.error("Please fill in all required fields.")
    
    # Account deactivation section
    st.subheader("Deactivate Account")
    if accounts:
        account_options = {f"{acc.account_code} - {acc.account_name}": acc.id for acc in accounts}
        selected_account = st.selectbox("Select Account to Deactivate", list(account_options.keys()))
        
        if st.button("Deactivate Account", type="secondary"):
            account_id = account_options[selected_account]
            account = session.query(Account).filter(Account.id == account_id).first()
            account.is_active = False
            session.commit()
            st.success(f"Account {selected_account} deactivated!")
            st.rerun()
    
    session.close()

def manage_journal_entries(db_manager):
    """Tab for managing journal entries."""
    st.header("Journal Entries")
    
    session = db_manager.get_session()
    
    # Display existing journal entries
    entries = session.query(JournalEntry).order_by(JournalEntry.date.desc()).limit(20).all()
    
    if entries:
        st.subheader("Recent Journal Entries")
        entry_data = []
        for entry in entries:
            entry_data.append({
                'Date': entry.date.strftime('%Y-%m-%d'),
                'Description': entry.description,
                'Reference': entry.reference or '',
                'Debit Account': f"{entry.debit_account.account_code} - {entry.debit_account.account_name}",
                'Credit Account': f"{entry.credit_account.account_code} - {entry.credit_account.account_name}",
                'Amount': f"CHF {entry.amount:,.2f}"
            })
        
        df = pd.DataFrame(entry_data)
        st.dataframe(df, use_container_width=True)
    
    st.subheader("Add New Journal Entry")
    
    # Get active accounts for dropdowns
    active_accounts = session.query(Account).filter(Account.is_active == True).order_by(Account.account_code).all()
    
    if len(active_accounts) < 2:
        st.warning("You need at least 2 active accounts to create journal entries.")
        session.close()
        return
    
    account_options = {f"{acc.account_code} - {acc.account_name}": acc.id for acc in active_accounts}
    account_list = list(account_options.keys())
    
    col1, col2 = st.columns(2)
    
    with col1:
        entry_date = st.date_input("Date", value=date.today())
        description = st.text_input("Description", help="Brief description of the transaction")
        reference = st.text_input("Reference", help="Optional reference number")
        
    with col2:
        debit_account = st.selectbox("Debit Account", account_list)
        credit_account = st.selectbox("Credit Account", account_list)
        amount = st.number_input("Amount", min_value=0.01, step=0.01, format="%.2f")
    
    if st.button("Add Journal Entry"):
        if description and amount > 0:
            debit_account_id = account_options[debit_account]
            credit_account_id = account_options[credit_account]
            
            is_valid, errors = validate_journal_entry(debit_account_id, credit_account_id, amount)
            
            if is_valid:
                new_entry = JournalEntry(
                    date=datetime.combine(entry_date, datetime.min.time()),
                    description=description,
                    reference=reference or None,
                    debit_account_id=debit_account_id,
                    credit_account_id=credit_account_id,
                    amount=amount
                )
                session.add(new_entry)
                session.commit()
                st.success("Journal entry added successfully!")
                st.rerun()
            else:
                for error in errors:
                    st.error(error)
        else:
            st.error("Please fill in all required fields and ensure amount is greater than zero.")
    
    session.close()

def view_account_balances(db_manager):
    """Tab for viewing account balances."""
    st.header("Account Balances")
    
    session = db_manager.get_session()
    
    # Get trial balance
    trial_balance = get_trial_balance(session)
    
    if not trial_balance.empty:
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            category_filter = st.selectbox(
                "Filter by Category",
                ["All"] + list(trial_balance['Category'].unique())
            )
        with col2:
            type_filter = st.selectbox(
                "Filter by Type",
                ["All"] + list(trial_balance['Account Type'].unique())
            )
        
        # Apply filters
        filtered_df = trial_balance.copy()
        if category_filter != "All":
            filtered_df = filtered_df[filtered_df['Category'] == category_filter]
        if type_filter != "All":
            filtered_df = filtered_df[filtered_df['Account Type'] == type_filter]
        
        # Format the balance column
        filtered_df['Balance'] = filtered_df['Balance'].apply(lambda x: f"CHF {x:,.2f}")
        
        st.dataframe(filtered_df, use_container_width=True)
        
        # Summary statistics
        st.subheader("Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_assets = trial_balance[trial_balance['Account Type'] == 'Asset']['Balance'].apply(
                lambda x: float(x.replace('$', '').replace(',', '')) if isinstance(x, str) else x
            ).sum()
            st.metric("Total Assets", f"CHF {total_assets:,.2f}")
        
        with col2:
            total_liabilities = trial_balance[trial_balance['Account Type'] == 'Liability']['Balance'].apply(
                lambda x: float(x.replace('CHF ', '').replace(',', '')) if isinstance(x, str) else x
            ).sum()
            st.metric("Total Liabilities", f"CHF {total_liabilities:,.2f}")
        
        with col3:
            total_equity = trial_balance[trial_balance['Account Type'] == 'Equity']['Balance'].apply(
                lambda x: float(x.replace('CHF ', '').replace(',', '')) if isinstance(x, str) else x
            ).sum()
            st.metric("Total Equity", f"CHF {total_equity:,.2f}")
        
        with col4:
            # Convert back to float for calculation
            numeric_balances = trial_balance['Balance'].apply(
                lambda x: float(x.replace('CHF ', '').replace(',', '')) if isinstance(x, str) else x
            )
            trial_balance['Numeric_Balance'] = numeric_balances
            
            total_revenue = trial_balance[trial_balance['Account Type'] == 'Revenue']['Numeric_Balance'].sum()
            total_expenses = trial_balance[trial_balance['Account Type'] == 'Expense']['Numeric_Balance'].sum()
            net_income = total_revenue - total_expenses
            st.metric("Net Income", f"CHF {net_income:,.2f}")
            
    else:
        st.info("No account balances to display. Add some journal entries first.")
    
    session.close()

def view_balance_sheet(db_manager):
    """Tab for viewing balance sheet."""
    st.header("Balance Sheet")
    
    session = db_manager.get_session()
    
    balance_sheet_data = get_balance_sheet_data(session)
    income_statement_data = get_income_statement_data(session)
    
    # Calculate table heights to align totals
    active_rows = len(balance_sheet_data['active']) + 2  # active + blank + total
    passive_rows = len(balance_sheet_data['passive']) + 2  # passive + blank + total
    
    # Add net income line if not zero
    if abs(income_statement_data['net_income']) > 0.01:
        passive_rows += 2  # net income line + blank line
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Active")
        if balance_sheet_data['active']:
            # Create DataFrame for active accounts
            active_data = []
            for account in balance_sheet_data['active']:
                active_data.append({
                    'Account': f"{account['code']} - {account['name']}",
                    'Amount': f"CHF {account['balance']:,.2f}"
                })
            
            # Add blank lines if active table is shorter
            if active_rows < passive_rows:
                blank_lines_needed = passive_rows - active_rows
                for _ in range(blank_lines_needed):
                    active_data.append({
                        'Account': '',
                        'Amount': ''
                    })
            
            # Add spacing and total
            active_data.append({
                'Account': '',
                'Amount': ''
            })
            active_data.append({
                'Account': 'TOTAL ACTIVE',
                'Amount': f"CHF {balance_sheet_data['total_active']:,.2f}"
            })
            
            active_df = pd.DataFrame(active_data)
            
            # Display table without index
            st.table(active_df)
        else:
            st.write("No active accounts to display")
    
    with col2:
        st.subheader("Passive")
        
        # Create DataFrame for passive accounts
        passive_data = []
        
        # Add passive accounts
        if balance_sheet_data['passive']:
            for account in balance_sheet_data['passive']:
                passive_data.append({
                    'Account': f"{account['code']} - {account['name']}",
                    'Amount': f"CHF {account['balance']:,.2f}"
                })
        
        # Add spacing
        passive_data.append({
            'Account': '',
            'Amount': ''
        })
        
        # Add net income/loss if not zero
        net_income = income_statement_data['net_income']
        if abs(net_income) > 0.01:
            if net_income >= 0:
                passive_data.append({
                    'Account': 'Net Income (Current Period)',
                    'Amount': f"CHF {net_income:,.2f}"
                })
            else:
                passive_data.append({
                    'Account': 'Net Loss (Current Period)',
                    'Amount': f"CHF {net_income:,.2f}"
                })
        
        # Add blank lines if passive table is shorter
        if passive_rows < active_rows:
            blank_lines_needed = active_rows - passive_rows
            for _ in range(blank_lines_needed):
                passive_data.append({
                    'Account': '',
                    'Amount': ''
                })
        
        # Calculate total including net income
        total_passive_with_net_income = balance_sheet_data['total_passive'] + net_income
        
        # Add spacing and grand total
        passive_data.append({
            'Account': '',
            'Amount': ''
        })
        passive_data.append({
            'Account': 'TOTAL PASSIVE',
            'Amount': f"CHF {total_passive_with_net_income:,.2f}"
        })
        
        if passive_data:
            passive_df = pd.DataFrame(passive_data)
            
            # Display table without index
            st.table(passive_df)
        else:
            st.write("No passive accounts to display")
    
    # Balance check
    st.markdown("---")
    total_passive_with_net_income = balance_sheet_data['total_passive'] + income_statement_data['net_income']
    difference = balance_sheet_data['total_active'] - total_passive_with_net_income
    if abs(difference) < 0.01:  # Allow for small rounding differences
        st.success("✅ Balance Sheet is balanced!")
    else:
        st.error(f"❌ Balance Sheet is not balanced. Difference: CHF {difference:,.2f}")
    
    # Show net income impact
    if abs(income_statement_data['net_income']) > 0.01:
        if income_statement_data['net_income'] >= 0:
            st.info(f"💰 Current period net income of CHF {income_statement_data['net_income']:,.2f} has been included in passive.")
        else:
            st.warning(f"⚠️ Current period net loss of CHF {income_statement_data['net_income']:,.2f} has been included in passive.")
    
    session.close()

def view_result_sheet(db_manager):
    """Tab for viewing result sheet (income statement)."""
    st.header("Result Sheet (Income Statement)")
    
    session = db_manager.get_session()
    
    income_statement_data = get_income_statement_data(session)
    
    # Calculate table heights to align totals
    products_rows = len(income_statement_data['products']) + 2  # products + blank + total
    expenses_rows = len(income_statement_data['expenses']) + 2  # expenses + blank + total
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Products")
        if income_statement_data['products']:
            # Create DataFrame for products
            products_data = []
            for product in income_statement_data['products']:
                products_data.append({
                    'Account': f"{product['code']} - {product['name']}",
                    'Amount': f"CHF {product['balance']:,.2f}"
                })
            
            # Add blank lines if products table is shorter
            if products_rows < expenses_rows:
                blank_lines_needed = expenses_rows - products_rows
                for _ in range(blank_lines_needed):
                    products_data.append({
                        'Account': '',
                        'Amount': ''
                    })
            
            # Add spacing and total
            products_data.append({
                'Account': '',
                'Amount': ''
            })
            products_data.append({
                'Account': 'TOTAL PRODUCTS',
                'Amount': f"CHF {income_statement_data['total_products']:,.2f}"
            })
            
            products_df = pd.DataFrame(products_data)
            
            # Display table without index
            st.table(products_df)
        else:
            st.write("No products to display")
    
    with col2:
        st.subheader("Expenses")
        if income_statement_data['expenses']:
            # Create DataFrame for expenses
            expenses_data = []
            for expense in income_statement_data['expenses']:
                expenses_data.append({
                    'Account': f"{expense['code']} - {expense['name']}",
                    'Amount': f"CHF {expense['balance']:,.2f}"
                })
            
            # Add blank lines if expenses table is shorter
            if expenses_rows < products_rows:
                blank_lines_needed = products_rows - expenses_rows
                for _ in range(blank_lines_needed):
                    expenses_data.append({
                        'Account': '',
                        'Amount': ''
                    })
            
            # Add spacing and total
            expenses_data.append({
                'Account': '',
                'Amount': ''
            })
            expenses_data.append({
                'Account': 'TOTAL EXPENSES',
                'Amount': f"CHF {income_statement_data['total_expenses']:,.2f}"
            })
            
            expenses_df = pd.DataFrame(expenses_data)
            
            # Display table without index
            st.table(expenses_df)
        else:
            st.write("No expenses to display")
    
    # Net income calculation
    st.markdown("---")
    net_income_col1, net_income_col2 = st.columns(2)
    
    with net_income_col1:
        st.markdown(f"### **NET INCOME**")
    
    with net_income_col2:
        net_income = income_statement_data['net_income']
        if net_income >= 0:
            st.markdown(f"### **CHF {net_income:,.2f}** 💰")
        else:
            st.markdown(f"### **CHF {net_income:,.2f}** ⚠️")
    
    # Additional metrics
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Products", f"CHF {income_statement_data['total_products']:,.2f}")
    
    with col2:
        st.metric("Total Expenses", f"CHF {income_statement_data['total_expenses']:,.2f}")
    
    with col3:
        if income_statement_data['total_products'] > 0:
            profit_margin = (net_income / income_statement_data['total_products']) * 100
            st.metric("Profit Margin", f"{profit_margin:.1f}%")
        else:
            st.metric("Profit Margin", "N/A")
    
    session.close()

if __name__ == "__main__":
    main()