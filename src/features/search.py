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
            categories: List of Category model objects
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
            cats_to_search = [c for c in categories if c.id == category_id]
        else:
            cats_to_search = categories

        for cat in cats_to_search:
            for task_idx, task in enumerate(cat.tasks):
                # Skip completed tasks if not included
                if not include_completed and task.completed:
                    continue

                # Track if task already matched to prevent duplicates
                matched = False

                # Check main task text
                if query_lower in task.text.lower():
                    results.append({
                        'category_id': cat.id,
                        'category_name': cat.name,
                        'task_idx': task_idx,
                        'task': task,
                        'match_type': 'task'
                    })
                    matched = True

                # Check subtasks (only if not already matched)
                if not matched:
                    for subtask in task.subtasks:
                        if query_lower in subtask.text.lower():
                            results.append({
                                'category_id': cat.id,
                                'category_name': cat.name,
                                'task_idx': task_idx,
                                'task': task,
                                'match_type': 'subtask'
                            })
                            matched = True
                            break

                # Check notes (only if not already matched)
                if not matched:
                    for note in task.notes:
                        if query_lower in note.lower():
                            results.append({
                                'category_id': cat.id,
                                'category_name': cat.name,
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
            tasks: List of Task model objects
            completed: None for all, True for completed only, False for pending only

        Returns:
            Filtered list of tasks
        """
        if completed is None:
            return tasks
        return [t for t in tasks if t.completed == completed]

    @staticmethod
    def filter_by_reminder(tasks, has_reminder=True):
        """
        Filter tasks by reminder status

        Args:
            tasks: List of Task model objects
            has_reminder: True for tasks with reminders, False for without

        Returns:
            Filtered list of tasks
        """
        if has_reminder:
            return [t for t in tasks if t.reminder]
        return [t for t in tasks if not t.reminder]
