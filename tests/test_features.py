"""
Unit tests for feature modules
Tests for MarkdownExporter, ShortcutManager, TaskSearcher, TaskSorter, UndoManager
"""

import unittest
import sys
import os
import tempfile

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.features.export import MarkdownExporter
from src.features.shortcuts import ShortcutManager, DefaultShortcuts
from src.features.search import TaskSearcher
from src.features.task_sorting import TaskSorter
from src.features.undo_manager import UndoManager
from src.models.checklist import Checklist
from src.models.category import Category
from src.models.task import Task, Subtask


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


class TestTaskSearcher(unittest.TestCase):
    """Tests for TaskSearcher class"""

    def setUp(self):
        """Set up test fixtures"""
        self.cat1 = Category(1, "Work")
        self.cat1.add_task(Task("Write report", notes=["quarterly review"]))
        self.cat1.add_task(Task("Fix bug in login", completed=True))
        task_with_sub = Task("Deploy application")
        task_with_sub.add_subtask(Subtask("Run tests"))
        task_with_sub.add_subtask(Subtask("Update config"))
        self.cat1.add_task(task_with_sub)

        self.cat2 = Category(2, "Personal")
        self.cat2.add_task(Task("Buy groceries"))
        self.cat2.add_task(Task("Write blog post"))

        self.categories = [self.cat1, self.cat2]

    def test_search_by_task_text(self):
        """Test searching by task text"""
        results = TaskSearcher.search_tasks(self.categories, "write")
        self.assertEqual(len(results), 2)  # "Write report" and "Write blog post"

    def test_search_by_subtask_text(self):
        """Test searching by subtask text"""
        results = TaskSearcher.search_tasks(self.categories, "run tests")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['match_type'], 'subtask')

    def test_search_by_note_text(self):
        """Test searching by note text"""
        results = TaskSearcher.search_tasks(self.categories, "quarterly")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['match_type'], 'note')

    def test_search_case_insensitive(self):
        """Test case-insensitive search"""
        results = TaskSearcher.search_tasks(self.categories, "WRITE")
        self.assertEqual(len(results), 2)

    def test_search_in_specific_category(self):
        """Test search within specific category"""
        results = TaskSearcher.search_tasks(self.categories, "write", category_id=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['category_name'], "Work")

    def test_search_exclude_completed(self):
        """Test searching excluding completed tasks"""
        results = TaskSearcher.search_tasks(self.categories, "bug", include_completed=False)
        self.assertEqual(len(results), 0)

    def test_search_include_completed(self):
        """Test searching including completed tasks"""
        results = TaskSearcher.search_tasks(self.categories, "bug", include_completed=True)
        self.assertEqual(len(results), 1)

    def test_search_empty_query(self):
        """Test searching with empty query"""
        results = TaskSearcher.search_tasks(self.categories, "")
        self.assertEqual(len(results), 0)

    def test_search_no_results(self):
        """Test searching with no matching results"""
        results = TaskSearcher.search_tasks(self.categories, "nonexistent")
        self.assertEqual(len(results), 0)

    def test_search_result_contains_task_object(self):
        """Test that results contain Task objects"""
        results = TaskSearcher.search_tasks(self.categories, "report")
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0]['task'], Task)

    def test_filter_by_status_completed(self):
        """Test filtering by completed status"""
        tasks = self.cat1.tasks
        completed = TaskSearcher.filter_by_status(tasks, completed=True)
        self.assertEqual(len(completed), 1)

    def test_filter_by_status_pending(self):
        """Test filtering by pending status"""
        tasks = self.cat1.tasks
        pending = TaskSearcher.filter_by_status(tasks, completed=False)
        self.assertEqual(len(pending), 2)

    def test_filter_by_status_all(self):
        """Test filtering all tasks"""
        tasks = self.cat1.tasks
        all_tasks = TaskSearcher.filter_by_status(tasks, completed=None)
        self.assertEqual(len(all_tasks), 3)

    def test_filter_by_reminder(self):
        """Test filtering by reminder"""
        task_with_reminder = Task("Reminder task", reminder="2025-12-01T10:00:00")
        task_without = Task("No reminder")
        tasks = [task_with_reminder, task_without]

        with_reminder = TaskSearcher.filter_by_reminder(tasks, has_reminder=True)
        self.assertEqual(len(with_reminder), 1)

        without_reminder = TaskSearcher.filter_by_reminder(tasks, has_reminder=False)
        self.assertEqual(len(without_reminder), 1)


class TestTaskSorter(unittest.TestCase):
    """Tests for TaskSorter class"""

    def setUp(self):
        """Set up test fixtures"""
        self.tasks = [
            Task("B task", priority='low', created='2025-01-03T10:00:00'),
            Task("A task", priority='high', created='2025-01-01T10:00:00', due_date='2025-06-01'),
            Task("C task", priority='medium', completed=True, created='2025-01-02T10:00:00', due_date='2025-03-01'),
        ]

    def test_sort_by_created(self):
        """Test sorting by creation date"""
        TaskSorter.sort_tasks(self.tasks, 'created')
        self.assertEqual(self.tasks[0].text, "A task")
        self.assertEqual(self.tasks[2].text, "B task")

    def test_sort_by_due_date(self):
        """Test sorting by due date"""
        TaskSorter.sort_tasks(self.tasks, 'due_date')
        self.assertEqual(self.tasks[0].text, "C task")  # 2025-03-01
        self.assertEqual(self.tasks[1].text, "A task")  # 2025-06-01
        self.assertEqual(self.tasks[2].text, "B task")  # no due date → 9999-12-31

    def test_sort_by_priority(self):
        """Test sorting by priority"""
        TaskSorter.sort_tasks(self.tasks, 'priority')
        self.assertEqual(self.tasks[0].priority, 'high')
        self.assertEqual(self.tasks[1].priority, 'medium')
        self.assertEqual(self.tasks[2].priority, 'low')

    def test_sort_by_completion(self):
        """Test sorting by completion status"""
        TaskSorter.sort_tasks(self.tasks, 'completion')
        self.assertFalse(self.tasks[0].completed)
        self.assertTrue(self.tasks[2].completed)

    def test_sort_alphabetically(self):
        """Test alphabetical sorting"""
        TaskSorter.sort_tasks(self.tasks, 'a-z')
        self.assertEqual(self.tasks[0].text, "A task")
        self.assertEqual(self.tasks[1].text, "B task")
        self.assertEqual(self.tasks[2].text, "C task")

    def test_sort_reverse(self):
        """Test reverse sorting"""
        TaskSorter.sort_tasks(self.tasks, 'a-z', reverse=True)
        self.assertEqual(self.tasks[0].text, "C task")
        self.assertEqual(self.tasks[2].text, "A task")

    def test_sort_smart(self):
        """Test smart sorting"""
        TaskSorter.sort_smart(self.tasks)
        # Incomplete first, then by priority (high first), then by due date
        self.assertFalse(self.tasks[0].completed)
        self.assertEqual(self.tasks[0].priority, 'high')
        self.assertTrue(self.tasks[2].completed)

    def test_sort_empty_list(self):
        """Test sorting empty list"""
        result = TaskSorter.sort_tasks([], 'created')
        self.assertEqual(result, [])

    def test_sort_smart_empty(self):
        """Test smart sort on empty list"""
        result = TaskSorter.sort_smart([])
        self.assertEqual(result, [])


class TestUndoManager(unittest.TestCase):
    """Tests for UndoManager class"""

    def setUp(self):
        """Set up test fixtures"""
        self.manager = UndoManager(max_history=5)

    def test_record_and_undo(self):
        """Test recording state and undoing"""
        state1 = {'value': 1}
        state2 = {'value': 2}

        self.manager.record_state(state1, "Set to 1")
        previous = self.manager.undo(state2)

        self.assertIsNotNone(previous)
        self.assertEqual(previous['value'], 1)

    def test_undo_empty(self):
        """Test undo with nothing to undo"""
        result = self.manager.undo({'value': 1})
        self.assertIsNone(result)

    def test_redo(self):
        """Test redo after undo"""
        state1 = {'value': 1}
        state2 = {'value': 2}

        self.manager.record_state(state1)
        self.manager.undo(state2)  # Now redo stack has state2
        redo_state = self.manager.redo({'value': 1})

        self.assertIsNotNone(redo_state)
        self.assertEqual(redo_state['value'], 2)

    def test_redo_empty(self):
        """Test redo with nothing to redo"""
        result = self.manager.redo({'value': 1})
        self.assertIsNone(result)

    def test_can_undo(self):
        """Test can_undo check"""
        self.assertFalse(self.manager.can_undo())
        self.manager.record_state({'value': 1})
        self.assertTrue(self.manager.can_undo())

    def test_can_redo(self):
        """Test can_redo check"""
        self.assertFalse(self.manager.can_redo())
        self.manager.record_state({'value': 1})
        self.manager.undo({'value': 2})
        self.assertTrue(self.manager.can_redo())

    def test_redo_cleared_on_new_action(self):
        """Test redo stack cleared when new action recorded"""
        self.manager.record_state({'value': 1})
        self.manager.undo({'value': 2})
        self.assertTrue(self.manager.can_redo())

        self.manager.record_state({'value': 3})
        self.assertFalse(self.manager.can_redo())

    def test_max_history(self):
        """Test max history enforcement"""
        for i in range(10):
            self.manager.record_state({'value': i})

        self.assertEqual(len(self.manager.undo_stack), 5)

    def test_clear(self):
        """Test clearing all history"""
        self.manager.record_state({'value': 1})
        self.manager.record_state({'value': 2})
        self.manager.clear()

        self.assertFalse(self.manager.can_undo())
        self.assertFalse(self.manager.can_redo())

    def test_deep_copy(self):
        """Test that states are deep-copied"""
        state = {'value': [1, 2, 3]}
        self.manager.record_state(state)
        state['value'].append(4)  # Modify original

        previous = self.manager.undo({'value': []})
        self.assertEqual(previous['value'], [1, 2, 3])  # Should not include 4

    def test_descriptions(self):
        """Test action descriptions"""
        self.manager.record_state({'value': 1}, "Add task")
        desc = self.manager.get_undo_description()
        self.assertEqual(desc, "Add task")

    def test_redo_description(self):
        """Test redo description after undo"""
        self.manager.record_state({'value': 1}, "Add task")
        self.manager.undo({'value': 2})
        desc = self.manager.get_redo_description()
        self.assertIsNotNone(desc)

    def test_undo_redo_with_checklist_objects(self):
        """Test undo/redo roundtrip with actual Checklist model objects"""
        manager = UndoManager()

        # Create initial checklist and record state
        checklist = Checklist()
        cat = Category(1, "Work")
        cat.add_task(Task("Task 1"))
        checklist.add_category(cat)
        checklist.set_current_category(1)

        # Record state before adding a task
        manager.record_state(checklist.to_dict(), "Add task")
        cat.add_task(Task("Task 2"))

        # Undo: should restore to 1 task
        previous = manager.undo(checklist.to_dict())
        self.assertIsNotNone(previous)
        restored = Checklist.from_dict(previous)
        self.assertEqual(restored.get_category(1).get_task_count(), 1)
        self.assertEqual(restored.current_category_id, 1)

        # Redo: should restore to 2 tasks
        redo_state = manager.redo(restored.to_dict())
        self.assertIsNotNone(redo_state)
        re_restored = Checklist.from_dict(redo_state)
        self.assertEqual(re_restored.get_category(1).get_task_count(), 2)


class TestTaskImporter(unittest.TestCase):
    """Tests for TaskImporter class"""

    def test_import_markdown_basic(self):
        """Test importing basic markdown tasks"""
        from src.features.importer import TaskImporter

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md',
                                        delete=False, encoding='utf-8') as f:
            f.write("- [ ] Buy groceries\n")
            f.write("- [x] Clean house\n")
            f.write("- [ ] Walk the dog\n")
            f.name
            path = f.name

        try:
            tasks = TaskImporter.import_from_markdown(path)
            self.assertEqual(len(tasks), 3)
            self.assertEqual(tasks[0].text, "Buy groceries")
            self.assertFalse(tasks[0].completed)
            self.assertEqual(tasks[1].text, "Clean house")
            self.assertTrue(tasks[1].completed)
        finally:
            os.unlink(path)

    def test_import_markdown_with_subtasks(self):
        """Test importing markdown with subtasks"""
        from src.features.importer import TaskImporter

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md',
                                        delete=False, encoding='utf-8') as f:
            f.write("- [ ] Main task\n")
            f.write("  - [ ] Sub one\n")
            f.write("  - [x] Sub two\n")
            path = f.name

        try:
            tasks = TaskImporter.import_from_markdown(path)
            self.assertEqual(len(tasks), 1)
            self.assertEqual(len(tasks[0].subtasks), 2)
            self.assertEqual(tasks[0].subtasks[0].text, "Sub one")
            self.assertTrue(tasks[0].subtasks[1].completed)
        finally:
            os.unlink(path)

    def test_import_markdown_with_notes(self):
        """Test importing markdown with notes"""
        from src.features.importer import TaskImporter

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md',
                                        delete=False, encoding='utf-8') as f:
            f.write("- [ ] Task with notes\n")
            f.write("  > This is a note\n")
            f.write("  \u2022 Another note\n")
            path = f.name

        try:
            tasks = TaskImporter.import_from_markdown(path)
            self.assertEqual(len(tasks), 1)
            self.assertEqual(len(tasks[0].notes), 2)
        finally:
            os.unlink(path)

    def test_import_markdown_empty_file(self):
        """Test importing empty markdown file"""
        from src.features.importer import TaskImporter

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md',
                                        delete=False, encoding='utf-8') as f:
            f.write("")
            path = f.name

        try:
            tasks = TaskImporter.import_from_markdown(path)
            self.assertEqual(len(tasks), 0)
        finally:
            os.unlink(path)

    def test_import_csv_basic(self):
        """Test importing basic CSV tasks"""
        from src.features.importer import TaskImporter

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv',
                                        delete=False, encoding='utf-8') as f:
            f.write("text,completed,priority,due_date\n")
            f.write("Buy milk,false,high,2026-01-15\n")
            f.write("Clean up,true,low,\n")
            path = f.name

        try:
            tasks = TaskImporter.import_from_csv(path)
            self.assertEqual(len(tasks), 2)
            self.assertEqual(tasks[0].text, "Buy milk")
            self.assertFalse(tasks[0].completed)
            self.assertEqual(tasks[0].priority, "high")
            self.assertEqual(tasks[0].due_date, "2026-01-15")
            self.assertTrue(tasks[1].completed)
        finally:
            os.unlink(path)

    def test_import_csv_invalid_priority_defaults(self):
        """Test CSV import clamps invalid priority to medium"""
        from src.features.importer import TaskImporter

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv',
                                        delete=False, encoding='utf-8') as f:
            f.write("text,completed,priority\n")
            f.write("Task,false,banana\n")
            path = f.name

        try:
            tasks = TaskImporter.import_from_csv(path)
            self.assertEqual(len(tasks), 1)
            self.assertEqual(tasks[0].priority, "medium")
        finally:
            os.unlink(path)

    def test_import_csv_skips_empty_text(self):
        """Test CSV import skips rows with empty text"""
        from src.features.importer import TaskImporter

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv',
                                        delete=False, encoding='utf-8') as f:
            f.write("text,completed\n")
            f.write(",false\n")
            f.write("Valid task,false\n")
            path = f.name

        try:
            tasks = TaskImporter.import_from_csv(path)
            self.assertEqual(len(tasks), 1)
            self.assertEqual(tasks[0].text, "Valid task")
        finally:
            os.unlink(path)

    def test_import_file_auto_detect(self):
        """Test import_file auto-detects format"""
        from src.features.importer import TaskImporter

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md',
                                        delete=False, encoding='utf-8') as f:
            f.write("- [ ] Test task\n")
            path = f.name

        try:
            tasks = TaskImporter.import_file(path)
            self.assertEqual(len(tasks), 1)
        finally:
            os.unlink(path)

    def test_import_file_unsupported_format(self):
        """Test import_file raises on unsupported format"""
        from src.features.importer import TaskImporter

        with self.assertRaises(ValueError):
            TaskImporter.import_file("file.xml")


class TestBackupRotation(unittest.TestCase):
    """Tests for ChecklistStorage.rotate_backups"""

    def test_rotate_keeps_newest(self):
        """Test backup rotation keeps only newest files"""
        import time
        from src.persistence.storage import ChecklistStorage

        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            f.write(b'{}')
            base_path = f.name

        storage = ChecklistStorage(base_path)

        try:
            # Create 7 backup files with staggered mtimes
            backup_paths = []
            for i in range(7):
                bp = f"{base_path}.backup_{i:02d}"
                with open(bp, 'w') as bf:
                    bf.write('{}')
                # Set mtime to ensure ordering
                os.utime(bp, (time.time() + i, time.time() + i))
                backup_paths.append(bp)

            deleted = storage.rotate_backups(max_backups=5)
            self.assertEqual(deleted, 2)

            remaining = [p for p in backup_paths if os.path.exists(p)]
            self.assertEqual(len(remaining), 5)
        finally:
            os.unlink(base_path)
            for bp in backup_paths:
                if os.path.exists(bp):
                    os.unlink(bp)


if __name__ == '__main__':
    unittest.main()
