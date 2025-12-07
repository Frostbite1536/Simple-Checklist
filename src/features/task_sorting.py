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
            tasks: List of task dictionaries
            sort_by: Sort key - 'created', 'due_date', 'priority', 'completion', 'a-z'
            reverse: Whether to reverse the sort order

        Returns:
            Sorted list of tasks (modifies in place and returns)
        """
        if not tasks:
            return tasks

        if sort_by == 'created':
            # Sort by creation date (oldest first by default)
            tasks.sort(key=lambda t: t.get('created', ''), reverse=reverse)

        elif sort_by == 'due_date':
            # Sort by due date (earliest first, tasks without due date at end)
            tasks.sort(
                key=lambda t: t.get('due_date', '9999-12-31') or '9999-12-31',
                reverse=reverse
            )

        elif sort_by == 'priority':
            # Sort by priority (high first by default)
            tasks.sort(
                key=lambda t: TaskSorter.PRIORITY_ORDER.get(
                    t.get('priority', 'medium'), 1
                ),
                reverse=reverse
            )

        elif sort_by == 'completion':
            # Sort by completion status (incomplete first by default)
            tasks.sort(key=lambda t: t.get('completed', False), reverse=reverse)

        elif sort_by == 'a-z':
            # Sort alphabetically by task text
            tasks.sort(key=lambda t: t.get('text', '').lower(), reverse=reverse)

        return tasks

    @staticmethod
    def sort_smart(tasks):
        """
        Smart sort: incomplete first, then by priority (high to low), then by due date

        Args:
            tasks: List of task dictionaries

        Returns:
            Sorted list of tasks
        """
        if not tasks:
            return tasks

        def smart_key(task):
            # Completed tasks go to the bottom
            completed = 1 if task.get('completed', False) else 0
            # Priority order (high=0, medium=1, low=2)
            priority = TaskSorter.PRIORITY_ORDER.get(
                task.get('priority', 'medium'), 1
            )
            # Due date (earlier dates first, no date at end)
            due_date = task.get('due_date', '9999-12-31') or '9999-12-31'
            return (completed, priority, due_date)

        tasks.sort(key=smart_key)
        return tasks
