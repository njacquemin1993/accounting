"""
Translation utilities for the accounting application.
"""

import streamlit as st
from translations import get_translation, get_available_languages


def init_language():
    """Initialize language in session state, checking URL params first."""
    # Check if language is in URL query parameters
    query_params = st.query_params
    url_language = query_params.get("lang", None)
    
    if "language" not in st.session_state:
        # Use URL language if available, otherwise default to English
        if url_language and url_language in ["en", "fr", "de"]:
            st.session_state.language = url_language
        else:
            st.session_state.language = "en"
    
    # Update URL to reflect current language if it's different
    current_url_lang = query_params.get("lang", None)
    if current_url_lang != st.session_state.language:
        st.query_params["lang"] = st.session_state.language


def get_current_language():
    """Get current language from session state."""
    init_language()
    return st.session_state.language


def set_language(language):
    """Set current language in session state and update URL."""
    st.session_state.language = language
    st.query_params["lang"] = language


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
        key="language_selectbox"
    )

    # Find selected language code and update if changed
    selected_lang = None
    for code, display in languages.items():
        if display == selected_display:
            selected_lang = code
            break
    
    # Update language and rerun to refresh translations
    if selected_lang and selected_lang != current_lang:
        set_language(selected_lang)
        st.rerun()
