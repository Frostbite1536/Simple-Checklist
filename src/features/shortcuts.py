"""
Keyboard Shortcut Manager
Centralized management of keyboard shortcuts and bindings
"""

from typing import Dict, Callable, Optional, Any, List
from ..utils.constants import Shortcuts


class ShortcutManager:
    """Manages keyboard shortcuts and their bindings"""

    def __init__(self, root_widget: Any = None):
        """
        Initialize shortcut manager

        Args:
            root_widget: Root widget to bind shortcuts to (e.g., tk.Tk instance)
        """
        self.root_widget = root_widget
        self.bindings: Dict[str, List[Callable]] = {}
        self.descriptions: Dict[str, str] = {}

    def register_shortcut(
        self,
        key_sequence: str,
        callback: Callable,
        description: str = ""
    ) -> None:
        """
        Register a keyboard shortcut

        Args:
            key_sequence: Key sequence (e.g., '<Control-s>', '<Shift-Return>')
            callback: Function to call when shortcut is triggered
            description: Human-readable description of what the shortcut does
        """
        if key_sequence not in self.bindings:
            self.bindings[key_sequence] = []

        self.bindings[key_sequence].append(callback)

        if description:
            self.descriptions[key_sequence] = description

    def unregister_shortcut(self, key_sequence: str, callback: Optional[Callable] = None) -> bool:
        """
        Unregister a keyboard shortcut

        Args:
            key_sequence: Key sequence to unregister
            callback: Specific callback to remove (if None, removes all)

        Returns:
            True if something was unregistered, False otherwise
        """
        if key_sequence not in self.bindings:
            return False

        if callback is None:
            # Remove all callbacks for this key sequence
            del self.bindings[key_sequence]
            if key_sequence in self.descriptions:
                del self.descriptions[key_sequence]
            return True
        else:
            # Remove specific callback
            if callback in self.bindings[key_sequence]:
                self.bindings[key_sequence].remove(callback)
                if not self.bindings[key_sequence]:
                    del self.bindings[key_sequence]
                    if key_sequence in self.descriptions:
                        del self.descriptions[key_sequence]
                return True

        return False

    def bind_all(self) -> None:
        """Bind all registered shortcuts to the root widget"""
        if not self.root_widget:
            return

        for key_sequence, callbacks in self.bindings.items():
            # Create a wrapper that calls all callbacks
            def make_handler(cbs):
                def handler(event):
                    for cb in cbs:
                        try:
                            cb(event)
                        except Exception as e:
                            print(f"Error in shortcut handler: {e}")
                    return "break"  # Prevent default handling
                return handler

            self.root_widget.bind(key_sequence, make_handler(callbacks))

    def unbind_all(self) -> None:
        """Unbind all shortcuts from the root widget"""
        if not self.root_widget:
            return

        for key_sequence in self.bindings.keys():
            try:
                self.root_widget.unbind(key_sequence)
            except Exception:
                pass

    def set_root_widget(self, widget: Any) -> None:
        """
        Set the root widget and bind all shortcuts

        Args:
            widget: Root widget to bind to
        """
        self.root_widget = widget
        self.bind_all()

    def get_all_shortcuts(self) -> Dict[str, str]:
        """
        Get all registered shortcuts with descriptions

        Returns:
            Dictionary mapping key sequences to descriptions
        """
        return self.descriptions.copy()

    def is_registered(self, key_sequence: str) -> bool:
        """
        Check if a shortcut is registered

        Args:
            key_sequence: Key sequence to check

        Returns:
            True if registered, False otherwise
        """
        return key_sequence in self.bindings

    def get_shortcut_count(self) -> int:
        """
        Get the number of registered shortcuts

        Returns:
            Number of registered shortcuts
        """
        return len(self.bindings)

    def clear_all(self) -> None:
        """Clear all registered shortcuts"""
        self.unbind_all()
        self.bindings.clear()
        self.descriptions.clear()

    def create_help_text(self) -> str:
        """
        Create help text showing all shortcuts

        Returns:
            Formatted help text
        """
        if not self.descriptions:
            return "No shortcuts registered."

        lines = ["Keyboard Shortcuts:", ""]

        # Group shortcuts by category (based on description)
        for key_seq, desc in sorted(self.descriptions.items()):
            # Format the key sequence for display
            display_key = self._format_key_for_display(key_seq)
            lines.append(f"  {display_key:<20} - {desc}")

        return '\n'.join(lines)

    def _format_key_for_display(self, key_sequence: str) -> str:
        """
        Format a key sequence for display

        Args:
            key_sequence: Key sequence (e.g., '<Control-s>')

        Returns:
            Formatted string (e.g., 'Ctrl+S')
        """
        # Remove angle brackets
        key = key_sequence.strip('<>')

        # Replace common terms
        replacements = {
            'Control-': 'Ctrl+',
            'Shift-': 'Shift+',
            'Alt-': 'Alt+',
            'Command-': 'Cmd+',
            'Return': 'Enter',
            'Key-': ''
        }

        for old, new in replacements.items():
            key = key.replace(old, new)

        return key


class DefaultShortcuts:
    """Default shortcut configurations for Simple Checklist"""

    @staticmethod
    def register_task_shortcuts(manager: ShortcutManager, callbacks: Dict[str, Callable]) -> None:
        """
        Register task-related shortcuts

        Args:
            manager: ShortcutManager instance
            callbacks: Dictionary mapping action names to callback functions
        """
        if 'add_task' in callbacks:
            manager.register_shortcut(
                Shortcuts.ADD_TASK,
                callbacks['add_task'],
                "Add new task"
            )

    @staticmethod
    def register_category_shortcuts(
        manager: ShortcutManager,
        switch_callback: Callable[[int], None]
    ) -> None:
        """
        Register category switching shortcuts (Ctrl+1 through Ctrl+9)

        Args:
            manager: ShortcutManager instance
            switch_callback: Callback function that takes category index
        """
        shortcuts = [
            (Shortcuts.CATEGORY_1, 0),
            (Shortcuts.CATEGORY_2, 1),
            (Shortcuts.CATEGORY_3, 2),
            (Shortcuts.CATEGORY_4, 3),
            (Shortcuts.CATEGORY_5, 4),
            (Shortcuts.CATEGORY_6, 5),
            (Shortcuts.CATEGORY_7, 6),
            (Shortcuts.CATEGORY_8, 7),
            (Shortcuts.CATEGORY_9, 8),
        ]

        for key_seq, index in shortcuts:
            manager.register_shortcut(
                key_seq,
                lambda e, idx=index: switch_callback(idx),
                f"Switch to category {index + 1}"
            )

    @staticmethod
    def register_all_defaults(
        manager: ShortcutManager,
        task_callbacks: Dict[str, Callable],
        switch_category_callback: Callable[[int], None]
    ) -> None:
        """
        Register all default shortcuts

        Args:
            manager: ShortcutManager instance
            task_callbacks: Task-related callbacks
            switch_category_callback: Category switching callback
        """
        DefaultShortcuts.register_task_shortcuts(manager, task_callbacks)
        DefaultShortcuts.register_category_shortcuts(manager, switch_category_callback)
