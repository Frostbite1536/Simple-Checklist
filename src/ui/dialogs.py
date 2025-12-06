"""
Dialog windows for Simple Checklist
Reusable dialog components for user interactions
"""

import tkinter as tk
from tkinter import messagebox


class AddCategoryDialog:
    """Dialog for adding a new category"""

    def __init__(self, parent, on_add_callback):
        """
        Initialize the add category dialog

        Args:
            parent: Parent window
            on_add_callback: Callback function(name) called when category is added
        """
        self.on_add_callback = on_add_callback

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Category")
        self.dialog.geometry("300x120")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._setup_ui()

    def _setup_ui(self):
        """Setup the dialog UI"""
        tk.Label(self.dialog, text="Category name:").pack(pady=10)

        self.entry = tk.Entry(self.dialog, font=('Segoe UI', 11))
        self.entry.pack(pady=5, padx=20, fill=tk.X)
        self.entry.focus()

        btn_frame = tk.Frame(self.dialog)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Cancel",
                 command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Add",
                 command=self._on_add).pack(side=tk.LEFT, padx=5)

        # Bind Enter key
        self.entry.bind('<Return>', lambda e: self._on_add())

    def _on_add(self):
        """Handle add button click"""
        name = self.entry.get().strip()
        if not name:
            messagebox.showwarning("Invalid Input",
                                  "Category name cannot be empty!")
            return

        self.on_add_callback(name)
        self.dialog.destroy()


class AddSubtaskDialog:
    """Dialog for adding a subtask to a task"""

    def __init__(self, parent, on_add_callback):
        """
        Initialize the add subtask dialog

        Args:
            parent: Parent window
            on_add_callback: Callback function(text) called when subtask is added
        """
        self.on_add_callback = on_add_callback

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Sub-task")
        self.dialog.geometry("400x180")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._setup_ui()

    def _setup_ui(self):
        """Setup the dialog UI"""
        tk.Label(self.dialog, text="Sub-task (Shift+Enter for new line):").pack(pady=10)

        self.text_input = tk.Text(self.dialog, font=('Segoe UI', 11), height=3,
                                  relief=tk.SOLID, borderwidth=1)
        self.text_input.pack(pady=5, padx=20, fill=tk.X)
        self.text_input.focus()

        btn_frame = tk.Frame(self.dialog)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Cancel",
                 command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Add",
                 command=self._on_add).pack(side=tk.LEFT, padx=5)

        # Bind Enter key to submit, Shift+Enter for new line
        self.text_input.bind('<Return>', self._handle_return)
        self.text_input.bind('<Shift-Return>', lambda e: None)  # Allow default new line

    def _handle_return(self, event):
        """Handle Enter key - submit unless Shift is held"""
        if not (event.state & 0x1):  # Shift not held
            self._on_add()
            return 'break'

    def _on_add(self):
        """Handle add button click"""
        text = self.text_input.get('1.0', tk.END).strip()
        if not text:
            messagebox.showwarning("Invalid Input",
                                  "Sub-task text cannot be empty!")
            return

        self.on_add_callback(text)
        self.dialog.destroy()


class EditTaskDialog:
    """Dialog for editing a task's text"""

    def __init__(self, parent, current_text, on_save_callback):
        """
        Initialize the edit task dialog

        Args:
            parent: Parent window
            current_text: Current task text to edit
            on_save_callback: Callback function(new_text) called when task is saved
        """
        self.on_save_callback = on_save_callback

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Task")
        self.dialog.geometry("500x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._setup_ui(current_text)

    def _setup_ui(self, current_text):
        """Setup the dialog UI"""
        tk.Label(self.dialog, text="Task text (Shift+Enter for new line):").pack(pady=10)

        self.text_input = tk.Text(self.dialog, font=('Segoe UI', 11), height=4,
                                  relief=tk.SOLID, borderwidth=1)
        self.text_input.pack(pady=5, padx=20, fill=tk.X)
        self.text_input.insert('1.0', current_text)
        self.text_input.focus()
        # Select all text
        self.text_input.tag_add(tk.SEL, '1.0', tk.END)
        self.text_input.mark_set(tk.INSERT, '1.0')

        btn_frame = tk.Frame(self.dialog)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Cancel",
                 command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Save",
                 command=self._on_save).pack(side=tk.LEFT, padx=5)

        # Bind Enter key to submit, Shift+Enter for new line
        self.text_input.bind('<Return>', self._handle_return)
        self.text_input.bind('<Shift-Return>', lambda e: None)  # Allow default new line

    def _handle_return(self, event):
        """Handle Enter key - submit unless Shift is held"""
        if not (event.state & 0x1):  # Shift not held
            self._on_save()
            return 'break'

    def _on_save(self):
        """Handle save button click"""
        text = self.text_input.get('1.0', tk.END).strip()
        if not text:
            messagebox.showwarning("Invalid Input",
                                  "Task text cannot be empty!")
            return

        self.on_save_callback(text)
        self.dialog.destroy()
