"""
Journal Entries tab functionality.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from database import Account, JournalEntry
from accounting_utils import validate_journal_entry
from translation_utils import t


def manage_journal_entries(db_manager):
    """Tab for managing journal entries."""
    st.header(t("journal_entries"))

    session = db_manager.get_session()

    # Display existing journal entries
    entries = (
        session.query(JournalEntry).order_by(JournalEntry.date.desc()).limit(20).all()
    )

    if entries:
        st.subheader(t("recent_journal_entries"))
        entry_data = []
        for entry in entries:
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
                    t("amount"): f"CHF {entry.amount:,.2f}",
                }
            )

        df = pd.DataFrame(entry_data).set_index("id")
        st.dataframe(df, width="stretch")
        
        # Edit/Delete section
        st.markdown("---")
        st.subheader(t("edit_journal_entries"))
        
        # Create entry selection dropdown
        entry_options = {}
        for entry in entries:
            entry_label = f"{entry.id} - {entry.date.strftime('%Y-%m-%d')} - {entry.description}"
            entry_options[entry_label] = entry.id
        
        if entry_options:
            selected_entry_label = st.selectbox(
                t("select_entry_to_modify"),
                list(entry_options.keys())
            )
            
            if selected_entry_label:
                selected_entry_id = entry_options[selected_entry_label]
                selected_entry = session.query(JournalEntry).filter(JournalEntry.id == selected_entry_id).first()
                
                if selected_entry:
                    # Edit and Delete buttons
                    edit_col, delete_col = st.columns([1, 1])
                    
                    with edit_col:
                        if st.button(t("edit_entry"), use_container_width=True):
                            st.session_state.editing_entry_id = selected_entry_id
                            st.rerun()
                    
                    with delete_col:
                        if st.button(t("delete_entry"), type="secondary", use_container_width=True):
                            st.session_state.deleting_entry_id = selected_entry_id
                            st.rerun()
                    
                    # Handle edit mode
                    if hasattr(st.session_state, 'editing_entry_id') and st.session_state.editing_entry_id == selected_entry_id:
                        st.markdown("---")
                        st.subheader(f"{t('edit_entry')}: {selected_entry_label}")
                        
                        # Get all active accounts for dropdowns
                        all_accounts = session.query(Account).filter(Account.is_active == True).order_by(Account.account_code).all()
                        account_options_edit = {f"{acc.account_code} - {acc.account_name}": acc.id for acc in all_accounts}
                        account_list_edit = list(account_options_edit.keys())
                        
                        # Find current selections
                        current_debit_label = f"{selected_entry.debit_account.account_code} - {selected_entry.debit_account.account_name}"
                        current_credit_label = f"{selected_entry.credit_account.account_code} - {selected_entry.credit_account.account_name}"
                        
                        edit_col1, edit_col2, edit_col3, edit_col4, edit_col5, edit_col6 = st.columns(6, vertical_alignment="bottom")
                        
                        with edit_col1:
                            edit_date = st.date_input(t("date"), value=selected_entry.date.date(), key="edit_date")
                        with edit_col2:
                            edit_description = st.text_input(t("description"), value=selected_entry.description, key="edit_description")
                        with edit_col3:
                            edit_debit_index = account_list_edit.index(current_debit_label) if current_debit_label in account_list_edit else 0
                            edit_debit_account = st.selectbox(t("debit_account"), account_list_edit, index=edit_debit_index, key="edit_debit")
                        with edit_col4:
                            edit_credit_index = account_list_edit.index(current_credit_label) if current_credit_label in account_list_edit else 0
                            edit_credit_account = st.selectbox(t("credit_account"), account_list_edit, index=edit_credit_index, key="edit_credit")
                        with edit_col5:
                            edit_amount = st.number_input(t("amount"), min_value=0.01, step=0.01, format="%.2f", value=float(selected_entry.amount), key="edit_amount")
                        with edit_col6:
                            if st.button(t("update_entry"),  use_container_width=True):
                                if edit_description and edit_amount > 0:
                                    edit_debit_account_id = account_options_edit[edit_debit_account]
                                    edit_credit_account_id = account_options_edit[edit_credit_account]
                                    
                                    is_valid, errors = validate_journal_entry(edit_debit_account_id, edit_credit_account_id, edit_amount)
                                    
                                    if is_valid:
                                        selected_entry.date = datetime.combine(edit_date, datetime.min.time())
                                        selected_entry.description = edit_description
                                        selected_entry.debit_account_id = edit_debit_account_id
                                        selected_entry.credit_account_id = edit_credit_account_id
                                        selected_entry.amount = edit_amount
                                        session.commit()
                                        st.success(t("entry_updated"))
                                        del st.session_state.editing_entry_id
                                        st.rerun()
                                    else:
                                        for error in errors:
                                            st.error(error)
                                else:
                                    st.error(t("invalid_entry"))
                        
                        # Cancel edit button
                        if st.button("Cancel", type="secondary"):
                            del st.session_state.editing_entry_id
                            st.rerun()
                    
                    # Handle delete confirmation
                    if hasattr(st.session_state, 'deleting_entry_id') and st.session_state.deleting_entry_id == selected_entry_id:
                        st.warning(t("confirm_delete"))
                        confirm_col, cancel_col = st.columns([1, 1])
                        
                        with confirm_col:
                            if st.button("Confirm Delete", type="primary", use_container_width=True):
                                session.delete(selected_entry)
                                session.commit()
                                st.success(t("entry_deleted"))
                                del st.session_state.deleting_entry_id
                                st.rerun()
                        
                        with cancel_col:
                            if st.button("Cancel Delete", type="secondary",  use_container_width=True):
                                del st.session_state.deleting_entry_id
                                st.rerun()

    st.subheader(t("add_new_journal_entry"))

    # Get active accounts for dropdowns
    active_accounts = (
        session.query(Account)
        .filter(Account.is_active)
        .order_by(Account.account_code)
        .all()
    )

    if len(active_accounts) < 2:
        st.warning(t("need_two_accounts"))
        session.close()
        return

    account_options = {
        f"{acc.account_code} - {acc.account_name}": acc.id for acc in active_accounts
    }
    account_list = list(account_options.keys())

    col1, col2, col3, col4, col5, col6 = st.columns(6, vertical_alignment="bottom")

    with col1:
        entry_date = st.date_input(t("date"), value=date.today())
    with col2:
        description = st.text_input(
            t("description"), help="Brief description of the transaction"
        )
    with col3:
        debit_account = st.selectbox(t("debit_account"), account_list)
    with col4:
        credit_account = st.selectbox(t("credit_account"), account_list)
    with col5:
        amount = st.number_input(
            t("amount"), min_value=0.01, step=0.01, format="%.2f", help=t("amount_help")
        )
    with col6:
        if st.button(t("add_entry"), use_container_width=True):
            if description and amount > 0:
                debit_account_id = account_options[debit_account]
                credit_account_id = account_options[credit_account]

                is_valid, errors = validate_journal_entry(
                    debit_account_id, credit_account_id, amount
                )

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

    session.close()
