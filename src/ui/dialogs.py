"""
Dialog windows for Simple Checklist
Reusable dialog components for user interactions
"""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta

# Maximum character limit for category names
# Bug #19 fix: Reduced from 17 to 16 to prevent delete button from being pushed off-screen
MAX_CATEGORY_NAME_LENGTH = 16


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

        if len(name) > MAX_CATEGORY_NAME_LENGTH:
            messagebox.showwarning("Invalid Input",
                                  f"Category name cannot exceed {MAX_CATEGORY_NAME_LENGTH} characters!\n"
                                  f"Current length: {len(name)}")
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
        # Bug #21 fix: Updated hint to reflect correct key bindings
        tk.Label(self.dialog, text="Sub-task (Enter for new line, Shift+Enter to add):").pack(pady=10)

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

        # Bug #21 fix: Swap Enter/Shift+Enter - Enter for newline, Shift+Enter to submit
        # This matches natural text editor behavior (e.g., Slack, Discord)
        self.text_input.bind('<Shift-Return>', self._handle_shift_return)

    def _handle_shift_return(self, event):
        """Handle Shift+Enter key - submit the subtask"""
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

    def __init__(self, parent, current_text, on_save_callback, title="Edit Task",
                 current_priority=None, current_due_date=None, show_options=False,
                 current_recurrence=None):
        """
        Initialize the edit task dialog

        Args:
            parent: Parent window
            current_text: Current task text to edit
            on_save_callback: Callback function(new_text) or function(new_text, priority, due_date)
            title: Dialog title (default: "Edit Task")
            current_priority: Current task priority ('low', 'medium', 'high')
            current_due_date: Current due date string (YYYY-MM-DD)
            show_options: Whether to show priority/due date options
        """
        self.on_save_callback = on_save_callback
        self.show_options = show_options

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        # Larger dialog if showing options
        height = 360 if show_options else 200
        self.dialog.geometry(f"500x{height}")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._setup_ui(current_text, current_priority, current_due_date,
                       current_recurrence)

    def _setup_ui(self, current_text, current_priority, current_due_date,
                  current_recurrence=None):
        """Setup the dialog UI"""
        # Bug #21 fix: Updated hint to reflect correct key bindings
        tk.Label(self.dialog, text="Text (Enter for new line, Shift+Enter to save):").pack(pady=10)

        self.text_input = tk.Text(self.dialog, font=('Segoe UI', 11), height=4,
                                  relief=tk.SOLID, borderwidth=1)
        self.text_input.pack(pady=5, padx=20, fill=tk.X)
        self.text_input.insert('1.0', current_text)
        self.text_input.focus()
        # Select all text
        self.text_input.tag_add(tk.SEL, '1.0', tk.END)
        self.text_input.mark_set(tk.INSERT, '1.0')

        # Feature #3 & #4: Priority and Due Date options
        if self.show_options:
            options_frame = tk.Frame(self.dialog)
            options_frame.pack(fill=tk.X, padx=20, pady=10)

            # Priority selector
            priority_frame = tk.Frame(options_frame)
            priority_frame.pack(side=tk.LEFT, padx=(0, 20))

            tk.Label(priority_frame, text="Priority:").pack(side=tk.LEFT, padx=(0, 5))

            self.priority_var = tk.StringVar(value=current_priority or 'medium')
            priorities = [('Low', 'low'), ('Medium', 'medium'), ('High', 'high')]

            for label, value in priorities:
                color = {'low': '#27ae60', 'medium': '#f39c12', 'high': '#e74c3c'}[value]
                rb = tk.Radiobutton(priority_frame, text=label, variable=self.priority_var,
                                   value=value, fg=color)
                rb.pack(side=tk.LEFT, padx=2)

            # Due date input
            due_frame = tk.Frame(options_frame)
            due_frame.pack(side=tk.LEFT)

            tk.Label(due_frame, text="Due Date:").pack(side=tk.LEFT, padx=(0, 5))

            self.due_date_var = tk.StringVar(value=current_due_date or '')
            self.due_entry = tk.Entry(due_frame, textvariable=self.due_date_var,
                                     width=12, font=('Segoe UI', 10))
            self.due_entry.pack(side=tk.LEFT)

            tk.Label(due_frame, text="(YYYY-MM-DD)", fg='#7f8c8d',
                    font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=5)

            # Recurrence selector
            recur_frame = tk.Frame(options_frame)
            recur_frame.pack(side=tk.LEFT, padx=(20, 0))

            tk.Label(recur_frame, text="Repeat:").pack(side=tk.LEFT, padx=(0, 5))
            self.recurrence_var = tk.StringVar(value=current_recurrence or 'none')
            recurrence_options = [('None', 'none'), ('Daily', 'daily'),
                                 ('Weekly', 'weekly'), ('Monthly', 'monthly')]
            for label, value in recurrence_options:
                rb = tk.Radiobutton(recur_frame, text=label,
                                   variable=self.recurrence_var, value=value)
                rb.pack(side=tk.LEFT, padx=2)

        btn_frame = tk.Frame(self.dialog)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Cancel",
                 command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Save",
                 command=self._on_save).pack(side=tk.LEFT, padx=5)

        # Bug #21 fix: Swap Enter/Shift+Enter - Enter for newline, Shift+Enter to submit
        # This matches natural text editor behavior (e.g., Slack, Discord)
        self.text_input.bind('<Shift-Return>', self._handle_shift_return)

    def _handle_shift_return(self, event):
        """Handle Shift+Enter key - save the task"""
        self._on_save()
        return 'break'

    def _on_save(self):
        """Handle save button click"""
        text = self.text_input.get('1.0', tk.END).strip()
        if not text:
            messagebox.showwarning("Invalid Input",
                                  "Task text cannot be empty!")
            return

        if self.show_options:
            priority = self.priority_var.get()
            due_date = self.due_date_var.get().strip() or None

            # Validate due date format if provided
            if due_date:
                try:
                    from datetime import datetime
                    datetime.strptime(due_date, '%Y-%m-%d')
                except ValueError:
                    messagebox.showwarning("Invalid Date",
                                          "Please enter date in YYYY-MM-DD format!")
                    return

            recurrence = self.recurrence_var.get()
            if recurrence == 'none':
                recurrence = None
            self.on_save_callback(text, priority, due_date, recurrence)
        else:
            self.on_save_callback(text)
        self.dialog.destroy()


class ReminderDialog:
    """Dialog for setting a reminder on a task"""

    def __init__(self, parent, task_text, on_set_callback, current_reminder=None):
        """
        Initialize the reminder dialog

        Args:
            parent: Parent window
            task_text: Text of the task (for display)
            on_set_callback: Callback function(datetime_iso) called when reminder is set
            current_reminder: Current reminder datetime ISO string (if editing)
        """
        self.on_set_callback = on_set_callback

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Set Reminder")
        self.dialog.geometry("400x320")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._setup_ui(task_text, current_reminder)

    def _setup_ui(self, task_text, current_reminder):
        """Setup the dialog UI"""
        # Task preview
        preview_text = task_text[:50] + "..." if len(task_text) > 50 else task_text
        tk.Label(self.dialog, text=f"Task: {preview_text}",
                font=('Segoe UI', 10), fg='#7f8c8d').pack(pady=(10, 5))

        # Relative time section
        rel_frame = tk.LabelFrame(self.dialog, text="Remind me in...", padx=10, pady=10)
        rel_frame.pack(fill=tk.X, padx=20, pady=10)

        time_row = tk.Frame(rel_frame)
        time_row.pack(fill=tk.X)

        # Minutes
        tk.Label(time_row, text="Min:").pack(side=tk.LEFT)
        self.minutes_var = tk.StringVar(value="0")
        self.minutes_entry = tk.Entry(time_row, textvariable=self.minutes_var, width=5)
        self.minutes_entry.pack(side=tk.LEFT, padx=(2, 10))

        # Hours
        tk.Label(time_row, text="Hours:").pack(side=tk.LEFT)
        self.hours_var = tk.StringVar(value="0")
        self.hours_entry = tk.Entry(time_row, textvariable=self.hours_var, width=5)
        self.hours_entry.pack(side=tk.LEFT, padx=(2, 10))

        # Days
        tk.Label(time_row, text="Days:").pack(side=tk.LEFT)
        self.days_var = tk.StringVar(value="0")
        self.days_entry = tk.Entry(time_row, textvariable=self.days_var, width=5)
        self.days_entry.pack(side=tk.LEFT, padx=(2, 0))

        tk.Button(rel_frame, text="Set Relative Reminder",
                 command=self._set_relative, bg='#3498db', fg='white',
                 relief=tk.FLAT).pack(pady=(10, 0))

        # Specific date/time section
        abs_frame = tk.LabelFrame(self.dialog, text="Or set specific date/time", padx=10, pady=10)
        abs_frame.pack(fill=tk.X, padx=20, pady=10)

        date_row = tk.Frame(abs_frame)
        date_row.pack(fill=tk.X)

        # Date
        tk.Label(date_row, text="Date (YYYY-MM-DD):").pack(side=tk.LEFT)
        now = datetime.now()
        self.date_var = tk.StringVar(value=now.strftime("%Y-%m-%d"))
        self.date_entry = tk.Entry(date_row, textvariable=self.date_var, width=12)
        self.date_entry.pack(side=tk.LEFT, padx=(5, 15))

        # Time
        tk.Label(date_row, text="Time (HH:MM):").pack(side=tk.LEFT)
        self.time_var = tk.StringVar(value=now.strftime("%H:%M"))
        self.time_entry = tk.Entry(date_row, textvariable=self.time_var, width=8)
        self.time_entry.pack(side=tk.LEFT, padx=(5, 0))

        tk.Button(abs_frame, text="Set Specific Reminder",
                 command=self._set_absolute, bg='#27ae60', fg='white',
                 relief=tk.FLAT).pack(pady=(10, 0))

        # Current reminder display
        if current_reminder:
            try:
                reminder_dt = datetime.fromisoformat(current_reminder)
                tk.Label(self.dialog,
                        text=f"Current reminder: {reminder_dt.strftime('%Y-%m-%d %H:%M')}",
                        font=('Segoe UI', 9), fg='#e67e22').pack(pady=5)
            except ValueError:
                pass

        # Bottom buttons
        btn_frame = tk.Frame(self.dialog)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Cancel",
                 command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

        if current_reminder:
            tk.Button(btn_frame, text="Clear Reminder",
                     command=self._clear_reminder, bg='#e74c3c', fg='white',
                     relief=tk.FLAT).pack(side=tk.LEFT, padx=5)

    def _set_relative(self):
        """Set reminder based on relative time"""
        try:
            minutes = int(self.minutes_var.get() or 0)
            hours = int(self.hours_var.get() or 0)
            days = int(self.days_var.get() or 0)

            if minutes == 0 and hours == 0 and days == 0:
                messagebox.showwarning("Invalid Input",
                                      "Please enter at least one time value!")
                return

            # Validate that values are not negative
            if minutes < 0 or hours < 0 or days < 0:
                messagebox.showwarning("Invalid Input",
                                      "Time values cannot be negative!")
                return

            reminder_time = datetime.now() + timedelta(
                days=days, hours=hours, minutes=minutes
            )
            self.on_set_callback(reminder_time.isoformat())
            self.dialog.destroy()

        except ValueError:
            messagebox.showwarning("Invalid Input",
                                  "Please enter valid numbers!")

    def _set_absolute(self):
        """Set reminder based on absolute date/time"""
        try:
            date_str = self.date_var.get()
            time_str = self.time_var.get()

            reminder_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")

            # Use < instead of <= to allow reminders set for the current minute
            if reminder_time < datetime.now():
                messagebox.showwarning("Invalid Time",
                                      "Reminder time must be in the future!")
                return

            self.on_set_callback(reminder_time.isoformat())
            self.dialog.destroy()

        except ValueError:
            messagebox.showwarning("Invalid Input",
                                  "Please enter valid date (YYYY-MM-DD) and time (HH:MM)!")

    def _clear_reminder(self):
        """Clear the reminder"""
        self.on_set_callback(None)
        self.dialog.destroy()


class AddNoteDialog:
    """Dialog for adding a note to a task"""

    def __init__(self, parent, on_add_callback):
        """
        Initialize the add note dialog

        Args:
            parent: Parent window
            on_add_callback: Callback function(text) called when note is added
        """
        self.on_add_callback = on_add_callback

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Note")
        self.dialog.geometry("400x120")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._setup_ui()

    def _setup_ui(self):
        """Setup the dialog UI"""
        tk.Label(self.dialog, text="Note text:").pack(pady=10)

        self.entry = tk.Entry(self.dialog, font=('Segoe UI', 11))
        self.entry.pack(pady=5, padx=20, fill=tk.X)
        self.entry.focus()

        btn_frame = tk.Frame(self.dialog)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Cancel",
                 command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Add",
                 command=self._on_add).pack(side=tk.LEFT, padx=5)

        self.entry.bind('<Return>', lambda e: self._on_add())

    def _on_add(self):
        """Handle add button click"""
        text = self.entry.get().strip()
        if not text:
            messagebox.showwarning("Invalid Input",
                                  "Note text cannot be empty!")
            return

        self.on_add_callback(text)
        self.dialog.destroy()


class HelpDialog:
    """Dialog showing keyboard shortcuts and app info"""

    def __init__(self, parent, shortcut_text=""):
        """
        Initialize the help dialog

        Args:
            parent: Parent window
            shortcut_text: Pre-formatted shortcut help text
        """
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Simple Checklist \u2014 Help")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._setup_ui(shortcut_text)

    def _setup_ui(self, shortcut_text):
        """Setup the dialog UI"""
        # Title
        tk.Label(self.dialog, text="Simple Checklist",
                font=('Segoe UI', 16, 'bold')).pack(pady=(15, 5))
        tk.Label(self.dialog, text="A lightweight, keyboard-driven task manager",
                font=('Segoe UI', 10), fg='#7f8c8d').pack(pady=(0, 10))

        # Scrollable text area
        text_frame = tk.Frame(self.dialog)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text = tk.Text(text_frame, wrap=tk.WORD, font=('Segoe UI', 10),
                           relief=tk.SOLID, borderwidth=1,
                           yscrollcommand=scrollbar.set)
        self.text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text.yview)

        # Build help content
        content = shortcut_text or "No shortcuts registered."
        content += "\n\n" + "=" * 40 + "\n\n"
        content += "Features:\n"
        content += "  - Nested sub-tasks with independent checkboxes\n"
        content += "  - Drag-and-drop category reordering\n"
        content += "  - Task priorities, due dates, and reminders\n"
        content += "  - Real-time search across all tasks\n"
        content += "  - Multiple sort options (smart, priority, etc.)\n"
        content += "  - Markdown export\n"
        content += "  - Undo/Redo support\n"
        content += "  - Multiple checklist file support\n"

        self.text.insert('1.0', content)
        self.text.config(state=tk.DISABLED)

        # Close button
        tk.Button(self.dialog, text="Close",
                 command=self.dialog.destroy,
                 padx=20, pady=5).pack(pady=10)

        # Escape to close
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())


class EditCategoryDialog:
    """Dialog for editing a category's name"""

    def __init__(self, parent, current_name, on_save_callback):
        """
        Initialize the edit category dialog

        Args:
            parent: Parent window
            current_name: Current category name to edit
            on_save_callback: Callback function(new_name) called when category is saved
        """
        self.on_save_callback = on_save_callback

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Category")
        self.dialog.geometry("300x120")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._setup_ui(current_name)

    def _setup_ui(self, current_name):
        """Setup the dialog UI"""
        tk.Label(self.dialog,
                 text=f"Category name (max {MAX_CATEGORY_NAME_LENGTH} chars):").pack(pady=10)

        self.entry = tk.Entry(self.dialog, font=('Segoe UI', 11))
        self.entry.pack(pady=5, padx=20, fill=tk.X)
        self.entry.insert(0, current_name)
        self.entry.focus()
        self.entry.select_range(0, tk.END)

        btn_frame = tk.Frame(self.dialog)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Cancel",
                 command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Save",
                 command=self._on_save).pack(side=tk.LEFT, padx=5)

        # Bind Enter key
        self.entry.bind('<Return>', lambda e: self._on_save())

    def _on_save(self):
        """Handle save button click"""
        name = self.entry.get().strip()
        if not name:
            messagebox.showwarning("Invalid Input",
                                  "Category name cannot be empty!")
            return

        if len(name) > MAX_CATEGORY_NAME_LENGTH:
            messagebox.showwarning("Invalid Input",
                                  f"Category name cannot exceed {MAX_CATEGORY_NAME_LENGTH} characters!\n"
                                  f"Current length: {len(name)}")
            return

        self.on_save_callback(name)
        self.dialog.destroy()
