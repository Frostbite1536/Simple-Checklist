"""
Unit tests for persistence layer
Tests for ChecklistStorage and SettingsManager
"""

import unittest
import sys
import os
import tempfile
import json
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.persistence.storage import ChecklistStorage
from src.persistence.settings import SettingsManager
from src.models.checklist import Checklist
from src.models.category import Category
from src.models.task import Task, Subtask


class TestChecklistStorage(unittest.TestCase):
    """Tests for ChecklistStorage class"""

    def setUp(self):
        """Set up test fixtures"""
        # Create temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.storage = ChecklistStorage(self.temp_file.name)

    def tearDown(self):
        """Clean up test files"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

        # Clean up any backup files
        backup_pattern = f"{self.temp_file.name}.backup_"
        dir_path = os.path.dirname(self.temp_file.name)
        for file in os.listdir(dir_path):
            if file.startswith(os.path.basename(self.temp_file.name) + ".backup_"):
                os.unlink(os.path.join(dir_path, file))

    def test_init_with_default_path(self):
        """Test initialization with default path"""
        storage = ChecklistStorage()
        self.assertIsNotNone(storage.get_file_path())

    def test_init_with_custom_path(self):
        """Test initialization with custom path"""
        self.assertEqual(self.storage.get_file_path(), self.temp_file.name)

    def test_save_and_load_empty_checklist(self):
        """Test saving and loading an empty checklist"""
        checklist = Checklist()
        result = self.storage.save_checklist(checklist)
        self.assertTrue(result)

        loaded = self.storage.load_checklist()
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.get_category_count(), 0)

    def test_save_and_load_checklist_with_data(self):
        """Test saving and loading a checklist with data"""
        # Create checklist with data
        checklist = Checklist()
        cat1 = Category(1, "Work")
        task1 = Task("Complete project", completed=False, notes=["Important"])
        task1.add_subtask(Subtask("Write code"))
        cat1.add_task(task1)
        checklist.add_category(cat1)
        checklist.set_current_category(1)

        # Save
        result = self.storage.save_checklist(checklist)
        self.assertTrue(result)

        # Load
        loaded = self.storage.load_checklist()
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.get_category_count(), 1)
        self.assertEqual(loaded.current_category_id, 1)

        # Check category
        cat = loaded.get_category(1)
        self.assertIsNotNone(cat)
        self.assertEqual(cat.name, "Work")
        self.assertEqual(cat.get_task_count(), 1)

        # Check task
        task = cat.get_task(0)
        self.assertEqual(task.text, "Complete project")
        self.assertFalse(task.completed)
        self.assertEqual(len(task.notes), 1)
        self.assertEqual(task.get_subtask_count(), 1)

    def test_load_nonexistent_file(self):
        """Test loading from a non-existent file"""
        os.unlink(self.temp_file.name)
        loaded = self.storage.load_checklist()
        self.assertIsNone(loaded)

    def test_file_exists(self):
        """Test file_exists method"""
        # File should exist after creation
        self.assertTrue(self.storage.file_exists())

        # Remove file
        os.unlink(self.temp_file.name)
        self.assertFalse(self.storage.file_exists())

    def test_set_file_path(self):
        """Test setting a new file path"""
        new_path = "/tmp/new_checklist.json"
        self.storage.set_file_path(new_path)
        self.assertEqual(self.storage.get_file_path(), new_path)

    def test_create_default_checklist(self):
        """Test creating a checklist with default categories"""
        checklist = self.storage.create_default_checklist()
        self.assertIsNotNone(checklist)
        self.assertGreater(checklist.get_category_count(), 0)
        self.assertIsNotNone(checklist.current_category_id)

    def test_export_to_markdown(self):
        """Test exporting to markdown"""
        # Create checklist with data
        checklist = Checklist()
        cat1 = Category(1, "Work")
        task1 = Task("Task 1", completed=True)
        task2 = Task("Task 2", completed=False)
        task2.add_subtask(Subtask("Sub 1", completed=True))
        task2.add_subtask(Subtask("Sub 2", completed=False))
        cat1.add_task(task1)
        cat1.add_task(task2)
        checklist.add_category(cat1)

        # Export
        md_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md')
        md_file.close()

        try:
            result = self.storage.export_to_markdown(checklist, md_file.name)
            self.assertTrue(result)

            # Read and verify
            with open(md_file.name, 'r', encoding='utf-8') as f:
                content = f.read()

            self.assertIn("# Checklist Export", content)
            self.assertIn("## Work", content)
            self.assertIn("[x] Task 1", content)
            self.assertIn("[ ] Task 2", content)
            self.assertIn("[x] Sub 1", content)
            self.assertIn("[ ] Sub 2", content)
        finally:
            if os.path.exists(md_file.name):
                os.unlink(md_file.name)

    def test_backup_file(self):
        """Test creating a backup"""
        # Create and save a checklist
        checklist = Checklist()
        self.storage.save_checklist(checklist)

        # Create backup
        result = self.storage.backup_file("test_backup")
        self.assertTrue(result)

        # Check backup exists
        backup_path = f"{self.temp_file.name}.test_backup"
        self.assertTrue(os.path.exists(backup_path))

        # Clean up
        os.unlink(backup_path)

    def test_backup_nonexistent_file(self):
        """Test backing up a non-existent file"""
        os.unlink(self.temp_file.name)
        result = self.storage.backup_file()
        self.assertFalse(result)

    def test_get_file_size(self):
        """Test getting file size"""
        # Empty file
        checklist = Checklist()
        self.storage.save_checklist(checklist)
        size = self.storage.get_file_size()
        self.assertGreater(size, 0)

        # Non-existent file
        os.unlink(self.temp_file.name)
        size = self.storage.get_file_size()
        self.assertEqual(size, 0)

    def test_get_last_modified(self):
        """Test getting last modified time"""
        checklist = Checklist()
        self.storage.save_checklist(checklist)

        last_mod = self.storage.get_last_modified()
        self.assertIsNotNone(last_mod)
        self.assertIsInstance(last_mod, datetime)

        # Non-existent file
        os.unlink(self.temp_file.name)
        last_mod = self.storage.get_last_modified()
        self.assertIsNone(last_mod)


class TestSettingsManager(unittest.TestCase):
    """Tests for SettingsManager class"""

    def setUp(self):
        """Set up test fixtures"""
        # Create temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.settings_manager = SettingsManager(self.temp_file.name)

    def tearDown(self):
        """Clean up test files"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_init_creates_default_settings(self):
        """Test initialization creates default settings"""
        self.assertIsNotNone(self.settings_manager.settings)
        self.assertIn('input_bg_color', self.settings_manager.settings)
        self.assertIn('recent_files', self.settings_manager.settings)

    def test_save_and_load_settings(self):
        """Test saving and loading settings"""
        self.settings_manager.set_input_bg_color('#FF0000')
        self.settings_manager.add_recent_file('/path/to/file.json')

        # Create new manager with same file
        new_manager = SettingsManager(self.temp_file.name)
        self.assertEqual(new_manager.get_input_bg_color(), '#FF0000')
        self.assertIn('/path/to/file.json', new_manager.get_recent_files())

    def test_get_and_set_input_bg_color(self):
        """Test getting and setting input background color"""
        color = '#FF0000'
        self.settings_manager.set_input_bg_color(color)
        self.assertEqual(self.settings_manager.get_input_bg_color(), color)

    def test_add_recent_file(self):
        """Test adding recent files"""
        self.settings_manager.add_recent_file('/path/to/file1.json')
        self.settings_manager.add_recent_file('/path/to/file2.json')

        recent = self.settings_manager.get_recent_files()
        self.assertEqual(len(recent), 2)
        self.assertEqual(recent[0], '/path/to/file2.json')  # Most recent first
        self.assertEqual(recent[1], '/path/to/file1.json')

    def test_add_duplicate_recent_file(self):
        """Test adding duplicate recent file moves it to front"""
        self.settings_manager.add_recent_file('/path/to/file1.json')
        self.settings_manager.add_recent_file('/path/to/file2.json')
        self.settings_manager.add_recent_file('/path/to/file1.json')

        recent = self.settings_manager.get_recent_files()
        self.assertEqual(len(recent), 2)  # No duplicates
        self.assertEqual(recent[0], '/path/to/file1.json')  # Moved to front

    def test_recent_files_max_limit(self):
        """Test recent files respects max limit"""
        # Add more than max
        for i in range(15):
            self.settings_manager.add_recent_file(f'/path/to/file{i}.json')

        recent = self.settings_manager.get_recent_files()
        self.assertEqual(len(recent), 10)  # Max 10
        self.assertEqual(recent[0], '/path/to/file14.json')  # Most recent

    def test_remove_recent_file(self):
        """Test removing a recent file"""
        self.settings_manager.add_recent_file('/path/to/file1.json')
        self.settings_manager.add_recent_file('/path/to/file2.json')

        result = self.settings_manager.remove_recent_file('/path/to/file1.json')
        self.assertTrue(result)

        recent = self.settings_manager.get_recent_files()
        self.assertNotIn('/path/to/file1.json', recent)

    def test_remove_nonexistent_recent_file(self):
        """Test removing a non-existent recent file"""
        result = self.settings_manager.remove_recent_file('/nonexistent.json')
        self.assertFalse(result)

    def test_clear_recent_files(self):
        """Test clearing all recent files"""
        self.settings_manager.add_recent_file('/path/to/file1.json')
        self.settings_manager.add_recent_file('/path/to/file2.json')

        self.settings_manager.clear_recent_files()
        recent = self.settings_manager.get_recent_files()
        self.assertEqual(len(recent), 0)

    def test_get_recent_files_existing(self):
        """Test getting only existing recent files"""
        # Create a temporary file that exists
        temp = tempfile.NamedTemporaryFile(delete=False)
        temp.close()

        self.settings_manager.add_recent_file(temp.name)
        self.settings_manager.add_recent_file('/nonexistent/file.json')

        existing = self.settings_manager.get_recent_files_existing()
        self.assertEqual(len(existing), 1)
        self.assertEqual(existing[0], temp.name)

        # Clean up
        os.unlink(temp.name)

    def test_cleanup_recent_files(self):
        """Test cleaning up non-existent recent files"""
        # Create a temporary file that exists
        temp = tempfile.NamedTemporaryFile(delete=False)
        temp.close()

        self.settings_manager.add_recent_file(temp.name)
        self.settings_manager.add_recent_file('/nonexistent1.json')
        self.settings_manager.add_recent_file('/nonexistent2.json')

        removed = self.settings_manager.cleanup_recent_files()
        self.assertEqual(removed, 2)

        recent = self.settings_manager.get_recent_files()
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0], temp.name)

        # Clean up
        os.unlink(temp.name)

    def test_get_and_set_setting(self):
        """Test generic get/set setting"""
        self.settings_manager.set_setting('custom_key', 'custom_value')
        value = self.settings_manager.get_setting('custom_key')
        self.assertEqual(value, 'custom_value')

    def test_get_setting_with_default(self):
        """Test getting setting with default value"""
        value = self.settings_manager.get_setting('nonexistent', 'default')
        self.assertEqual(value, 'default')

    def test_reset_to_defaults(self):
        """Test resetting to default settings"""
        self.settings_manager.set_input_bg_color('#FF0000')
        self.settings_manager.add_recent_file('/path/to/file.json')

        self.settings_manager.reset_to_defaults()

        self.assertNotEqual(self.settings_manager.get_input_bg_color(), '#FF0000')
        self.assertEqual(len(self.settings_manager.get_recent_files()), 0)

    def test_get_all_settings(self):
        """Test getting all settings"""
        all_settings = self.settings_manager.get_all_settings()
        self.assertIsInstance(all_settings, dict)
        self.assertIn('input_bg_color', all_settings)
        self.assertIn('recent_files', all_settings)

    def test_import_export_settings(self):
        """Test importing and exporting settings"""
        self.settings_manager.set_input_bg_color('#FF0000')
        self.settings_manager.add_recent_file('/path/to/file.json')

        # Export
        exported = self.settings_manager.export_settings()

        # Create new manager and import
        new_manager = SettingsManager(self.temp_file.name)
        new_manager.reset_to_defaults()
        new_manager.import_settings(exported)

        self.assertEqual(new_manager.get_input_bg_color(), '#FF0000')
        self.assertIn('/path/to/file.json', new_manager.get_recent_files())


if __name__ == '__main__':
    unittest.main()
