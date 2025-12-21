import streamlit as st
import io
import zipfile
from datetime import datetime
from accountr.database import Account, JournalEntry
from accountr.database_switcher import get_current_db_manager, DatabaseSwitcher
from accountr.accounting_utils import (
    get_income_statement_data,
    get_account_balance,
)
from accountr.translation_utils import t
from accountr.helpers import format_currency
from accountr.excel_export import create_excel_export
from accountr.pages.base_page import BasePage


def create_year_end_closing_package(retained_earnings_account_id):
    """Create year-end closing package with backup and Excel export."""
    try:
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 1. Create database backup
        db_switcher = DatabaseSwitcher()
        db_backup_data = db_switcher.get_download_data()

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
        db_manager = get_current_db_manager()
        session = db_manager.get_session()

        # Get retained earnings account
        retained_earnings_account = (
            session.query(Account).filter(Account.id == retained_earnings_account_id, Account.is_active).first()
        )

        if not retained_earnings_account or retained_earnings_account.category != "Passive":
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
            session.query(Account).filter(Account.category.in_(["Active", "Passive"]), Account.is_active).all()
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


class YearClosingPage(BasePage):
    def __init__(self):
        super().__init__(title="year_end_closing", icon="🔒")

    def content(self, session):
        # Page
        st.warning(t("year_end_closing_info"))
        st.error(t("warning_year_end_closing"))

        passive_accounts = (
            session.query(Account)
            .filter(Account.category == "Passive", Account.is_active)
            .order_by(Account.account_code)
            .all()
        )

        session.close()

        if not passive_accounts:
            st.error("No passive accounts available. Create at least one passive account before year-end closing.")
        else:
            # Account selection
            account_options = [f"{acc.account_code} - {acc.account_name}" for acc in passive_accounts]
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
                db_manager = get_current_db_manager()
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
                    width="stretch",
                ):
                    # Create progress tracking
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    try:
                        # Step 1: Create backup and Excel export
                        status_text.text(t("step_backup"))
                        progress_bar.progress(20)

                        zip_data, backup_data, excel_data = create_year_end_closing_package(selected_account.id)

                        if not zip_data:
                            st.error(t("year_end_closing_error") + " Failed to create backup package")
                            exit()

                        progress_bar.progress(40)

                        # Step 2: Perform year-end closing
                        status_text.text(t("updating_balances"))
                        progress_bar.progress(60)

                        success, message = perform_year_end_closing(selected_account.id)

                        if not success:
                            st.error(f"{t('year_end_closing_error')} {message}")
                            exit()

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
                                width="stretch",
                            )

                        with col2:
                            st.download_button(
                                label=t("download_database"),
                                data=backup_data,
                                file_name=f"backup_{timestamp}.db",
                                mime="application/octet-stream",
                                type="secondary",
                                width="stretch",
                            )

                        with col3:
                            st.download_button(
                                label=t("download_excel_file"),
                                data=excel_data,
                                file_name=f"export_{timestamp}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                type="secondary",
                                width="stretch",
                            )

                        # Clear session state to refresh the app
                        keys_to_clear = []
                        for key in st.session_state.keys():
                            if "database" in key.lower() or "session" in key.lower():
                                keys_to_clear.append(key)

                        for key in keys_to_clear:
                            del st.session_state[key]

                        # Suggest refresh
                        st.info("💡 Please refresh the page to see the updated database.")

                    except Exception as e:
                        st.error(f"{t('year_end_closing_error')} {str(e)}")
