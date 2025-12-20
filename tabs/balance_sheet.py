"""
Balance Sheet tab functionality.
"""
import streamlit as st
import pandas as pd
from accounting_utils import get_balance_sheet_data, get_income_statement_data
from translation_utils import t

def view_balance_sheet(db_manager):
    """Tab for viewing balance sheet."""
    st.header(t("balance_sheet"))
    
    session = db_manager.get_session()
    
    balance_sheet_data = get_balance_sheet_data(session)
    income_statement_data = get_income_statement_data(session)
    
    # Calculate table heights to align totals
    active_rows = len(balance_sheet_data['active']) + 2  # active + blank + total
    passive_rows = len(balance_sheet_data['passive']) + 2  # passive + blank + total
    
    # Add net income line if not zero
    if abs(income_statement_data['net_income']) > 0.01:
        passive_rows += 2  # net income line + blank line
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(t("active_title"))
        if balance_sheet_data['active']:
            # Create DataFrame for active accounts
            active_data = []
            for account in balance_sheet_data['active']:
                active_data.append({
                    t('account_column'): f"{account['code']} - {account['name']}",
                    t('amount_column'): f"CHF {account['balance']:,.2f}"
                })
            
            # Add blank lines if active table is shorter
            if active_rows < passive_rows:
                blank_lines_needed = passive_rows - active_rows
                for _ in range(blank_lines_needed):
                    active_data.append({
                        t('account_column'): '',
                        t('amount_column'): ''
                    })
            
            # Add spacing and total
            active_data.append({
                t('account_column'): '',
                t('amount_column'): ''
            })
            active_data.append({
                t('account_column'): t('total_active'),
                t('amount_column'): f"CHF {balance_sheet_data['total_active']:,.2f}"
            })
            
            active_df = pd.DataFrame(active_data)
            
            # Display table without index
            st.table(active_df)
        else:
            st.write(t("no_active_accounts_display"))
    
    with col2:
        st.subheader(t("passive_title"))
        
        # Create DataFrame for passive accounts
        passive_data = []
        
        # Add passive accounts
        if balance_sheet_data['passive']:
            for account in balance_sheet_data['passive']:
                passive_data.append({
                    t('account_column'): f"{account['code']} - {account['name']}",
                    t('amount_column'): f"CHF {account['balance']:,.2f}"
                })
        
        # Add spacing
        passive_data.append({
            t('account_column'): '',
            t('amount_column'): ''
        })
        
        # Add net income/loss if not zero
        net_income = income_statement_data['net_income']
        if abs(net_income) > 0.01:
            if net_income >= 0:
                passive_data.append({
                    t('account_column'): t('retained_earnings'),
                    t('amount_column'): f"CHF {net_income:,.2f}"
                })
            else:
                passive_data.append({
                    t('account_column'): t('retained_earnings'),
                    t('amount_column'): f"CHF {net_income:,.2f}"
                })
        
        # Add blank lines if passive table is shorter
        if passive_rows < active_rows:
            blank_lines_needed = active_rows - passive_rows
            for _ in range(blank_lines_needed):
                passive_data.append({
                    t('account_column'): '',
                    t('amount_column'): ''
                })
        
        # Calculate total including net income
        total_passive_with_net_income = balance_sheet_data['total_passive'] + net_income
        
        # Add spacing and grand total
        passive_data.append({
            t('account_column'): '',
            t('amount_column'): ''
        })
        passive_data.append({
            t('account_column'): t('total_passive'),
            t('amount_column'): f"CHF {total_passive_with_net_income:,.2f}"
        })
        
        if passive_data:
            passive_df = pd.DataFrame(passive_data)
            
            # Display table without index
            st.table(passive_df)
        else:
            st.write(t("no_passive_accounts_display"))
    
    # Balance check
    st.markdown("---")
    total_passive_with_net_income = balance_sheet_data['total_passive'] + income_statement_data['net_income']
    difference = balance_sheet_data['total_active'] - total_passive_with_net_income
    if abs(difference) < 0.01:  # Allow for small rounding differences
        st.success(t("balance_sheet_balanced_checkmark"))
    else:
        st.error(f"{t('balance_sheet_not_balanced_x')} CHF {difference:,.2f}")
    
    # Show net income impact
    if abs(income_statement_data['net_income']) > 0.01:
        if income_statement_data['net_income'] >= 0:
            st.info(f"{t('net_income_info')} CHF {income_statement_data['net_income']:,.2f} {t('has_been_included_in_passive')}")
        else:
            st.warning(f"{t('net_loss_warning')} CHF {abs(income_statement_data['net_income']):,.2f} {t('has_been_included_in_passive')}")
    
    session.close()
