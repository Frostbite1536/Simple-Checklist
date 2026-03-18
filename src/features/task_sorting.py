"""
Task Sorting functionality for Simple Checklist
Provides various sorting options for tasks
"""


class TaskSorter:
    """Sort tasks by various criteria"""

    # Priority order for sorting
    PRIORITY_ORDER = {'high': 0, 'medium': 1, 'low': 2}

    @staticmethod
    def sort_tasks(tasks, sort_by='created', reverse=False):
        """
        Sort tasks by specified criteria

        Args:
            tasks: List of Task model objects
            sort_by: Sort key - 'created', 'due_date', 'priority', 'completion', 'a-z'
            reverse: Whether to reverse the sort order

        Returns:
            Sorted list of tasks (modifies in place and returns)
        """
        if not tasks:
            return tasks

        if sort_by == 'created':
            tasks.sort(key=lambda t: t.created or '', reverse=reverse)

        elif sort_by == 'due_date':
            tasks.sort(
                key=lambda t: t.due_date or '9999-12-31',
                reverse=reverse
            )

        elif sort_by == 'priority':
            tasks.sort(
                key=lambda t: TaskSorter.PRIORITY_ORDER.get(t.priority, 1),
                reverse=reverse
            )

        elif sort_by == 'completion':
            tasks.sort(key=lambda t: t.completed, reverse=reverse)

        elif sort_by == 'a-z':
            tasks.sort(key=lambda t: t.text.lower(), reverse=reverse)

        return tasks

    @staticmethod
    def sort_smart(tasks):
        """
        Smart sort: incomplete first, then by priority (high to low), then by due date

        Args:
            tasks: List of Task model objects

        Returns:
            Sorted list of tasks
        """
        if not tasks:
            return tasks

        def smart_key(task):
            completed = 1 if task.completed else 0
            priority = TaskSorter.PRIORITY_ORDER.get(task.priority, 1)
            due_date = task.due_date or '9999-12-31'
            return (completed, priority, due_date)

        tasks.sort(key=smart_key)
        return tasks
