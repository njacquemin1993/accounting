"""
Database management UI components.
Provides interface for switching between databases and creating new ones.
"""

import streamlit as st
from accountr.database_switcher import DatabaseSwitcher
from accountr.translation_utils import t


def render_database_switcher_sidebar():
    """Render the database switcher in the sidebar."""
    with st.sidebar:
        st.markdown("---")
        st.subheader(t("database_management"))

        # Initialize database switcher
        if "db_switcher" not in st.session_state:
            st.session_state.db_switcher = DatabaseSwitcher()

        db_switcher = st.session_state.db_switcher

        # Current database display
        current_db = db_switcher.get_current_database()
        st.info(f"{t('current_database')}: **{current_db}**")

        # Database selector
        available_databases = db_switcher.get_available_databases()

        if len(available_databases) > 1:
            selected_db = st.selectbox(
                t("switch_to_database"),
                available_databases,
                index=available_databases.index(current_db) if current_db in available_databases else 0,
                key="database_selector",
            )

            if selected_db != current_db:
                if st.button(t("switch_database"), type="primary"):
                    if db_switcher.switch_database(selected_db):
                        st.success(t("database_switched_successfully"))
                        st.rerun()
                    else:
                        st.error(t("database_switch_error"))

        # Create new database section
        with st.expander(t("create_new_database")):
            new_db_name = st.text_input(
                t("database_name"),
                placeholder=t("enter_database_name"),
                help=t("database_name_help"),
            )

            if st.button(t("create_database")):
                if new_db_name:
                    success, message = db_switcher.create_database(new_db_name)
                    if success:
                        st.success(message)
                        # Switch to the new database
                        db_switcher.switch_database(new_db_name)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error(t("database_name_required"))

        # Delete database section (only show if there are multiple databases)
        if len(available_databases) > 1:
            with st.expander(t("delete_database")):
                # Don't allow deleting the current database or default database
                deletable_databases = [db for db in available_databases if db != current_db]

                if deletable_databases:
                    db_to_delete = st.selectbox(
                        t("select_database_to_delete"),
                        deletable_databases,
                        key="database_deleter",
                    )

                    st.warning(t("delete_database_warning"))

                    if st.button(t("delete_database_confirm"), type="secondary"):
                        success, message = db_switcher.delete_database(db_to_delete)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                else:
                    st.info(t("no_deletable_databases"))


def render_database_switcher_main():
    """Render the database switcher in the main area (for dedicated database management page)."""
    st.title(t("database_management"))

    # Initialize database switcher
    if "db_switcher" not in st.session_state:
        st.session_state.db_switcher = DatabaseSwitcher()

    db_switcher = st.session_state.db_switcher

    # Current database info
    current_db = db_switcher.get_current_database()
    current_path = db_switcher.get_current_database_path()

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader(t("current_database"))
        st.info(f"**{t('database_name')}**: {current_db}")
        st.info(f"**{t('database_path')}**: {current_path}")

    with col2:
        # Database statistics
        try:
            db_manager = db_switcher.get_database_manager()
            with db_manager.get_session() as session:
                from accountr.database import Account, JournalEntry

                account_count = session.query(Account).count()
                entry_count = session.query(JournalEntry).count()

            st.metric(t("total_accounts"), account_count)
            st.metric(t("total_entries"), entry_count)
        except Exception:
            st.warning(t("unable_to_load_stats"))

    st.markdown("---")

    # Available databases
    st.subheader(t("available_databases"))
    available_databases = db_switcher.get_available_databases()

    if not available_databases:
        st.info(t("no_databases_found"))
    else:
        # Display databases in a table-like format
        for db_name in available_databases:
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                if db_name == current_db:
                    st.markdown(f"**{db_name}** ✅ *({t('current')})*")
                else:
                    st.markdown(f"**{db_name}**")

            with col2:
                if db_name != current_db:
                    if st.button(t("switch"), key=f"switch_{db_name}"):
                        if db_switcher.switch_database(db_name):
                            st.success(t("database_switched_successfully"))
                            st.rerun()
                        else:
                            st.error(t("database_switch_error"))

            with col3:
                if db_name != current_db:
                    if st.button("🗑️", key=f"delete_{db_name}", help=t("delete_database")):
                        # Add confirmation
                        if f"confirm_delete_{db_name}" not in st.session_state:
                            st.session_state[f"confirm_delete_{db_name}"] = True
                            st.rerun()

        # Handle deletion confirmations
        for db_name in available_databases:
            if f"confirm_delete_{db_name}" in st.session_state:
                st.error(f"{t('confirm_delete_database')}: **{db_name}**")
                col1, col2, col3 = st.columns([1, 1, 1])

                with col1:
                    if st.button(t("yes_delete"), key=f"yes_delete_{db_name}", type="primary"):
                        success, message = db_switcher.delete_database(db_name)
                        if success:
                            st.success(message)
                            del st.session_state[f"confirm_delete_{db_name}"]
                            st.rerun()
                        else:
                            st.error(message)

                with col2:
                    if st.button(t("cancel"), key=f"cancel_delete_{db_name}"):
                        del st.session_state[f"confirm_delete_{db_name}"]
                        st.rerun()

    st.markdown("---")

    # Create new database
    st.subheader(t("create_new_database"))

    col1, col2 = st.columns([2, 1])

    with col1:
        new_db_name = st.text_input(
            t("database_name"),
            placeholder=t("enter_database_name"),
            help=t("database_name_help"),
        )

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
        if st.button(t("create_database"), type="primary"):
            if new_db_name:
                success, message = db_switcher.create_database(new_db_name)
                if success:
                    st.success(message)
                    # Switch to the new database
                    db_switcher.switch_database(new_db_name)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error(t("database_name_required"))
