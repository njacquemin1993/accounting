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
        st.dataframe(display_df, use_container_width=True)
        
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
                    
                    # Prepare display dataframe
                    display_entries = entries_df[['Date', 'Description', 'Reference', 'Counterparty', 'Debit', 'Credit']].copy()
                    
                    # Format amounts with color coding
                    def format_amount(row):
                        if row['Debit'] > 0:
                            return f"<span style='color: black;'>+CHF {row['Debit']:,.2f}</span>"
                        elif row['Credit'] > 0:
                            return f"<span style='color: red;'>-CHF {row['Credit']:,.2f}</span>"
                        return ""
                    
                    # Create HTML table for styled display
                    html_table = "<table style='width:100%; border-collapse: collapse;'>"
                    html_table += "<thead><tr style='background-color: #f0f2f6;'>"
                    html_table += "<th style='padding: 10px; text-align: left; border-bottom: 2px solid #ddd;'>Date</th>"
                    html_table += "<th style='padding: 10px; text-align: left; border-bottom: 2px solid #ddd;'>Description</th>"
                    html_table += "<th style='padding: 10px; text-align: left; border-bottom: 2px solid #ddd;'>Reference</th>"
                    html_table += "<th style='padding: 10px; text-align: left; border-bottom: 2px solid #ddd;'>Counterparty</th>"
                    html_table += "<th style='padding: 10px; text-align: right; border-bottom: 2px solid #ddd;'>Amount</th>"
                    html_table += "</tr></thead><tbody>"
                    
                    for _, row in entries_df.iterrows():
                        html_table += "<tr style='border-bottom: 1px solid #eee;'>"
                        html_table += f"<td style='padding: 8px;'>{row['Date']}</td>"
                        html_table += f"<td style='padding: 8px;'>{row['Description']}</td>"
                        html_table += f"<td style='padding: 8px;'>{row['Reference']}</td>"
                        html_table += f"<td style='padding: 8px;'>{row['Counterparty']}</td>"
                        
                        if row['Debit'] > 0:
                            html_table += f"<td style='padding: 8px; text-align: right; color: black;'>+CHF {row['Debit']:,.2f}</td>"
                        else:
                            html_table += f"<td style='padding: 8px; text-align: right; color: red;'>-CHF {row['Credit']:,.2f}</td>"
                        
                        html_table += "</tr>"
                    
                    html_table += "</tbody></table>"
                    
                    st.markdown(html_table, unsafe_allow_html=True)
                else:
                    st.info("No entries found for this account.")
            
    else:
        st.info("No account balances to display. Add some journal entries first.")
    
    session.close()
