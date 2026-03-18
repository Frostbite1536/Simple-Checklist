"""
Unit tests for model classes
Tests for Task, Subtask, Category, and Checklist
"""

import unittest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models.task import Task, Subtask
from src.models.category import Category
from src.models.checklist import Checklist


class TestSubtask(unittest.TestCase):
    """Tests for Subtask class"""

    def test_create_subtask(self):
        """Test creating a subtask"""
        st = Subtask("Buy milk")
        self.assertEqual(st.text, "Buy milk")
        self.assertFalse(st.completed)

    def test_create_completed_subtask(self):
        """Test creating a completed subtask"""
        st = Subtask("Buy milk", completed=True)
        self.assertTrue(st.completed)

    def test_toggle_completion(self):
        """Test toggling subtask completion"""
        st = Subtask("Buy milk")
        self.assertFalse(st.completed)
        st.toggle_completion()
        self.assertTrue(st.completed)
        st.toggle_completion()
        self.assertFalse(st.completed)

    def test_to_dict(self):
        """Test converting subtask to dictionary"""
        st = Subtask("Buy milk", completed=True)
        data = st.to_dict()
        self.assertEqual(data['text'], "Buy milk")
        self.assertTrue(data['completed'])

    def test_from_dict(self):
        """Test creating subtask from dictionary"""
        data = {'text': 'Buy milk', 'completed': True}
        st = Subtask.from_dict(data)
        self.assertEqual(st.text, "Buy milk")
        self.assertTrue(st.completed)


    def test_subtask_empty_text_raises(self):
        """Test creating subtask with empty text raises ValueError"""
        with self.assertRaises(ValueError):
            Subtask("")
        with self.assertRaises(ValueError):
            Subtask("   ")

    def test_subtask_text_stripped(self):
        """Test subtask text is stripped of whitespace"""
        st = Subtask("  Buy milk  ")
        self.assertEqual(st.text, "Buy milk")


class TestTask(unittest.TestCase):
    """Tests for Task class"""

    def test_create_task(self):
        """Test creating a task"""
        task = Task("Complete project")
        self.assertEqual(task.text, "Complete project")
        self.assertFalse(task.completed)
        self.assertEqual(len(task.notes), 0)
        self.assertEqual(len(task.subtasks), 0)
        self.assertIsNotNone(task.created)

    def test_create_task_with_notes(self):
        """Test creating a task with notes"""
        task = Task("Complete project", notes=["Important", "Urgent"])
        self.assertEqual(len(task.notes), 2)

    def test_toggle_completion(self):
        """Test toggling task completion"""
        task = Task("Complete project")
        self.assertFalse(task.completed)
        task.toggle_completion()
        self.assertTrue(task.completed)

    def test_add_subtask(self):
        """Test adding subtasks"""
        task = Task("Complete project")
        st1 = Subtask("Write code")
        st2 = Subtask("Test code")
        task.add_subtask(st1)
        task.add_subtask(st2)
        self.assertEqual(task.get_subtask_count(), 2)

    def test_remove_subtask(self):
        """Test removing subtasks"""
        task = Task("Complete project")
        st1 = Subtask("Write code")
        st2 = Subtask("Test code")
        task.add_subtask(st1)
        task.add_subtask(st2)

        removed = task.remove_subtask(0)
        self.assertEqual(removed.text, "Write code")
        self.assertEqual(task.get_subtask_count(), 1)

    def test_remove_subtask_invalid_index(self):
        """Test removing subtask with invalid index"""
        task = Task("Complete project")
        result = task.remove_subtask(0)
        self.assertIsNone(result)

    def test_add_note(self):
        """Test adding notes"""
        task = Task("Complete project")
        task.add_note("Important")
        task.add_note("Urgent")
        self.assertEqual(len(task.notes), 2)

    def test_get_completed_subtask_count(self):
        """Test counting completed subtasks"""
        task = Task("Complete project")
        task.add_subtask(Subtask("Write code", completed=True))
        task.add_subtask(Subtask("Test code", completed=False))
        task.add_subtask(Subtask("Deploy", completed=True))
        self.assertEqual(task.get_completed_subtask_count(), 2)

    def test_is_fully_completed(self):
        """Test checking if task is fully completed"""
        task = Task("Complete project")
        task.add_subtask(Subtask("Write code"))
        task.add_subtask(Subtask("Test code"))

        # Task not completed
        self.assertFalse(task.is_fully_completed())

        # Task completed but subtasks not
        task.toggle_completion()
        self.assertFalse(task.is_fully_completed())

        # All completed
        task.subtasks[0].toggle_completion()
        task.subtasks[1].toggle_completion()
        self.assertTrue(task.is_fully_completed())

    def test_to_dict(self):
        """Test converting task to dictionary"""
        task = Task("Complete project", notes=["Important"])
        task.add_subtask(Subtask("Write code"))
        data = task.to_dict()

        self.assertEqual(data['text'], "Complete project")
        self.assertFalse(data['completed'])
        self.assertEqual(len(data['notes']), 1)
        self.assertEqual(len(data['subtasks']), 1)

    def test_from_dict(self):
        """Test creating task from dictionary"""
        data = {
            'text': 'Complete project',
            'completed': True,
            'notes': ['Important'],
            'subtasks': [{'text': 'Write code', 'completed': False}],
            'created': '2025-01-01T10:00:00'
        }
        task = Task.from_dict(data)

        self.assertEqual(task.text, "Complete project")
        self.assertTrue(task.completed)
        self.assertEqual(len(task.notes), 1)
        self.assertEqual(task.get_subtask_count(), 1)

    def test_task_empty_text_raises(self):
        """Test creating task with empty text raises ValueError"""
        with self.assertRaises(ValueError):
            Task("")
        with self.assertRaises(ValueError):
            Task("   ")

    def test_task_text_stripped(self):
        """Test task text is stripped of whitespace"""
        task = Task("  Complete project  ")
        self.assertEqual(task.text, "Complete project")

    def test_invalid_priority_raises(self):
        """Test invalid priority raises ValueError"""
        with self.assertRaises(ValueError):
            Task("Test", priority='banana')
        with self.assertRaises(ValueError):
            Task("Test", priority='')

    def test_default_priority(self):
        """Test default priority value"""
        task = Task("Test")
        self.assertEqual(task.priority, 'medium')

    def test_custom_priority(self):
        """Test setting custom priority"""
        task = Task("Test", priority='high')
        self.assertEqual(task.priority, 'high')

    def test_due_date(self):
        """Test due_date field"""
        task = Task("Test", due_date='2025-12-31')
        self.assertEqual(task.due_date, '2025-12-31')

    def test_due_date_default_none(self):
        """Test due_date defaults to None"""
        task = Task("Test")
        self.assertIsNone(task.due_date)

    def test_reminder(self):
        """Test reminder field"""
        task = Task("Test", reminder='2025-12-01T10:00:00')
        self.assertEqual(task.reminder, '2025-12-01T10:00:00')

    def test_reminder_default_none(self):
        """Test reminder defaults to None"""
        task = Task("Test")
        self.assertIsNone(task.reminder)

    def test_to_dict_with_all_fields(self):
        """Test to_dict includes priority/due_date/reminder when set"""
        task = Task("Test", priority='high', due_date='2025-12-31',
                    reminder='2025-12-01T10:00:00')
        data = task.to_dict()
        self.assertEqual(data['priority'], 'high')
        self.assertEqual(data['due_date'], '2025-12-31')
        self.assertEqual(data['reminder'], '2025-12-01T10:00:00')

    def test_to_dict_omits_defaults(self):
        """Test to_dict omits fields with default values"""
        task = Task("Test")
        data = task.to_dict()
        self.assertNotIn('priority', data)
        self.assertNotIn('due_date', data)
        self.assertNotIn('reminder', data)
        self.assertNotIn('notes', data)
        self.assertNotIn('subtasks', data)

    def test_from_dict_with_priority_due_reminder(self):
        """Test from_dict handles priority, due_date, and reminder"""
        data = {
            'text': 'Test',
            'completed': False,
            'created': '2025-01-01T10:00:00',
            'priority': 'low',
            'due_date': '2025-06-15',
            'reminder': '2025-06-14T09:00:00'
        }
        task = Task.from_dict(data)
        self.assertEqual(task.priority, 'low')
        self.assertEqual(task.due_date, '2025-06-15')
        self.assertEqual(task.reminder, '2025-06-14T09:00:00')

    def test_from_dict_defaults_missing_fields(self):
        """Test from_dict applies defaults for missing optional fields"""
        data = {'text': 'Minimal', 'completed': False}
        task = Task.from_dict(data)
        self.assertEqual(task.priority, 'medium')
        self.assertIsNone(task.due_date)
        self.assertIsNone(task.reminder)
        self.assertEqual(task.notes, [])
        self.assertEqual(task.subtasks, [])

    def test_from_dict_clamps_invalid_priority(self):
        """Test from_dict clamps invalid priority to 'medium'"""
        data = {'text': 'Test', 'priority': 'banana'}
        task = Task.from_dict(data)
        self.assertEqual(task.priority, 'medium')

    def test_from_dict_skips_malformed_subtasks(self):
        """Test from_dict skips malformed subtask entries"""
        data = {
            'text': 'Test',
            'completed': False,
            'subtasks': [
                {'text': 'Valid', 'completed': False},
                {'completed': True},           # missing text
                None,                          # not a dict
                {'text': '', 'completed': False},  # empty text
                {'text': 'Also valid', 'completed': True}
            ]
        }
        task = Task.from_dict(data)
        self.assertEqual(task.get_subtask_count(), 2)
        self.assertEqual(task.subtasks[0].text, 'Valid')
        self.assertEqual(task.subtasks[1].text, 'Also valid')

    def test_from_dict_notes_not_aliased(self):
        """Test from_dict creates a copy of notes list (no aliasing)"""
        data = {'text': 'Test', 'notes': ['note1', 'note2']}
        task = Task.from_dict(data)
        task.notes.append('note3')
        self.assertEqual(len(data['notes']), 2)  # Original unchanged


class TestCategory(unittest.TestCase):
    """Tests for Category class"""

    def test_create_category(self):
        """Test creating a category"""
        cat = Category(1, "Work")
        self.assertEqual(cat.id, 1)
        self.assertEqual(cat.name, "Work")
        self.assertEqual(len(cat.tasks), 0)

    def test_category_empty_name_raises(self):
        """Test creating category with empty name raises ValueError"""
        with self.assertRaises(ValueError):
            Category(1, "")
        with self.assertRaises(ValueError):
            Category(1, "   ")

    def test_category_name_stripped(self):
        """Test category name is stripped of whitespace"""
        cat = Category(1, "  Work  ")
        self.assertEqual(cat.name, "Work")

    def test_add_task(self):
        """Test adding tasks"""
        cat = Category(1, "Work")
        task1 = Task("Task 1")
        task2 = Task("Task 2")
        cat.add_task(task1)
        cat.add_task(task2)
        self.assertEqual(cat.get_task_count(), 2)

    def test_remove_task(self):
        """Test removing tasks"""
        cat = Category(1, "Work")
        task1 = Task("Task 1")
        task2 = Task("Task 2")
        cat.add_task(task1)
        cat.add_task(task2)

        removed = cat.remove_task(0)
        self.assertEqual(removed.text, "Task 1")
        self.assertEqual(cat.get_task_count(), 1)

    def test_get_task(self):
        """Test getting a task by index"""
        cat = Category(1, "Work")
        task1 = Task("Task 1")
        cat.add_task(task1)

        retrieved = cat.get_task(0)
        self.assertEqual(retrieved.text, "Task 1")

    def test_get_completed_tasks(self):
        """Test getting completed tasks"""
        cat = Category(1, "Work")
        task1 = Task("Task 1", completed=True)
        task2 = Task("Task 2", completed=False)
        task3 = Task("Task 3", completed=True)
        cat.add_task(task1)
        cat.add_task(task2)
        cat.add_task(task3)

        completed = cat.get_completed_tasks()
        self.assertEqual(len(completed), 2)

    def test_get_pending_tasks(self):
        """Test getting pending tasks"""
        cat = Category(1, "Work")
        task1 = Task("Task 1", completed=True)
        task2 = Task("Task 2", completed=False)
        task3 = Task("Task 3", completed=False)
        cat.add_task(task1)
        cat.add_task(task2)
        cat.add_task(task3)

        pending = cat.get_pending_tasks()
        self.assertEqual(len(pending), 2)

    def test_clear_completed(self):
        """Test clearing completed tasks"""
        cat = Category(1, "Work")
        cat.add_task(Task("Task 1", completed=True))
        cat.add_task(Task("Task 2", completed=False))
        cat.add_task(Task("Task 3", completed=True))

        count = cat.clear_completed()
        self.assertEqual(count, 2)
        self.assertEqual(cat.get_task_count(), 1)

    def test_get_completion_percentage(self):
        """Test getting completion percentage"""
        cat = Category(1, "Work")
        cat.add_task(Task("Task 1", completed=True))
        cat.add_task(Task("Task 2", completed=False))
        cat.add_task(Task("Task 3", completed=True))
        cat.add_task(Task("Task 4", completed=True))

        percentage = cat.get_completion_percentage()
        self.assertEqual(percentage, 75.0)

    def test_to_dict(self):
        """Test converting category to dictionary"""
        cat = Category(1, "Work")
        cat.add_task(Task("Task 1"))
        data = cat.to_dict()

        self.assertEqual(data['id'], 1)
        self.assertEqual(data['name'], "Work")
        self.assertEqual(len(data['tasks']), 1)

    def test_from_dict(self):
        """Test creating category from dictionary"""
        data = {
            'id': 1,
            'name': 'Work',
            'tasks': [
                {'text': 'Task 1', 'completed': False, 'created': '2025-01-01T10:00:00'}
            ]
        }
        cat = Category.from_dict(data)

        self.assertEqual(cat.id, 1)
        self.assertEqual(cat.name, "Work")
        self.assertEqual(cat.get_task_count(), 1)


class TestChecklist(unittest.TestCase):
    """Tests for Checklist class"""

    def test_create_checklist(self):
        """Test creating a checklist"""
        cl = Checklist()
        self.assertEqual(len(cl.categories), 0)
        self.assertIsNone(cl.current_category_id)

    def test_add_category(self):
        """Test adding categories"""
        cl = Checklist()
        cat1 = Category(1, "Work")
        cat2 = Category(2, "Personal")
        cl.add_category(cat1)
        cl.add_category(cat2)
        self.assertEqual(cl.get_category_count(), 2)

    def test_remove_category(self):
        """Test removing categories"""
        cl = Checklist()
        cat1 = Category(1, "Work")
        cat2 = Category(2, "Personal")
        cl.add_category(cat1)
        cl.add_category(cat2)

        removed = cl.remove_category(1)
        self.assertEqual(removed.name, "Work")
        self.assertEqual(cl.get_category_count(), 1)

    def test_get_category(self):
        """Test getting category by ID"""
        cl = Checklist()
        cat1 = Category(1, "Work")
        cl.add_category(cat1)

        retrieved = cl.get_category(1)
        self.assertEqual(retrieved.name, "Work")

    def test_get_current_category(self):
        """Test getting current category"""
        cl = Checklist()
        cat1 = Category(1, "Work")
        cl.add_category(cat1)

        # No current category
        self.assertIsNone(cl.get_current_category())

        # Set current category
        cl.set_current_category(1)
        current = cl.get_current_category()
        self.assertEqual(current.name, "Work")

    def test_set_current_category(self):
        """Test setting current category"""
        cl = Checklist()
        cat1 = Category(1, "Work")
        cl.add_category(cat1)

        # Valid ID
        result = cl.set_current_category(1)
        self.assertTrue(result)
        self.assertEqual(cl.current_category_id, 1)

        # Invalid ID
        result = cl.set_current_category(999)
        self.assertFalse(result)

    def test_get_next_category_id(self):
        """Test getting next category ID"""
        cl = Checklist()

        # Empty checklist
        self.assertEqual(cl.get_next_category_id(), 1)

        # With categories
        cl.add_category(Category(1, "Work"))
        cl.add_category(Category(5, "Personal"))
        self.assertEqual(cl.get_next_category_id(), 6)

    def test_reorder_categories(self):
        """Test reordering categories"""
        cl = Checklist()
        cat1 = Category(1, "First")
        cat2 = Category(2, "Second")
        cat3 = Category(3, "Third")
        cl.add_category(cat1)
        cl.add_category(cat2)
        cl.add_category(cat3)

        # Move first to last
        result = cl.reorder_categories(0, 2)
        self.assertTrue(result)
        self.assertEqual(cl.categories[0].name, "Second")
        self.assertEqual(cl.categories[2].name, "First")

    def test_get_category_by_index(self):
        """Test getting category by index"""
        cl = Checklist()
        cat1 = Category(1, "Work")
        cl.add_category(cat1)

        retrieved = cl.get_category_by_index(0)
        self.assertEqual(retrieved.name, "Work")

    def test_get_total_task_count(self):
        """Test getting total task count"""
        cl = Checklist()
        cat1 = Category(1, "Work")
        cat1.add_task(Task("Task 1"))
        cat1.add_task(Task("Task 2"))
        cat2 = Category(2, "Personal")
        cat2.add_task(Task("Task 3"))
        cl.add_category(cat1)
        cl.add_category(cat2)

        self.assertEqual(cl.get_total_task_count(), 3)

    def test_get_total_completed_count(self):
        """Test getting total completed count"""
        cl = Checklist()
        cat1 = Category(1, "Work")
        cat1.add_task(Task("Task 1", completed=True))
        cat1.add_task(Task("Task 2", completed=False))
        cat2 = Category(2, "Personal")
        cat2.add_task(Task("Task 3", completed=True))
        cl.add_category(cat1)
        cl.add_category(cat2)

        self.assertEqual(cl.get_total_completed_count(), 2)

    def test_to_dict(self):
        """Test converting checklist to dictionary"""
        cl = Checklist()
        cat1 = Category(1, "Work")
        cat1.add_task(Task("Task 1"))
        cl.add_category(cat1)
        cl.set_current_category(1)

        data = cl.to_dict()
        self.assertEqual(len(data['categories']), 1)
        self.assertEqual(data['current_category'], 1)

    def test_from_dict(self):
        """Test creating checklist from dictionary"""
        data = {
            'categories': [
                {
                    'id': 1,
                    'name': 'Work',
                    'tasks': [
                        {'text': 'Task 1', 'completed': False, 'created': '2025-01-01T10:00:00'}
                    ]
                }
            ],
            'current_category': 1
        }
        cl = Checklist.from_dict(data)

        self.assertEqual(cl.get_category_count(), 1)
        self.assertEqual(cl.current_category_id, 1)

    def test_from_dict_does_not_mutate_input(self):
        """Test from_dict does not modify the input dictionary"""
        import copy
        data = {
            'categories': [
                {
                    'id': 1,
                    'name': 'Work',
                    'tasks': [
                        {'text': 'Task 1', 'completed': False}
                    ]
                }
            ],
            'current_category': 1
        }
        original = copy.deepcopy(data)
        Checklist.from_dict(data)
        self.assertEqual(data, original)

    def test_from_dict_skips_invalid_categories(self):
        """Test from_dict skips categories without id"""
        data = {
            'categories': [
                {'name': 'No ID', 'tasks': []},
                {'id': 1, 'name': 'Valid', 'tasks': []}
            ],
            'current_category': 1
        }
        cl = Checklist.from_dict(data)
        self.assertEqual(cl.get_category_count(), 1)
        self.assertEqual(cl.categories[0].name, 'Valid')

    def test_from_dict_skips_empty_text_tasks(self):
        """Test from_dict skips tasks with empty or missing text"""
        data = {
            'categories': [{
                'id': 1, 'name': 'Work',
                'tasks': [
                    {'text': 'Valid task', 'completed': False},
                    {'text': '', 'completed': False},
                    {'completed': True}
                ]
            }]
        }
        cl = Checklist.from_dict(data)
        self.assertEqual(cl.get_category(1).get_task_count(), 1)

    def test_from_dict_fixes_invalid_current_category(self):
        """Test from_dict corrects invalid current_category_id"""
        data = {
            'categories': [{'id': 1, 'name': 'Work', 'tasks': []}],
            'current_category': 999
        }
        cl = Checklist.from_dict(data)
        self.assertEqual(cl.current_category_id, 1)

    def test_from_dict_defaults_missing_fields(self):
        """Test from_dict applies defaults for missing optional fields"""
        data = {
            'categories': [{
                'id': 1, 'name': 'Work',
                'tasks': [{'text': 'Minimal task'}]
            }]
        }
        cl = Checklist.from_dict(data)
        task = cl.get_category(1).get_task(0)
        self.assertFalse(task.completed)
        self.assertEqual(task.priority, 'medium')
        self.assertIsNone(task.due_date)
        self.assertIsNone(task.reminder)

    def test_roundtrip_to_dict_from_dict(self):
        """Test that to_dict/from_dict roundtrip preserves data"""
        cl = Checklist()
        cat = Category(1, "Work")
        task = Task("My task", priority='high', due_date='2025-12-31',
                    reminder='2025-12-30T09:00:00', notes=['note1'])
        task.add_subtask(Subtask("Sub 1", completed=True))
        cat.add_task(task)
        cl.add_category(cat)
        cl.set_current_category(1)

        data = cl.to_dict()
        restored = Checklist.from_dict(data)

        self.assertEqual(restored.get_category_count(), 1)
        self.assertEqual(restored.current_category_id, 1)
        restored_task = restored.get_category(1).get_task(0)
        self.assertEqual(restored_task.text, "My task")
        self.assertEqual(restored_task.priority, 'high')
        self.assertEqual(restored_task.due_date, '2025-12-31')
        self.assertEqual(restored_task.reminder, '2025-12-30T09:00:00')
        self.assertEqual(restored_task.notes, ['note1'])
        self.assertEqual(restored_task.get_subtask_count(), 1)
        self.assertTrue(restored_task.subtasks[0].completed)


if __name__ == '__main__':
    unittest.main()
