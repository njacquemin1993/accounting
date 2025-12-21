"""
File management UI components for the accounting application.
"""

import streamlit as st
import pandas as pd
import io
import zipfile
from datetime import datetime
from file_manager import FileManager
from database import DatabaseManager, Account, JournalEntry
from accounting_utils import (
    get_income_statement_data,
    get_balance_sheet_data,
    get_account_balance,
)
from translation_utils import t
from helpers import format_currency
from excel_utils import create_excel_formats
from excel_export import (
    export_journal_entries_sheet,
    export_account_detail_sheet,
    export_result_sheet,
    export_balance_sheet,
)


def create_excel_export():
    """Create Excel file with multiple tabs for accounting data export."""
    try:
        # Initialize database
        db_manager = DatabaseManager()
        session = db_manager.get_session()

        # Create Excel writer object in memory
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine="xlsxwriter")
        workbook = writer.book

        # Define formats using utility
        formats = create_excel_formats(workbook)

        # 1. Journal Entries Tab
        export_journal_entries_sheet(writer, session, formats, t)

        # 2. Individual Account Details (one tab per account)
        accounts = (
            session.query(Account)
            .filter(Account.is_active)
            .order_by(Account.account_code)
            .all()
        )
        for account in accounts:
            export_account_detail_sheet(writer, session, account, formats, t)

        # 3. Result Sheet (Income Statement)
        income_data = get_income_statement_data(session)
        export_result_sheet(writer, workbook, income_data, formats, t)

        # 4. Balance Sheet (including net income)
        balance_data = get_balance_sheet_data(session)
        net_income = income_data.get("net_income", 0)
        export_balance_sheet(writer, workbook, balance_data, net_income, formats, t)

        # Close the writer and get the data
        writer.close()
        session.close()
        db_manager.dispose()

        output.seek(0)
        return output.getvalue()

    except Exception as e:
        print(f"Error creating Excel export: {e}")
        return None


def create_year_end_closing_package(retained_earnings_account_id):
    """Create year-end closing package with backup and Excel export."""
    try:
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 1. Create database backup
        file_manager = FileManager()
        db_backup_data = file_manager.get_download_data()

        # 2. Create Excel export
        excel_data = create_excel_export()

        if not db_backup_data or not excel_data:
            return None, None, None

        # 3. Create ZIP package
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            # Add database backup
            zip_file.writestr(f"backup_{timestamp}.db", db_backup_data)
            # Add Excel export
            zip_file.writestr(f"export_{timestamp}.xlsx", excel_data)

        zip_buffer.seek(0)

        return zip_buffer.getvalue(), db_backup_data, excel_data

    except Exception as e:
        print(f"Error creating year-end closing package: {e}")
        return None, None, None


def perform_year_end_closing(retained_earnings_account_id):
    """Perform the year-end closing process."""
    try:
        db_manager = DatabaseManager()
        session = db_manager.get_session()

        # Get retained earnings account
        retained_earnings_account = (
            session.query(Account)
            .filter(Account.id == retained_earnings_account_id, Account.is_active)
            .first()
        )

        if (
            not retained_earnings_account
            or retained_earnings_account.category != "Passive"
        ):
            return False, "Selected account is not a valid passive account"

        # Get current net income
        income_data = get_income_statement_data(session)
        net_income = income_data.get("net_income", 0)

        # 1. Transfer net result to retained earnings account
        if net_income != 0:
            current_balance = getattr(retained_earnings_account, "balance", 0.0)
            new_balance = current_balance + net_income
            retained_earnings_account.balance = new_balance

        # 2. Update all Active and Passive accounts with their current balances
        active_passive_accounts = (
            session.query(Account)
            .filter(Account.category.in_(["Active", "Passive"]), Account.is_active)
            .all()
        )

        for account in active_passive_accounts:
            current_balance = get_account_balance(session, account.id)
            account.balance = current_balance

        # 3. Remove all journal entries
        session.query(JournalEntry).delete()

        # Commit all changes
        session.commit()
        session.close()
        db_manager.dispose()

        return True, "Year-end closing completed successfully"

    except Exception as e:
        session.rollback()
        session.close()
        db_manager.dispose()
        return False, f"Error during year-end closing: {str(e)}"


@st.dialog(t("file_management"), width="large")
def show_file_management_dialog():
    """Show file management dialog."""
    file_manager = FileManager()

    # Current database info
    st.subheader(t("current_database"))
    db_info = file_manager.get_database_info()

    if db_info:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(t("accounts"), db_info["accounts"])
        with col2:
            st.metric(
                t("entries_for").replace(" for", ""), db_info["entries"]
            )  # Use entries translation
        with col3:
            size_mb = db_info["size"] / (1024 * 1024)
            st.metric(t("size"), f"{size_mb:.2f} MB")

        st.write(
            f"**{t('last_modified')}:** {db_info['modified'].strftime('%Y-%m-%d %H:%M:%S')}"
        )

    st.markdown("---")

    # File operations
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            t("create_new_database"),
            t("load_from_computer"),
            t("download_database"),
            t("export_as_excel"),
            t("bouclement"),
        ]
    )

    with tab1:
        st.warning(t("confirm_new_database"))
        if st.button(t("create_new_database"), type="primary", key="create_new"):
            # Clear all cached database connections first
            # Clear all session state that might contain database objects
            keys_to_clear = []
            for key in st.session_state.keys():
                if "database" in key.lower() or "session" in key.lower():
                    keys_to_clear.append(key)

            for key in keys_to_clear:
                del st.session_state[key]

            # Force garbage collection to close any remaining connections
            import gc

            gc.collect()

            if file_manager.create_new_database():
                st.success(t("database_created"))
                st.rerun()
            else:
                st.error(t("database_error"))

    with tab2:
        st.info(t("select_database_file"))
        uploaded_file = st.file_uploader(
            t("select_database_file"),
            type=["db", "sqlite", "sqlite3"],
            label_visibility="collapsed",
        )

        if uploaded_file is not None:
            st.warning(t("confirm_load_database"))
            if st.button(t("load_from_computer"), type="primary", key="load_computer"):
                # Clear all cached database connections first
                keys_to_clear = []
                for key in st.session_state.keys():
                    if "database" in key.lower() or "session" in key.lower():
                        keys_to_clear.append(key)

                for key in keys_to_clear:
                    del st.session_state[key]

                # Force garbage collection
                import gc

                gc.collect()

                if file_manager.load_database_from_file(uploaded_file):
                    st.success(t("database_loaded"))
                    st.rerun()
                else:
                    st.error(t("invalid_database_file"))

    with tab3:
        st.info(t("download_info"))

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"accounting_backup_{timestamp}.db"

        # Get database data
        db_data = file_manager.get_download_data()

        if db_data:
            st.download_button(
                label=t("download_database"),
                data=db_data,
                file_name=filename,
                mime="application/octet-stream",
                type="primary",
                use_container_width=True,
            )
        else:
            st.error(t("database_error"))

    with tab4:
        st.info(t("export_excel_info"))

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"accounting_export_{timestamp}.xlsx"

        # Create Excel export
        if st.button(
            t("export_as_excel"),
            type="primary",
            key="export_excel",
            use_container_width=True,
        ):
            try:
                excel_data = create_excel_export()
                if excel_data:
                    st.download_button(
                        label=t("download_excel_file"),
                        data=excel_data,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="secondary",
                        use_container_width=True,
                    )
                else:
                    st.error(t("export_error"))
            except Exception as e:
                st.error(f"{t('export_error')}: {str(e)}")

    with tab5:
        st.warning(t("year_end_closing_info"))
        st.error(t("warning_year_end_closing"))

        # Get passive accounts for selection
        db_manager = DatabaseManager()
        session = db_manager.get_session()

        passive_accounts = (
            session.query(Account)
            .filter(Account.category == "Passive", Account.is_active)
            .order_by(Account.account_code)
            .all()
        )

        session.close()
        db_manager.dispose()

        if not passive_accounts:
            st.error(
                "No passive accounts available. Create at least one passive account before year-end closing."
            )
        else:
            # Account selection
            account_options = [
                f"{acc.account_code} - {acc.account_name}" for acc in passive_accounts
            ]
            selected_account_idx = st.selectbox(
                t("select_retained_earnings_account"),
                range(len(account_options)),
                format_func=lambda x: account_options[x],
                help=t("retained_earnings_account_help"),
            )

            if selected_account_idx is not None:
                selected_account = passive_accounts[selected_account_idx]

                # Show year-end steps
                with st.expander(t("year_end_steps"), expanded=True):
                    st.write(f"• {t('step_backup')}")
                    st.write(f"• {t('step_excel')}")
                    st.write(f"• {t('step_transfer')}")
                    st.write(f"• {t('step_update')}")
                    st.write(f"• {t('step_clear')}")

                # Show current net income
                db_manager = DatabaseManager()
                session = db_manager.get_session()
                income_data = get_income_statement_data(session)
                net_income = income_data.get("net_income", 0)
                session.close()
                db_manager.dispose()

                if net_income > 0:
                    st.success(f"📈 {t('net_income')}: {format_currency(net_income)}")
                elif net_income < 0:
                    st.error(f"📉 {t('net_loss')}: {format_currency(abs(net_income))}")
                else:
                    st.info(f"➖ {t('net_income')}: {format_currency(0.0)}")

                st.write(
                    f"**{t('net_result_transfer')}:** {selected_account.account_code} - {selected_account.account_name}"
                )

                # Confirmation checkbox
                confirm = st.checkbox(t("confirm_year_end_closing"))

                # Year-end closing button
                if st.button(
                    t("start_year_end_closing"),
                    type="primary",
                    disabled=not confirm,
                    use_container_width=True,
                ):
                    # Create progress tracking
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    try:
                        # Step 1: Create backup and Excel export
                        status_text.text(t("step_backup"))
                        progress_bar.progress(20)

                        zip_data, backup_data, excel_data = (
                            create_year_end_closing_package(selected_account.id)
                        )

                        if not zip_data:
                            st.error(
                                t("year_end_closing_error")
                                + " Failed to create backup package"
                            )
                            return

                        progress_bar.progress(40)

                        # Step 2: Perform year-end closing
                        status_text.text(t("updating_balances"))
                        progress_bar.progress(60)

                        success, message = perform_year_end_closing(selected_account.id)

                        if not success:
                            st.error(f"{t('year_end_closing_error')} {message}")
                            return

                        progress_bar.progress(80)
                        status_text.text(t("year_end_process_complete"))
                        progress_bar.progress(100)

                        # Success message
                        st.success(t("year_end_closing_success"))

                        # Download buttons
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.download_button(
                                label=t("download_backup_and_excel"),
                                data=zip_data,
                                file_name=f"year_end_closing_{timestamp}.zip",
                                mime="application/zip",
                                type="secondary",
                                use_container_width=True,
                            )

                        with col2:
                            st.download_button(
                                label=t("download_database"),
                                data=backup_data,
                                file_name=f"backup_{timestamp}.db",
                                mime="application/octet-stream",
                                type="secondary",
                                use_container_width=True,
                            )

                        with col3:
                            st.download_button(
                                label=t("download_excel_file"),
                                data=excel_data,
                                file_name=f"export_{timestamp}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                type="secondary",
                                use_container_width=True,
                            )

                        # Clear session state to refresh the app
                        keys_to_clear = []
                        for key in st.session_state.keys():
                            if "database" in key.lower() or "session" in key.lower():
                                keys_to_clear.append(key)

                        for key in keys_to_clear:
                            del st.session_state[key]

                        # Suggest refresh
                        st.info(
                            "💡 Please refresh the page to see the updated database."
                        )

                    except Exception as e:
                        st.error(f"{t('year_end_closing_error')} {str(e)}")

    # Close button
    st.markdown("---")
    if st.button(t("close"), use_container_width=True):
        st.rerun()


def file_management_button():
    """Display compact file management button."""
    if st.button("📁", help=t("file_management"), use_container_width=True):
        show_file_management_dialog()
