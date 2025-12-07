"""
Undo/Redo Manager for Simple Checklist
Tracks state changes and allows undoing/redoing operations
"""

import copy


class UndoManager:
    """Manages undo/redo state history for the application"""

    def __init__(self, max_history=20):
        """
        Initialize the undo manager

        Args:
            max_history: Maximum number of states to keep in history
        """
        self.undo_stack = []
        self.redo_stack = []
        self.max_history = max_history

    def record_state(self, state, action_description=""):
        """
        Record a state snapshot before a change

        Args:
            state: The current state dict to save
            action_description: Optional description of the action
        """
        self.undo_stack.append({
            'state': copy.deepcopy(state),
            'description': action_description
        })

        # Clear redo stack when new action is recorded
        self.redo_stack = []

        # Limit history size
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)

    def undo(self, current_state):
        """
        Undo the last action

        Args:
            current_state: The current state to save for redo

        Returns:
            The previous state to restore, or None if nothing to undo
        """
        if not self.undo_stack:
            return None

        # Save current state for redo
        self.redo_stack.append({
            'state': copy.deepcopy(current_state),
            'description': 'Redo'
        })

        # Pop and return the previous state
        previous = self.undo_stack.pop()
        return previous['state']

    def redo(self, current_state):
        """
        Redo the last undone action

        Args:
            current_state: The current state to save for undo

        Returns:
            The state to restore, or None if nothing to redo
        """
        if not self.redo_stack:
            return None

        # Save current state for undo
        self.undo_stack.append({
            'state': copy.deepcopy(current_state),
            'description': 'Undo'
        })

        # Pop and return the redo state
        redo_state = self.redo_stack.pop()
        return redo_state['state']

    def can_undo(self):
        """Check if undo is available"""
        return len(self.undo_stack) > 0

    def can_redo(self):
        """Check if redo is available"""
        return len(self.redo_stack) > 0

    def clear(self):
        """Clear all history"""
        self.undo_stack = []
        self.redo_stack = []

    def get_undo_description(self):
        """Get description of the action that would be undone"""
        if self.undo_stack:
            return self.undo_stack[-1].get('description', 'Undo')
        return None

    def get_redo_description(self):
        """Get description of the action that would be redone"""
        if self.redo_stack:
            return self.redo_stack[-1].get('description', 'Redo')
        return None
