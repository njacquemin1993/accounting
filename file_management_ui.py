"""
File management UI components for the accounting application.
"""

import streamlit as st
from file_manager import FileManager
from datetime import datetime
from translation_utils import t


@st.dialog(t("file_management"), width="large")
def show_file_management_dialog():
    """Show file management dialog."""
    file_manager = FileManager()

    # Current database info
    st.subheader(t("current_database"))
    db_info = file_manager.get_database_info()

    if db_info:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(t("accounts"), db_info["accounts"])
        with col2:
            st.metric(
                t("entries_for").replace(" for", ""), db_info["entries"]
            )  # Use entries translation
        with col3:
            size_mb = db_info["size"] / (1024 * 1024)
            st.metric(t("size"), f"{size_mb:.2f} MB")

        st.write(
            f"**{t('last_modified')}:** {db_info['modified'].strftime('%Y-%m-%d %H:%M:%S')}"
        )

    st.markdown("---")

    # File operations
    tab1, tab2, tab3 = st.tabs(
        [
            t("create_new_database"),
            t("load_from_computer"),
            t("download_database"),
        ]
    )

    with tab1:
        st.warning(t("confirm_new_database"))
        if st.button(t("create_new_database"), type="primary", key="create_new"):
            # Clear all cached database connections first
            # Clear all session state that might contain database objects
            keys_to_clear = []
            for key in st.session_state.keys():
                if "database" in key.lower() or "session" in key.lower():
                    keys_to_clear.append(key)

            for key in keys_to_clear:
                del st.session_state[key]

            # Force garbage collection to close any remaining connections
            import gc

            gc.collect()

            if file_manager.create_new_database():
                st.success(t("database_created"))
                st.rerun()
            else:
                st.error(t("database_error"))

    with tab2:
        st.info(t("select_database_file"))
        uploaded_file = st.file_uploader(
            t("select_database_file"),
            type=["db", "sqlite", "sqlite3"],
            label_visibility="collapsed",
        )

        if uploaded_file is not None:
            st.warning(t("confirm_load_database"))
            if st.button(t("load_from_computer"), type="primary", key="load_computer"):
                # Clear all cached database connections first
                keys_to_clear = []
                for key in st.session_state.keys():
                    if "database" in key.lower() or "session" in key.lower():
                        keys_to_clear.append(key)

                for key in keys_to_clear:
                    del st.session_state[key]

                # Force garbage collection
                import gc

                gc.collect()

                if file_manager.load_database_from_file(uploaded_file):
                    st.success(t("database_loaded"))
                    st.rerun()
                else:
                    st.error(t("invalid_database_file"))

    with tab3:
        st.info(t("download_info"))

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"accounting_backup_{timestamp}.db"

        # Get database data
        db_data = file_manager.get_download_data()

        if db_data:
            st.download_button(
                label=t("download_database"),
                data=db_data,
                file_name=filename,
                mime="application/octet-stream",
                type="primary",
                use_container_width=True,
            )
        else:
            st.error(t("database_error"))

    # Close button
    st.markdown("---")
    if st.button(t("close"), use_container_width=True):
        st.rerun()


def file_management_button():
    """Display compact file management button."""
    if st.button("📁", help=t("file_management"), use_container_width=True):
        show_file_management_dialog()
