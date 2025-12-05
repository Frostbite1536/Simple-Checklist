"""
Drag and Drop Manager
Handles drag-and-drop functionality for category reordering
"""

from typing import Optional, Callable, Any
from ..models.checklist import Checklist


class DragDropManager:
    """Manages drag-and-drop state and operations for category reordering"""

    def __init__(self, checklist: Checklist, on_reorder: Optional[Callable[[], None]] = None):
        """
        Initialize drag-drop manager

        Args:
            checklist: Checklist instance to manage
            on_reorder: Optional callback to invoke after reordering
        """
        self.checklist = checklist
        self.on_reorder = on_reorder
        self.drag_data = {
            'source': None,
            'index': None,
            'source_widget': None
        }

    def start_drag(self, source_index: int, source_widget: Any = None) -> None:
        """
        Begin a drag operation

        Args:
            source_index: Index of the category being dragged
            source_widget: Optional UI widget reference (for cursor updates)
        """
        if 0 <= source_index < self.checklist.get_category_count():
            self.drag_data['index'] = source_index
            self.drag_data['source_widget'] = source_widget

    def handle_drag_motion(self, event: Any = None) -> None:
        """
        Handle drag motion event

        Args:
            event: Optional event object (for UI integration)
        """
        # This can be used to update cursor or visual feedback
        # Implementation depends on UI framework
        pass

    def end_drag(self, target_index: int) -> bool:
        """
        Complete a drag operation and reorder categories

        Args:
            target_index: Index where the category should be dropped

        Returns:
            True if reordering occurred, False otherwise
        """
        source_index = self.drag_data.get('index')

        if source_index is None:
            self.reset_drag()
            return False

        if source_index != target_index:
            # Perform the reorder
            success = self.checklist.reorder_categories(source_index, target_index)

            if success and self.on_reorder:
                self.on_reorder()

            self.reset_drag()
            return success

        self.reset_drag()
        return False

    def reset_drag(self) -> None:
        """Reset drag state"""
        self.drag_data = {
            'source': None,
            'index': None,
            'source_widget': None
        }

    def is_dragging(self) -> bool:
        """
        Check if a drag operation is in progress

        Returns:
            True if dragging, False otherwise
        """
        return self.drag_data.get('index') is not None

    def get_drag_source_index(self) -> Optional[int]:
        """
        Get the index being dragged

        Returns:
            Source index or None if not dragging
        """
        return self.drag_data.get('index')

    def set_cursor_dragging(self, widget: Any) -> None:
        """
        Set drag cursor on widget

        Args:
            widget: Widget to update cursor on
        """
        if hasattr(widget, 'config'):
            widget.config(cursor='fleur')

    def set_cursor_normal(self, widget: Any) -> None:
        """
        Set normal cursor on widget

        Args:
            widget: Widget to update cursor on
        """
        if hasattr(widget, 'config'):
            widget.config(cursor='hand2')

    def validate_reorder(self, from_index: int, to_index: int) -> bool:
        """
        Validate if a reorder operation is valid

        Args:
            from_index: Source index
            to_index: Target index

        Returns:
            True if valid, False otherwise
        """
        count = self.checklist.get_category_count()
        return (0 <= from_index < count and
                0 <= to_index < count and
                from_index != to_index)

    def get_reorder_preview(self, from_index: int, to_index: int) -> Optional[list]:
        """
        Get a preview of how categories would be ordered after reordering

        Args:
            from_index: Source index
            to_index: Target index

        Returns:
            List of category names in new order, or None if invalid
        """
        if not self.validate_reorder(from_index, to_index):
            return None

        # Create a copy of category list
        categories = self.checklist.categories[:]

        # Simulate the reorder
        category = categories.pop(from_index)
        categories.insert(to_index, category)

        # Return category names
        return [cat.name for cat in categories]
