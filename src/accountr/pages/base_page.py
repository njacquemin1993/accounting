import streamlit as st
from streamlit.navigation.page import StreamlitPage
from accountr.translation_utils import language_selector
from abc import abstractmethod
from accountr.translation_utils import t
from accountr.database_switcher import get_current_db_manager
from accountr.helpers import get_app_version


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
        """Display page footer with version and copyright information."""
        # Use CSS to push footer to bottom of viewport
        st.markdown(
            """
        <style>
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: rgb(255, 255, 255);
            border-top: 1px solid rgb(230, 234, 241);
            padding: 10px 0;
            z-index: 1000;
        }
        @media (prefers-color-scheme: dark) {
            .footer {
                background-color: rgb(14, 17, 23);
                border-top: 1px solid rgb(49, 51, 56);
            }
        }
        .main .block-container {
            padding-bottom: 80px;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
        <div class="footer">
            <div style="display: flex; justify-content: space-between;
            align-items: center;  margin: 0 auto; padding: 0 20px;">
                <div>💼 <strong>{} v{}</strong></div>
                <div>© 2025 Nicolas Jacquemin</div>
                <div>
            <a href="https://github.com/njacquemin1993/accounting" target="_blank" style="text-decoration: none;">
                GitHub Repository</a></div>
            </div>
        </div>
        """.format(t("app_title"), get_app_version()),
            unsafe_allow_html=True,
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
