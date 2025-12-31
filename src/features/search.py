"""
Search functionality for Simple Checklist
Provides task searching and filtering capabilities
"""


class TaskSearcher:
    """Search and filter tasks across categories"""

    @staticmethod
    def search_tasks(categories, query, category_id=None, include_completed=True):
        """
        Search for tasks matching query string

        Args:
            categories: List of category dictionaries
            query: Search query string
            category_id: Optional - only search in this category
            include_completed: Whether to include completed tasks

        Returns:
            List of result dicts with category info and task details
        """
        results = []
        query_lower = query.lower().strip()

        if not query_lower:
            return results

        # Filter categories if specific category requested
        if category_id is not None:
            cats_to_search = [c for c in categories if c['id'] == category_id]
        else:
            cats_to_search = categories

        for cat in cats_to_search:
            for task_idx, task in enumerate(cat.get('tasks', [])):
                # Skip completed tasks if not included
                if not include_completed and task.get('completed', False):
                    continue

                # Track if task already matched to prevent duplicates
                matched = False

                # Check main task text
                if query_lower in task.get('text', '').lower():
                    results.append({
                        'category_id': cat['id'],
                        'category_name': cat['name'],
                        'task_idx': task_idx,
                        'task': task,
                        'match_type': 'task'
                    })
                    matched = True

                # Check subtasks (only if not already matched)
                if not matched:
                    for subtask in task.get('subtasks', []):
                        if query_lower in subtask.get('text', '').lower():
                            results.append({
                                'category_id': cat['id'],
                                'category_name': cat['name'],
                                'task_idx': task_idx,
                                'task': task,
                                'match_type': 'subtask'
                            })
                            matched = True
                            break

                # Check notes (only if not already matched)
                if not matched:
                    for note in task.get('notes', []):
                        if query_lower in note.lower():
                            results.append({
                                'category_id': cat['id'],
                                'category_name': cat['name'],
                                'task_idx': task_idx,
                                'task': task,
                                'match_type': 'note'
                            })
                            break

        return results

    @staticmethod
    def filter_by_status(tasks, completed=None):
        """
        Filter tasks by completion status

        Args:
            tasks: List of task dictionaries
            completed: None for all, True for completed only, False for pending only

        Returns:
            Filtered list of tasks
        """
        if completed is None:
            return tasks
        return [t for t in tasks if t.get('completed', False) == completed]

    @staticmethod
    def filter_by_reminder(tasks, has_reminder=True):
        """
        Filter tasks by reminder status

        Args:
            tasks: List of task dictionaries
            has_reminder: True for tasks with reminders, False for without

        Returns:
            Filtered list of tasks
        """
        if has_reminder:
            return [t for t in tasks if t.get('reminder')]
        return [t for t in tasks if not t.get('reminder')]
