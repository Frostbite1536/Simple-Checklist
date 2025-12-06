"""
Task display panel component for Simple Checklist
Handles scrollable task list with checkboxes, subtasks, and notes
"""

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont


class TaskPanel:
    """Scrollable task display panel"""

    def __init__(self, parent, on_toggle_task, on_delete_task,
                 on_add_subtask, on_toggle_subtask, on_delete_subtask,
                 on_edit_task=None, on_edit_subtask=None):
        """
        Initialize the task panel

        Args:
            parent: Parent widget
            on_toggle_task: Callback function(task_idx) when task checkbox is toggled
            on_delete_task: Callback function(task_idx) when task is deleted
            on_add_subtask: Callback function(task_idx) when add subtask is clicked
            on_toggle_subtask: Callback function(task_idx, subtask_idx) when subtask is toggled
            on_delete_subtask: Callback function(task_idx, subtask_idx) when subtask is deleted
            on_edit_task: Callback function(task_idx) when edit button is clicked
            on_edit_subtask: Callback function(task_idx, subtask_idx) when subtask edit is clicked
        """
        self.on_toggle_task = on_toggle_task
        self.on_delete_task = on_delete_task
        self.on_add_subtask = on_add_subtask
        self.on_toggle_subtask = on_toggle_subtask
        self.on_delete_subtask = on_delete_subtask
        self.on_edit_task = on_edit_task
        self.on_edit_subtask = on_edit_subtask

        # Create task container
        self.container = tk.Frame(parent, bg='white')

        # Canvas for scrolling
        self.canvas = tk.Canvas(self.container, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.container, orient='vertical',
                                 command=self.canvas.yview)

        self.task_frame = tk.Frame(self.canvas, bg='white')
        self.task_frame.bind('<Configure>',
                           lambda e: self.canvas.configure(
                               scrollregion=self.canvas.bbox('all')))

        self.canvas_window = self.canvas.create_window((0, 0),
                                                       window=self.task_frame,
                                                       anchor='nw')
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Update canvas width when window resizes
        self.canvas.bind('<Configure>', self._on_canvas_resize)

        # Bind mouse wheel scrolling
        self.canvas.bind('<Enter>', self._bind_mousewheel)
        self.canvas.bind('<Leave>', self._unbind_mousewheel)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                        padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _bind_mousewheel(self, event):
        """Bind mousewheel when mouse enters canvas"""
        self.canvas.bind_all('<MouseWheel>', self._on_mousewheel)
        self.canvas.bind_all('<Button-4>', self._on_mousewheel_linux)
        self.canvas.bind_all('<Button-5>', self._on_mousewheel_linux)

    def _unbind_mousewheel(self, event):
        """Unbind mousewheel when mouse leaves canvas"""
        self.canvas.unbind_all('<MouseWheel>')
        self.canvas.unbind_all('<Button-4>')
        self.canvas.unbind_all('<Button-5>')

    def _on_mousewheel(self, event):
        """Handle mousewheel scroll (Windows/Mac)"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')

    def _on_mousewheel_linux(self, event):
        """Handle mousewheel scroll (Linux)"""
        if event.num == 4:
            self.canvas.yview_scroll(-1, 'units')
        elif event.num == 5:
            self.canvas.yview_scroll(1, 'units')

    def pack(self, **kwargs):
        """Pack the task panel container"""
        self.container.pack(**kwargs)

    def grid(self, **kwargs):
        """Grid the task panel container"""
        self.container.grid(**kwargs)

    def _on_canvas_resize(self, event):
        """Update canvas window width when canvas is resized"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def render_tasks(self, category):
        """
        Render tasks for a category

        Args:
            category: Category dictionary with 'name' and 'tasks', or None
        """
        # Clear existing widgets
        for widget in self.task_frame.winfo_children():
            widget.destroy()

        if not category:
            empty = tk.Label(self.task_frame, text="No category selected",
                           bg='white', fg='#95a5a6',
                           font=('Segoe UI', 14))
            empty.pack(pady=50)
            return

        if not category['tasks']:
            empty = tk.Label(self.task_frame,
                           text="No tasks yet\nStart typing below to add your first task!",
                           bg='white', fg='#95a5a6',
                           font=('Segoe UI', 12))
            empty.pack(pady=50)
            return

        # Render each task
        for idx, task in enumerate(category['tasks']):
            self._render_task(idx, task)

    def _render_task(self, idx, task):
        """
        Render a single task with its subtasks and notes

        Args:
            idx: Task index
            task: Task dictionary
        """
        task_widget = tk.Frame(self.task_frame, bg='#f8f9fa',
                              relief=tk.FLAT, borderwidth=1)
        task_widget.pack(fill=tk.X, pady=5, padx=10)

        # Left border
        border = tk.Frame(task_widget,
                        bg='#95a5a6' if task['completed'] else '#3498db',
                        width=3)
        border.pack(side=tk.LEFT, fill=tk.Y)

        # Main task content
        content = tk.Frame(task_widget, bg='#f8f9fa')
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=8)

        # Checkbox and text row
        main_row = tk.Frame(content, bg='#f8f9fa')
        main_row.pack(fill=tk.X)

        # Checkbox with explicit styling for visibility
        var = tk.BooleanVar(value=task['completed'])
        cb = tk.Checkbutton(main_row, variable=var, bg='#f8f9fa',
                           activebackground='#f8f9fa',
                           selectcolor='white',
                           command=lambda i=idx: self.on_toggle_task(i))
        cb.pack(side=tk.LEFT)

        # Button frame for task actions - pack FIRST so it gets space
        btn_frame = tk.Frame(main_row, bg='#f8f9fa')
        btn_frame.pack(side=tk.RIGHT, padx=(5, 0))

        # Add sub-task button
        add_sub_btn = tk.Button(btn_frame, text="+",
                               bg='#3498db', fg='white',
                               relief=tk.FLAT, width=3,
                               font=('Segoe UI', 10, 'bold'),
                               command=lambda i=idx: self.on_add_subtask(i))
        add_sub_btn.pack(side=tk.LEFT, padx=1)

        # Edit button
        if self.on_edit_task:
            edit_btn = tk.Button(btn_frame, text="✎",
                                bg='#9b59b6', fg='white',
                                relief=tk.FLAT, width=3,
                                font=('Segoe UI', 10),
                                command=lambda i=idx: self.on_edit_task(i))
            edit_btn.pack(side=tk.LEFT, padx=1)

        # Delete button
        del_btn = tk.Button(btn_frame, text="×",
                          bg='#e74c3c', fg='white',
                          relief=tk.FLAT, width=3,
                          font=('Segoe UI', 10, 'bold'),
                          command=lambda i=idx: self.on_delete_task(i))
        del_btn.pack(side=tk.LEFT, padx=1)

        # Text styling
        text_style = {'cursor': 'xterm'}
        if task['completed']:
            text_style['fg'] = '#7f8c8d'
            text_style['font'] = tkfont.Font(family='Segoe UI', size=11, overstrike=True)
        else:
            text_style['font'] = ('Segoe UI', 11)

        # Calculate height based on number of lines in text
        line_count = task['text'].count('\n') + 1

        # Use Text widget for selectable/copyable text - pack AFTER buttons
        task_text = tk.Text(main_row, height=line_count,
                          bg='#f8f9fa', relief=tk.FLAT,
                          wrap=tk.WORD, **text_style)
        task_text.insert('1.0', task['text'])
        task_text.config(state=tk.DISABLED)
        task_text.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Render subtasks
        if task.get('subtasks'):
            self._render_subtasks(content, idx, task['subtasks'])

        # Render notes
        if task.get('notes'):
            self._render_notes(content, task['notes'])

    def _render_subtasks(self, parent, task_idx, subtasks):
        """
        Render subtasks for a task

        Args:
            parent: Parent widget
            task_idx: Task index
            subtasks: List of subtask dictionaries
        """
        subtasks_frame = tk.Frame(parent, bg='#f8f9fa')
        subtasks_frame.pack(fill=tk.X, padx=20, pady=5)

        for sub_idx, subtask in enumerate(subtasks):
            sub_row = tk.Frame(subtasks_frame, bg='#f8f9fa')
            sub_row.pack(fill=tk.X, pady=2)

            sub_var = tk.BooleanVar(value=subtask['completed'])
            sub_cb = tk.Checkbutton(sub_row, variable=sub_var, bg='#f8f9fa',
                                   activebackground='#f8f9fa',
                                   selectcolor='white',
                                   command=lambda i=task_idx, si=sub_idx:
                                   self.on_toggle_subtask(i, si))
            sub_cb.pack(side=tk.LEFT)

            # Button frame for subtask actions - pack FIRST
            sub_btn_frame = tk.Frame(sub_row, bg='#f8f9fa')
            sub_btn_frame.pack(side=tk.RIGHT)

            # Edit subtask button
            if self.on_edit_subtask:
                edit_sub_btn = tk.Button(sub_btn_frame, text="✎",
                                        bg='#9b59b6', fg='white',
                                        relief=tk.FLAT, width=2,
                                        font=('Segoe UI', 9),
                                        command=lambda i=task_idx, si=sub_idx:
                                        self.on_edit_subtask(i, si))
                edit_sub_btn.pack(side=tk.LEFT, padx=1)

            # Delete sub-task button
            del_sub_btn = tk.Button(sub_btn_frame, text="×",
                                  bg='#e67e22', fg='white',
                                  relief=tk.FLAT, width=2,
                                  font=('Segoe UI', 9),
                                  command=lambda i=task_idx, si=sub_idx:
                                  self.on_delete_subtask(i, si))
            del_sub_btn.pack(side=tk.LEFT, padx=1)

            sub_text_style = {}
            if subtask['completed']:
                sub_text_style['fg'] = '#7f8c8d'
                sub_text_style['font'] = tkfont.Font(family='Segoe UI', size=10, overstrike=True)
            else:
                sub_text_style['fg'] = '#2c3e50'
                sub_text_style['font'] = ('Segoe UI', 10)

            # Use Label for subtasks - auto-sizes properly
            sub_text = tk.Label(sub_row, text=f"↳ {subtask['text']}",
                               bg='#f8f9fa', anchor='w', justify=tk.LEFT,
                               **sub_text_style)
            sub_text.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _render_notes(self, parent, notes):
        """
        Render notes for a task

        Args:
            parent: Parent widget
            notes: List of note strings
        """
        notes_frame = tk.Frame(parent, bg='#f8f9fa')
        notes_frame.pack(fill=tk.X, padx=20, pady=5)

        for note in notes:
            note_label = tk.Label(notes_frame, text=f"• {note}",
                                bg='#f8f9fa', fg='#7f8c8d',
                                font=('Segoe UI', 9),
                                anchor='w', cursor='xterm')
            note_label.pack(fill=tk.X)
