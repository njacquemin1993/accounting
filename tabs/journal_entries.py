"""
Journal Entries tab functionality.
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date
from database import Account, JournalEntry
from accounting_utils import validate_journal_entry

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
    
    col1, col2, col3, col4, col5, col6 = st.columns(6, vertical_alignment='bottom')
    
    with col1:
        entry_date = st.date_input("Date", value=date.today())
    with col2:
        description = st.text_input("Description", help="Brief description of the transaction")        
    with col3:
        debit_account = st.selectbox("Debit Account", account_list)
    with col4:
        credit_account = st.selectbox("Credit Account", account_list)
    with col5:
        amount = st.number_input("Amount", min_value=0.01, step=0.01, format="%.2f")
    with col6:
        if st.button("Add Journal Entry"):
            if description and amount > 0:
                debit_account_id = account_options[debit_account]
                credit_account_id = account_options[credit_account]
                
                is_valid, errors = validate_journal_entry(debit_account_id, credit_account_id, amount)
                
                if is_valid:
                    new_entry = JournalEntry(
                        date=datetime.combine(entry_date, datetime.min.time()),
                        description=description,
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
