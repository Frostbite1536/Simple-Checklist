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
        Create a Checklist from a dictionary

        Args:
            data: Dictionary containing checklist data

        Returns:
            New Checklist instance
        """
        categories = []
        if 'categories' in data:
            categories = [Category.from_dict(cat_data) for cat_data in data['categories']]

        return cls(
            categories=categories,
            current_category_id=data.get('current_category')
        )

    def __repr__(self) -> str:
        total_tasks = self.get_total_task_count()
        total_completed = self.get_total_completed_count()
        return f"Checklist({len(self.categories)} categories, {total_completed}/{total_tasks} tasks)"
