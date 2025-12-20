"""
Account Balances tab functionality.
"""

import streamlit as st
from accounting_utils import get_trial_balance, get_account_entries, get_account_balance
from translation_utils import t


def view_account_balances(db_manager):
    """Tab for viewing account balances."""
    st.header(t("account_balances"))

    session = db_manager.get_session()

    # Get trial balance
    trial_balance = get_trial_balance(session)

    if not trial_balance.empty:
        # Create translation mapping for categories
        category_display_map = {
            "Active": t("active"),
            "Passive": t("passive"),
            "Expenses": t("expenses"),
            "Products": t("products"),
        }

        # Get unique categories and translate them
        unique_categories = trial_balance["Category"].unique()
        translated_categories = [
            category_display_map.get(cat, cat) for cat in unique_categories
        ]

        # Filter options
        category_filter = st.selectbox(
            t("filter_by_category"), [t("all")] + translated_categories
        )

        # Apply filters - need to map back to database category if not "All"
        filtered_df = trial_balance.copy()
        if category_filter != t("all"):
            # Find the database category that corresponds to the selected translated category
            db_category = None
            for db_cat, trans_cat in category_display_map.items():
                if trans_cat == category_filter:
                    db_category = db_cat
                    break
            if db_category:
                filtered_df = filtered_df[filtered_df["Category"] == db_category]

        # Create a display dataframe without Account ID and with translated categories
        display_df = filtered_df[
            ["Account Code", "Account Name", "Category", "Balance"]
        ].copy()

        # Translate categories in display dataframe
        display_df["Category"] = display_df["Category"].map(category_display_map)

        # Translate column headers
        display_df = display_df.rename(
            columns={
                "Account Code": t("code"),
                "Account Name": t("name"),
                "Category": t("category"),
                "Balance": t("balance"),
            }
        )

        # Format the balance column
        display_df[t("balance")] = display_df[t("balance")].apply(
            lambda x: f"CHF {x:,.2f}"
        )

        # Display the dataframe
        st.dataframe(display_df, width="stretch")

        # Account selection for details
        st.markdown("---")
        st.subheader(t("account_details"))

        # Create account selection dropdown
        account_options = {}
        for _, row in filtered_df.iterrows():
            account_label = f"{row['Account Code']} - {row['Account Name']}"
            account_options[account_label] = row["Account ID"]

        if account_options:
            selected_account_label = st.selectbox(
                t("select_account"), list(account_options.keys())
            )

            if selected_account_label:
                selected_account_id = account_options[selected_account_label]

                # Get account entries
                entries_df = get_account_entries(session, selected_account_id)

                if not entries_df.empty:
                    # Display account balance
                    account_balance = get_account_balance(session, selected_account_id)
                    st.metric(t("account_balance"), f"CHF {account_balance:,.2f}")

                    st.subheader(f"{t('entries_for')} {selected_account_label}")

                    # Prepare display dataframe with formatted amount column
                    display_df = entries_df.copy()

                    # Create a single Amount column with + for debits and - for credits
                    display_df["Amount"] = display_df.apply(
                        lambda row: f"+CHF {row['Debit']:,.2f}"
                        if row["Debit"] > 0
                        else f"-CHF {row['Credit']:,.2f}",
                        axis=1,
                    )

                    # Select and reorder columns for display, then translate headers
                    display_df = display_df[
                        ["Date", "Description", "Counterparty", "Amount"]
                    ]
                    display_df = display_df.rename(
                        columns={
                            "Date": t("date"),
                            "Description": t("description"),
                            "Counterparty": t("counterparty"),
                            "Amount": t("amount"),
                        }
                    )

                    # Display using st.table for better formatting
                    st.table(display_df)
                else:
                    st.info(t("no_entries_found"))

    else:
        st.info(t("no_balances_display"))

    session.close()
