"""
Main window component for Simple Checklist
Coordinates all UI components and handles window layout
"""

import tkinter as tk
from tkinter import messagebox
import os


class MainWindow:
    """Main application window with menu bar and layout"""

    def __init__(self, root, callbacks):
        """
        Initialize the main window

        Args:
            root: Tkinter root window
            callbacks: Dictionary of callback functions:
                - on_new_checklist: Called when File > New is clicked
                - on_open_checklist: Called when File > Open is clicked
                - on_save_as: Called when File > Save As is clicked
                - on_exit: Called when File > Exit is clicked
                - on_change_color: Called when Settings > Change Color is clicked
                - on_export_markdown: Called when Export MD button is clicked
                - on_clear_completed: Called when Clear Done button is clicked
                - get_recent_files: Function that returns list of recent file paths
                - on_load_recent_file: Function(filepath) to load a recent file
                - on_clear_recent_files: Called when Clear Recent Files is clicked
        """
        self.root = root
        self.callbacks = callbacks

        # Setup menu bar
        self._setup_menu()

        # Main container
        self.main_container = tk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Sidebar container (left)
        self.sidebar_container = tk.Frame(self.main_container, bg='#2c3e50', width=200)
        self.sidebar_container.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar_container.pack_propagate(False)

        # Right container
        self.right_container = tk.Frame(self.main_container, bg='white')
        self.right_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Header
        self._setup_header()

        # Separator
        separator = tk.Frame(self.right_container, height=1, bg='#e0e0e0')
        separator.pack(fill=tk.X)

        # Task panel container
        self.task_panel_container = tk.Frame(self.right_container, bg='white')
        self.task_panel_container.pack(fill=tk.BOTH, expand=True)

        # Input area container
        self.input_container = tk.Frame(self.right_container, bg='white')
        self.input_container.pack(fill=tk.X)

    def _setup_menu(self):
        """Setup the menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Checklist",
                             command=self.callbacks['on_new_checklist'])
        file_menu.add_command(label="Open Checklist...",
                             command=self.callbacks['on_open_checklist'])
        file_menu.add_command(label="Save As...",
                             command=self.callbacks['on_save_as'])
        file_menu.add_separator()

        # Recent files submenu
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Recent Files", menu=self.recent_menu)
        self.update_recent_menu()

        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.callbacks['on_exit'])

        # Edit menu (Feature #1: Undo/Redo)
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo",
                             command=self.callbacks.get('on_undo', lambda: None),
                             accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo",
                             command=self.callbacks.get('on_redo', lambda: None),
                             accelerator="Ctrl+Y")

        # Sort menu (Feature #9)
        sort_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Sort", menu=sort_menu)
        sort_menu.add_command(label="Smart Sort (Recommended)",
                             command=lambda: self._call_sort('smart'))
        sort_menu.add_separator()
        sort_menu.add_command(label="By Priority (High → Low)",
                             command=lambda: self._call_sort('priority'))
        sort_menu.add_command(label="By Due Date (Earliest First)",
                             command=lambda: self._call_sort('due_date'))
        sort_menu.add_command(label="By Creation Date",
                             command=lambda: self._call_sort('created'))
        sort_menu.add_command(label="Alphabetically (A → Z)",
                             command=lambda: self._call_sort('a-z'))
        sort_menu.add_separator()
        sort_menu.add_command(label="By Completion Status",
                             command=lambda: self._call_sort('completion'))

        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Change Input Box Color",
                                 command=self.callbacks['on_change_color'])

    def _setup_header(self):
        """Setup the header with title and action buttons"""
        header = tk.Frame(self.right_container, bg='white', height=60)
        header.pack(fill=tk.X, padx=20, pady=10)
        header.pack_propagate(False)

        self.title_label = tk.Label(header, text="Select a category",
                                    bg='white', fg='#2c3e50',
                                    font=('Segoe UI', 16, 'bold'))
        self.title_label.pack(side=tk.LEFT)

        # Header buttons
        btn_frame = tk.Frame(header, bg='white')
        btn_frame.pack(side=tk.RIGHT)

        export_btn = tk.Button(btn_frame, text="📥 Export MD",
                              bg='#27ae60', fg='white',
                              relief=tk.FLAT, padx=12, pady=6,
                              command=self.callbacks['on_export_markdown'])
        export_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = tk.Button(btn_frame, text="🗑️ Clear Done",
                             bg='#e74c3c', fg='white',
                             relief=tk.FLAT, padx=12, pady=6,
                             command=self.callbacks['on_clear_completed'])
        clear_btn.pack(side=tk.LEFT)

    def update_title(self, title):
        """
        Update the header title

        Args:
            title: New title text
        """
        self.title_label.config(text=title)

    def update_window_title(self, filename):
        """
        Update the window title

        Args:
            filename: Path to the current checklist file
        """
        self.root.title(f"Simple Checklist - {os.path.basename(filename)}")

    def update_recent_menu(self):
        """Update the recent files menu"""
        self.recent_menu.delete(0, tk.END)
        recent_files = self.callbacks['get_recent_files']()

        if not recent_files:
            self.recent_menu.add_command(label="(No recent files)", state=tk.DISABLED)
        else:
            for filepath in recent_files:
                if os.path.exists(filepath):
                    self.recent_menu.add_command(
                        label=os.path.basename(filepath),
                        command=lambda f=filepath: self.callbacks['on_load_recent_file'](f)
                    )
                else:
                    # Show non-existent files as disabled with indicator
                    self.recent_menu.add_command(
                        label=f"{os.path.basename(filepath)} (missing)",
                        state=tk.DISABLED
                    )

            # Add separator and clear option
            if recent_files:
                self.recent_menu.add_separator()
                self.recent_menu.add_command(
                    label="Clear Recent Files",
                    command=self._on_clear_recent_files
                )

    def _on_clear_recent_files(self):
        """Handle clear recent files with confirmation"""
        if messagebox.askyesno("Clear Recent Files",
                              "Clear all recent files from the list?"):
            self.callbacks['on_clear_recent_files']()
            self.update_recent_menu()

    def get_sidebar_container(self):
        """Get the sidebar container for adding sidebar widget"""
        return self.sidebar_container

    def get_task_panel_container(self):
        """Get the task panel container for adding task panel widget"""
        return self.task_panel_container

    def get_input_container(self):
        """Get the input container for adding input area widget"""
        return self.input_container

    def _call_sort(self, sort_by):
        """Call the sort callback if available"""
        if 'on_sort_tasks' in self.callbacks:
            self.callbacks['on_sort_tasks'](sort_by)
