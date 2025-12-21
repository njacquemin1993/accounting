"""
Database switching and management utilities.
Handles multiple databases stored on the server.
"""

import os
import streamlit as st
import sqlite3
from datetime import datetime
from pathlib import Path
from accountr.database import DatabaseManager
from accountr.constants import (
    DEFAULT_SERVER_FILES_DIR,
    DEFAULT_DB_NAME,
    DATABASE_EXTENSION,
)
from accountr.translation_utils import t


class DatabaseSwitcher:
    """Manages switching between multiple databases stored on the server."""

    def __init__(self):
        self.server_dir = Path(DEFAULT_SERVER_FILES_DIR)
        self.server_dir.mkdir(exist_ok=True)

    def get_default_db_path(self):
        """Get the path to the default database."""
        return self.server_dir / DEFAULT_DB_NAME

    def get_available_databases(self):
        """Get list of available database files on the server."""
        if not self.server_dir.exists():
            return []

        db_files = []
        for file in self.server_dir.glob(f"*{DATABASE_EXTENSION}"):
            db_files.append(file.stem)  # Get filename without extension

        return sorted(db_files)

    def get_download_data(self, db_name=None):
        """
        Get database file data for download.

        Returns:
            bytes: Database file content
        """
        try:
            if db_name is None:
                db_path = self.get_current_database_path()
            else:
                db_path = self.server_dir / f"{db_name}{DATABASE_EXTENSION}"

            if not db_path.exists():
                return None

            with open(db_path, "rb") as f:
                return f.read()

        except Exception as e:
            print(f"Error getting download data: {e}")
            return None

    def get_database_info(self, db_name=None):
        """
        Get information about the database.

        Returns:
            dict: Database information
        """
        try:
            if db_name is None:
                db_path = self.get_current_database_path()
            else:
                db_path = self.server_dir / f"{db_name}{DATABASE_EXTENSION}"

            if not db_path.exists():
                return None

            stat = os.stat(db_path)

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Count accounts and journal entries
            cursor.execute("SELECT COUNT(*) FROM accounts WHERE is_active = 1")
            account_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM journal_entries")
            entry_count = cursor.fetchone()[0]

            conn.close()

            return {
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime),
                "accounts": account_count,
                "entries": entry_count,
            }

        except Exception as e:
            print(f"Error getting database info: {e}")
            return None

    def get_current_database(self):
        """Get the current database name from session state."""
        if "current_database" not in st.session_state:
            # Initialize with default database
            default_name = Path(DEFAULT_DB_NAME).stem
            st.session_state.current_database = default_name

            # Create default database if it doesn't exist
            default_path = self.get_default_db_path()
            if not default_path.exists():
                self.create_database(default_name)

        return st.session_state.current_database

    def get_current_database_path(self):
        """Get the full path to the current database."""
        current_db = self.get_current_database()
        return self.server_dir / f"{current_db}{DATABASE_EXTENSION}"

    def switch_database(self, database_name):
        """Switch to a different database."""
        if database_name in self.get_available_databases():
            st.session_state.current_database = database_name
            # Clear any cached database connections
            if "db_manager" in st.session_state:
                st.session_state.db_manager.dispose()
                del st.session_state.db_manager
            return True
        return False

    def load_database_from_file(self, uploaded_file):
        """
        Load database from uploaded file.

        Args:
            uploaded_file: Streamlit uploaded file object

        Returns:
            bool: Success status
        """
        try:
            target_path = self.server_files_dir / uploaded_file.name

            with target_path.open("wb") as f:
                f.write(uploaded_file.getvalue())

            # Validate it's a valid SQLite database
            if not self.validate_database(target_path):
                target_path.unlink()
                return False

            return True

        except Exception as e:
            print(f"Error loading database from file: {e}")
            # Cleanup temp file if it exists
            if target_path.exists():
                target_path.unlink()
            return False

    def create_database(self, database_name):
        """Create a new database with the given name."""
        if not database_name or len(database_name.strip()) == 0:
            return False, t("database_name_required")

        # Sanitize the database name
        database_name = database_name.strip()
        if len(database_name) > 50:
            return False, t("database_name_too_long")

        # Remove any invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            database_name = database_name.replace(char, "_")

        db_path = self.server_dir / f"{database_name}{DATABASE_EXTENSION}"

        if db_path.exists():
            return False, t("database_already_exists")

        try:
            # Create the database
            db_manager = DatabaseManager(str(db_path))
            db_manager.create_tables()
            db_manager.dispose()
            return True, t("database_created_successfully")
        except Exception as e:
            return False, f"{t('database_creation_error')}: {str(e)}"

    def delete_database(self, database_name):
        """Delete a database (except the default one)."""
        if database_name == Path(DEFAULT_DB_NAME).stem:
            return False, t("cannot_delete_default_database")

        db_path = self.server_dir / f"{database_name}{DATABASE_EXTENSION}"
        if not db_path.exists():
            return False, t("database_not_found")

        try:
            # If this is the current database, switch to default
            if database_name == self.get_current_database():
                self.switch_database(Path(DEFAULT_DB_NAME).stem)

            db_path.unlink()
            return True, t("database_deleted_successfully")
        except Exception as e:
            return False, f"{t('database_deletion_error')}: {str(e)}"

    def get_database_manager(self):
        """Get a DatabaseManager instance for the current database."""
        current_path = self.get_current_database_path()
        return DatabaseManager(str(current_path))


def get_current_db_manager():
    """Get the current database manager, creating it if necessary."""
    if "db_switcher" not in st.session_state:
        st.session_state.db_switcher = DatabaseSwitcher()

    if "db_manager" not in st.session_state:
        st.session_state.db_manager = st.session_state.db_switcher.get_database_manager()

    return st.session_state.db_manager


def refresh_db_manager():
    """Refresh the database manager (useful after switching databases)."""
    if "db_manager" in st.session_state:
        st.session_state.db_manager.dispose()
        del st.session_state.db_manager

    if "db_switcher" in st.session_state:
        st.session_state.db_manager = st.session_state.db_switcher.get_database_manager()
