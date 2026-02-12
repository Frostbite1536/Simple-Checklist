"""
Task display panel component for Simple Checklist
Handles scrollable task list with checkboxes, subtasks, and notes
"""

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
from datetime import datetime


class TaskPanel:
    """Scrollable task display panel"""

    def __init__(self, parent, on_toggle_task, on_delete_task,
                 on_add_subtask, on_toggle_subtask, on_delete_subtask,
                 on_edit_task=None, on_edit_subtask=None, on_set_reminder=None):
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
            on_set_reminder: Callback function(task_idx) when reminder button is clicked
        """
        self.on_toggle_task = on_toggle_task
        self.on_delete_task = on_delete_task
        self.on_add_subtask = on_add_subtask
        self.on_toggle_subtask = on_toggle_subtask
        self.on_delete_subtask = on_delete_subtask
        self.on_edit_task = on_edit_task
        self.on_edit_subtask = on_edit_subtask
        self.on_set_reminder = on_set_reminder

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
        # Use bind() on canvas instead of bind_all() to avoid global binding conflicts
        self.canvas.bind('<MouseWheel>', self._on_mousewheel)
        self.canvas.bind('<Button-4>', self._on_mousewheel_linux)
        self.canvas.bind('<Button-5>', self._on_mousewheel_linux)
        # Also bind to the task_frame for events that occur on child widgets
        self.task_frame.bind('<MouseWheel>', self._on_mousewheel)
        self.task_frame.bind('<Button-4>', self._on_mousewheel_linux)
        self.task_frame.bind('<Button-5>', self._on_mousewheel_linux)

    def _unbind_mousewheel(self, event):
        """Unbind mousewheel when mouse leaves canvas"""
        self.canvas.unbind('<MouseWheel>')
        self.canvas.unbind('<Button-4>')
        self.canvas.unbind('<Button-5>')
        self.task_frame.unbind('<MouseWheel>')
        self.task_frame.unbind('<Button-4>')
        self.task_frame.unbind('<Button-5>')

    def _on_mousewheel(self, event):
        """Handle mousewheel scroll (Windows/Mac)"""
        # On Windows, event.delta is a multiple of 120; on macOS it is +/-1.
        # Normalize to a consistent scroll direction and apply a 3-unit speed.
        if abs(event.delta) >= 120:
            direction = -1 if event.delta > 0 else 1
        else:
            direction = -1 if event.delta > 0 else 1
        self.canvas.yview_scroll(direction * 3, 'units')

    def _on_mousewheel_linux(self, event):
        """Handle mousewheel scroll (Linux)"""
        # Bug #20 fix: Increased scroll speed from 1 to 3 units for more responsive scrolling
        if event.num == 4:
            self.canvas.yview_scroll(-3, 'units')
        elif event.num == 5:
            self.canvas.yview_scroll(3, 'units')

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

        # Feature #3: Priority-based left border color
        priority = task.get('priority', 'medium')
        priority_colors = {
            'high': '#e74c3c',    # Red
            'medium': '#f39c12',  # Orange
            'low': '#27ae60'      # Green
        }
        border_color = priority_colors.get(priority, '#3498db')
        if task['completed']:
            border_color = '#95a5a6'  # Gray for completed

        # Left border
        border = tk.Frame(task_widget, bg=border_color, width=3)
        border.pack(side=tk.LEFT, fill=tk.Y)

        # Main task content
        content = tk.Frame(task_widget, bg='#f8f9fa')
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=8)

        # Checkbox and text row
        main_row = tk.Frame(content, bg='#f8f9fa')
        main_row.pack(fill=tk.X)

        # Feature #3: Priority indicator
        if priority != 'medium' and not task['completed']:
            priority_symbols = {'high': '●', 'low': '○'}
            priority_label = tk.Label(main_row, text=priority_symbols.get(priority, ''),
                                     fg=priority_colors.get(priority, '#3498db'),
                                     bg='#f8f9fa', font=('Segoe UI', 10))
            priority_label.pack(side=tk.LEFT, padx=(0, 2))

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

        # Reminder button
        if self.on_set_reminder:
            has_reminder = task.get('reminder') is not None
            reminder_btn = tk.Button(btn_frame, text="🔔",
                                    bg='#f39c12' if has_reminder else '#95a5a6',
                                    fg='white',
                                    relief=tk.FLAT, width=3,
                                    font=('Segoe UI', 10),
                                    command=lambda i=idx: self.on_set_reminder(i))
            reminder_btn.pack(side=tk.LEFT, padx=1)

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
        # Bug fix: Account for both explicit newlines AND potential word-wrap lines
        explicit_lines = task['text'].count('\n') + 1

        # Estimate additional lines from word wrap
        # Assume approximately 60 characters per visual line as a conservative estimate
        # This ensures long single-line text will have adequate height
        text_length = len(task['text'])
        chars_per_line = 60
        estimated_wrap_lines = max(1, (text_length + chars_per_line - 1) // chars_per_line)

        # Use the maximum of explicit lines and estimated wrap lines
        # Cap at 10 lines to prevent extremely long tasks from dominating the view
        line_count = min(max(explicit_lines, estimated_wrap_lines), 10)

        # Use Text widget for selectable/copyable text - pack AFTER buttons
        task_text = tk.Text(main_row, height=line_count,
                          bg='#f8f9fa', relief=tk.FLAT,
                          wrap=tk.WORD, **text_style)
        task_text.insert('1.0', task['text'])
        task_text.config(state=tk.DISABLED)
        task_text.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Feature #4: Due date display
        due_date = task.get('due_date')
        if due_date and not task['completed']:
            try:
                due_dt = datetime.strptime(due_date, '%Y-%m-%d')
                days_left = (due_dt.date() - datetime.now().date()).days

                if days_left < 0:
                    due_color = '#e74c3c'  # Red - overdue
                    due_text = f"⚠️ Overdue ({abs(days_left)}d)"
                elif days_left == 0:
                    due_color = '#e74c3c'  # Red - due today
                    due_text = "📌 Due Today"
                elif days_left <= 3:
                    due_color = '#f39c12'  # Orange - due soon
                    due_text = f"📌 Due in {days_left}d"
                else:
                    due_color = '#7f8c8d'  # Gray - due later
                    due_text = f"📅 {due_dt.strftime('%b %d')}"

                due_row = tk.Frame(content, bg='#f8f9fa')
                due_row.pack(fill=tk.X, pady=(2, 0))
                due_label = tk.Label(due_row, text=due_text, fg=due_color,
                                    bg='#f8f9fa', font=('Segoe UI', 9))
                due_label.pack(side=tk.LEFT, padx=25)
            except ValueError:
                pass  # Invalid date format

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

            # Use Label for subtasks with wraplength for long text
            # wraplength=400 allows text to wrap within the panel width
            sub_text = tk.Label(sub_row, text=f"↳ {subtask['text']}",
                               bg='#f8f9fa', anchor='w', justify=tk.LEFT,
                               wraplength=400,
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
                                anchor='w', cursor='xterm',
                                wraplength=400, justify=tk.LEFT)
            note_label.pack(fill=tk.X)
