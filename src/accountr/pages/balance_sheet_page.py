"""
Balance Sheet page for navigation.
"""

import streamlit as st
import pandas as pd
from accountr.accounting_utils import (
    get_balance_sheet_data,
    get_income_statement_data,
)
from accountr.translation_utils import t
from accountr.helpers import format_currency
from accountr.pages.base_page import BasePage


class BalanceSheetPage(BasePage):
    def __init__(self):
        super().__init__(title="balance_sheet", icon="📋")

    def content(self, session):
        balance_sheet_data = get_balance_sheet_data(session)
        income_statement_data = get_income_statement_data(session)

        # Build both sides first, then align them
        col1, col2 = st.columns(2)

        # Build active side data
        active_data = []
        if balance_sheet_data["active"]:
            for account in balance_sheet_data["active"]:
                active_data.append(
                    {
                        t("account_column"): f"{account['code']} - {account['name']}",
                        t("amount_column"): format_currency(account["balance"]),
                    }
                )

        # Build passive side data
        passive_data = []
        if balance_sheet_data["passive"]:
            for account in balance_sheet_data["passive"]:
                passive_data.append(
                    {
                        t("account_column"): f"{account['code']} - {account['name']}",
                        t("amount_column"): format_currency(account["balance"]),
                    }
                )

        # Add net income to passive side if not zero
        net_income = income_statement_data["net_income"]
        if abs(net_income) > 0.01:
            passive_data.append(
                {
                    t("account_column"): t("retained_earnings"),
                    t("amount_column"): format_currency(net_income),
                }
            )

        # Calculate how many rows each side has (before spacing and totals)
        active_account_rows = len(active_data)
        passive_account_rows = len(passive_data)

        # Add empty rows to the shorter side to align them
        if active_account_rows < passive_account_rows:
            for _ in range(passive_account_rows - active_account_rows):
                active_data.append({t("account_column"): "", t("amount_column"): ""})
        elif passive_account_rows < active_account_rows:
            for _ in range(active_account_rows - passive_account_rows):
                passive_data.append({t("account_column"): "", t("amount_column"): ""})

        # Add spacing and totals to both sides
        active_data.append({t("account_column"): "", t("amount_column"): ""})
        active_data.append(
            {
                t("account_column"): t("total_active"),
                t("amount_column"): format_currency(balance_sheet_data["total_active"]),
            }
        )

        passive_data.append({t("account_column"): "", t("amount_column"): ""})
        total_passive_with_net_income = balance_sheet_data["total_passive"] + net_income
        passive_data.append(
            {
                t("account_column"): t("total_passive"),
                t("amount_column"): format_currency(total_passive_with_net_income),
            }
        )

        # Display both sides
        with col1:
            st.subheader(t("active_title"))
            if active_data:
                active_df = pd.DataFrame(active_data)
                st.table(active_df)
            else:
                st.write(t("no_active_accounts_display"))

        with col2:
            st.subheader(t("passive_title"))
            if passive_data:
                passive_df = pd.DataFrame(passive_data)
                st.table(passive_df)
            else:
                st.write(t("no_passive_accounts_display"))

        # Balance check
        st.markdown("---")
        total_passive_with_net_income = balance_sheet_data["total_passive"] + income_statement_data["net_income"]
        difference = balance_sheet_data["total_active"] - total_passive_with_net_income
        if abs(difference) < 0.01:  # Allow for small rounding differences
            st.success(t("balance_sheet_balanced_checkmark"))
        else:
            st.error(f"{t('balance_sheet_not_balanced_x')} {format_currency(difference)}")

        # Show net income impact
        if abs(income_statement_data["net_income"]) > 0.01:
            income = format_currency(abs(income_statement_data["net_income"]))
            if income_statement_data["net_income"] >= 0:
                st.info(f"{t('net_income_info')} {income} {t('has_been_included_in_passive')}")
            else:
                st.warning(f"{t('net_loss_warning')} {income} {t('has_been_included_in_passive')}")
