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

    # Initialize active tab in session state
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = 0

    # Create custom tab navigation
    tab_names = [
        t("tab_chart_of_accounts"),
        t("tab_journal_entries"),
        t("tab_account_balances"),
        t("tab_result_sheet"),
        t("tab_balance_sheet"),
    ]

    # Create tab buttons
    cols = st.columns(len(tab_names))
    for i, tab_name in enumerate(tab_names):
        with cols[i]:
            button_clicked = st.button(
                tab_name,
                key=f"tab_{i}",
                use_container_width=True,
                type="primary" if st.session_state.active_tab == i else "secondary"
            )
            if button_clicked:
                st.session_state.active_tab = i
                st.rerun()

    st.markdown("---")

    # Display content based on active tab
    if st.session_state.active_tab == 0:
        manage_chart_of_accounts(db_manager)
    elif st.session_state.active_tab == 1:
        manage_journal_entries(db_manager)
    elif st.session_state.active_tab == 2:
        view_account_balances(db_manager)
    elif st.session_state.active_tab == 3:
        view_result_sheet(db_manager)
    elif st.session_state.active_tab == 4:
        view_balance_sheet(db_manager)


if __name__ == "__main__":
    main()
