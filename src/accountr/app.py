"""
Main Streamlit application for the accounting system using st.navigation.
"""

import streamlit as st
from accountr.translation_utils import t

from accountr.pages.account_balances_page import AccountBalancesPage
from accountr.pages.balance_sheet_page import BalanceSheetPage
from accountr.pages.chart_of_accounts_page import ChartOfAccountsPage
from accountr.pages.file_management_page import FileManagementPage
from accountr.pages.journal_entries_page import JournalEntriesPage
from accountr.pages.result_sheet_page import ResultSheetPage
from accountr.pages.stock_management_page import StockManagementPage
from accountr.pages.year_closing_page import YearClosingPage


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
