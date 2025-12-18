"""
Main Streamlit application for the accounting system.
"""
import streamlit as st
from database import DatabaseManager
from tabs import (
    manage_chart_of_accounts,
    manage_journal_entries,
    view_account_balances,
    view_result_sheet,
    view_balance_sheet
)

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

if __name__ == "__main__":
    main()