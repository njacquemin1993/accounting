"""
Journal Entries page for navigation.
"""

import streamlit as st
from database import DatabaseManager
from tabs import manage_journal_entries
from translation_utils import t, language_selector


@st.cache_resource
def get_database():
    db_manager = DatabaseManager()
    db_manager.initialize_default_accounts()
    return db_manager


# Page header with language selector
header_col1, header_col2 = st.columns([3, 1])

with header_col1:
    st.title(f"💰 {t('app_title')}")

with header_col2:
    st.markdown("<br>", unsafe_allow_html=True)
    language_selector()

st.markdown("---")

# Initialize database and show content
db_manager = get_database()
manage_journal_entries(db_manager)
