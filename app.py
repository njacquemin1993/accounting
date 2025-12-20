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
    view_balance_sheet,
)
from translation_utils import t, language_selector


# Initialize database
@st.cache_resource
def get_database():
    db_manager = DatabaseManager()
    db_manager.initialize_default_accounts()
    return db_manager


def main():
    st.set_page_config(page_title="Accounting System", page_icon="💰", layout="wide")

    st.title(f"💰 {t('app_title')}")

    # Add language selector in sidebar
    with st.sidebar:
        st.markdown("---")
        language_selector()

    # Initialize database
    db_manager = get_database()

    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            t("tab_chart_of_accounts"),
            t("tab_journal_entries"),
            t("tab_account_balances"),
            t("tab_result_sheet"),
            t("tab_balance_sheet"),
        ]
    )

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
