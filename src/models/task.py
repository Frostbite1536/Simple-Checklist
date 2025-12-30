"""
Task and Subtask models
Pure business logic with no UI dependencies
"""

from datetime import datetime
from typing import List, Dict, Any, Optional


class Subtask:
    """Represents a sub-task within a task"""

    def __init__(self, text: str, completed: bool = False):
        """
        Initialize a subtask

        Args:
            text: The subtask text
            completed: Whether the subtask is completed
        """
        self.text = text
        self.completed = completed

    def toggle_completion(self) -> None:
        """Toggle the completion status of this subtask"""
        self.completed = not self.completed

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert subtask to dictionary for serialization

        Returns:
            Dictionary representation of the subtask
        """
        return {
            'text': self.text,
            'completed': self.completed
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Subtask':
        """
        Create a Subtask from a dictionary

        Args:
            data: Dictionary containing subtask data

        Returns:
            New Subtask instance
        """
        return cls(
            text=data['text'],
            completed=data.get('completed', False)
        )

    def __repr__(self) -> str:
        status = "✓" if self.completed else "○"
        return f"Subtask({status} {self.text})"


class Task:
    """Represents a task with optional notes and subtasks"""

    def __init__(
        self,
        text: str,
        completed: bool = False,
        notes: Optional[List[str]] = None,
        subtasks: Optional[List[Subtask]] = None,
        created: Optional[str] = None,
        priority: str = 'medium',
        due_date: Optional[str] = None,
        reminder: Optional[str] = None
    ):
        """
        Initialize a task

        Args:
            text: The main task text
            completed: Whether the task is completed
            notes: Optional list of notes
            subtasks: Optional list of Subtask objects
            created: ISO format timestamp of creation (auto-generated if None)
            priority: Task priority ('low', 'medium', 'high')
            due_date: Due date in YYYY-MM-DD format
            reminder: Reminder datetime in ISO format
        """
        self.text = text
        self.completed = completed
        self.notes = notes or []
        self.subtasks = subtasks or []
        self.created = created or datetime.now().isoformat()
        self.priority = priority
        self.due_date = due_date
        self.reminder = reminder

    def toggle_completion(self) -> None:
        """Toggle the completion status of this task"""
        self.completed = not self.completed

    def add_subtask(self, subtask: Subtask) -> None:
        """
        Add a subtask to this task

        Args:
            subtask: Subtask to add
        """
        self.subtasks.append(subtask)

    def remove_subtask(self, index: int) -> Optional[Subtask]:
        """
        Remove a subtask by index

        Args:
            index: Index of the subtask to remove

        Returns:
            The removed subtask, or None if index is invalid
        """
        if 0 <= index < len(self.subtasks):
            return self.subtasks.pop(index)
        return None

    def add_note(self, note: str) -> None:
        """
        Add a note to this task

        Args:
            note: Note text to add
        """
        self.notes.append(note)

    def get_subtask_count(self) -> int:
        """Get the number of subtasks"""
        return len(self.subtasks)

    def get_completed_subtask_count(self) -> int:
        """Get the number of completed subtasks"""
        return sum(1 for st in self.subtasks if st.completed)

    def is_fully_completed(self) -> bool:
        """
        Check if task and all subtasks are completed

        Returns:
            True if task and all subtasks are completed
        """
        if not self.completed:
            return False
        return all(st.completed for st in self.subtasks)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert task to dictionary for serialization

        Returns:
            Dictionary representation of the task
        """
        result = {
            'text': self.text,
            'completed': self.completed,
            'created': self.created
        }

        if self.notes:
            result['notes'] = self.notes

        if self.subtasks:
            result['subtasks'] = [st.to_dict() for st in self.subtasks]

        # Include priority, due_date, and reminder if set
        if self.priority != 'medium':
            result['priority'] = self.priority

        if self.due_date:
            result['due_date'] = self.due_date

        if self.reminder:
            result['reminder'] = self.reminder

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """
        Create a Task from a dictionary

        Args:
            data: Dictionary containing task data

        Returns:
            New Task instance
        """
        subtasks = []
        if 'subtasks' in data:
            subtasks = [Subtask.from_dict(st) for st in data['subtasks']]

        return cls(
            text=data.get('text', ''),  # Default to empty string if missing
            completed=data.get('completed', False),
            notes=data.get('notes', []),
            subtasks=subtasks,
            created=data.get('created'),
            priority=data.get('priority', 'medium'),
            due_date=data.get('due_date'),
            reminder=data.get('reminder')
        )

    def __repr__(self) -> str:
        status = "✓" if self.completed else "○"
        subtask_info = f" [{self.get_completed_subtask_count()}/{self.get_subtask_count()}]" if self.subtasks else ""
        return f"Task({status} {self.text}{subtask_info})"
