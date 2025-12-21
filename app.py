"""
Main Streamlit application for the accounting system using st.navigation.
"""

import streamlit as st
from translation_utils import t


def main():
    st.set_page_config(page_title=t("app_title"), page_icon="💰", layout="wide")

    # Create navigation pages - each as its own top-level tab
    pages = [
        st.Page(
            "pages/file_management_page.py",
            title=t("tab_file_management"),
            icon="📁",
        ),
        st.Page(
            "pages/chart_of_accounts_page.py",
            title=t("tab_chart_of_accounts"),
            icon="📊",
        ),
        st.Page(
            "pages/journal_entries_page.py", title=t("tab_journal_entries"), icon="📝"
        ),
        st.Page(
            "pages/account_balances_page.py", title=t("tab_account_balances"), icon="⚖️"
        ),
        st.Page("pages/result_sheet_page.py", title=t("tab_result_sheet"), icon="📈"),
        st.Page("pages/balance_sheet_page.py", title=t("tab_balance_sheet"), icon="📋"),
        st.Page(
            "pages/year_closing_page.py",
            title=t("tab_year_closing"),
            icon="🗄️",
        ),
    ]

    # Create navigation with top position (naturally sticky)
    pg = st.navigation(pages, position="top")
    pg.run()


if __name__ == "__main__":
    main()
