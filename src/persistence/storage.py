"""
Storage management for checklists
Handles JSON file operations for saving and loading checklists
"""

import fcntl
import glob
import json
import logging
import os
from typing import Optional
from datetime import datetime

from ..models.checklist import Checklist
from ..utils.constants import Paths, Defaults

logger = logging.getLogger(__name__)


class ChecklistStorage:
    """Manages persistent storage of checklist data"""

    def __init__(self, file_path: Optional[str] = None):
        """
        Initialize storage manager

        Args:
            file_path: Path to the checklist JSON file (uses default if None)
        """
        self.file_path = file_path or Paths.DEFAULT_CHECKLIST_FILE

    def save_checklist(self, checklist: Checklist) -> bool:
        """
        Save checklist to JSON file

        Args:
            checklist: Checklist object to save

        Returns:
            True if successful, False otherwise
        """
        try:
            data = checklist.to_dict()
            os.makedirs(os.path.dirname(os.path.abspath(self.file_path)), exist_ok=True)
            with open(self.file_path, 'w', encoding='utf-8') as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                try:
                    json.dump(data, f, indent=2)
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)
            return True
        except Exception as e:
            logger.warning("Error saving checklist: %s", e)
            return False

    def load_checklist(self) -> Optional[Checklist]:
        """
        Load checklist from JSON file

        Returns:
            Checklist object if successful, None otherwise
        """
        if not os.path.exists(self.file_path):
            return None

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return Checklist.from_dict(data)
        except Exception as e:
            logger.warning("Error loading checklist: %s", e)
            return None

    def file_exists(self) -> bool:
        """
        Check if the checklist file exists

        Returns:
            True if file exists, False otherwise
        """
        return os.path.exists(self.file_path)

    def get_file_path(self) -> str:
        """
        Get the current file path

        Returns:
            Current file path
        """
        return self.file_path

    def set_file_path(self, file_path: str) -> None:
        """
        Set a new file path

        Args:
            file_path: New file path to use
        """
        self.file_path = file_path

    def create_default_checklist(self) -> Checklist:
        """
        Create a checklist with default categories

        Returns:
            New Checklist with default categories
        """
        from ..models.category import Category

        checklist = Checklist()

        # Add default categories
        for cat_data in Defaults.CATEGORIES:
            category = Category(
                category_id=cat_data['id'],
                name=cat_data['name'],
                tasks=[]
            )
            checklist.add_category(category)

        # Set first category as current
        if checklist.get_category_count() > 0:
            checklist.set_current_category(Defaults.CATEGORIES[0]['id'])

        return checklist

    def backup_file(self, backup_suffix: Optional[str] = None) -> bool:
        """
        Create a backup of the current checklist file

        Args:
            backup_suffix: Optional suffix for backup file (default: timestamp)

        Returns:
            True if successful, False otherwise
        """
        if not self.file_exists():
            return False

        try:
            if backup_suffix is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_suffix = f"backup_{timestamp}"

            backup_path = f"{self.file_path}.{backup_suffix}"
            os.makedirs(os.path.dirname(os.path.abspath(backup_path)), exist_ok=True)

            with open(self.file_path, 'r', encoding='utf-8') as src:
                data = src.read()

            with open(backup_path, 'w', encoding='utf-8') as dst:
                dst.write(data)

            return True
        except Exception as e:
            logger.warning("Error creating backup: %s", e)
            return False

    def rotate_backups(self, max_backups: int = 5) -> int:
        """
        Remove old timestamped backups, keeping only the newest max_backups.

        Args:
            max_backups: Maximum number of backup files to keep

        Returns:
            Number of backup files deleted
        """
        pattern = f"{self.file_path}.backup_*"
        backup_files = glob.glob(pattern)
        if len(backup_files) <= max_backups:
            return 0

        # Sort by modification time, oldest first
        backup_files.sort(key=lambda f: os.path.getmtime(f))
        to_delete = backup_files[:len(backup_files) - max_backups]
        deleted = 0
        for f in to_delete:
            try:
                os.remove(f)
                deleted += 1
            except OSError as e:
                logger.warning("Error deleting old backup %s: %s", f, e)
        return deleted

    def get_file_size(self) -> int:
        """
        Get the size of the checklist file in bytes

        Returns:
            File size in bytes, or 0 if file doesn't exist
        """
        if not self.file_exists():
            return 0

        try:
            return os.path.getsize(self.file_path)
        except Exception:
            return 0

    def get_last_modified(self) -> Optional[datetime]:
        """
        Get the last modification time of the checklist file

        Returns:
            Last modification datetime, or None if file doesn't exist
        """
        if not self.file_exists():
            return None

        try:
            timestamp = os.path.getmtime(self.file_path)
            return datetime.fromtimestamp(timestamp)
        except Exception:
            return None
