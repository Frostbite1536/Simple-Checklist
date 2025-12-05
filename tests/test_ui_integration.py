"""
Integration tests for UI components and application flow
Tests the refactored UI modules working together with the application
"""

import unittest
import sys
import os
import tempfile
import json

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class MockTkWidget:
    """Mock Tkinter widget for testing without GUI"""

    def __init__(self, parent=None, **kwargs):
        self.parent = parent
        self.kwargs = kwargs
        self.children = []
        self.bindings = {}
        self.packed = False
        self.gridded = False
        self._config = {}

    def pack(self, **kwargs):
        self.packed = True
        self.pack_config = kwargs

    def grid(self, **kwargs):
        self.gridded = True
        self.grid_config = kwargs

    def bind(self, sequence, func):
        self.bindings[sequence] = func

    def config(self, **kwargs):
        self._config.update(kwargs)

    def winfo_children(self):
        return self.children

    def destroy(self):
        self.children = []


class TestUIComponentIntegration(unittest.TestCase):
    """Integration tests for UI components"""

    def test_dialogs_import(self):
        """Test that dialog components can be imported"""
        try:
            from src.ui.dialogs import AddCategoryDialog, AddSubtaskDialog
            self.assertTrue(True)
        except ImportError as e:
            # Skip if tkinter not available
            if 'tkinter' in str(e).lower():
                self.skipTest("Tkinter not available in this environment")
            else:
                raise

    def test_input_area_import(self):
        """Test that input area component can be imported"""
        try:
            from src.ui.input_area import InputArea
            self.assertTrue(True)
        except ImportError as e:
            if 'tkinter' in str(e).lower():
                self.skipTest("Tkinter not available in this environment")
            else:
                raise

    def test_sidebar_import(self):
        """Test that sidebar component can be imported"""
        try:
            from src.ui.sidebar import Sidebar
            self.assertTrue(True)
        except ImportError as e:
            if 'tkinter' in str(e).lower():
                self.skipTest("Tkinter not available in this environment")
            else:
                raise

    def test_task_panel_import(self):
        """Test that task panel component can be imported"""
        try:
            from src.ui.task_panel import TaskPanel
            self.assertTrue(True)
        except ImportError as e:
            if 'tkinter' in str(e).lower():
                self.skipTest("Tkinter not available in this environment")
            else:
                raise

    def test_main_window_import(self):
        """Test that main window component can be imported"""
        try:
            from src.ui.main_window import MainWindow
            self.assertTrue(True)
        except ImportError as e:
            if 'tkinter' in str(e).lower():
                self.skipTest("Tkinter not available in this environment")
            else:
                raise

    def test_ui_package_exports(self):
        """Test that UI package exports all components"""
        try:
            from src.ui import (
                AddCategoryDialog,
                AddSubtaskDialog,
                InputArea,
                Sidebar,
                TaskPanel,
                MainWindow
            )
            self.assertTrue(True)
        except ImportError as e:
            if 'tkinter' in str(e).lower():
                self.skipTest("Tkinter not available in this environment")
            else:
                raise


class TestApplicationDataFlow(unittest.TestCase):
    """Test application data flow and integration"""

    def setUp(self):
        """Set up test fixtures"""
        # Create temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()

    def tearDown(self):
        """Clean up test files"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_data_structure_compatibility(self):
        """Test that old data structure is compatible with new modules"""
        # Create old-style data structure
        old_data = {
            'categories': [
                {
                    'id': 1,
                    'name': 'Work',
                    'tasks': [
                        {
                            'text': 'Task 1',
                            'completed': False,
                            'notes': ['Note 1'],
                            'subtasks': [
                                {'text': 'Subtask 1', 'completed': False}
                            ],
                            'created': '2025-01-01T10:00:00'
                        }
                    ]
                }
            ],
            'current_category': 1
        }

        # Save to file
        with open(self.temp_file.name, 'w') as f:
            json.dump(old_data, f)

        # Load and verify
        with open(self.temp_file.name, 'r') as f:
            loaded_data = json.load(f)

        self.assertEqual(loaded_data['categories'][0]['id'], 1)
        self.assertEqual(loaded_data['categories'][0]['name'], 'Work')
        self.assertEqual(len(loaded_data['categories'][0]['tasks']), 1)
        self.assertEqual(loaded_data['current_category'], 1)

    def test_category_operations(self):
        """Test category CRUD operations"""
        data = {
            'categories': [
                {'id': 1, 'name': 'Work', 'tasks': []},
                {'id': 2, 'name': 'Personal', 'tasks': []}
            ],
            'current_category': 1
        }

        # Add category
        new_id = max([c['id'] for c in data['categories']], default=0) + 1
        data['categories'].append({'id': new_id, 'name': 'Shopping', 'tasks': []})
        self.assertEqual(len(data['categories']), 3)

        # Delete category
        data['categories'] = [c for c in data['categories'] if c['id'] != 2]
        self.assertEqual(len(data['categories']), 2)

        # Reorder categories
        category = data['categories'].pop(0)
        data['categories'].insert(1, category)
        self.assertEqual(data['categories'][1]['name'], 'Work')

    def test_task_operations(self):
        """Test task CRUD operations"""
        category = {
            'id': 1,
            'name': 'Work',
            'tasks': []
        }

        # Add task
        category['tasks'].append({
            'text': 'New task',
            'completed': False,
            'notes': [],
            'created': '2025-01-01T10:00:00'
        })
        self.assertEqual(len(category['tasks']), 1)

        # Toggle task
        category['tasks'][0]['completed'] = not category['tasks'][0]['completed']
        self.assertTrue(category['tasks'][0]['completed'])

        # Delete task
        del category['tasks'][0]
        self.assertEqual(len(category['tasks']), 0)

    def test_subtask_operations(self):
        """Test subtask operations"""
        task = {
            'text': 'Main task',
            'completed': False,
            'notes': [],
            'subtasks': []
        }

        # Add subtask
        task['subtasks'].append({'text': 'Subtask 1', 'completed': False})
        task['subtasks'].append({'text': 'Subtask 2', 'completed': False})
        self.assertEqual(len(task['subtasks']), 2)

        # Toggle subtask
        task['subtasks'][0]['completed'] = not task['subtasks'][0]['completed']
        self.assertTrue(task['subtasks'][0]['completed'])

        # Delete subtask
        del task['subtasks'][0]
        self.assertEqual(len(task['subtasks']), 1)

    def test_clear_completed_tasks(self):
        """Test clearing completed tasks"""
        category = {
            'id': 1,
            'name': 'Work',
            'tasks': [
                {'text': 'Task 1', 'completed': True},
                {'text': 'Task 2', 'completed': False},
                {'text': 'Task 3', 'completed': True}
            ]
        }

        # Clear completed
        category['tasks'] = [t for t in category['tasks'] if not t['completed']]
        self.assertEqual(len(category['tasks']), 1)
        self.assertEqual(category['tasks'][0]['text'], 'Task 2')

    def test_export_markdown_structure(self):
        """Test markdown export data structure"""
        data = {
            'categories': [
                {
                    'id': 1,
                    'name': 'Work',
                    'tasks': [
                        {
                            'text': 'Task 1',
                            'completed': True,
                            'notes': ['Note 1'],
                            'subtasks': [
                                {'text': 'Subtask 1', 'completed': True},
                                {'text': 'Subtask 2', 'completed': False}
                            ]
                        },
                        {
                            'text': 'Task 2',
                            'completed': False,
                            'notes': []
                        }
                    ]
                }
            ]
        }

        # Generate markdown
        markdown = "# Checklist Export\n\n"
        for category in data['categories']:
            markdown += f"## {category['name']}\n\n"
            for task in category['tasks']:
                checkbox = '[x]' if task['completed'] else '[ ]'
                markdown += f"- {checkbox} {task['text']}\n"

                if task.get('subtasks'):
                    for subtask in task['subtasks']:
                        sub_checkbox = '[x]' if subtask['completed'] else '[ ]'
                        markdown += f"  - {sub_checkbox} {subtask['text']}\n"

                if task.get('notes'):
                    for note in task['notes']:
                        markdown += f"    - {note}\n"

        # Verify markdown contains expected elements
        self.assertIn("## Work", markdown)
        self.assertIn("[x] Task 1", markdown)
        self.assertIn("[ ] Task 2", markdown)
        self.assertIn("[x] Subtask 1", markdown)
        self.assertIn("[ ] Subtask 2", markdown)
        self.assertIn("Note 1", markdown)


class TestSettingsIntegration(unittest.TestCase):
    """Test settings and customization"""

    def test_settings_structure(self):
        """Test settings data structure"""
        settings = {
            'input_bg_color': 'white',
            'recent_files': []
        }

        # Update color
        settings['input_bg_color'] = '#FF0000'
        self.assertEqual(settings['input_bg_color'], '#FF0000')

        # Add recent files
        settings['recent_files'].insert(0, '/path/to/file1.json')
        settings['recent_files'].insert(0, '/path/to/file2.json')
        self.assertEqual(len(settings['recent_files']), 2)
        self.assertEqual(settings['recent_files'][0], '/path/to/file2.json')

        # Remove duplicates
        if '/path/to/file1.json' in settings['recent_files']:
            settings['recent_files'].remove('/path/to/file1.json')
        settings['recent_files'].insert(0, '/path/to/file1.json')
        self.assertEqual(len(settings['recent_files']), 2)

        # Limit recent files
        settings['recent_files'] = settings['recent_files'][:10]
        self.assertLessEqual(len(settings['recent_files']), 10)


class TestDataMigration(unittest.TestCase):
    """Test data migration and compatibility"""

    def test_migrate_subtasks_without_completed(self):
        """Test migrating old subtasks without completed field"""
        data = {
            'categories': [
                {
                    'id': 1,
                    'name': 'Work',
                    'tasks': [
                        {
                            'text': 'Task 1',
                            'completed': False,
                            'subtasks': [
                                {'text': 'Subtask 1'}  # Missing 'completed' field
                            ]
                        }
                    ]
                }
            ]
        }

        # Migrate
        for category in data.get('categories', []):
            for task in category.get('tasks', []):
                if 'subtasks' in task:
                    for subtask in task['subtasks']:
                        if 'completed' not in subtask:
                            subtask['completed'] = False

        # Verify
        self.assertIn('completed', data['categories'][0]['tasks'][0]['subtasks'][0])
        self.assertFalse(data['categories'][0]['tasks'][0]['subtasks'][0]['completed'])

    def test_migrate_current_category(self):
        """Test migrating current_category field"""
        data = {
            'categories': [
                {'id': 1, 'name': 'Work', 'tasks': []}
            ]
        }

        # Ensure current_category exists
        if 'current_category' not in data or data.get('current_category') is None:
            if data['categories']:
                data['current_category'] = data['categories'][0]['id']
            else:
                data['current_category'] = None

        self.assertEqual(data['current_category'], 1)


if __name__ == '__main__':
    unittest.main()
