"""
File management UI components for the accounting application.
"""

import streamlit as st
import pandas as pd
import io
from file_manager import FileManager
from database import DatabaseManager, Account, JournalEntry
from accounting_utils import (
    get_income_statement_data,
    get_balance_sheet_data,
    get_account_entries,
)
from datetime import datetime
from translation_utils import t


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

        # Define formats
        header_format = workbook.add_format(
            {
                "bold": True,
                "bg_color": "#D7E4BC",
                "border": 1,
                "align": "center",
                "font_size": 11,
            }
        )
        currency_format = workbook.add_format(
            {"num_format": "#,##0.00", "border": 1, "align": "right"}
        )
        total_format = workbook.add_format(
            {
                "bold": True,
                "num_format": "#,##0.00",
                "bg_color": "#E6E6FA",
                "border": 1,
                "align": "right",
            }
        )
        section_format = workbook.add_format(
            {
                "bold": True,
                "bg_color": "#F0F0F0",
                "border": 1,
                "align": "center",
                "font_size": 10,
            }
        )
        starting_balance_format = workbook.add_format(
            {
                "italic": True,
                "bg_color": "#FFF8DC",
                "num_format": "#,##0.00",
                "border": 1,
                "align": "right",
            }
        )
        text_format = workbook.add_format({"border": 1, "align": "left"})
        date_format = workbook.add_format(
            {"border": 1, "align": "center", "num_format": "yyyy-mm-dd"}
        )

        # 1. Journal Entries Tab
        entries = session.query(JournalEntry).order_by(JournalEntry.date.desc()).all()
        journal_data = []
        for entry in entries:
            journal_data.append(
                {
                    t("date"): entry.date.strftime("%Y-%m-%d"),
                    t("description"): entry.description,
                    t(
                        "debit_account"
                    ): f"{entry.debit_account.account_code} - {entry.debit_account.account_name}",
                    t(
                        "credit_account"
                    ): f"{entry.credit_account.account_code} - {entry.credit_account.account_name}",
                    t("amount"): entry.amount,
                }
            )

        if journal_data:
            journal_df = pd.DataFrame(journal_data)
            journal_df.to_excel(
                writer, sheet_name=t("journal_entries"), index=False, startrow=1
            )

            # Format the journal sheet
            worksheet = writer.sheets[t("journal_entries")]

            # Add title
            worksheet.merge_range("A1:E1", t("journal_entries"), section_format)

            # Format headers
            for col_num, value in enumerate(journal_df.columns.values):
                worksheet.write(1, col_num, value, header_format)

            # Set column widths and formats
            worksheet.set_column("A:A", 12, date_format)  # Date column
            worksheet.set_column("B:B", 30, text_format)  # Description column
            worksheet.set_column("C:D", 25, text_format)  # Account columns
            worksheet.set_column("E:E", 15, currency_format)  # Amount column

            # Apply formats to data rows
            for row_num in range(len(journal_data)):
                worksheet.write(
                    row_num + 2, 4, journal_data[row_num][t("amount")], currency_format
                )

        # 2. Individual Account Details (one tab per account)
        accounts = (
            session.query(Account)
            .filter(Account.is_active)
            .order_by(Account.account_code)
            .all()
        )
        for account in accounts:
            account_entries_df = get_account_entries(session, account.id)

            # Limit sheet name length (Excel limit is 31 characters)
            sheet_name = f"{account.account_code}_{account.account_name}"
            if len(sheet_name) > 31:
                sheet_name = f"{account.account_code}_{account.account_name[:20]}"

            # Create account detail with starting balance, entries, and final total
            account_detail_data = []
            row_formats = []  # Track formatting for each row

            # Get starting balance (base balance for Active and Passive accounts)
            starting_balance = (
                getattr(account, "balance", 0.0)
                if account.category in ["Active", "Passive"]
                else 0.0
            )

            # Add starting balance row if it exists or for Active/Passive accounts
            if starting_balance != 0.0 or account.category in ["Active", "Passive"]:
                debit_amount = ""
                credit_amount = ""

                if starting_balance > 0:
                    if account.category == "Active":
                        debit_amount = starting_balance
                    elif account.category == "Passive":
                        credit_amount = starting_balance

                account_detail_data.append(
                    {
                        t("date"): "",
                        t("description"): t("opening_balance"),
                        t("debit"): debit_amount,
                        t("credit"): credit_amount,
                        t("counterparty"): "",
                    }
                )
                row_formats.append("starting_balance")

            # Add journal entries
            if not account_entries_df.empty:
                entries_data = account_entries_df.copy()
                entries_data = entries_data.rename(
                    columns={
                        "Date": t("date"),
                        "Description": t("description"),
                        "Debit": t("debit"),
                        "Credit": t("credit"),
                        "Counterparty": t("counterparty"),
                    }
                )

                # Convert entries to dict and add to account_detail_data
                for _, row in entries_data.iterrows():
                    account_detail_data.append(
                        {
                            t("date"): row[t("date")].strftime("%Y-%m-%d")
                            if hasattr(row[t("date")], "strftime")
                            else str(row[t("date")]),
                            t("description"): row[t("description")],
                            t("debit"): row[t("debit")] if row[t("debit")] > 0 else "",
                            t("credit"): row[t("credit")]
                            if row[t("credit")] > 0
                            else "",
                            t("counterparty"): row[t("counterparty")],
                        }
                    )
                    row_formats.append("normal")

            # Calculate and add final balance
            from accounting_utils import get_account_balance

            final_balance = get_account_balance(session, account.id)

            debit_final = ""
            credit_final = ""
            if final_balance > 0:
                if account.category in ["Active", "Expenses"]:
                    debit_final = final_balance
                elif account.category in ["Passive", "Products"]:
                    credit_final = final_balance
            elif final_balance < 0:
                if account.category in ["Active", "Expenses"]:
                    credit_final = abs(final_balance)
                elif account.category in ["Passive", "Products"]:
                    debit_final = abs(final_balance)

            account_detail_data.append(
                {
                    t("date"): "",
                    t("description"): t("final_balance").upper(),
                    t("debit"): debit_final,
                    t("credit"): credit_final,
                    t("counterparty"): "",
                }
            )
            row_formats.append("total")

            if account_detail_data:
                detail_df = pd.DataFrame(account_detail_data)
                detail_df.to_excel(
                    writer, sheet_name=sheet_name, index=False, startrow=2
                )

                # Format the account detail sheet
                worksheet = writer.sheets[sheet_name]

                # Add title with account info
                account_title = f"{account.account_code} - {account.account_name} ({t(account.category.lower())})"
                worksheet.merge_range("A1:E1", account_title, section_format)

                # Format headers
                for col_num, value in enumerate(detail_df.columns.values):
                    worksheet.write(2, col_num, value, header_format)

                # Set column widths
                worksheet.set_column("A:A", 12)  # Date column
                worksheet.set_column("B:B", 30)  # Description column
                worksheet.set_column("C:C", 15)  # Debit column
                worksheet.set_column("D:D", 15)  # Credit column
                worksheet.set_column("E:E", 25)  # Counterparty column

                # Apply specific formatting to each row
                for row_idx, (_, row_data) in enumerate(detail_df.iterrows()):
                    actual_row = row_idx + 3  # Account for title and header rows
                    format_type = (
                        row_formats[row_idx] if row_idx < len(row_formats) else "normal"
                    )
                    if format_type == "total":
                        _format = total_format
                    elif format_type == "starting_balance":
                        _format = starting_balance_format
                    else:
                        _format = currency_format

                    # Date column
                    if row_data[t("date")] and row_data[t("date")] != t(
                        "starting_balance"
                    ):
                        try:
                            # Try to parse the date string
                            from datetime import datetime

                            date_obj = datetime.strptime(
                                row_data[t("date")], "%Y-%m-%d"
                            )
                            worksheet.write_datetime(
                                actual_row, 0, date_obj, date_format
                            )
                        except Exception:
                            worksheet.write(
                                actual_row, 0, row_data[t("date")], text_format
                            )
                    else:
                        worksheet.write(actual_row, 0, row_data[t("date")], text_format)

                    # Description column
                    worksheet.write(actual_row, 1, row_data[t("description")], _format)

                    # Debit column
                    if row_data[t("debit")] != "":
                        text = float(row_data[t("debit")])
                    else:
                        text = ""
                    worksheet.write(actual_row, 2, text, _format)

                    # Credit column
                    if row_data[t("credit")] != "":
                        text = float(row_data[t("credit")])
                    else:
                        text = ""
                    worksheet.write(actual_row, 3, text, _format)

                    # Counterparty column
                    worksheet.write(actual_row, 4, row_data[t("counterparty")], _format)

        # 3. Result Sheet (Income Statement) - 2 Column Layout
        income_data = get_income_statement_data(session)

        # Create worksheet manually for better control over layout
        result_worksheet = workbook.add_worksheet(t("result_sheet"))

        # Add title
        result_worksheet.merge_range("A1:E1", t("result_sheet"), section_format)

        # Set column widths
        result_worksheet.set_column("A:A", 25)  # Product account names
        result_worksheet.set_column("B:B", 15)  # Product amounts
        result_worksheet.set_column("C:C", 3)  # Separator column
        result_worksheet.set_column("D:D", 25)  # Expense account names
        result_worksheet.set_column("E:E", 15)  # Expense amounts
        result_worksheet.set_column("F:F", 3)  # Extra separator

        # Column headers
        result_worksheet.write(2, 0, t("products"), header_format)
        result_worksheet.write(2, 1, t("amount"), header_format)
        result_worksheet.write(2, 3, t("expenses"), header_format)
        result_worksheet.write(2, 4, t("amount"), header_format)

        # Products (left side)
        current_row = 3
        for product in income_data.get("products", []):
            account_name = f"{product['code']} - {product['name']}"
            result_worksheet.write(current_row, 0, account_name, text_format)
            result_worksheet.write(current_row, 1, product["balance"], currency_format)
            current_row += 1

        products_end_row = current_row

        # Expenses (right side)
        current_row = 3
        for expense in income_data.get("expenses", []):
            account_name = f"{expense['code']} - {expense['name']}"
            result_worksheet.write(current_row, 3, account_name, text_format)
            result_worksheet.write(current_row, 4, expense["balance"], currency_format)
            current_row += 1

        expenses_end_row = current_row

        # Find the maximum row to align totals
        max_detail_row = max(products_end_row, expenses_end_row)

        # Add blank lines to align totals if needed
        if products_end_row < max_detail_row:
            for row in range(products_end_row, max_detail_row):
                result_worksheet.write(row, 0, "", text_format)
                result_worksheet.write(row, 1, "", text_format)

        if expenses_end_row < max_detail_row:
            for row in range(expenses_end_row, max_detail_row):
                result_worksheet.write(row, 3, "", text_format)
                result_worksheet.write(row, 4, "", text_format)

        # Products total (aligned)
        result_worksheet.write(
            max_detail_row, 0, f"{t('total')} {t('products')}", total_format
        )
        result_worksheet.write(
            max_detail_row, 1, income_data.get("total_products", 0), total_format
        )

        # Expenses total (aligned)
        result_worksheet.write(
            max_detail_row, 3, f"{t('total')} {t('expenses')}", total_format
        )
        result_worksheet.write(
            max_detail_row, 4, income_data.get("total_expenses", 0), total_format
        )

        # Find the maximum row used
        max_row = max_detail_row

        # Add separator line
        for col in range(5):
            result_worksheet.write(max_row + 1, col, "", text_format)

        # Net Income - centered across both columns
        net_income_row = max_row + 2
        result_worksheet.merge_range(
            f"A{net_income_row + 1}:B{net_income_row + 1}",
            f"{t('net_income')}: {income_data.get('net_income', 0):.2f}",
            total_format,
        )

        # 4. Balance Sheet (including net income in equity) - 2 Column Layout
        balance_data = get_balance_sheet_data(session)
        net_income = income_data.get("net_income", 0)

        # Create worksheet manually for better control over layout
        balance_worksheet = workbook.add_worksheet(t("balance_sheet"))

        # Add title
        balance_worksheet.merge_range("A1:E1", t("balance_sheet"), section_format)

        # Set column widths
        balance_worksheet.set_column("A:A", 25)  # Active account names
        balance_worksheet.set_column("B:B", 15)  # Active amounts
        balance_worksheet.set_column("C:C", 3)  # Separator column
        balance_worksheet.set_column("D:D", 25)  # Passive account names
        balance_worksheet.set_column("E:E", 15)  # Passive amounts
        balance_worksheet.set_column("F:F", 3)  # Extra separator

        # Column headers
        balance_worksheet.write(2, 0, t("active"), header_format)
        balance_worksheet.write(2, 1, t("amount"), header_format)
        balance_worksheet.write(2, 3, t("passive"), header_format)
        balance_worksheet.write(2, 4, t("amount"), header_format)

        # Active accounts (left side)
        current_row = 3
        for active in balance_data.get("active", []):
            account_name = f"{active['code']} - {active['name']}"
            balance_worksheet.write(current_row, 0, account_name, text_format)
            balance_worksheet.write(current_row, 1, active["balance"], currency_format)
            current_row += 1

        active_end_row = current_row

        # Passive accounts (right side)
        current_row = 3
        for passive in balance_data.get("passive", []):
            account_name = f"{passive['code']} - {passive['name']}"
            balance_worksheet.write(current_row, 3, account_name, text_format)
            balance_worksheet.write(current_row, 4, passive["balance"], currency_format)
            current_row += 1

        # Add net income to passive side if it exists
        if net_income != 0:
            net_income_format = workbook.add_format(
                {
                    "italic": True,
                    "num_format": "#,##0.00",
                    "bg_color": "#E6F7FF",
                    "border": 1,
                    "align": "right",
                }
            )
            balance_worksheet.write(current_row, 3, t("net_income"), net_income_format)
            balance_worksheet.write(current_row, 4, net_income, net_income_format)
            current_row += 1

        passive_end_row = current_row

        # Find the maximum row to align totals
        max_detail_row = max(active_end_row, passive_end_row)

        # Add blank lines to align totals if needed
        if active_end_row < max_detail_row:
            for row in range(active_end_row, max_detail_row):
                balance_worksheet.write(row, 0, "", text_format)
                balance_worksheet.write(row, 1, "", text_format)

        if passive_end_row < max_detail_row:
            for row in range(passive_end_row, max_detail_row):
                balance_worksheet.write(row, 3, "", text_format)
                balance_worksheet.write(row, 4, "", text_format)

        # Calculate total passive including net income
        total_passive_with_income = balance_data.get("total_passive", 0) + net_income

        # Active total (aligned)
        balance_worksheet.write(
            max_detail_row, 0, f"{t('total')} {t('active')}", total_format
        )
        balance_worksheet.write(
            max_detail_row, 1, balance_data.get("total_active", 0), total_format
        )

        # Passive total (aligned)
        balance_worksheet.write(
            max_detail_row, 3, f"{t('total')} {t('passive')}", total_format
        )
        balance_worksheet.write(
            max_detail_row, 4, total_passive_with_income, total_format
        )

        # Find the maximum row used
        max_row = max_detail_row

        # Add separator line
        for col in range(5):
            balance_worksheet.write(max_row + 1, col, "", text_format)

        # Balance verification - show if totals match
        balance_diff = balance_data.get("total_active", 0) - total_passive_with_income
        balance_status_row = max_row + 2

        if abs(balance_diff) < 0.01:  # Allow for small rounding differences
            balance_status = (
                f"✓ {t('balance_verified')}: {balance_data.get('total_active', 0):.2f}"
            )
            balance_status_format = workbook.add_format(
                {
                    "bold": True,
                    "bg_color": "#D4EDDA",
                    "border": 1,
                    "align": "center",
                    "color": "#155724",
                }
            )
        else:
            balance_status = f"⚠ {t('balance_difference')}: {balance_diff:.2f}"
            balance_status_format = workbook.add_format(
                {
                    "bold": True,
                    "bg_color": "#F8D7DA",
                    "border": 1,
                    "align": "center",
                    "color": "#721C24",
                }
            )

        balance_worksheet.merge_range(
            f"A{balance_status_row + 1}:E{balance_status_row + 1}",
            balance_status,
            balance_status_format,
        )

        # Close the writer and get the data
        writer.close()
        session.close()
        db_manager.dispose()

        output.seek(0)
        return output.getvalue()

    except Exception as e:
        print(f"Error creating Excel export: {e}")
        return None


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
    tab1, tab2, tab3, tab4 = st.tabs(
        [
            t("create_new_database"),
            t("load_from_computer"),
            t("download_database"),
            t("export_as_excel"),
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

    # Close button
    st.markdown("---")
    if st.button(t("close"), use_container_width=True):
        st.rerun()


def file_management_button():
    """Display compact file management button."""
    if st.button("📁", help=t("file_management"), use_container_width=True):
        show_file_management_dialog()
