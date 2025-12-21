"""
Main Streamlit application for the accounting system using st.navigation.
"""

import streamlit as st
from accounting.translation_utils import t

from accounting.pages.account_balances_page import AccountBalancesPage
from accounting.pages.balance_sheet_page import BalanceSheetPage
from accounting.pages.chart_of_accounts_page import ChartOfAccountsPage
from accounting.pages.file_management_page import FileManagementPage
from accounting.pages.journal_entries_page import JournalEntriesPage
from accounting.pages.result_sheet_page import ResultSheetPage
from accounting.pages.stock_management_page import StockManagementPage
from accounting.pages.year_closing_page import YearClosingPage


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
    StockManagementPage(),
]

# Create navigation with top position (naturally sticky)
pg = st.navigation(pages, position="top")
pg.run()
