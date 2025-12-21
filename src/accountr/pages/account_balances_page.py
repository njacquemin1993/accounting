"""
Account Balances page for navigation.
"""

import streamlit as st
from accountr.accounting_utils import (
    get_trial_balance,
    get_account_entries,
    get_account_balance,
)
from accountr.translation_utils import t
from accountr.helpers import format_currency
from accountr.pages.base_page import BasePage


@st.dialog(t("account_details"), width="large")
def show_account_details_dialog(session, account_id, account_label):
    """Show account details in a dialog."""
    # Get account entries
    entries_df = get_account_entries(session, account_id)

    if not entries_df.empty:
        # Display account balance
        account_balance = get_account_balance(session, account_id)
        st.metric(t("account_balance"), format_currency(account_balance))

        st.subheader(f"{t('entries_for')} {account_label}")

        # Prepare display dataframe with formatted amount column
        display_df = entries_df.copy()

        # Select and reorder columns for display, then translate headers
        display_df = display_df[["Date", "Description", "Counterparty", "Debit", "Credit"]]
        display_df = display_df.rename(
            columns={
                "Date": t("date"),
                "Description": t("description"),
                "Debit": t("debit"),
                "Credit": t("credit"),
                "Counterparty": t("counterparty"),
            }
        )

        # Display using st.dataframe for scrollable content in dialog
        st.dataframe(display_df, width="stretch")
    else:
        st.info(t("no_entries_found"))

    # Close button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button(t("close"), width="stretch", type="primary"):
            # Clear the selection by setting a session state flag
            st.session_state.clear_selection = True
            st.rerun()


class AccountBalancesPage(BasePage):
    def __init__(self):
        super().__init__(title="account_balances", icon="⚖️")

    def content(self, session):
        # Get trial balance
        trial_balance = get_trial_balance(session)

        if not trial_balance.empty:
            # Create translation mapping for categories
            category_display_map = {
                "Active": t("active"),
                "Passive": t("passive"),
                "Expenses": t("expenses"),
                "Products": t("products"),
            }

            # Get unique categories and translate them
            unique_categories = trial_balance["Category"].unique()
            translated_categories = [category_display_map.get(cat, cat) for cat in unique_categories]

            # Filter options
            category_filter = st.selectbox(t("filter_by_category"), [t("all")] + translated_categories)

            # Apply filters - need to map back to database category if not "All"
            filtered_df = trial_balance.copy()
            if category_filter != t("all"):
                # Find the database category that corresponds to the selected translated category
                db_category = None
                for db_cat, trans_cat in category_display_map.items():
                    if trans_cat == category_filter:
                        db_category = db_cat
                        break
                if db_category:
                    filtered_df = filtered_df[filtered_df["Category"] == db_category]

            # Create a display dataframe without Account ID and with translated categories
            display_df = filtered_df[["Account Code", "Account Name", "Category", "Balance"]].copy()

            # Translate categories in display dataframe
            display_df["Category"] = display_df["Category"].map(category_display_map)

            # Translate column headers
            display_df = display_df.rename(
                columns={
                    "Account Code": t("code"),
                    "Account Name": t("name"),
                    "Category": t("category"),
                    "Balance": t("balance"),
                }
            )

            # Format the balance column
            display_df[t("balance")] = display_df[t("balance")].apply(lambda x: format_currency(x))

            # Check for clear selection flag
            if st.session_state.get("clear_selection", False):
                st.session_state.clear_selection = False
                # Reset the dataframe key to clear selection
                if "account_balances_table" in st.session_state:
                    del st.session_state["account_balances_table"]
                st.rerun()

            # Display the dataframe with selection enabled
            selected_data = st.dataframe(
                display_df,
                width="stretch",
                selection_mode="single-row",
                on_select="rerun",
                key="account_balances_table",
            )

            # Check if a row is selected and show details in popup
            if selected_data.selection.rows:
                selected_row_index = selected_data.selection.rows[0]
                # Get the corresponding account ID from the filtered dataframe
                selected_account_id = filtered_df.iloc[selected_row_index]["Account ID"].tolist()
                selected_account_code = filtered_df.iloc[selected_row_index]["Account Code"]
                selected_account_name = filtered_df.iloc[selected_row_index]["Account Name"]
                selected_account_label = f"{selected_account_code} - {selected_account_name}"

                # Show the account details dialog
                show_account_details_dialog(session, selected_account_id, selected_account_label)

        else:
            st.info(t("no_balances_display"))
