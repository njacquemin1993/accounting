"""
File management utilities for the accounting application.
"""

import os
import shutil
import sqlite3
import time
import gc
from datetime import datetime
from database import DatabaseManager
from constants import (
    DEFAULT_DB_PATH,
    DEFAULT_SERVER_FILES_DIR,
    FILE_OPERATION_MAX_ATTEMPTS,
    FILE_OPERATION_RETRY_DELAY,
    FILE_MOVE_MAX_ATTEMPTS,
    FILE_CLOSE_DELAY,
)


class FileManager:
    """Handles database file operations."""

    def __init__(
        self, current_db_path=DEFAULT_DB_PATH, server_files_dir=DEFAULT_SERVER_FILES_DIR
    ):
        self.current_db_path = current_db_path
        self.server_files_dir = server_files_dir
        self.ensure_server_directory()

    def ensure_server_directory(self):
        """Create server files directory if it doesn't exist."""
        if not os.path.exists(self.server_files_dir):
            os.makedirs(self.server_files_dir)

    def create_new_database(self, file_path=None):
        """
        Create a new empty database.

        Args:
            file_path: Optional path for the new database. If None, uses current path.

        Returns:
            bool: Success status
        """
        try:
            target_path = file_path or self.current_db_path

            # Create a temporary new database first
            temp_path = f"temp_new_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

            # Create new empty database with just the schema
            db_manager = DatabaseManager(db_path=temp_path)
            # Don't initialize default accounts - keep it completely empty

            # IMPORTANT: Dispose of the engine and close all connections
            db_manager.dispose()
            del db_manager

            # Force garbage collection to ensure all connections are closed
            gc.collect()

            # Small delay to ensure file handles are released
            time.sleep(FILE_CLOSE_DELAY)

            # Now safely replace the existing database
            if os.path.exists(target_path):
                # Try to remove the existing file
                for attempt in range(FILE_OPERATION_MAX_ATTEMPTS):
                    try:
                        os.remove(target_path)
                        break
                    except PermissionError:
                        if attempt < FILE_OPERATION_MAX_ATTEMPTS - 1:
                            # Wait a bit and try again
                            time.sleep(FILE_OPERATION_RETRY_DELAY)
                        else:
                            # If we can't remove it, try to overwrite it
                            try:
                                shutil.move(temp_path, target_path)
                                return True
                            except Exception as e:
                                print(f"Error replacing database file: {e}")
                                if os.path.exists(temp_path):
                                    os.remove(temp_path)
                                return False

            # Move the temp database to the target location
            for attempt in range(FILE_MOVE_MAX_ATTEMPTS):
                try:
                    shutil.move(temp_path, target_path)
                    return True
                except PermissionError as e:
                    if attempt < FILE_MOVE_MAX_ATTEMPTS - 1:
                        print(f"Attempt {attempt + 1} failed, retrying in {FILE_OPERATION_RETRY_DELAY}s: {e}")
                        time.sleep(FILE_OPERATION_RETRY_DELAY)
                    else:
                        print(
                            f"Error moving temp file after {FILE_MOVE_MAX_ATTEMPTS} attempts: {e}"
                        )
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                        return False

        except Exception as e:
            print(f"Error creating new database: {e}")
            # Cleanup temp file if it exists
            if "temp_path" in locals() and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
            return False

    def load_database_from_file(self, uploaded_file, target_path=None):
        """
        Load database from uploaded file.

        Args:
            uploaded_file: Streamlit uploaded file object
            target_path: Target path for the database. If None, uses current path.

        Returns:
            bool: Success status
        """
        try:
            target_path = target_path or self.current_db_path

            # Save uploaded file temporarily
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getvalue())

            # Validate it's a valid SQLite database
            if not self.validate_database(temp_path):
                os.remove(temp_path)
                return False

            # Replace current database
            shutil.move(temp_path, target_path)
            return True

        except Exception as e:
            print(f"Error loading database from file: {e}")
            # Cleanup temp file if it exists
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return False

    def load_database_from_server(self, server_filename, target_path=None):
        """
        Load database from server files directory.

        Args:
            server_filename: Name of the file in server directory
            target_path: Target path for the database. If None, uses current path.

        Returns:
            bool: Success status
        """
        try:
            target_path = target_path or self.current_db_path
            source_path = os.path.join(self.server_files_dir, server_filename)

            if not os.path.exists(source_path):
                return False

            # Validate it's a valid SQLite database
            if not self.validate_database(source_path):
                return False

            # Copy server file to current location
            shutil.copy2(source_path, target_path)
            return True

        except Exception as e:
            print(f"Error loading database from server: {e}")
            return False

    def get_server_files(self):
        """
        Get list of database files in server directory.

        Returns:
            list: List of database filenames
        """
        try:
            if not os.path.exists(self.server_files_dir):
                return []

            files = []
            for filename in os.listdir(self.server_files_dir):
                filepath = os.path.join(self.server_files_dir, filename)
                if filename.endswith(".db") and self.validate_database(filepath):
                    # Get file info
                    stat = os.stat(filepath)
                    size = stat.st_size
                    modified = datetime.fromtimestamp(stat.st_mtime)
                    files.append(
                        {"filename": filename, "size": size, "modified": modified}
                    )

            # Sort by modification date (newest first)
            files.sort(key=lambda x: x["modified"], reverse=True)
            return files

        except Exception as e:
            print(f"Error getting server files: {e}")
            return []

    def save_to_server(self, filename, source_path=None):
        """
        Save current database to server directory.

        Args:
            filename: Name for the saved file
            source_path: Source path of the database. If None, uses current path.

        Returns:
            bool: Success status
        """
        try:
            source_path = source_path or self.current_db_path

            if not os.path.exists(source_path):
                return False

            # Ensure filename has .db extension
            if not filename.endswith(".db"):
                filename += ".db"

            target_path = os.path.join(self.server_files_dir, filename)
            shutil.copy2(source_path, target_path)
            return True

        except Exception as e:
            print(f"Error saving to server: {e}")
            return False

    def validate_database(self, db_path):
        """
        Validate that a file is a proper SQLite database with required tables.

        Args:
            db_path: Path to the database file

        Returns:
            bool: True if valid, False otherwise
        """
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Check if required tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [table[0] for table in cursor.fetchall()]

            required_tables = ["accounts", "journal_entries"]
            has_required_tables = all(table in tables for table in required_tables)

            conn.close()
            return has_required_tables

        except Exception:
            return False

    def get_database_info(self, db_path=None):
        """
        Get information about the database.

        Args:
            db_path: Path to the database. If None, uses current path.

        Returns:
            dict: Database information
        """
        try:
            db_path = db_path or self.current_db_path

            if not os.path.exists(db_path):
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

    def get_download_data(self, db_path=None):
        """
        Get database file data for download.

        Args:
            db_path: Path to the database. If None, uses current path.

        Returns:
            bytes: Database file content
        """
        try:
            db_path = db_path or self.current_db_path

            if not os.path.exists(db_path):
                return None

            with open(db_path, "rb") as f:
                return f.read()

        except Exception as e:
            print(f"Error getting download data: {e}")
            return None
