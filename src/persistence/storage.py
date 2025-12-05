"""
Storage management for checklists
Handles JSON file operations for saving and loading checklists
"""

import json
import os
from typing import Optional
from datetime import datetime

from ..models.checklist import Checklist
from ..utils.constants import Paths, Defaults, FileTypes


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
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving checklist: {e}")
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
            print(f"Error loading checklist: {e}")
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

    def export_to_markdown(self, checklist: Checklist, file_path: str) -> bool:
        """
        Export checklist to Markdown file

        Args:
            checklist: Checklist to export
            file_path: Path to save the markdown file

        Returns:
            True if successful, False otherwise
        """
        try:
            markdown = self._generate_markdown(checklist)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(markdown)

            return True
        except Exception as e:
            print(f"Error exporting to markdown: {e}")
            return False

    def _generate_markdown(self, checklist: Checklist) -> str:
        """
        Generate markdown content from checklist

        Args:
            checklist: Checklist to convert

        Returns:
            Markdown string
        """
        # Add timestamp header
        timestamp = datetime.now().strftime(Defaults.EXPORT_TIMESTAMP_FORMAT)
        markdown = f"# Checklist Export\n\n"
        markdown += f"**Exported:** {timestamp}\n"
        markdown += f"**File:** {os.path.basename(self.file_path)}\n\n"
        markdown += "---\n\n"

        # Add each category
        for category in checklist.categories:
            markdown += f"## {category.name}\n\n"

            if not category.tasks:
                markdown += "_No tasks_\n\n"
            else:
                for task in category.tasks:
                    checkbox = '[x]' if task.completed else '[ ]'
                    markdown += f"- {checkbox} {task.text}\n"

                    # Export sub-tasks
                    if task.subtasks:
                        for subtask in task.subtasks:
                            sub_checkbox = '[x]' if subtask.completed else '[ ]'
                            markdown += f"  - {sub_checkbox} {subtask.text}\n"

                    # Export notes
                    if task.notes:
                        for note in task.notes:
                            markdown += f"    - {note}\n"

                markdown += "\n"

        return markdown

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

            with open(self.file_path, 'r', encoding='utf-8') as src:
                data = src.read()

            with open(backup_path, 'w', encoding='utf-8') as dst:
                dst.write(data)

            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False

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
