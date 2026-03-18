"""
Task display panel component for Simple Checklist
Handles scrollable task list with checkboxes, subtasks, and notes
"""

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
from datetime import datetime
from . import scrollable_mixin


class TaskPanel:
    """Scrollable task display panel"""

    def __init__(self, parent, on_toggle_task, on_delete_task,
                 on_add_subtask, on_toggle_subtask, on_delete_subtask,
                 on_edit_task=None, on_edit_subtask=None, on_set_reminder=None,
                 on_add_note=None, on_edit_note=None, on_delete_note=None,
                 on_reorder_task=None):
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
        self.on_add_note = on_add_note
        self.on_edit_note = on_edit_note
        self.on_delete_note = on_delete_note
        self.on_reorder_task = on_reorder_task

        # Drag-and-drop state for task reordering
        self.task_widgets = []
        self.drag_data = {
            'source': None, 'index': None,
            'start_y': None, 'dragging': False
        }

        # Filter state
        self.active_filter = 'all'
        self.on_filter_change = None

        # Selection mode state
        self.selection_mode = False
        self.selected_tasks = set()
        self.on_bulk_complete = None
        self.on_bulk_delete = None
        self.on_toggle_selection = None

        # Create task container
        self.container = tk.Frame(parent, bg='white')

        # Filter bar
        self.filter_frame = tk.Frame(self.container, bg='white')
        self.filter_frame.pack(fill=tk.X, padx=20, pady=(5, 0))
        self.filter_buttons = {}
        for label, key in [('All', 'all'), ('High', 'high'), ('Overdue', 'overdue'),
                           ('Pending', 'pending'), ('Done', 'done')]:
            btn = tk.Button(self.filter_frame, text=label,
                           relief=tk.FLAT, padx=8, pady=2,
                           font=('Segoe UI', 9),
                           command=lambda k=key: self._set_filter(k))
            btn.pack(side=tk.LEFT, padx=2)
            self.filter_buttons[key] = btn
        self._update_filter_buttons()

        # Selection action bar (hidden by default)
        self.action_bar = tk.Frame(self.container, bg='#2c3e50')
        self.action_bar_buttons = {}
        for label, key, color in [
            ('\u2713 Complete', 'complete', '#27ae60'),
            ('\u00d7 Delete', 'delete', '#e74c3c'),
            ('Select All', 'select_all', '#3498db'),
            ('Cancel', 'cancel', '#95a5a6')
        ]:
            btn = tk.Button(self.action_bar, text=label,
                           bg=color, fg='white',
                           relief=tk.FLAT, padx=8, pady=3,
                           font=('Segoe UI', 9))
            btn.pack(side=tk.LEFT, padx=3, pady=3)
            self.action_bar_buttons[key] = btn
        # action_bar is NOT packed yet — shown only in selection mode

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
        scrollable_mixin.bind_mousewheel(self.canvas, self.task_frame)

    def _unbind_mousewheel(self, event):
        """Unbind mousewheel when mouse leaves canvas"""
        scrollable_mixin.unbind_mousewheel(self.canvas, self.task_frame)

    def pack(self, **kwargs):
        """Pack the task panel container"""
        self.container.pack(**kwargs)

    def grid(self, **kwargs):
        """Grid the task panel container"""
        self.container.grid(**kwargs)

    def set_filter_callback(self, callback):
        """Set the filter change callback"""
        self.on_filter_change = callback

    def _set_filter(self, filter_key):
        """Handle filter button click"""
        self.active_filter = filter_key
        self._update_filter_buttons()
        if self.on_filter_change:
            self.on_filter_change(filter_key)

    def set_bulk_callbacks(self, on_bulk_complete, on_bulk_delete, on_toggle_selection):
        """Set bulk operation callbacks"""
        self.on_bulk_complete = on_bulk_complete
        self.on_bulk_delete = on_bulk_delete
        self.on_toggle_selection = on_toggle_selection

        self.action_bar_buttons['complete'].config(
            command=lambda: self.on_bulk_complete(list(self.selected_tasks)))
        self.action_bar_buttons['delete'].config(
            command=lambda: self.on_bulk_delete(list(self.selected_tasks)))
        self.action_bar_buttons['select_all'].config(
            command=self._select_all_tasks)
        self.action_bar_buttons['cancel'].config(
            command=lambda: self.on_toggle_selection())

    def toggle_selection_mode(self):
        """Toggle selection mode on/off"""
        self.selection_mode = not self.selection_mode
        self.selected_tasks.clear()
        if self.selection_mode:
            self.action_bar.pack(fill=tk.X, padx=20, pady=(2, 0),
                               before=self.canvas)
        else:
            self.action_bar.pack_forget()

    def _select_all_tasks(self):
        """Select all visible tasks and update checkbox state"""
        for item in self.task_widgets:
            self.selected_tasks.add(item['index'])
            # Update the checkbox variable if it exists
            if 'sel_var' in item:
                item['sel_var'].set(True)

    def _update_filter_buttons(self):
        """Update filter button styling to highlight active filter"""
        for key, btn in self.filter_buttons.items():
            if key == self.active_filter:
                btn.config(bg='#3498db', fg='white')
            else:
                btn.config(bg='#ecf0f1', fg='#2c3e50')

    def apply_theme(self, theme_colors):
        """Apply theme colors to the task panel"""
        bg = theme_colors.CONTENT_BG
        self.container.config(bg=bg)
        self.canvas.config(bg=bg)
        self.task_frame.config(bg=bg)
        self.filter_frame.config(bg=bg)
        for btn in self.filter_buttons.values():
            btn.config(highlightbackground=bg)

    def _on_canvas_resize(self, event):
        """Update canvas window width when canvas is resized"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def render_tasks(self, category):
        """
        Render tasks for a category

        Args:
            category: Category model object, or None
        """
        # Clear existing widgets
        for widget in self.task_frame.winfo_children():
            widget.destroy()
        self.task_widgets = []
        self.drag_data = {
            'source': None, 'index': None,
            'start_y': None, 'dragging': False
        }

        if not category:
            empty = tk.Label(self.task_frame, text="No category selected",
                           bg='white', fg='#95a5a6',
                           font=('Segoe UI', 14))
            empty.pack(pady=50)
            return

        if not category.tasks:
            empty = tk.Label(self.task_frame,
                           text="No tasks yet\nStart typing below to add your first task!",
                           bg='white', fg='#95a5a6',
                           font=('Segoe UI', 12))
            empty.pack(pady=50)
            return

        # Render each task
        for idx, task in enumerate(category.tasks):
            self._render_task(idx, task)

    def _render_task(self, idx, task):
        """
        Render a single task with its subtasks and notes

        Args:
            idx: Task index
            task: Task model object
        """
        task_widget = tk.Frame(self.task_frame, bg='#f8f9fa',
                              relief=tk.FLAT, borderwidth=1)
        task_widget.pack(fill=tk.X, pady=5, padx=10)

        # Store widget reference for drag-and-drop target detection
        self.task_widgets.append({'frame': task_widget, 'index': idx})

        # Drag handle for reordering
        if self.on_reorder_task:
            drag_handle = tk.Label(task_widget, text='\u2261', bg='#dcdde1',
                                  fg='#7f8c8d', font=('Segoe UI', 12),
                                  width=2, cursor='fleur')
            drag_handle.pack(side=tk.LEFT, fill=tk.Y)
            drag_handle.bind('<Button-1>',
                            lambda e, i=idx: self._on_task_drag_start(e, i))
            drag_handle.bind('<B1-Motion>', self._on_task_drag_motion)
            drag_handle.bind('<ButtonRelease-1>', self._on_task_drag_release)

        # Selection checkbox (when in selection mode)
        if self.selection_mode:
            sel_var = tk.BooleanVar(value=idx in self.selected_tasks)
            # Store reference so _select_all_tasks can update it
            self.task_widgets[-1]['sel_var'] = sel_var
            def _toggle_select(i=idx, v=sel_var):
                if v.get():
                    self.selected_tasks.add(i)
                else:
                    self.selected_tasks.discard(i)
            sel_cb = tk.Checkbutton(task_widget, variable=sel_var,
                                   bg='#f8f9fa', activebackground='#f8f9fa',
                                   selectcolor='white',
                                   command=_toggle_select)
            sel_cb.pack(side=tk.LEFT, padx=(2, 0))

        # Feature #3: Priority-based left border color
        priority = task.priority
        priority_colors = {
            'high': '#e74c3c',    # Red
            'medium': '#f39c12',  # Orange
            'low': '#27ae60'      # Green
        }
        border_color = priority_colors.get(priority, '#3498db')
        if task.completed:
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
        if priority != 'medium' and not task.completed:
            priority_symbols = {'high': '●', 'low': '○'}
            priority_label = tk.Label(main_row, text=priority_symbols.get(priority, ''),
                                     fg=priority_colors.get(priority, '#3498db'),
                                     bg='#f8f9fa', font=('Segoe UI', 10))
            priority_label.pack(side=tk.LEFT, padx=(0, 2))

        # Checkbox with explicit styling for visibility
        var = tk.BooleanVar(value=task.completed)
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
            has_reminder = task.reminder is not None
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

        # Add note button
        if self.on_add_note:
            note_btn = tk.Button(btn_frame, text="\U0001f4dd",
                                bg='#16a085', fg='white',
                                relief=tk.FLAT, width=3,
                                font=('Segoe UI', 10),
                                command=lambda i=idx: self.on_add_note(i))
            note_btn.pack(side=tk.LEFT, padx=1)

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
        if task.completed:
            text_style['fg'] = '#7f8c8d'
            text_style['font'] = tkfont.Font(family='Segoe UI', size=11, overstrike=True)
        else:
            text_style['font'] = ('Segoe UI', 11)

        # Calculate height based on number of lines in text
        # Bug fix: Account for both explicit newlines AND potential word-wrap lines
        explicit_lines = task.text.count('\n') + 1

        # Estimate additional lines from word wrap
        # Assume approximately 60 characters per visual line as a conservative estimate
        # This ensures long single-line text will have adequate height
        text_length = len(task.text)
        chars_per_line = 60
        estimated_wrap_lines = max(1, (text_length + chars_per_line - 1) // chars_per_line)

        # Use the maximum of explicit lines and estimated wrap lines
        # Cap at 10 lines to prevent extremely long tasks from dominating the view
        line_count = min(max(explicit_lines, estimated_wrap_lines), 10)

        # Use Text widget for selectable/copyable text - pack AFTER buttons
        task_text = tk.Text(main_row, height=line_count,
                          bg='#f8f9fa', relief=tk.FLAT,
                          wrap=tk.WORD, **text_style)
        task_text.insert('1.0', task.text)
        task_text.config(state=tk.DISABLED)
        task_text.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Feature #4: Due date display
        due_date = task.due_date
        if due_date and not task.completed:
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

        # Recurrence indicator
        if getattr(task, 'recurrence', None) and not task.completed:
            recur_labels = {'daily': '\U0001f504 Daily', 'weekly': '\U0001f504 Weekly',
                           'monthly': '\U0001f504 Monthly'}
            recur_row = tk.Frame(content, bg='#f8f9fa')
            recur_row.pack(fill=tk.X, pady=(2, 0))
            recur_label = tk.Label(recur_row,
                                  text=recur_labels.get(task.recurrence, ''),
                                  fg='#8e44ad', bg='#f8f9fa',
                                  font=('Segoe UI', 9))
            recur_label.pack(side=tk.LEFT, padx=25)

        # Render subtasks
        if task.subtasks:
            self._render_subtasks(content, idx, task.subtasks)

        # Render notes
        if task.notes:
            self._render_notes(content, idx, task.notes)

    def _on_task_drag_start(self, event, index):
        """Start dragging a task"""
        self.drag_data['source'] = event.widget
        self.drag_data['index'] = index
        self.drag_data['start_y'] = event.y_root
        self.drag_data['dragging'] = False

    def _on_task_drag_motion(self, event):
        """Handle task drag motion"""
        if self.drag_data['source'] and self.drag_data['start_y'] is not None:
            if abs(event.y_root - self.drag_data['start_y']) > 5:
                self.drag_data['dragging'] = True

    def _on_task_drag_release(self, event):
        """Handle task drop to reorder"""
        source_index = self.drag_data['index']

        if self.drag_data['dragging'] and source_index is not None:
            target_index = self._get_task_drop_target(event.y_root)
            if target_index is not None and source_index != target_index:
                self.on_reorder_task(source_index, target_index)

        self.drag_data = {
            'source': None, 'index': None,
            'start_y': None, 'dragging': False
        }

    def _get_task_drop_target(self, y_root):
        """Determine which task index the mouse is over"""
        for item in self.task_widgets:
            frame = item['frame']
            try:
                frame_y = frame.winfo_rooty()
                frame_height = frame.winfo_height()
                if frame_y <= y_root < frame_y + frame_height:
                    return item['index']
            except tk.TclError:
                continue

        # If below all tasks, return last index
        if self.task_widgets:
            last = self.task_widgets[-1]['frame']
            try:
                if y_root >= last.winfo_rooty():
                    return self.task_widgets[-1]['index']
            except tk.TclError:
                pass
        return None

    def _render_subtasks(self, parent, task_idx, subtasks):
        """
        Render subtasks for a task

        Args:
            parent: Parent widget
            task_idx: Task index
            subtasks: List of Subtask model objects
        """
        subtasks_frame = tk.Frame(parent, bg='#f8f9fa')
        subtasks_frame.pack(fill=tk.X, padx=20, pady=5)

        for sub_idx, subtask in enumerate(subtasks):
            sub_row = tk.Frame(subtasks_frame, bg='#f8f9fa')
            sub_row.pack(fill=tk.X, pady=2)

            sub_var = tk.BooleanVar(value=subtask.completed)
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
            if subtask.completed:
                sub_text_style['fg'] = '#7f8c8d'
                sub_text_style['font'] = tkfont.Font(family='Segoe UI', size=10, overstrike=True)
            else:
                sub_text_style['fg'] = '#2c3e50'
                sub_text_style['font'] = ('Segoe UI', 10)

            # Use Label for subtasks with wraplength for long text
            # wraplength=400 allows text to wrap within the panel width
            sub_text = tk.Label(sub_row, text=f"↳ {subtask.text}",
                               bg='#f8f9fa', anchor='w', justify=tk.LEFT,
                               wraplength=400,
                               **sub_text_style)
            sub_text.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _render_notes(self, parent, task_idx, notes):
        """
        Render notes for a task

        Args:
            parent: Parent widget
            task_idx: Task index
            notes: List of note strings
        """
        notes_frame = tk.Frame(parent, bg='#f8f9fa')
        notes_frame.pack(fill=tk.X, padx=20, pady=5)

        for note_idx, note in enumerate(notes):
            note_row = tk.Frame(notes_frame, bg='#f8f9fa')
            note_row.pack(fill=tk.X, pady=1)

            # Note action buttons (pack first so they get space)
            note_btn_frame = tk.Frame(note_row, bg='#f8f9fa')
            note_btn_frame.pack(side=tk.RIGHT)

            if self.on_edit_note:
                edit_note_btn = tk.Button(note_btn_frame, text="\u270e",
                                         bg='#9b59b6', fg='white',
                                         relief=tk.FLAT, width=2,
                                         font=('Segoe UI', 8),
                                         command=lambda ti=task_idx, ni=note_idx:
                                             self.on_edit_note(ti, ni))
                edit_note_btn.pack(side=tk.LEFT, padx=1)

            if self.on_delete_note:
                del_note_btn = tk.Button(note_btn_frame, text="\u00d7",
                                        bg='#e67e22', fg='white',
                                        relief=tk.FLAT, width=2,
                                        font=('Segoe UI', 8),
                                        command=lambda ti=task_idx, ni=note_idx:
                                            self.on_delete_note(ti, ni))
                del_note_btn.pack(side=tk.LEFT, padx=1)

            note_label = tk.Label(note_row, text=f"\u2022 {note}",
                                bg='#f8f9fa', fg='#7f8c8d',
                                font=('Segoe UI', 9),
                                anchor='w', cursor='xterm',
                                wraplength=400, justify=tk.LEFT)
            note_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
