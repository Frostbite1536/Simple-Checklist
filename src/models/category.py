"""
Category model
Manages a collection of tasks
"""

from typing import List, Dict, Any, Optional
from .task import Task


class Category:
    """Represents a category containing tasks"""

    def __init__(self, category_id: int, name: str, tasks: Optional[List[Task]] = None):
        """
        Initialize a category

        Args:
            category_id: Unique identifier for this category
            name: Display name of the category
            tasks: Optional list of Task objects
        """
        self.id = category_id
        self.name = name
        self.tasks = tasks or []

    def add_task(self, task: Task) -> None:
        """
        Add a task to this category

        Args:
            task: Task to add
        """
        self.tasks.append(task)

    def remove_task(self, index: int) -> Optional[Task]:
        """
        Remove a task by index

        Args:
            index: Index of the task to remove

        Returns:
            The removed task, or None if index is invalid
        """
        if 0 <= index < len(self.tasks):
            return self.tasks.pop(index)
        return None

    def get_task(self, index: int) -> Optional[Task]:
        """
        Get a task by index

        Args:
            index: Index of the task

        Returns:
            The task at the index, or None if invalid
        """
        if 0 <= index < len(self.tasks):
            return self.tasks[index]
        return None

    def get_task_count(self) -> int:
        """Get the total number of tasks"""
        return len(self.tasks)

    def get_completed_tasks(self) -> List[Task]:
        """
        Get all completed tasks

        Returns:
            List of completed tasks
        """
        return [task for task in self.tasks if task.completed]

    def get_pending_tasks(self) -> List[Task]:
        """
        Get all pending (incomplete) tasks

        Returns:
            List of pending tasks
        """
        return [task for task in self.tasks if not task.completed]

    def clear_completed(self) -> int:
        """
        Remove all completed tasks

        Returns:
            Number of tasks removed
        """
        completed_count = len(self.get_completed_tasks())
        self.tasks = self.get_pending_tasks()
        return completed_count

    def get_completion_percentage(self) -> float:
        """
        Get the completion percentage

        Returns:
            Percentage of completed tasks (0-100)
        """
        if not self.tasks:
            return 0.0
        completed = len(self.get_completed_tasks())
        return (completed / len(self.tasks)) * 100

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert category to dictionary for serialization

        Returns:
            Dictionary representation of the category
        """
        return {
            'id': self.id,
            'name': self.name,
            'tasks': [task.to_dict() for task in self.tasks]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Category':
        """
        Create a Category from a dictionary

        Args:
            data: Dictionary containing category data

        Returns:
            New Category instance
        """
        tasks = []
        if 'tasks' in data:
            tasks = [Task.from_dict(task_data) for task_data in data['tasks']]

        return cls(
            category_id=data['id'],
            name=data['name'],
            tasks=tasks
        )

    def __repr__(self) -> str:
        completed = len(self.get_completed_tasks())
        total = len(self.tasks)
        return f"Category({self.name}, {completed}/{total} tasks)"
