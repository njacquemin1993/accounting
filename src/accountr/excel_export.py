"""
Excel export functionality for accounting data.
Breaks down the large excel export function into smaller, focused functions.
"""

import pandas as pd
from datetime import datetime
from accountr.database import JournalEntry
from accountr.accounting_utils import get_account_entries, get_account_balance
from accountr.excel_utils import (
    set_journal_column_widths,
    set_account_detail_column_widths,
    set_two_column_report_widths,
    write_sheet_title,
    format_account_name,
    truncate_sheet_name,
)
from accountr.helpers import (
    is_balance_sheet_category,
    get_balance_side,
)
from accountr.accounting_utils import (
    get_income_statement_data,
    get_balance_sheet_data,
)
import io
from accountr.database import Account
from accountr.translation_utils import t
from accountr.excel_utils import create_excel_formats
from accountr.constants import (
    EXCEL_MAX_SHEET_NAME_LENGTH,
    BALANCE_ROUNDING_PRECISION,
)
from accountr.database_switcher import DatabaseSwitcher


def export_journal_entries_sheet(writer, session, formats, t):
    """Export journal entries to Excel sheet."""
    entries = session.query(JournalEntry).order_by(JournalEntry.date.desc()).all()
    journal_data = []

    for entry in entries:
        journal_data.append(
            {
                t("date"): entry.date.strftime("%Y-%m-%d"),
                t("description"): entry.description,
                t("debit_account"): format_account_name(
                    entry.debit_account.account_code, entry.debit_account.account_name
                ),
                t("credit_account"): format_account_name(
                    entry.credit_account.account_code, entry.credit_account.account_name
                ),
                t("amount"): entry.amount,
            }
        )

    if journal_data:
        journal_df = pd.DataFrame(journal_data)
        journal_df.to_excel(writer, sheet_name=t("journal_entries"), index=False, startrow=1)

        worksheet = writer.sheets[t("journal_entries")]
        write_sheet_title(worksheet, t("journal_entries"), formats, "A1:E1")

        # Format headers
        for col_num, value in enumerate(journal_df.columns.values):
            worksheet.write(1, col_num, value, formats["header"])

        set_journal_column_widths(worksheet)

        # Apply formats to data rows
        for row_num in range(len(journal_data)):
            worksheet.write(row_num + 2, 4, journal_data[row_num][t("amount")], formats["currency"])


def export_account_detail_sheet(writer, session, account, formats, t):
    """Export individual account detail to Excel sheet."""
    account_entries_df = get_account_entries(session, account.id)

    # Create sheet name
    sheet_name = truncate_sheet_name(f"{account.account_code}_{account.account_name}", EXCEL_MAX_SHEET_NAME_LENGTH)

    # Create account detail with starting balance, entries, and final total
    account_detail_data = []
    row_formats = []

    # Get starting balance
    starting_balance = getattr(account, "balance", 0.0) if is_balance_sheet_category(account.category) else 0.0

    # Add starting balance row if applicable
    if starting_balance != 0.0 or is_balance_sheet_category(account.category):
        debit_amount, credit_amount = get_balance_side(starting_balance, account.category)

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

        for _, row in entries_data.iterrows():
            account_detail_data.append(
                {
                    t("date"): row[t("date")].strftime("%Y-%m-%d")
                    if hasattr(row[t("date")], "strftime")
                    else str(row[t("date")]),
                    t("description"): row[t("description")],
                    t("debit"): row[t("debit")] if row[t("debit")] > 0 else "",
                    t("credit"): row[t("credit")] if row[t("credit")] > 0 else "",
                    t("counterparty"): row[t("counterparty")],
                }
            )
            row_formats.append("normal")

    # Calculate and add final balance
    final_balance = get_account_balance(session, account.id)
    debit_final, credit_final = get_balance_side(final_balance, account.category)

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
        detail_df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=2)

        worksheet = writer.sheets[sheet_name]

        # Add title with account info
        account_title = f"{account.account_code} - {account.account_name} ({t(account.category.lower())})"
        write_sheet_title(worksheet, account_title, formats, "A1:E1")

        # Format headers
        for col_num, value in enumerate(detail_df.columns.values):
            worksheet.write(2, col_num, value, formats["header"])

        set_account_detail_column_widths(worksheet)

        # Apply specific formatting to each row
        _apply_row_formats(worksheet, detail_df, row_formats, formats, t)


def _apply_row_formats(worksheet, detail_df, row_formats, formats, t):
    """Apply formatting to account detail rows."""
    for row_idx, (_, row_data) in enumerate(detail_df.iterrows()):
        actual_row = row_idx + 3  # Account for title and header rows
        format_type = row_formats[row_idx] if row_idx < len(row_formats) else "normal"

        if format_type == "total":
            _format = formats["total"]
        elif format_type == "starting_balance":
            _format = formats["starting_balance"]
        else:
            _format = formats["currency"]

        # Date column
        if row_data[t("date")] and row_data[t("date")] != t("starting_balance"):
            try:
                date_obj = datetime.strptime(row_data[t("date")], "%Y-%m-%d")
                worksheet.write_datetime(actual_row, 0, date_obj, formats["date"])
            except Exception:
                worksheet.write(actual_row, 0, row_data[t("date")], formats["text"])
        else:
            worksheet.write(actual_row, 0, row_data[t("date")], formats["text"])

        # Description column
        worksheet.write(actual_row, 1, row_data[t("description")], _format)

        # Debit column
        debit_value = float(row_data[t("debit")]) if row_data[t("debit")] != "" else ""
        worksheet.write(actual_row, 2, debit_value, _format)

        # Credit column
        credit_value = float(row_data[t("credit")]) if row_data[t("credit")] != "" else ""
        worksheet.write(actual_row, 3, credit_value, _format)

        # Counterparty column
        worksheet.write(actual_row, 4, row_data[t("counterparty")], _format)


def export_result_sheet(writer, workbook, income_data, formats, t):
    """Export result sheet (income statement) to Excel."""
    result_worksheet = workbook.add_worksheet(t("result_sheet"))
    write_sheet_title(result_worksheet, t("result_sheet"), formats, "A1:E1")
    set_two_column_report_widths(result_worksheet)

    # Column headers
    result_worksheet.write(2, 0, t("products"), formats["header"])
    result_worksheet.write(2, 1, t("amount"), formats["header"])
    result_worksheet.write(2, 3, t("expenses"), formats["header"])
    result_worksheet.write(2, 4, t("amount"), formats["header"])

    # Products (left side)
    current_row = 3
    for product in income_data.get("products", []):
        account_name = format_account_name(product["code"], product["name"])
        result_worksheet.write(current_row, 0, account_name, formats["text"])
        result_worksheet.write(current_row, 1, product["balance"], formats["currency"])
        current_row += 1
    products_end_row = current_row

    # Expenses (right side)
    current_row = 3
    for expense in income_data.get("expenses", []):
        account_name = format_account_name(expense["code"], expense["name"])
        result_worksheet.write(current_row, 3, account_name, formats["text"])
        result_worksheet.write(current_row, 4, expense["balance"], formats["currency"])
        current_row += 1
    expenses_end_row = current_row

    # Align totals
    max_detail_row = max(products_end_row, expenses_end_row)
    _fill_blank_rows(result_worksheet, products_end_row, max_detail_row, [0, 1], formats["text"])
    _fill_blank_rows(result_worksheet, expenses_end_row, max_detail_row, [3, 4], formats["text"])

    # Write totals
    result_worksheet.write(max_detail_row, 0, f"{t('total')} {t('products')}", formats["total"])
    result_worksheet.write(max_detail_row, 1, income_data.get("total_products", 0), formats["total"])
    result_worksheet.write(max_detail_row, 3, f"{t('total')} {t('expenses')}", formats["total"])
    result_worksheet.write(max_detail_row, 4, income_data.get("total_expenses", 0), formats["total"])

    # Net income
    _write_separator_row(result_worksheet, max_detail_row + 1, 5, formats["text"])
    net_income_row = max_detail_row + 2
    result_worksheet.merge_range(
        f"A{net_income_row + 1}:B{net_income_row + 1}",
        f"{t('net_income')}: {income_data.get('net_income', 0):.2f}",
        formats["total"],
    )


def export_balance_sheet(writer, workbook, balance_data, net_income, formats, t):
    """Export balance sheet to Excel."""
    balance_worksheet = workbook.add_worksheet(t("balance_sheet"))
    write_sheet_title(balance_worksheet, t("balance_sheet"), formats, "A1:E1")
    set_two_column_report_widths(balance_worksheet)

    # Column headers
    balance_worksheet.write(2, 0, t("active"), formats["header"])
    balance_worksheet.write(2, 1, t("amount"), formats["header"])
    balance_worksheet.write(2, 3, t("passive"), formats["header"])
    balance_worksheet.write(2, 4, t("amount"), formats["header"])

    # Active accounts (left side)
    current_row = 3
    for active in balance_data.get("active", []):
        account_name = format_account_name(active["code"], active["name"])
        balance_worksheet.write(current_row, 0, account_name, formats["text"])
        balance_worksheet.write(current_row, 1, active["balance"], formats["currency"])
        current_row += 1
    active_end_row = current_row

    # Passive accounts (right side)
    current_row = 3
    for passive in balance_data.get("passive", []):
        account_name = format_account_name(passive["code"], passive["name"])
        balance_worksheet.write(current_row, 3, account_name, formats["text"])
        balance_worksheet.write(current_row, 4, passive["balance"], formats["currency"])
        current_row += 1

    # Add net income to passive side
    if net_income != 0:
        balance_worksheet.write(current_row, 3, t("net_income"), formats["net_income"])
        balance_worksheet.write(current_row, 4, net_income, formats["net_income"])
        current_row += 1
    passive_end_row = current_row

    # Align totals
    max_detail_row = max(active_end_row, passive_end_row)
    _fill_blank_rows(balance_worksheet, active_end_row, max_detail_row, [0, 1], formats["text"])
    _fill_blank_rows(balance_worksheet, passive_end_row, max_detail_row, [3, 4], formats["text"])

    # Write totals
    total_passive_with_income = balance_data.get("total_passive", 0) + net_income
    balance_worksheet.write(max_detail_row, 0, f"{t('total')} {t('active')}", formats["total"])
    balance_worksheet.write(max_detail_row, 1, balance_data.get("total_active", 0), formats["total"])
    balance_worksheet.write(max_detail_row, 3, f"{t('total')} {t('passive')}", formats["total"])
    balance_worksheet.write(max_detail_row, 4, total_passive_with_income, formats["total"])

    # Balance verification
    _write_separator_row(balance_worksheet, max_detail_row + 1, 5, formats["text"])
    balance_diff = balance_data.get("total_active", 0) - total_passive_with_income
    balance_status_row = max_detail_row + 2

    if abs(balance_diff) < BALANCE_ROUNDING_PRECISION:
        balance_status = f"✓ {t('balance_sheet_balanced_checkmark')}"
        balance_status_format = formats["total"]
    else:
        balance_status = f"✗ {t('balance_sheet_not_balanced_x')} ({balance_diff:.2f})"
        balance_status_format = workbook.add_format(
            {
                "bold": True,
                "bg_color": "#FFE6E6",
                "border": 1,
                "align": "center",
            }
        )

    balance_worksheet.merge_range(
        f"A{balance_status_row + 1}:E{balance_status_row + 1}",
        balance_status,
        balance_status_format,
    )


def _fill_blank_rows(worksheet, start_row, end_row, columns, format_obj):
    """Fill blank rows for alignment."""
    for row in range(start_row, end_row):
        for col in columns:
            worksheet.write(row, col, "", format_obj)


def _write_separator_row(worksheet, row, num_cols, format_obj):
    """Write a separator row."""
    for col in range(num_cols):
        worksheet.write(row, col, "", format_obj)


def create_excel_export(db_name):
    """Create Excel file with multiple tabs for accounting data export."""
    try:
        # Initialize database
        switcher = DatabaseSwitcher()
        current_db = switcher.get_current_database()
        switcher.switch_database(db_name)
        session = switcher.get_database_manager().get_session()

        # Create Excel writer object in memory
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine="xlsxwriter")
        workbook = writer.book

        # Define formats using utility
        formats = create_excel_formats(workbook)

        # 1. Journal Entries Tab
        export_journal_entries_sheet(writer, session, formats, t)

        # 2. Individual Account Details (one tab per account)
        accounts = session.query(Account).filter(Account.is_active).order_by(Account.account_code).all()
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

        output.seek(0)
        return output.getvalue()

    except Exception as e:
        print(f"Error creating Excel export: {e}")
        return None
    finally:
        # Ensure we switch back to the original database
        switcher.switch_database(current_db)
