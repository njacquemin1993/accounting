"""
Chart of Accounts page for navigation.
"""

import streamlit as st
import pandas as pd
from accountr.database import Account, JournalEntry
from accountr.translation_utils import t
from accountr.helpers import (
    validate_account_code,
    get_category_display_map,
    get_reverse_category_map,
    is_balance_sheet_category,
    format_currency,
)
from accountr.pages.base_page import BasePage


@st.dialog(t("edit_account"))
def show_edit_account_dialog(session, account_id):
    """Show edit account dialog."""
    account = session.query(Account).filter(Account.id == account_id).first()
    if not account:
        st.error(t("account_not_found"))
        return

    # Form fields with current values
    edit_code = st.text_input(t("account_code"), value=account.account_code, help=t("account_code_help"))
    edit_name = st.text_input(t("account_name"), value=account.account_name, help=t("account_name_help"))

    # Category selection with current value
    category_map = get_category_display_map()
    categories = list(category_map.values())

    current_category_translated = category_map.get(account.category, t("active"))
    current_index = categories.index(current_category_translated) if current_category_translated in categories else 0

    edit_category = st.selectbox(t("category"), categories, index=current_index)

    # Map translated category back to English for validation
    reverse_category_map = get_reverse_category_map()
    db_category = reverse_category_map.get(edit_category, "Active")

    # Show balance field only for Active and Passive accounts
    edit_balance = 0.0
    if is_balance_sheet_category(db_category):
        current_balance = account.balance if hasattr(account, "balance") else 0.0
        edit_balance = st.number_input(
            t("balance"),
            min_value=0.0,
            step=0.01,
            format="%.2f",
            value=float(current_balance),
            help=t("initial_balance_help"),
        )

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button(t("update_account"), width="stretch", type="primary"):
            if edit_code and edit_name:
                # Validate account code for the category
                is_valid, validation_error = validate_account_code(edit_code, db_category, t)
                if not is_valid:
                    st.error(validation_error)
                    return

                # Check if account code already exists (excluding current account)
                existing = (
                    session.query(Account).filter(Account.account_code == edit_code, Account.id != account_id).first()
                )
                if existing:
                    st.error(t("account_exists"))
                else:
                    account.account_code = edit_code
                    account.account_name = edit_name
                    account.category = db_category
                    # Update balance for Active/Passive accounts
                    if is_balance_sheet_category(db_category):
                        account.balance = edit_balance
                    else:
                        account.balance = 0.0
                    session.commit()
                    st.success(t("account_updated"))
                    st.rerun()
            else:
                st.error(t("fill_all_fields"))

    with col2:
        if st.button(t("cancel"), width="stretch"):
            st.rerun()


@st.dialog(t("confirm_delete"))
def show_delete_account_dialog(session, account_id):
    """Show delete account confirmation dialog."""
    account = session.query(Account).filter(Account.id == account_id).first()
    if not account:
        st.error(t("account_not_found"))
        return

    # Check if account has any journal entries
    entries_count = (
        session.query(JournalEntry)
        .filter((JournalEntry.debit_account_id == account_id) | (JournalEntry.credit_account_id == account_id))
        .count()
    )

    st.write(f"**{t('code')}:** {account.account_code}")
    st.write(f"**{t('name')}:** {account.account_name}")
    st.write(f"**{t('category')}:** {account.category}")

    if entries_count > 0:
        st.warning(f"{t('account_has_entries')}: {entries_count}")
        st.info(t("deactivate_instead_of_delete"))

        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.button(t("deactivate_account"), width="stretch", type="primary"):
                account.is_active = False
                session.commit()
                st.success(t("account_deactivated_success"))
                st.rerun()

        with col2:
            if st.button(t("force_delete"), width="stretch", type="secondary"):
                st.warning(t("force_delete_warning"))
                if st.button(t("confirm_force_delete"), width="stretch"):
                    session.delete(account)
                    session.commit()
                    st.success(t("account_deleted"))
                    st.rerun()

        with col3:
            if st.button(t("cancel"), width="stretch"):
                st.rerun()
    else:
        st.warning(t("confirm_delete_message"))

        col1, col2 = st.columns([1, 1])

        with col1:
            if st.button(t("confirm_delete"), width="stretch", type="primary"):
                session.delete(account)
                session.commit()
                st.success(t("account_deleted"))
                st.rerun()

        with col2:
            if st.button(t("cancel"), width="stretch"):
                st.rerun()


@st.dialog(t("add_new_account"))
def show_add_account_dialog(session):
    """Show add new account dialog."""
    # Form fields
    account_code = st.text_input(t("account_code"), help=t("account_code_help"))
    account_name = st.text_input(t("account_name"), help=t("account_name_help"))
    category = st.selectbox(t("category"), [t("active"), t("passive"), t("expenses"), t("products")])

    # Map translated category back to English for validation
    category_map = {
        t("active"): "Active",
        t("passive"): "Passive",
        t("expenses"): "Expenses",
        t("products"): "Products",
    }
    db_category = category_map.get(category, "Active")

    # Show balance field only for Active and Passive accounts
    balance = 0.0
    if db_category in ["Active", "Passive"]:
        balance = st.number_input(
            t("initial_balance"),
            min_value=0.0,
            step=0.01,
            format="%.2f",
            help=t("initial_balance_help"),
        )

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button(t("add_account"), width="stretch", type="primary"):
            if account_code and account_name:
                # Validate account code for the category
                is_valid, validation_error = validate_account_code(account_code, db_category)
                if not is_valid:
                    st.error(validation_error)
                    return

                # Check if account code already exists
                existing = session.query(Account).filter(Account.account_code == account_code).first()
                if existing:
                    st.error(t("account_exists"))
                else:
                    new_account = Account(
                        account_code=account_code,
                        account_name=account_name,
                        category=db_category,
                        balance=balance,
                    )
                    session.add(new_account)
                    session.commit()
                    st.success(t("account_added"))
                    st.rerun()
            else:
                st.error(t("fill_all_fields"))

    with col2:
        if st.button(t("cancel"), width="stretch"):
            st.rerun()


class ChartOfAccountsPage(BasePage):
    def __init__(self):
        super().__init__(title="chart_of_accounts", icon="📊")

    def content(self, session):
        # Account management section
        st.subheader(t("manage_accounts"))
        manage_col, add_col = st.columns([2, 1], vertical_alignment="bottom")

        # Get active accounts for management
        accounts = session.query(Account).filter(Account.is_active).order_by(Account.account_code).all()

        with add_col:
            if st.button(t("add_new_account"), type="primary", width="stretch"):
                show_add_account_dialog(session)

        if accounts:
            with manage_col:
                # Create account selection dropdown
                account_options = {}
                for account in accounts:
                    account_label = f"{account.account_code} - {account.account_name}"
                    account_options[account_label] = account.id

                if account_options:
                    selected_account_label = st.selectbox(t("select_account_to_modify"), list(account_options.keys()))

                    if selected_account_label:
                        selected_account_id = account_options[selected_account_label]

                        # Edit and Delete buttons
                        edit_col, delete_col = st.columns(2)

                        with edit_col:
                            if st.button(t("edit_account"), width="stretch"):
                                show_edit_account_dialog(session, selected_account_id)

                        with delete_col:
                            if st.button(
                                t("delete_account"),
                                type="secondary",
                                width="stretch",
                            ):
                                show_delete_account_dialog(session, selected_account_id)

        st.markdown("---")

        # Display existing accounts in 2x2 layout
        accounts = session.query(Account).filter(Account.is_active).order_by(Account.account_code).all()

        if accounts:
            # Group accounts by category
            accounts_by_category = {
                "Active": [],
                "Passive": [],
                "Expenses": [],
                "Products": [],
            }

            for account in accounts:
                if account.category in accounts_by_category:
                    accounts_by_category[account.category].append(account)

            # Calculate table heights to align them
            active_rows = (
                len(accounts_by_category["Active"]) if accounts_by_category["Active"] else 1
            )  # 1 for empty message
            passive_rows = len(accounts_by_category["Passive"]) if accounts_by_category["Passive"] else 1
            products_rows = len(accounts_by_category["Products"]) if accounts_by_category["Products"] else 1
            expenses_rows = len(accounts_by_category["Expenses"]) if accounts_by_category["Expenses"] else 1

            # Create 2x2 layout
            col1, col2 = st.columns(2)

            with col1:
                # Active accounts
                st.subheader(f"📈 {t('active')}")
                if accounts_by_category["Active"]:
                    active_data = []
                    for account in accounts_by_category["Active"]:
                        active_data.append(
                            {
                                t("code"): account.account_code,
                                t("name"): account.account_name,
                                t("balance"): format_currency(account.balance)
                                if hasattr(account, "balance")
                                else format_currency(0.0),
                            }
                        )

                    # Add blank lines if active table is shorter than passive
                    if active_rows < passive_rows:
                        blank_lines_needed = passive_rows - active_rows
                        for _ in range(blank_lines_needed):
                            active_data.append(
                                {
                                    t("code"): "",
                                    t("name"): "",
                                    t("balance"): "",
                                }
                            )

                    active_df = pd.DataFrame(active_data)
                    st.table(active_df)
                else:
                    # Show empty message and add blank lines if needed
                    st.write(t("no_active_accounts_display"))
                    if passive_rows > 1:
                        # Create empty DataFrame with blank lines to match passive height
                        empty_data = []
                        for _ in range(passive_rows - 1):
                            empty_data.append(
                                {
                                    t("code"): "",
                                    t("name"): "",
                                    t("balance"): "",
                                }
                            )
                        if empty_data:
                            empty_df = pd.DataFrame(empty_data)
                            st.table(empty_df)

                st.markdown("---")

                # Products accounts
                st.subheader(f"💰 {t('products')}")
                if accounts_by_category["Products"]:
                    products_data = []
                    for account in accounts_by_category["Products"]:
                        products_data.append(
                            {
                                t("code"): account.account_code,
                                t("name"): account.account_name,
                            }
                        )

                    # Add blank lines if products table is shorter than expenses
                    if products_rows < expenses_rows:
                        blank_lines_needed = expenses_rows - products_rows
                        for _ in range(blank_lines_needed):
                            products_data.append(
                                {
                                    t("code"): "",
                                    t("name"): "",
                                }
                            )

                    products_df = pd.DataFrame(products_data)
                    st.table(products_df)
                else:
                    # Show empty message and add blank lines if needed
                    st.write(t("no_products_display"))
                    if expenses_rows > 1:
                        # Create empty DataFrame with blank lines to match expenses height
                        empty_data = []
                        for _ in range(expenses_rows - 1):
                            empty_data.append(
                                {
                                    t("code"): "",
                                    t("name"): "",
                                }
                            )
                        if empty_data:
                            empty_df = pd.DataFrame(empty_data)
                            st.table(empty_df)

            with col2:
                # Passive accounts
                st.subheader(f"📉 {t('passive')}")
                if accounts_by_category["Passive"]:
                    passive_data = []
                    for account in accounts_by_category["Passive"]:
                        passive_data.append(
                            {
                                t("code"): account.account_code,
                                t("name"): account.account_name,
                                t("balance"): format_currency(account.balance)
                                if hasattr(account, "balance")
                                else format_currency(0.0),
                            }
                        )

                    # Add blank lines if passive table is shorter than active
                    if passive_rows < active_rows:
                        blank_lines_needed = active_rows - passive_rows
                        for _ in range(blank_lines_needed):
                            passive_data.append(
                                {
                                    t("code"): "",
                                    t("name"): "",
                                    t("balance"): "",
                                }
                            )

                    passive_df = pd.DataFrame(passive_data)
                    st.table(passive_df)
                else:
                    # Show empty message and add blank lines if needed
                    st.write(t("no_passive_accounts_display"))
                    if active_rows > 1:
                        # Create empty DataFrame with blank lines to match active height
                        empty_data = []
                        for _ in range(active_rows - 1):
                            empty_data.append(
                                {
                                    t("code"): "",
                                    t("name"): "",
                                    t("balance"): "",
                                }
                            )
                        if empty_data:
                            empty_df = pd.DataFrame(empty_data)
                            st.table(empty_df)

                st.markdown("---")

                # Expenses accounts
                st.subheader(f"💸 {t('expenses')}")
                if accounts_by_category["Expenses"]:
                    expenses_data = []
                    for account in accounts_by_category["Expenses"]:
                        expenses_data.append(
                            {
                                t("code"): account.account_code,
                                t("name"): account.account_name,
                            }
                        )

                    # Add blank lines if expenses table is shorter than products
                    if expenses_rows < products_rows:
                        blank_lines_needed = products_rows - expenses_rows
                        for _ in range(blank_lines_needed):
                            expenses_data.append(
                                {
                                    t("code"): "",
                                    t("name"): "",
                                }
                            )

                    expenses_df = pd.DataFrame(expenses_data)
                    st.table(expenses_df)
                else:
                    # Show empty message and add blank lines if needed
                    st.write(t("no_expenses_display"))
                    if products_rows > 1:
                        # Create empty DataFrame with blank lines to match products height
                        empty_data = []
                        for _ in range(products_rows - 1):
                            empty_data.append(
                                {
                                    t("code"): "",
                                    t("name"): "",
                                }
                            )
                        if empty_data:
                            empty_df = pd.DataFrame(empty_data)
                            st.table(empty_df)

        else:
            st.info(t("no_accounts_found"))
