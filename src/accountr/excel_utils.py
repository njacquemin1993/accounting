"""
Utility functions for Excel export formatting and configuration.
"""

from accountr.constants import (
    EXCEL_COLOR_HEADER,
    EXCEL_COLOR_TOTAL,
    EXCEL_COLOR_SECTION,
    EXCEL_COLOR_STARTING_BALANCE,
    EXCEL_COLOR_NET_INCOME,
    EXCEL_COLUMN_WIDTH_DATE,
    EXCEL_COLUMN_WIDTH_DESCRIPTION,
    EXCEL_COLUMN_WIDTH_ACCOUNT,
    EXCEL_COLUMN_WIDTH_AMOUNT,
    EXCEL_COLUMN_WIDTH_SEPARATOR,
)


def create_excel_formats(workbook):
    """
    Create standard Excel formats for accounting exports.

    Args:
        workbook: xlsxwriter Workbook object

    Returns:
        dict: Dictionary of format objects
    """
    return {
        "header": workbook.add_format(
            {
                "bold": True,
                "bg_color": EXCEL_COLOR_HEADER,
                "border": 1,
                "align": "center",
                "font_size": 11,
            }
        ),
        "currency": workbook.add_format({"num_format": "#,##0.00", "border": 1, "align": "right"}),
        "total": workbook.add_format(
            {
                "bold": True,
                "num_format": "#,##0.00",
                "bg_color": EXCEL_COLOR_TOTAL,
                "border": 1,
                "align": "right",
            }
        ),
        "section": workbook.add_format(
            {
                "bold": True,
                "bg_color": EXCEL_COLOR_SECTION,
                "border": 1,
                "align": "center",
                "font_size": 10,
            }
        ),
        "starting_balance": workbook.add_format(
            {
                "italic": True,
                "bg_color": EXCEL_COLOR_STARTING_BALANCE,
                "num_format": "#,##0.00",
                "border": 1,
                "align": "right",
            }
        ),
        "text": workbook.add_format({"border": 1, "align": "left"}),
        "date": workbook.add_format({"border": 1, "align": "center", "num_format": "yyyy-mm-dd"}),
        "net_income": workbook.add_format(
            {
                "italic": True,
                "num_format": "#,##0.00",
                "bg_color": EXCEL_COLOR_NET_INCOME,
                "border": 1,
                "align": "right",
            }
        ),
    }


def set_journal_column_widths(worksheet):
    """Set standard column widths for journal entry sheets."""
    worksheet.set_column("A:A", EXCEL_COLUMN_WIDTH_DATE)  # Date
    worksheet.set_column("B:B", EXCEL_COLUMN_WIDTH_DESCRIPTION)  # Description
    worksheet.set_column("C:D", EXCEL_COLUMN_WIDTH_ACCOUNT)  # Account columns
    worksheet.set_column("E:E", EXCEL_COLUMN_WIDTH_AMOUNT)  # Amount


def set_account_detail_column_widths(worksheet):
    """Set standard column widths for account detail sheets."""
    worksheet.set_column("A:A", EXCEL_COLUMN_WIDTH_DATE)  # Date
    worksheet.set_column("B:B", EXCEL_COLUMN_WIDTH_DESCRIPTION)  # Description
    worksheet.set_column("C:C", EXCEL_COLUMN_WIDTH_AMOUNT)  # Debit
    worksheet.set_column("D:D", EXCEL_COLUMN_WIDTH_AMOUNT)  # Credit
    worksheet.set_column("E:E", EXCEL_COLUMN_WIDTH_ACCOUNT)  # Counterparty


def set_two_column_report_widths(worksheet):
    """Set standard column widths for two-column reports (Result Sheet, Balance Sheet)."""
    worksheet.set_column("A:A", EXCEL_COLUMN_WIDTH_ACCOUNT)  # Left account names
    worksheet.set_column("B:B", EXCEL_COLUMN_WIDTH_AMOUNT)  # Left amounts
    worksheet.set_column("C:C", EXCEL_COLUMN_WIDTH_SEPARATOR)  # Separator
    worksheet.set_column("D:D", EXCEL_COLUMN_WIDTH_ACCOUNT)  # Right account names
    worksheet.set_column("E:E", EXCEL_COLUMN_WIDTH_AMOUNT)  # Right amounts
    worksheet.set_column("F:F", EXCEL_COLUMN_WIDTH_SEPARATOR)  # Extra separator


def write_sheet_title(worksheet, title, formats, merge_range="A1:E1"):
    """Write a formatted title at the top of a sheet."""
    worksheet.merge_range(merge_range, title, formats["section"])


def write_headers(worksheet, headers, row_num, formats):
    """Write column headers with standard formatting."""
    for col_num, header in enumerate(headers):
        worksheet.write(row_num, col_num, header, formats["header"])


def format_account_name(account_code, account_name):
    """Format account code and name consistently."""
    return f"{account_code} - {account_name}"


def truncate_sheet_name(name, max_length=31):
    """
    Truncate sheet name to fit Excel's limitations.

    Args:
        name: Original sheet name
        max_length: Maximum allowed length (Excel limit is 31)

    Returns:
        str: Truncated sheet name
    """
    if len(name) <= max_length:
        return name
    return name[:max_length]
