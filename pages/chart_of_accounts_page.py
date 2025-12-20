"""
Chart of Accounts page for navigation.
"""

import streamlit as st
import pandas as pd
from database import DatabaseManager, Account
from translation_utils import t, language_selector


@st.cache_resource
def get_database():
    db_manager = DatabaseManager()
    db_manager.initialize_default_accounts()
    return db_manager


# Page header with language selector
header_col1, header_col2 = st.columns([3, 1])

with header_col1:
    st.title(f"📊 {t('chart_of_accounts')}")

with header_col2:
    st.markdown("<br>", unsafe_allow_html=True)
    language_selector()

st.markdown("---")

# Initialize database and show content
db_manager = get_database()

session = db_manager.get_session()

# Display existing accounts
accounts = (
    session.query(Account)
    .filter(Account.is_active)
    .order_by(Account.account_code)
    .all()
)

if accounts:
    account_data = []
    for account in accounts:
        # Map database category to translated category
        category_display_map = {
            "Active": t("active"),
            "Passive": t("passive"),
            "Expenses": t("expenses"),
            "Products": t("products"),
        }
        translated_category = category_display_map.get(
            account.category, account.category
        )

        account_data.append(
            {
                t("id"): account.id,
                t("code"): account.account_code,
                t("name"): account.account_name,
                t("category"): translated_category,
            }
        )

    df = pd.DataFrame(account_data)
    st.dataframe(df, width="stretch")
else:
    st.info(t("no_accounts_found"))

st.subheader(t("add_new_account"))

col1, col2, col3, col4 = st.columns(
    [0.2, 0.4, 0.2, 0.2], vertical_alignment="bottom"
)

with col1:
    account_code = st.text_input(t("account_code"), help=t("account_code_help"))
with col2:
    account_name = st.text_input(t("account_name"), help=t("account_name_help"))

with col3:
    category = st.selectbox(
        t("category"), [t("active"), t("passive"), t("expenses"), t("products")]
    )

with col4:
    if st.button(t("add_account"), width="stretch"):
        if account_code and account_name:
            # Check if account code already exists
            existing = (
                session.query(Account)
                .filter(Account.account_code == account_code)
                .first()
            )
            if existing:
                st.error(t("account_exists"))
            else:
                # Map translated category back to English for database storage
                category_map = {
                    t("active"): "Active",
                    t("passive"): "Passive",
                    t("expenses"): "Expenses",
                    t("products"): "Products",
                }
                db_category = category_map.get(category, "Active")

                new_account = Account(
                    account_code=account_code,
                    account_name=account_name,
                    category=db_category,
                )
                session.add(new_account)
                session.commit()
                st.success(t("account_added"))
                st.rerun()
        else:
            st.error(t("fill_all_fields"))

# Account deactivation section
st.subheader(t("deactivate_account"))
if accounts:
    account_options = {
        f"{acc.account_code} - {acc.account_name}": acc.id for acc in accounts
    }
    selected_account = st.selectbox(
        t("select_account_deactivate"), list(account_options.keys())
    )

    if st.button(t("deactivate_account"), type="secondary"):
        account_id = account_options[selected_account]
        account = session.query(Account).filter(Account.id == account_id).first()
        account.is_active = False
        session.commit()
        st.success(f"{t('account_deactivated')} {selected_account}")
        st.rerun()

session.close()
