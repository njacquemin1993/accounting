"""
Main Streamlit application for the accounting system using st.navigation.
"""

import streamlit as st
from translation_utils import t

from pages.account_balances_page import AccountBalancesPage
from pages.balance_sheet_page import BalanceSheetPage
from pages.chart_of_accounts_page import ChartOfAccountsPage
from pages.file_management_page import FileManagementPage
from pages.journal_entries_page import JournalEntriesPage
from pages.result_sheet_page import ResultSheetPage
from pages.year_closing_page import YearClosingPage


def main():
    st.set_page_config(page_title=t("app_title"), page_icon="💰", layout="wide")

    # Create navigation pages - each as its own top-level tab
    pages = [
        FileManagementPage(),
        ChartOfAccountsPage(),
        JournalEntriesPage(),
        AccountBalancesPage(),
        ResultSheetPage(),
        BalanceSheetPage(),
        YearClosingPage(),
    ]

    # Create navigation with top position (naturally sticky)
    pg = st.navigation(pages, position="top")
    pg.run()


if __name__ == "__main__":
    main()
