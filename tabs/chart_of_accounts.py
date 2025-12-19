"""
Chart of Accounts tab functionality.
"""
import streamlit as st
import pandas as pd
from database import Account

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
    
    col1, col2, col3, col4 = st.columns([0.2, 0.4, 0.3, 0.1], vertical_alignment='bottom')
    
    with col1:
        account_code = st.text_input("Account Code", help="e.g., 1000, 2000, etc.")
    with col2:
        account_name = st.text_input("Account Name", help="e.g., Cash, Accounts Payable")
        
    with col3:
        category = st.selectbox(
            "Category",
            ["Active", "Passive", "Expenses", "Products"]
        )

    with col4:
        if st.button("Add Account", width="stretch"):
            if account_code and account_name:
                # Check if account code already exists
                existing = session.query(Account).filter(Account.account_code == account_code).first()
                if existing:
                    st.error("Account code already exists!")
                else:
                    new_account = Account(
                        account_code=account_code,
                        account_name=account_name,
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
