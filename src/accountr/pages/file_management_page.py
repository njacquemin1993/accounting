"""
File management UI components for the accounting application.
"""

import streamlit as st
from datetime import datetime
from accountr.database_switcher import DatabaseSwitcher
from accountr.constants import FILE_LIST_COLUMNS_WIDTH, DATABASE_EXTENSION
from accountr.translation_utils import t
from accountr.pages.base_page import BasePage
from accountr.excel_export import create_excel_export


@st.dialog(t("export_as_excel"))
def export_db(db_name):
    """Show dialog to export current database as Excel."""

    st.info(t("export_excel_info"))
    st.write(f"**{t('database_name')}:** {db_name}")

    col1, col2 = st.columns([1, 1])

    with col1:
        with st.spinner(t("creating_excel_export")):
            try:
                excel_data = create_excel_export(db_name)
                if excel_data:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{db_name}_export_{timestamp}.xlsx"

                    if st.download_button(
                        label=t("download_excel"),
                        data=excel_data,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="download_excel_file",
                        width="stretch",
                        type="primary",
                    ):
                        st.rerun()
                else:
                    st.error(t("export_error"))
            except Exception as e:
                st.error(f"{t('export_error')}: {str(e)}")

    with col2:
        if st.button(
            t("cancel"),
            key="cancel_export_excel_dialog",
            width="stretch",
        ):
            st.rerun()


@st.dialog(t("delete_database"))
def delete_db(db_name):
    """Show dialog to confirm database deletion."""
    st.warning(t("confirm_delete_database") + f": **{db_name}**")
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button(t("yes_delete"), key=f"yes_delete_dialog_{db_name}", type="primary"):
            db_switcher = DatabaseSwitcher()
            success, message = db_switcher.delete_database(db_name)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    with col2:
        if st.button(t("cancel"), key=f"cancel_delete_dialog_{db_name}"):
            st.rerun()


def switch_db(db_name):
    db_switcher = DatabaseSwitcher()
    db_switcher.switch_database(db_name)
    st.rerun()


@st.dialog(t("download_database"))
def download_db(db_name):
    """Show dialog to confirm database download."""
    st.info(t("download") + f" {db_name}")
    db_switcher = DatabaseSwitcher()
    db_data = db_switcher.get_download_data(db_name)

    cols = st.columns([1, 1])
    with cols[0]:
        if st.download_button(
            label=t("download_database"),
            data=db_data,
            file_name=db_name + DATABASE_EXTENSION,
            mime="application/octet-stream",
            type="primary",
            width="stretch",
        ):
            st.success(t("database_download_started"))
            st.rerun()
    with cols[1]:
        if st.button(t("cancel"), key="cancel_download_dialog", width="stretch"):
            st.rerun()


@st.dialog(t("create_database"))
def create_db():
    st.info(t("enter_new_database_name"))
    new_db_name = st.text_input(
        t("database_name"),
        placeholder=t("enter_database_name"),
        help=t("database_name_help"),
        key="new_db_name_dialog",
    )

    switch_to_new = st.checkbox(t("switch_to_the_new_database"), key="confirm_create_db_dialog")

    if st.button(t("create_database"), type="primary", key="create_db_dialog"):
        if new_db_name:
            db_switcher = DatabaseSwitcher()
            success, message = db_switcher.create_database(new_db_name)
            if success:
                st.success(message)
                if switch_to_new:
                    db_switcher.switch_database(new_db_name)
                st.rerun()
            else:
                st.error(message)
        else:
            st.error(t("database_name_required"))


@st.dialog(t("upload_database"))
def upload_db():
    st.info(t("upload_database"))
    uploaded_file = st.file_uploader(t("choose_file"), type=[DATABASE_EXTENSION], key="upload_db_file")
    switch_to_new = st.checkbox(t("switch_to_the_new_database"), key="confirm_create_db_dialog")

    if st.button(t("upload"), type="primary", key="upload_db_button"):
        if uploaded_file:
            db_switcher = DatabaseSwitcher()
            success = db_switcher.load_database_from_file(uploaded_file)
            if success:
                st.success(t("database_uploaded_successfully"))
                if switch_to_new:
                    db_switcher.switch_database(uploaded_file.name)
                st.rerun()
            else:
                st.error(t("database_upload_failed"))
        else:
            st.error(t("no_file_selected"))


def db_info_line(db_switcher, db_name):
    current_db = db_switcher.get_current_database()
    db_info = db_switcher.get_database_info(db_name)
    if db_info:
        cols = st.columns(FILE_LIST_COLUMNS_WIDTH)
        with cols[0]:
            if db_name == current_db:
                st.markdown(f"{db_name} ✅ *({t('current')})*")
            else:
                st.markdown(db_name)

        with cols[1]:
            st.caption(db_info["modified"].strftime("%Y-%m-%d %H:%M:%S"))

        with cols[2]:
            st.caption(f"{db_info['size'] / (1024 * 1024):.2f} MB")

        with cols[3]:
            st.caption(db_info["accounts"])

        with cols[4]:
            st.caption(db_info["entries"])

        with cols[5]:
            choose_btn = st.button(
                "✔️",
                key=f"choose_db_{db_name}",
                help=t("choose_database"),
                disabled=(db_name == current_db),
            )

        with cols[6]:
            download_btn = st.button("💾", key=f"download_db_{db_name}", help=t("download_database"))

        with cols[7]:
            export_btn = st.button(
                "📊",
                key=f"export_db_{db_name}",
                help=t("export_as_excel"),
            )

        with cols[8]:
            delete_btn = st.button(
                "🗑️",
                key=f"delete_db_{db_name}",
                help=t("delete_database"),
                disabled=(db_name == current_db),
            )

        return choose_btn, download_btn, export_btn, delete_btn
    return False, False, False


def database_list():
    # Current database display
    db_switcher = st.session_state.db_switcher
    available_databases = db_switcher.get_available_databases()
    cols = st.columns(FILE_LIST_COLUMNS_WIDTH)

    with cols[0]:
        st.markdown(f"**{t('database_name')}**")
    with cols[1]:
        st.markdown(f"**{t('last_modified')}**")
    with cols[2]:
        st.markdown(f"**{t('size')}**")
    with cols[3]:
        st.markdown(f"**{t('total_accounts')}**")
    with cols[4]:
        st.markdown(f"**{t('total_entries')}**")

    buttons = {
        "choose": {},
        "download": {},
        "export": {},
        "delete": {},
    }

    for db_name in available_databases:
        (
            buttons["choose"][db_name],
            buttons["download"][db_name],
            buttons["export"][db_name],
            buttons["delete"][db_name],
        ) = db_info_line(db_switcher, db_name)

    for db_name, pressed in buttons["delete"].items():
        if pressed:
            delete_db(db_name)

    for db_name, pressed in buttons["choose"].items():
        if pressed:
            switch_db(db_name)

    for db_name, pressed in buttons["export"].items():
        if pressed:
            export_db(db_name)

    for db_name, pressed in buttons["download"].items():
        if pressed:
            download_db(db_name)


class FileManagementPage(BasePage):
    def __init__(self):
        super().__init__(title="file_management", icon="🗂️")

    def content(self, session):
        # Initialize database switcher
        if "db_switcher" not in st.session_state:
            st.session_state.db_switcher = DatabaseSwitcher()

        database_list()

        st.markdown("---")

        cols = st.columns(5)
        with cols[0]:
            if st.button(
                t("create_new_database"),
                key="create_db_tab",
                icon="➕",
                width="stretch",
            ):
                create_db()
        with cols[1]:
            if st.button(
                t("upload_database"),
                key="upload_db_tab",
                icon="📤",
                width="stretch",
            ):
                upload_db()
