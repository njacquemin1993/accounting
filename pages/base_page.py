import streamlit as st
from streamlit.navigation.page import StreamlitPage
from translation_utils import language_selector
from abc import abstractmethod
from translation_utils import t
from database_switcher import get_current_db_manager


class BasePage(StreamlitPage):
    """Base page class with common functionality for all pages."""

    def __init__(self, title: str, icon: str):
        super().__init__(self.run, title=t(title), icon=icon, url_path=title)

    def _header(self, title: str):
        """Display page header with language selector and file management in the same row."""
        header_col1, header_col2 = st.columns([3, 1])
        with header_col1:
            st.title(t(title))

        with header_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            language_selector()

        st.markdown("---")

    def _footer(self):
        """Display page footer."""
        st.markdown("---")
        st.markdown(
            "💼 **Accounting Application** | "
            "[GitHub Repository](https://github.com/your-repo)"
        )

    def run(self):
        """Run the page with header and content."""

        self._header(f"{self.icon} {self.title}")
        manager = get_current_db_manager()
        session = manager.get_session()
        try:
            self.content(session)
        finally:
            session.close()
        self._footer()

    @abstractmethod
    def content(self, session):
        """Method to be overridden by subclasses to display page content."""
        pass
