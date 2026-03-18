"""
Checklist model
Manages the entire checklist with multiple categories
"""

from typing import List, Dict, Any, Optional
from .category import Category
from .task import Task


class Checklist:
    """Represents a complete checklist with multiple categories"""

    def __init__(self, categories: Optional[List[Category]] = None, current_category_id: Optional[int] = None):
        """
        Initialize a checklist

        Args:
            categories: Optional list of Category objects
            current_category_id: ID of the currently selected category
        """
        self.categories = categories or []
        self.current_category_id = current_category_id

    def add_category(self, category: Category) -> None:
        """
        Add a category to the checklist

        Args:
            category: Category to add
        """
        self.categories.append(category)

    def remove_category(self, category_id: int) -> Optional[Category]:
        """
        Remove a category by ID

        Args:
            category_id: ID of the category to remove

        Returns:
            The removed category, or None if not found
        """
        for i, cat in enumerate(self.categories):
            if cat.id == category_id:
                return self.categories.pop(i)
        return None

    def get_category(self, category_id: int) -> Optional[Category]:
        """
        Get a category by ID

        Args:
            category_id: ID of the category

        Returns:
            The category, or None if not found
        """
        for cat in self.categories:
            if cat.id == category_id:
                return cat
        return None

    def get_current_category(self) -> Optional[Category]:
        """
        Get the currently selected category

        Returns:
            The current category, or None if no category is selected
        """
        if self.current_category_id is None:
            return None
        return self.get_category(self.current_category_id)

    def set_current_category(self, category_id: int) -> bool:
        """
        Set the current category

        Args:
            category_id: ID of the category to set as current

        Returns:
            True if successful, False if category not found
        """
        if self.get_category(category_id) is not None:
            self.current_category_id = category_id
            return True
        return False

    def get_category_count(self) -> int:
        """Get the total number of categories"""
        return len(self.categories)

    def get_next_category_id(self) -> int:
        """
        Get the next available category ID

        Returns:
            Next unused category ID
        """
        if not self.categories:
            return 1
        return max(cat.id for cat in self.categories) + 1

    def reorder_categories(self, from_index: int, to_index: int) -> bool:
        """
        Reorder categories by moving one from one index to another

        Args:
            from_index: Source index
            to_index: Destination index

        Returns:
            True if successful, False otherwise
        """
        if (0 <= from_index < len(self.categories) and
            0 <= to_index < len(self.categories) and
            from_index != to_index):
            category = self.categories.pop(from_index)
            self.categories.insert(to_index, category)
            return True
        return False

    def get_category_by_index(self, index: int) -> Optional[Category]:
        """
        Get a category by its position index

        Args:
            index: Position index

        Returns:
            The category at that index, or None if invalid
        """
        if 0 <= index < len(self.categories):
            return self.categories[index]
        return None

    def get_total_task_count(self) -> int:
        """Get the total number of tasks across all categories"""
        return sum(cat.get_task_count() for cat in self.categories)

    def get_total_completed_count(self) -> int:
        """Get the total number of completed tasks across all categories"""
        return sum(len(cat.get_completed_tasks()) for cat in self.categories)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert checklist to dictionary for serialization

        Returns:
            Dictionary representation of the checklist
        """
        return {
            'categories': [cat.to_dict() for cat in self.categories],
            'current_category': self.current_category_id
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Checklist':
        """
        Create a Checklist from a dictionary with data migration/validation

        Args:
            data: Dictionary containing checklist data

        Returns:
            New Checklist instance
        """
        categories = []
        for raw_cat in data.get('categories', []):
            # Validate category has required fields
            if 'id' not in raw_cat:
                continue
            # Work on a copy to avoid mutating the input
            cat_data = dict(raw_cat)
            if 'name' not in cat_data:
                cat_data['name'] = f"Category {cat_data['id']}"
            if 'tasks' not in cat_data:
                cat_data['tasks'] = []

            # Validate and clean tasks
            valid_tasks = []
            for raw_task in cat_data.get('tasks', []):
                if 'text' not in raw_task or not raw_task['text']:
                    continue
                task_data = dict(raw_task)
                if 'completed' not in task_data:
                    task_data['completed'] = False
                # Validate subtasks
                if 'subtasks' in task_data:
                    valid_subtasks = []
                    for st_data in task_data['subtasks']:
                        if not isinstance(st_data, dict):
                            continue
                        if 'text' not in st_data or not st_data['text']:
                            continue
                        if 'completed' not in st_data:
                            st_data = dict(st_data)
                            st_data['completed'] = False
                        valid_subtasks.append(st_data)
                    task_data['subtasks'] = valid_subtasks
                valid_tasks.append(task_data)

            cat_data['tasks'] = valid_tasks
            categories.append(Category.from_dict(cat_data))

        current_id = data.get('current_category')
        checklist = cls(categories=categories, current_category_id=current_id)

        # Ensure current_category_id is valid
        if current_id is not None and checklist.get_category(current_id) is None:
            if checklist.categories:
                checklist.current_category_id = checklist.categories[0].id
            else:
                checklist.current_category_id = None

        return checklist

    def __repr__(self) -> str:
        total_tasks = self.get_total_task_count()
        total_completed = self.get_total_completed_count()
        return f"Checklist({len(self.categories)} categories, {total_completed}/{total_tasks} tasks)"
