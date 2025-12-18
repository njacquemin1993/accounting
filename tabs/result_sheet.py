"""
Result Sheet (Income Statement) tab functionality.
"""
import streamlit as st
import pandas as pd
from accounting_utils import get_income_statement_data

def view_result_sheet(db_manager):
    """Tab for viewing result sheet (income statement)."""
    st.header("Result Sheet (Income Statement)")
    
    session = db_manager.get_session()
    
    income_statement_data = get_income_statement_data(session)
    
    # Calculate table heights to align totals
    products_rows = len(income_statement_data['products']) + 2  # products + blank + total
    expenses_rows = len(income_statement_data['expenses']) + 2  # expenses + blank + total
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Products")
        if income_statement_data['products']:
            # Create DataFrame for products
            products_data = []
            for product in income_statement_data['products']:
                products_data.append({
                    'Account': f"{product['code']} - {product['name']}",
                    'Amount': f"CHF {product['balance']:,.2f}"
                })
            
            # Add blank lines if products table is shorter
            if products_rows < expenses_rows:
                blank_lines_needed = expenses_rows - products_rows
                for _ in range(blank_lines_needed):
                    products_data.append({
                        'Account': '',
                        'Amount': ''
                    })
            
            # Add spacing and total
            products_data.append({
                'Account': '',
                'Amount': ''
            })
            products_data.append({
                'Account': 'TOTAL PRODUCTS',
                'Amount': f"CHF {income_statement_data['total_products']:,.2f}"
            })
            
            products_df = pd.DataFrame(products_data)
            
            # Display table without index
            st.table(products_df)
        else:
            st.write("No products to display")
    
    with col2:
        st.subheader("Expenses")
        if income_statement_data['expenses']:
            # Create DataFrame for expenses
            expenses_data = []
            for expense in income_statement_data['expenses']:
                expenses_data.append({
                    'Account': f"{expense['code']} - {expense['name']}",
                    'Amount': f"CHF {expense['balance']:,.2f}"
                })
            
            # Add blank lines if expenses table is shorter
            if expenses_rows < products_rows:
                blank_lines_needed = products_rows - expenses_rows
                for _ in range(blank_lines_needed):
                    expenses_data.append({
                        'Account': '',
                        'Amount': ''
                    })
            
            # Add spacing and total
            expenses_data.append({
                'Account': '',
                'Amount': ''
            })
            expenses_data.append({
                'Account': 'TOTAL EXPENSES',
                'Amount': f"CHF {income_statement_data['total_expenses']:,.2f}"
            })
            
            expenses_df = pd.DataFrame(expenses_data)
            
            # Display table without index
            st.table(expenses_df)
        else:
            st.write("No expenses to display")
    
    # Net income calculation
    st.markdown("---")
    net_income_col1, net_income_col2 = st.columns(2)
    
    with net_income_col1:
        st.markdown(f"### **NET INCOME**")
    
    with net_income_col2:
        net_income = income_statement_data['net_income']
        if net_income >= 0:
            st.markdown(f"### **CHF {net_income:,.2f}** 💰")
        else:
            st.markdown(f"### **CHF {net_income:,.2f}** ⚠️")
    
    # Additional metrics
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Products", f"CHF {income_statement_data['total_products']:,.2f}")
    
    with col2:
        st.metric("Total Expenses", f"CHF {income_statement_data['total_expenses']:,.2f}")
    
    with col3:
        if income_statement_data['total_products'] > 0:
            profit_margin = (net_income / income_statement_data['total_products']) * 100
            st.metric("Profit Margin", f"{profit_margin:.1f}%")
        else:
            st.metric("Profit Margin", "N/A")
    
    session.close()
