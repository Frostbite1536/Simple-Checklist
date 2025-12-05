"""
Unit tests for feature modules
Tests for DragDropManager, MarkdownExporter, and ShortcutManager
"""

import unittest
import sys
import os
import tempfile

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.features.drag_drop import DragDropManager
from src.features.export import MarkdownExporter
from src.features.shortcuts import ShortcutManager, DefaultShortcuts
from src.models.checklist import Checklist
from src.models.category import Category
from src.models.task import Task, Subtask


class TestDragDropManager(unittest.TestCase):
    """Tests for DragDropManager class"""

    def setUp(self):
        """Set up test fixtures"""
        self.checklist = Checklist()
        self.checklist.add_category(Category(1, "First"))
        self.checklist.add_category(Category(2, "Second"))
        self.checklist.add_category(Category(3, "Third"))

        self.reorder_called = False

        def on_reorder():
            self.reorder_called = True

        self.manager = DragDropManager(self.checklist, on_reorder)

    def test_init(self):
        """Test initialization"""
        self.assertEqual(self.manager.checklist, self.checklist)
        self.assertIsNotNone(self.manager.on_reorder)
        self.assertIsNone(self.manager.drag_data['index'])

    def test_start_drag(self):
        """Test starting a drag operation"""
        self.manager.start_drag(0)
        self.assertEqual(self.manager.get_drag_source_index(), 0)
        self.assertTrue(self.manager.is_dragging())

    def test_start_drag_invalid_index(self):
        """Test starting drag with invalid index"""
        self.manager.start_drag(10)
        self.assertIsNone(self.manager.get_drag_source_index())
        self.assertFalse(self.manager.is_dragging())

    def test_end_drag_reorder(self):
        """Test completing a drag with reordering"""
        self.manager.start_drag(0)
        result = self.manager.end_drag(2)

        self.assertTrue(result)
        self.assertTrue(self.reorder_called)
        self.assertFalse(self.manager.is_dragging())
        # Check reordering occurred
        self.assertEqual(self.checklist.categories[0].name, "Second")
        self.assertEqual(self.checklist.categories[2].name, "First")

    def test_end_drag_same_position(self):
        """Test ending drag at same position"""
        self.manager.start_drag(1)
        result = self.manager.end_drag(1)

        self.assertFalse(result)
        self.assertFalse(self.reorder_called)

    def test_end_drag_without_start(self):
        """Test ending drag without starting"""
        result = self.manager.end_drag(1)
        self.assertFalse(result)

    def test_reset_drag(self):
        """Test resetting drag state"""
        self.manager.start_drag(0)
        self.assertTrue(self.manager.is_dragging())

        self.manager.reset_drag()
        self.assertFalse(self.manager.is_dragging())
        self.assertIsNone(self.manager.get_drag_source_index())

    def test_validate_reorder(self):
        """Test reorder validation"""
        self.assertTrue(self.manager.validate_reorder(0, 2))
        self.assertFalse(self.manager.validate_reorder(0, 0))  # Same index
        self.assertFalse(self.manager.validate_reorder(-1, 2))  # Invalid source
        self.assertFalse(self.manager.validate_reorder(0, 10))  # Invalid target

    def test_get_reorder_preview(self):
        """Test getting reorder preview"""
        preview = self.manager.get_reorder_preview(0, 2)
        self.assertEqual(preview, ["Second", "Third", "First"])

    def test_get_reorder_preview_invalid(self):
        """Test getting preview with invalid indices"""
        preview = self.manager.get_reorder_preview(0, 10)
        self.assertIsNone(preview)


class TestMarkdownExporter(unittest.TestCase):
    """Tests for MarkdownExporter class"""

    def setUp(self):
        """Set up test fixtures"""
        # Create checklist with data
        self.checklist = Checklist()

        cat1 = Category(1, "Work")
        task1 = Task("Task 1", completed=True)
        task2 = Task("Task 2", completed=False, notes=["Important"])
        task2.add_subtask(Subtask("Subtask 1", completed=True))
        task2.add_subtask(Subtask("Subtask 2", completed=False))
        cat1.add_task(task1)
        cat1.add_task(task2)

        cat2 = Category(2, "Personal")
        task3 = Task("Task 3", completed=False)
        cat2.add_task(task3)

        self.checklist.add_category(cat1)
        self.checklist.add_category(cat2)

        self.exporter = MarkdownExporter(self.checklist, "/path/to/checklist.json")

    def test_init(self):
        """Test initialization"""
        self.assertEqual(self.exporter.checklist, self.checklist)
        self.assertEqual(self.exporter.source_file, "/path/to/checklist.json")

    def test_export_to_string_with_metadata(self):
        """Test exporting to string with metadata"""
        result = self.exporter.export_to_string(include_metadata=True)

        self.assertIn("# Checklist Export", result)
        self.assertIn("**Exported:**", result)
        self.assertIn("**File:** checklist.json", result)
        self.assertIn("## Work", result)
        self.assertIn("## Personal", result)
        self.assertIn("[x] Task 1", result)
        self.assertIn("[ ] Task 2", result)

    def test_export_to_string_without_metadata(self):
        """Test exporting to string without metadata"""
        result = self.exporter.export_to_string(include_metadata=False)

        self.assertNotIn("# Checklist Export", result)
        self.assertIn("## Work", result)
        self.assertIn("## Personal", result)

    def test_export_to_file(self):
        """Test exporting to file"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md')
        temp_file.close()

        try:
            result = self.exporter.export_to_file(temp_file.name)
            self.assertTrue(result)
            self.assertTrue(os.path.exists(temp_file.name))

            # Read and verify
            with open(temp_file.name, 'r', encoding='utf-8') as f:
                content = f.read()

            self.assertIn("# Checklist Export", content)
            self.assertIn("## Work", content)
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)

    def test_format_task_with_subtasks(self):
        """Test task formatting with subtasks"""
        result = self.exporter.export_to_string(include_metadata=False)

        self.assertIn("[x] Subtask 1", result)
        self.assertIn("[ ] Subtask 2", result)

    def test_format_task_with_notes(self):
        """Test task formatting with notes"""
        result = self.exporter.export_to_string(include_metadata=False)
        self.assertIn("Important", result)

    def test_export_category(self):
        """Test exporting single category"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md')
        temp_file.close()

        try:
            result = self.exporter.export_category(1, temp_file.name)
            self.assertTrue(result)

            with open(temp_file.name, 'r', encoding='utf-8') as f:
                content = f.read()

            self.assertIn("# Work", content)
            self.assertIn("Task 1", content)
            self.assertNotIn("Personal", content)
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)

    def test_export_category_invalid_id(self):
        """Test exporting category with invalid ID"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md')
        temp_file.close()

        try:
            result = self.exporter.export_category(999, temp_file.name)
            self.assertFalse(result)
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)

    def test_export_completed_only(self):
        """Test exporting only completed tasks"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md')
        temp_file.close()

        try:
            result = self.exporter.export_completed_only(temp_file.name)
            self.assertTrue(result)

            with open(temp_file.name, 'r', encoding='utf-8') as f:
                content = f.read()

            self.assertIn("# Completed Tasks", content)
            self.assertIn("[x] Task 1", content)
            self.assertNotIn("[ ] Task 2", content)
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)

    def test_export_pending_only(self):
        """Test exporting only pending tasks"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md')
        temp_file.close()

        try:
            result = self.exporter.export_pending_only(temp_file.name)
            self.assertTrue(result)

            with open(temp_file.name, 'r', encoding='utf-8') as f:
                content = f.read()

            self.assertIn("# Pending Tasks", content)
            self.assertIn("[ ] Task 2", content)
            self.assertNotIn("[x] Task 1", content)
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)

    def test_get_export_preview(self):
        """Test getting export preview"""
        preview = self.exporter.get_export_preview(max_lines=5)
        lines = preview.split('\n')
        # Should have approximately 5 lines + ellipsis (may vary slightly)
        self.assertLessEqual(len(lines), 10)
        self.assertIn("...", preview)

    def test_get_statistics(self):
        """Test getting export statistics"""
        stats = self.exporter.get_statistics()

        self.assertEqual(stats['categories'], 2)
        self.assertEqual(stats['total_tasks'], 3)
        self.assertEqual(stats['completed_tasks'], 1)
        self.assertEqual(stats['pending_tasks'], 2)
        self.assertEqual(stats['total_subtasks'], 2)
        self.assertEqual(stats['completed_subtasks'], 1)
        self.assertIn('export_timestamp', stats)


class MockWidget:
    """Mock widget for testing shortcuts"""

    def __init__(self):
        self.bindings = {}
        self.cursor = None

    def bind(self, sequence, func):
        """Mock bind method"""
        self.bindings[sequence] = func

    def unbind(self, sequence):
        """Mock unbind method"""
        if sequence in self.bindings:
            del self.bindings[sequence]

    def config(self, **kwargs):
        """Mock config method"""
        if 'cursor' in kwargs:
            self.cursor = kwargs['cursor']


class TestShortcutManager(unittest.TestCase):
    """Tests for ShortcutManager class"""

    def setUp(self):
        """Set up test fixtures"""
        self.widget = MockWidget()
        self.manager = ShortcutManager(self.widget)
        self.callback_called = False

    def test_init(self):
        """Test initialization"""
        self.assertEqual(self.manager.root_widget, self.widget)
        self.assertEqual(len(self.manager.bindings), 0)

    def test_register_shortcut(self):
        """Test registering a shortcut"""
        def callback(event):
            self.callback_called = True

        self.manager.register_shortcut('<Control-s>', callback, "Save")

        self.assertTrue(self.manager.is_registered('<Control-s>'))
        self.assertEqual(self.manager.get_shortcut_count(), 1)

    def test_register_multiple_callbacks_same_key(self):
        """Test registering multiple callbacks for same key"""
        calls = []

        def callback1(event):
            calls.append(1)

        def callback2(event):
            calls.append(2)

        self.manager.register_shortcut('<Control-s>', callback1)
        self.manager.register_shortcut('<Control-s>', callback2)

        self.assertEqual(len(self.manager.bindings['<Control-s>']), 2)

    def test_unregister_shortcut_all(self):
        """Test unregistering all callbacks for a key"""
        def callback(event):
            pass

        self.manager.register_shortcut('<Control-s>', callback)
        result = self.manager.unregister_shortcut('<Control-s>')

        self.assertTrue(result)
        self.assertFalse(self.manager.is_registered('<Control-s>'))

    def test_unregister_shortcut_specific(self):
        """Test unregistering specific callback"""
        def callback1(event):
            pass

        def callback2(event):
            pass

        self.manager.register_shortcut('<Control-s>', callback1)
        self.manager.register_shortcut('<Control-s>', callback2)

        result = self.manager.unregister_shortcut('<Control-s>', callback1)
        self.assertTrue(result)
        self.assertEqual(len(self.manager.bindings['<Control-s>']), 1)

    def test_unregister_nonexistent(self):
        """Test unregistering non-existent shortcut"""
        result = self.manager.unregister_shortcut('<Control-x>')
        self.assertFalse(result)

    def test_bind_all(self):
        """Test binding all shortcuts to widget"""
        def callback(event):
            pass

        self.manager.register_shortcut('<Control-s>', callback)
        self.manager.bind_all()

        self.assertIn('<Control-s>', self.widget.bindings)

    def test_unbind_all(self):
        """Test unbinding all shortcuts"""
        def callback(event):
            pass

        self.manager.register_shortcut('<Control-s>', callback)
        self.manager.bind_all()
        self.manager.unbind_all()

        self.assertNotIn('<Control-s>', self.widget.bindings)

    def test_set_root_widget(self):
        """Test setting root widget"""
        new_widget = MockWidget()

        def callback(event):
            pass

        self.manager.register_shortcut('<Control-s>', callback)
        self.manager.set_root_widget(new_widget)

        self.assertEqual(self.manager.root_widget, new_widget)
        self.assertIn('<Control-s>', new_widget.bindings)

    def test_get_all_shortcuts(self):
        """Test getting all shortcuts"""
        def callback(event):
            pass

        self.manager.register_shortcut('<Control-s>', callback, "Save")
        self.manager.register_shortcut('<Control-o>', callback, "Open")

        shortcuts = self.manager.get_all_shortcuts()
        self.assertEqual(len(shortcuts), 2)
        self.assertEqual(shortcuts['<Control-s>'], "Save")

    def test_clear_all(self):
        """Test clearing all shortcuts"""
        def callback(event):
            pass

        self.manager.register_shortcut('<Control-s>', callback)
        self.manager.bind_all()
        self.manager.clear_all()

        self.assertEqual(self.manager.get_shortcut_count(), 0)
        self.assertEqual(len(self.widget.bindings), 0)

    def test_create_help_text(self):
        """Test creating help text"""
        def callback(event):
            pass

        self.manager.register_shortcut('<Control-s>', callback, "Save")
        self.manager.register_shortcut('<Shift-Return>', callback, "Add task")

        help_text = self.manager.create_help_text()
        self.assertIn("Keyboard Shortcuts", help_text)
        self.assertIn("Save", help_text)
        self.assertIn("Add task", help_text)

    def test_format_key_for_display(self):
        """Test formatting keys for display"""
        formatted = self.manager._format_key_for_display('<Control-s>')
        self.assertEqual(formatted, "Ctrl+s")

        formatted = self.manager._format_key_for_display('<Shift-Return>')
        self.assertEqual(formatted, "Shift+Enter")


class TestDefaultShortcuts(unittest.TestCase):
    """Tests for DefaultShortcuts helper class"""

    def setUp(self):
        """Set up test fixtures"""
        self.widget = MockWidget()
        self.manager = ShortcutManager(self.widget)

    def test_register_task_shortcuts(self):
        """Test registering task shortcuts"""
        called = []

        def add_task(event):
            called.append('add')

        callbacks = {'add_task': add_task}
        DefaultShortcuts.register_task_shortcuts(self.manager, callbacks)

        self.assertTrue(self.manager.is_registered('<Shift-Return>'))

    def test_register_category_shortcuts(self):
        """Test registering category shortcuts"""
        switched_to = []

        def switch_category(index):
            switched_to.append(index)

        DefaultShortcuts.register_category_shortcuts(self.manager, switch_category)

        # Should have 9 category shortcuts
        count = sum(1 for key in self.manager.bindings.keys() if 'Control-Key-' in key)
        self.assertEqual(count, 9)

    def test_register_all_defaults(self):
        """Test registering all default shortcuts"""
        def add_task(event):
            pass

        def switch_category(index):
            pass

        task_callbacks = {'add_task': add_task}
        DefaultShortcuts.register_all_defaults(
            self.manager,
            task_callbacks,
            switch_category
        )

        # Should have task shortcuts + 9 category shortcuts
        self.assertGreaterEqual(self.manager.get_shortcut_count(), 10)


if __name__ == '__main__':
    unittest.main()
