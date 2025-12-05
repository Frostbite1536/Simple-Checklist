"""
Task input area component for Simple Checklist
Handles task input with multi-line support and keyboard shortcuts
"""

import tkinter as tk


class InputArea:
    """Task input component with hints and shortcuts"""

    def __init__(self, parent, on_add_task_callback, input_bg_color='white'):
        """
        Initialize the input area

        Args:
            parent: Parent widget
            on_add_task_callback: Callback function() called when Shift+Enter is pressed
            input_bg_color: Background color for the input box
        """
        self.on_add_task_callback = on_add_task_callback
        self.input_bg_color = input_bg_color

        # Create the input frame
        self.frame = tk.Frame(parent, bg='#fafafa')

        self.task_input = tk.Text(self.frame, height=3,
                                 font=('Segoe UI', 11),
                                 relief=tk.FLAT, bg=self.input_bg_color,
                                 borderwidth=2)
        self.task_input.pack(fill=tk.X)

        hints = tk.Label(self.frame,
                        text="💡 Shift+Enter: New task | Enter: New line | Ctrl+1-9: Switch categories",
                        bg='#fafafa', fg='#7f8c8d',
                        font=('Segoe UI', 9))
        hints.pack(pady=5)

        # Setup keyboard shortcuts
        self._setup_shortcuts()

    def _setup_shortcuts(self):
        """Setup keyboard shortcuts for input"""
        def add_task_handler(e):
            self.on_add_task_callback()
            return 'break'

        self.task_input.bind('<Shift-Return>', add_task_handler)

    def pack(self, **kwargs):
        """Pack the input area frame"""
        self.frame.pack(**kwargs)

    def grid(self, **kwargs):
        """Grid the input area frame"""
        self.frame.grid(**kwargs)

    def get_text(self):
        """
        Get the text from the input field

        Returns:
            Stripped text from the input field
        """
        return self.task_input.get('1.0', tk.END).strip()

    def clear(self):
        """Clear the input field"""
        self.task_input.delete('1.0', tk.END)

    def set_bg_color(self, color):
        """
        Set the background color of the input field

        Args:
            color: Color string (hex or name)
        """
        self.input_bg_color = color
        self.task_input.config(bg=color)

    def focus(self):
        """Set focus to the input field"""
        self.task_input.focus()
