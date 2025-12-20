"""
Result Sheet page for navigation.
"""

import streamlit as st
import pandas as pd
from database import DatabaseManager
from accounting_utils import get_income_statement_data
from translation_utils import t, language_selector, header_with_controls
from file_management_ui import file_management_button


def get_database():
    db_manager = DatabaseManager()
    return db_manager


# Page header with controls
header_col1, header_col2, header_col3 = header_with_controls()

with header_col1:
    st.title(f"📈 {t('result_sheet')}")

with header_col2:
    st.markdown("<br>", unsafe_allow_html=True)
    language_selector()

with header_col3:
    st.markdown("<br>", unsafe_allow_html=True)
    file_management_button()

st.markdown("---")

# Initialize database and show content
db_manager = get_database()

session = db_manager.get_session()

income_statement_data = get_income_statement_data(session)

# Calculate table heights to align totals
products_rows = len(income_statement_data["products"]) + 2  # products + blank + total
expenses_rows = len(income_statement_data["expenses"]) + 2  # expenses + blank + total

col1, col2 = st.columns(2)

with col1:
    st.subheader(t("products_title"))
    if income_statement_data["products"]:
        # Create DataFrame for products
        products_data = []
        for product in income_statement_data["products"]:
            products_data.append(
                {
                    t("account_column"): f"{product['code']} - {product['name']}",
                    t("amount_column"): f"CHF {product['balance']:,.2f}",
                }
            )

        # Add blank lines if products table is shorter
        if products_rows < expenses_rows:
            blank_lines_needed = expenses_rows - products_rows
            for _ in range(blank_lines_needed):
                products_data.append({t("account_column"): "", t("amount_column"): ""})

        # Add spacing and total
        products_data.append({t("account_column"): "", t("amount_column"): ""})
        products_data.append(
            {
                t("account_column"): t("total_products"),
                t(
                    "amount_column"
                ): f"CHF {income_statement_data['total_products']:,.2f}",
            }
        )

        products_df = pd.DataFrame(products_data)

        # Display table without index
        st.table(products_df)
    else:
        st.write(t("no_products_display"))

with col2:
    st.subheader(t("expenses_title"))
    if income_statement_data["expenses"]:
        # Create DataFrame for expenses
        expenses_data = []
        for expense in income_statement_data["expenses"]:
            expenses_data.append(
                {
                    t("account_column"): f"{expense['code']} - {expense['name']}",
                    t("amount_column"): f"CHF {expense['balance']:,.2f}",
                }
            )

        # Add blank lines if expenses table is shorter
        if expenses_rows < products_rows:
            blank_lines_needed = products_rows - expenses_rows
            for _ in range(blank_lines_needed):
                expenses_data.append({t("account_column"): "", t("amount_column"): ""})

        # Add spacing and total
        expenses_data.append({t("account_column"): "", t("amount_column"): ""})
        expenses_data.append(
            {
                t("account_column"): t("total_expenses"),
                t(
                    "amount_column"
                ): f"CHF {income_statement_data['total_expenses']:,.2f}",
            }
        )

        expenses_df = pd.DataFrame(expenses_data)

        # Display table without index
        st.table(expenses_df)
    else:
        st.write(t("no_expenses_display"))

# Net income calculation
st.markdown("---")
net_income_col1, net_income_col2 = st.columns(2)

with net_income_col1:
    net_income = income_statement_data["net_income"]
    if net_income >= 0:
        st.markdown(f"### **{t('net_income')}**")
    else:
        st.markdown(f"### **{t('net_loss')}**")

with net_income_col2:
    if net_income >= 0:
        st.markdown(f"### **CHF {net_income:,.2f}** 💰")
    else:
        st.markdown(f"### **CHF {abs(net_income):,.2f}** ⚠️")

# Additional metrics
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        t("total_products"), f"CHF {income_statement_data['total_products']:,.2f}"
    )

with col2:
    st.metric(
        t("total_expenses"), f"CHF {income_statement_data['total_expenses']:,.2f}"
    )

with col3:
    if income_statement_data["total_products"] > 0:
        profit_margin = (net_income / income_statement_data["total_products"]) * 100
        st.metric(t("profit_margin"), f"{profit_margin:.1f}%")
    else:
        st.metric(t("profit_margin"), "N/A")

session.close()
