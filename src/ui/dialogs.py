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
        self.dialog.geometry("400x120")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._setup_ui()

    def _setup_ui(self):
        """Setup the dialog UI"""
        tk.Label(self.dialog, text="Sub-task:").pack(pady=10)

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
        text = self.entry.get().strip()
        if not text:
            messagebox.showwarning("Invalid Input",
                                  "Sub-task text cannot be empty!")
            return

        self.on_add_callback(text)
        self.dialog.destroy()
