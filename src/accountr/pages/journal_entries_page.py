"""
Journal Entries page for navigation.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from accountr.database import Account, JournalEntry
from accountr.accounting_utils import validate_journal_entry
from accountr.translation_utils import t
from accountr.helpers import has_sufficient_accounts, format_currency
from accountr.pages.base_page import BasePage


@st.dialog(t("edit_entry"))
def show_edit_dialog(session, entry_id):
    """Show edit entry dialog."""
    entry = session.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
    if not entry:
        st.error(t("entry_not_found"))
        return

    # Get all active accounts for dropdowns
    all_accounts = session.query(Account).filter(Account.is_active).order_by(Account.account_code).all()
    account_options = {f"{acc.account_code} - {acc.account_name}": acc.id for acc in all_accounts}
    account_list = list(account_options.keys())

    # Find current selections
    current_debit_label = f"{entry.debit_account.account_code} - {entry.debit_account.account_name}"
    current_credit_label = f"{entry.credit_account.account_code} - {entry.credit_account.account_name}"

    # Form fields
    try:
        edit_date = st.date_input(t("date"), value=entry.date.date())
    except Exception:
        # Handle invalid date gracefully
        edit_date = st.date_input(t("date"), value=date.today())
    edit_description = st.text_input(t("description"), value=entry.description)

    edit_debit_index = account_list.index(current_debit_label) if current_debit_label in account_list else 0
    edit_debit_account = st.selectbox(t("debit_account"), account_list, index=edit_debit_index)

    edit_credit_index = account_list.index(current_credit_label) if current_credit_label in account_list else 0
    edit_credit_account = st.selectbox(t("credit_account"), account_list, index=edit_credit_index)

    edit_amount = st.number_input(t("amount"), min_value=0.01, step=0.01, format="%.2f", value=float(entry.amount))

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button(t("update_entry"), width="stretch", type="primary"):
            if edit_description and edit_amount > 0:
                edit_debit_account_id = account_options[edit_debit_account]
                edit_credit_account_id = account_options[edit_credit_account]

                is_valid, errors = validate_journal_entry(edit_debit_account_id, edit_credit_account_id, edit_amount)

                if is_valid:
                    entry.date = datetime.combine(edit_date, datetime.min.time())
                    entry.description = edit_description
                    entry.debit_account_id = edit_debit_account_id
                    entry.credit_account_id = edit_credit_account_id
                    entry.amount = edit_amount
                    session.commit()
                    st.success(t("entry_updated"))
                    st.rerun()
                else:
                    for error in errors:
                        st.error(error)
            else:
                st.error(t("invalid_entry"))

    with col2:
        if st.button(t("cancel"), width="stretch"):
            st.rerun()


@st.dialog(t("confirm_delete"))
def show_delete_dialog(session, entry_id):
    """Show delete confirmation dialog."""
    entry = session.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
    if not entry:
        st.error(t("entry_not_found"))
        return

    st.write(f"**{t('entry')}:** {entry.id} - {entry.date.strftime('%Y-%m-%d')} - {entry.description}")
    st.write(f"**{t('amount')}:** {format_currency(entry.amount)}")
    st.warning(t("confirm_delete_message"))

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button(t("confirm_delete"), width="stretch", type="primary"):
            session.delete(entry)
            session.commit()
            st.success(t("entry_deleted"))
            st.rerun()

    with col2:
        if st.button(t("cancel"), width="stretch"):
            st.rerun()


@st.dialog(t("add_new_journal_entry"))
def show_add_entry_dialog(session):
    """Show add new entry dialog."""
    # Get active accounts for dropdowns
    active_accounts = session.query(Account).filter(Account.is_active).order_by(Account.account_code).all()

    if not has_sufficient_accounts(len(active_accounts)):
        st.warning(t("need_two_accounts"))
        return

    account_options = {f"{acc.account_code} - {acc.account_name}": acc.id for acc in active_accounts}
    account_list = list(account_options.keys())

    # Form fields
    entry_date = st.date_input(t("date"), value=date.today())
    description = st.text_input(t("description"), help="Brief description of the transaction")
    debit_account = st.selectbox(t("debit_account"), account_list)
    credit_account = st.selectbox(t("credit_account"), account_list)
    amount = st.number_input(t("amount"), min_value=0.01, step=0.01, format="%.2f", help=t("amount_help"))

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button(t("add_entry"), width="stretch", type="primary"):
            if description and amount > 0:
                debit_account_id = account_options[debit_account]
                credit_account_id = account_options[credit_account]

                is_valid, errors = validate_journal_entry(debit_account_id, credit_account_id, amount)

                if is_valid:
                    new_entry = JournalEntry(
                        date=datetime.combine(entry_date, datetime.min.time()),
                        description=description,
                        debit_account_id=debit_account_id,
                        credit_account_id=credit_account_id,
                        amount=amount,
                    )
                    session.add(new_entry)
                    session.commit()
                    st.success(t("journal_entry_added"))
                    st.rerun()
                else:
                    for error in errors:
                        st.error(error)
            else:
                st.error(t("invalid_entry"))

    with col2:
        if st.button(t("cancel"), width="stretch"):
            st.rerun()


class JournalEntriesPage(BasePage):
    """Journal Entries Page."""

    def __init__(self):
        super().__init__(title="journal_entries", icon="📝")

    def content(self, session):
        # Display existing journal entries
        try:
            entries = session.query(JournalEntry).order_by(JournalEntry.date.desc()).limit(20).all()
        except Exception as e:
            st.error(f"{t('error_loading_entries')}: {str(e)}")
            entries = []

        st.subheader(t("edit_journal_entries"))
        edit_col, add_col = st.columns([2, 1], vertical_alignment="bottom")

        with add_col:
            if st.button(t("add_new_journal_entry"), type="primary", width="stretch"):
                show_add_entry_dialog(session)

        if entries:
            with edit_col:
                # Create entry selection dropdown
                entry_options = {}
                for entry in entries:
                    try:
                        entry_label = f"{entry.id} - {entry.date.strftime('%Y-%m-%d')} - {entry.description}"
                        entry_options[entry_label] = entry.id
                    except Exception:
                        # Handle datetime formatting errors gracefully
                        entry_label = f"{entry.id} - [Invalid Date] - {entry.description}"
                        entry_options[entry_label] = entry.id

                if entry_options:
                    selected_entry_label = st.selectbox(t("select_entry_to_modify"), list(entry_options.keys()))

                    if selected_entry_label:
                        selected_entry_id = entry_options[selected_entry_label]

                        # Edit and Delete buttons
                        edit_col, delete_col = st.columns(2)

                        with edit_col:
                            if st.button(t("edit_entry"), width="stretch"):
                                show_edit_dialog(session, selected_entry_id)

                        with delete_col:
                            if st.button(
                                t("delete_entry"),
                                type="secondary",
                                width="stretch",
                            ):
                                show_delete_dialog(session, selected_entry_id)

            st.markdown("---")
            st.subheader(t("recent_journal_entries"))
            entry_data = []
            for entry in entries:
                try:
                    entry_data.append(
                        {
                            "id": entry.id,
                            t("date"): entry.date.strftime("%Y-%m-%d"),
                            t("description"): entry.description,
                            t(
                                "debit_account"
                            ): f"{entry.debit_account.account_code} - {entry.debit_account.account_name}",
                            t(
                                "credit_account"
                            ): f"{entry.credit_account.account_code} - {entry.credit_account.account_name}",
                            t("amount"): format_currency(entry.amount),
                        }
                    )
                except Exception:
                    # Handle any display errors gracefully
                    entry_data.append(
                        {
                            "id": entry.id,
                            t("date"): "[Invalid Date]",
                            t("description"): entry.description,
                            t("debit_account"): "[Error loading account]",
                            t("credit_account"): "[Error loading account]",
                            t("amount"): format_currency(entry.amount),
                        }
                    )

            if entry_data:
                df = pd.DataFrame(entry_data).set_index("id")
                st.dataframe(df, width="stretch")
