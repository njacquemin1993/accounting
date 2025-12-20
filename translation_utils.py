"""
Translation utilities for the accounting application.
"""

import streamlit as st
from translations import get_translation, get_available_languages


def init_language():
    """Initialize language in session state."""
    if "language" not in st.session_state:
        st.session_state.language = "en"


def get_current_language():
    """Get current language from session state."""
    init_language()
    return st.session_state.language


def set_language(language):
    """Set current language in session state."""
    st.session_state.language = language


def t(key: str) -> str:
    """Translate a key using current language."""
    return get_translation(key, get_current_language())


def language_selector():
    """Display language selector in sidebar."""
    init_language()

    languages = get_available_languages()
    current_lang = get_current_language()

    # Find current language display name
    current_display = languages.get(current_lang, "English")

    selected_display = st.selectbox(
        t("language_selector"),
        list(languages.values()),
        index=list(languages.values()).index(current_display),
        key="language_selectbox",
    )

    # Find selected language code
    selected_lang = None
    for code, display in languages.items():
        if display == selected_display:
            selected_lang = code
            break

    if selected_lang and selected_lang != current_lang:
        set_language(selected_lang)
        st.rerun()
