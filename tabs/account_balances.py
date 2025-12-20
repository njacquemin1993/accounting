"""
Account Balances tab functionality.
"""
import streamlit as st
from accounting_utils import get_trial_balance, get_account_entries, get_account_balance

def view_account_balances(db_manager):
    """Tab for viewing account balances."""
    st.header("Account Balances")
    
    session = db_manager.get_session()
    
    # Get trial balance
    trial_balance = get_trial_balance(session)
    
    if not trial_balance.empty:
        # Filter options
        category_filter = st.selectbox(
            "Filter by Category",
            ["All"] + list(trial_balance['Category'].unique())
        )
        
        # Apply filters
        filtered_df = trial_balance.copy()
        if category_filter != "All":
            filtered_df = filtered_df[filtered_df['Category'] == category_filter]
        
        # Create a display dataframe without Account ID
        display_df = filtered_df[['Account Code', 'Account Name', 'Category', 'Balance']].copy()
        
        # Format the balance column
        display_df['Balance'] = display_df['Balance'].apply(lambda x: f"CHF {x:,.2f}")
        
        # Display the dataframe
        st.dataframe(display_df, width="stretch")
        
        # Account selection for details
        st.markdown("---")
        st.subheader("Account Details")
        
        # Create account selection dropdown
        account_options = {}
        for _, row in filtered_df.iterrows():
            account_label = f"{row['Account Code']} - {row['Account Name']}"
            account_options[account_label] = row['Account ID']
        
        if account_options:
            selected_account_label = st.selectbox(
                "Select an account to view details",
                list(account_options.keys())
            )
            
            if selected_account_label:
                selected_account_id = account_options[selected_account_label]
                
                # Get account entries
                entries_df = get_account_entries(session, selected_account_id)
                
                if not entries_df.empty:
                    # Display account balance
                    account_balance = get_account_balance(session, selected_account_id)
                    st.metric("Account Balance", f"CHF {account_balance:,.2f}")
                    
                    st.subheader(f"Entries for {selected_account_label}")
                    
                    # Prepare display dataframe with formatted amount column
                    display_df = entries_df.copy()
                    
                    # Create a single Amount column with + for debits and - for credits
                    display_df['Amount'] = display_df.apply(
                        lambda row: f"+CHF {row['Debit']:,.2f}" if row['Debit'] > 0 else f"-CHF {row['Credit']:,.2f}",
                        axis=1
                    )
                    
                    # Select and reorder columns for display
                    display_df = display_df[['Date', 'Description', 'Counterparty', 'Amount']]
                    
                    # Display using st.table for better formatting
                    st.table(display_df)
                else:
                    st.info("No entries found for this account.")
            
    else:
        st.info("No account balances to display. Add some journal entries first.")
    
    session.close()
