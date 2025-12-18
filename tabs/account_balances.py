"""
Account Balances tab functionality.
"""
import streamlit as st
from accounting_utils import get_trial_balance

def view_account_balances(db_manager):
    """Tab for viewing account balances."""
    st.header("Account Balances")
    
    session = db_manager.get_session()
    
    # Get trial balance
    trial_balance = get_trial_balance(session)
    
    if not trial_balance.empty:
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            category_filter = st.selectbox(
                "Filter by Category",
                ["All"] + list(trial_balance['Category'].unique())
            )
        with col2:
            type_filter = st.selectbox(
                "Filter by Type",
                ["All"] + list(trial_balance['Account Type'].unique())
            )
        
        # Apply filters
        filtered_df = trial_balance.copy()
        if category_filter != "All":
            filtered_df = filtered_df[filtered_df['Category'] == category_filter]
        if type_filter != "All":
            filtered_df = filtered_df[filtered_df['Account Type'] == type_filter]
        
        # Format the balance column
        filtered_df['Balance'] = filtered_df['Balance'].apply(lambda x: f"CHF {x:,.2f}")
        
        st.dataframe(filtered_df, use_container_width=True)
        
        # Summary statistics
        st.subheader("Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_assets = trial_balance[trial_balance['Account Type'] == 'Asset']['Balance'].apply(
                lambda x: float(x.replace('$', '').replace(',', '')) if isinstance(x, str) else x
            ).sum()
            st.metric("Total Assets", f"CHF {total_assets:,.2f}")
        
        with col2:
            total_liabilities = trial_balance[trial_balance['Account Type'] == 'Liability']['Balance'].apply(
                lambda x: float(x.replace('CHF ', '').replace(',', '')) if isinstance(x, str) else x
            ).sum()
            st.metric("Total Liabilities", f"CHF {total_liabilities:,.2f}")
        
        with col3:
            total_equity = trial_balance[trial_balance['Account Type'] == 'Equity']['Balance'].apply(
                lambda x: float(x.replace('CHF ', '').replace(',', '')) if isinstance(x, str) else x
            ).sum()
            st.metric("Total Equity", f"CHF {total_equity:,.2f}")
        
        with col4:
            # Convert back to float for calculation
            numeric_balances = trial_balance['Balance'].apply(
                lambda x: float(x.replace('CHF ', '').replace(',', '')) if isinstance(x, str) else x
            )
            trial_balance['Numeric_Balance'] = numeric_balances
            
            total_revenue = trial_balance[trial_balance['Account Type'] == 'Revenue']['Numeric_Balance'].sum()
            total_expenses = trial_balance[trial_balance['Account Type'] == 'Expense']['Numeric_Balance'].sum()
            net_income = total_revenue - total_expenses
            st.metric("Net Income", f"CHF {net_income:,.2f}")
            
    else:
        st.info("No account balances to display. Add some journal entries first.")
    
    session.close()
