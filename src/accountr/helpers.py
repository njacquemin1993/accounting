"""
Common helper functions to reduce code duplication across the application.
"""

import importlib.metadata
from accountr.constants import (
    ACCOUNT_CODE_RANGES,
    CATEGORY_ACTIVE,
    CATEGORY_PASSIVE,
    CATEGORY_EXPENSES,
    CATEGORY_PRODUCTS,
    BALANCE_SHEET_CATEGORIES,
    DEBIT_BALANCE_CATEGORIES,
    CREDIT_BALANCE_CATEGORIES,
    MIN_ACCOUNTS_FOR_JOURNAL_ENTRY,
    DEFAULT_CURRENCY,
)
from accountr.translation_utils import t


def get_app_version() -> str:
    """
    Get the application version from package metadata.

    Returns:
        str: The application version (e.g., "0.1.0")
    """
    try:
        return importlib.metadata.version("accountr")
    except importlib.metadata.PackageNotFoundError:
        return "unknown"  # Fallback version


def get_category_display_map():
    """
    Get a mapping from internal category names to translated display names.

    Args:
        t: Translation function

    Returns:
        dict: Mapping of category names to translations
    """
    return {
        CATEGORY_ACTIVE: t("active"),
        CATEGORY_PASSIVE: t("passive"),
        CATEGORY_EXPENSES: t("expenses"),
        CATEGORY_PRODUCTS: t("products"),
    }


def get_reverse_category_map():
    """
    Get a mapping from translated display names to internal category names.

    Args:
        t: Translation function

    Returns:
        dict: Mapping of translations to category names
    """
    return {
        t("active"): CATEGORY_ACTIVE,
        t("passive"): CATEGORY_PASSIVE,
        t("expenses"): CATEGORY_EXPENSES,
        t("products"): CATEGORY_PRODUCTS,
    }


def validate_account_code(account_code: str, category: str) -> tuple[bool, str]:
    """
    Validate account code based on category.

    Args:
        account_code: The account code to validate
        category: The account category
        t: Translation function

    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        code_num = int(account_code)
    except ValueError:
        return False, t("account_code_must_be_numeric")

    if category in ACCOUNT_CODE_RANGES:
        min_code, max_code = ACCOUNT_CODE_RANGES[category]
        if not (min_code <= code_num <= max_code):
            # Get the appropriate error message key
            error_key = f"account_code_range_{category.lower()}"
            return False, t(error_key)

    return True, ""


def is_balance_sheet_category(category: str) -> bool:
    """Check if a category supports opening balance."""
    return category in BALANCE_SHEET_CATEGORIES


def is_debit_balance_category(category: str) -> bool:
    """Check if a category has normal debit balance."""
    return category in DEBIT_BALANCE_CATEGORIES


def is_credit_balance_category(category: str) -> bool:
    """Check if a category has normal credit balance."""
    return category in CREDIT_BALANCE_CATEGORIES


def get_balance_side(balance: float, category: str) -> tuple[str, str]:
    """
    Determine which side (debit/credit) a balance should be displayed on.

    Args:
        balance: The account balance
        category: The account category

    Returns:
        tuple: (debit_value, credit_value) - one will be the balance, other will be empty string
    """
    debit_value = ""
    credit_value = ""

    if balance > 0:
        if is_debit_balance_category(category):
            debit_value = balance
        elif is_credit_balance_category(category):
            credit_value = balance
    elif balance < 0:
        if is_debit_balance_category(category):
            credit_value = abs(balance)
        elif is_credit_balance_category(category):
            debit_value = abs(balance)

    return debit_value, credit_value


def format_account_option(account_code: str, account_name: str) -> str:
    """Format account for dropdown display."""
    return f"{account_code} - {account_name}"


def has_sufficient_accounts(accounts_count: int) -> bool:
    """Check if there are enough accounts to create journal entries."""
    return accounts_count >= MIN_ACCOUNTS_FOR_JOURNAL_ENTRY


def format_currency(amount: float, currency: str = DEFAULT_CURRENCY) -> str:
    """
    Format an amount as currency string.

    Args:
        amount: The amount to format
        currency: The currency code (defaults to DEFAULT_CURRENCY)

    Returns:
        str: Formatted currency string (e.g., "CHF 1,234.56")
    """
    return f"{currency} {amount:,.2f}"
