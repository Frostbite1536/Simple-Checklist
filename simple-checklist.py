"""
Simple Checklist - Desktop Version
A lightweight, keyboard-driven task manager with categories and Markdown export
Features:
- Nested sub-tasks with independent checkboxes
- Drag-and-drop category reordering
- Customizable input box colors
- Multiple checklist file support
- Timestamped Markdown exports
- Easy text selection and copying
"""

import tkinter as tk
from tkinter import messagebox, filedialog, colorchooser
import copy
import os
import shutil
from datetime import datetime

# Import UI components
from src.ui import (
    MainWindow,
    Sidebar,
    TaskPanel,
    InputArea,
    AddCategoryDialog,
    AddSubtaskDialog,
    EditTaskDialog,
    EditCategoryDialog,
    ReminderDialog,
    SearchBar
)

# Try to import plyer for cross-platform notifications
try:
    from plyer import notification as plyer_notification
    HAS_PLYER = True
except ImportError:
    HAS_PLYER = False

# Import business logic
from src.models import Category, Task, Subtask, Checklist
from src.persistence.storage import ChecklistStorage
from src.persistence.settings import SettingsManager

# Import features
from src.features.undo_manager import UndoManager
from src.features.search import TaskSearcher
from src.features.task_sorting import TaskSorter
from src.features.export import MarkdownExporter
from src.features.shortcuts import ShortcutManager


class ChecklistApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Checklist")
        self.root.geometry("900x600")

        # Persistence
        self.storage = ChecklistStorage()
        self.settings_mgr = SettingsManager()

        # Data — model objects throughout
        self.checklist = Checklist()

        # Initialize undo/redo manager (Feature #1)
        self.undo_manager = UndoManager(max_history=20)

        # Load data
        self.load_data()
        if not self.checklist.categories:
            self.init_default_categories()

        # Setup UI components
        self.setup_ui()

        # Render initial state
        self.refresh_ui()

        # Keyboard shortcuts
        self.setup_shortcuts()

    def init_default_categories(self):
        """Initialize with default categories"""
        self.checklist = self.storage.create_default_checklist()
        self.save_data()

    def refresh_ui(self):
        """Refresh sidebar and task panel to match current data."""
        self.sidebar.render_categories(self.checklist.categories,
                                       self.checklist.current_category_id)
        self.render_tasks()

    def setup_ui(self):
        """Create the UI layout using modular components"""
        # Create main window with callbacks
        callbacks = {
            'on_new_checklist': self.new_checklist,
            'on_open_checklist': self.open_checklist,
            'on_save_as': self.save_checklist_as,
            'on_exit': self.root.quit,
            'on_change_color': self.change_input_color,
            'on_export_markdown': self.export_markdown,
            'on_clear_completed': self.clear_completed,
            'get_recent_files': self.settings_mgr.get_recent_files,
            'on_load_recent_file': self.load_checklist_file,
            'on_clear_recent_files': self.clear_recent_files,
            # Feature #1: Undo/Redo callbacks
            'on_undo': self.undo_action,
            'on_redo': self.redo_action,
            'can_undo': self.undo_manager.can_undo,
            'can_redo': self.undo_manager.can_redo,
            # Feature #9: Task sorting callback
            'on_sort_tasks': self.sort_tasks
        }
        self.main_window = MainWindow(self.root, callbacks)

        # Create sidebar
        self.sidebar = Sidebar(
            self.main_window.get_sidebar_container(),
            on_category_click=self.switch_category,
            on_category_delete=self.delete_category,
            on_add_category=self.add_category_dialog,
            on_category_reorder=self.reorder_categories,
            on_category_edit=self.edit_category_dialog
        )
        self.sidebar.pack(fill=tk.BOTH, expand=True)

        # Feature #2: Create search bar
        self.search_bar = SearchBar(
            self.main_window.get_task_panel_container(),
            on_search_callback=self.search_tasks,
            on_clear_callback=self.clear_search
        )
        self.search_bar.pack(fill=tk.X, padx=20, pady=(10, 0))

        # Create task panel
        self.task_panel = TaskPanel(
            self.main_window.get_task_panel_container(),
            on_toggle_task=self.toggle_task,
            on_delete_task=self.delete_task,
            on_add_subtask=self.add_subtask_dialog,
            on_toggle_subtask=self.toggle_subtask,
            on_delete_subtask=self.delete_subtask,
            on_edit_task=self.edit_task_dialog,
            on_edit_subtask=self.edit_subtask_dialog,
            on_set_reminder=self.set_reminder_dialog
        )
        self.task_panel.pack(fill=tk.BOTH, expand=True)

        # Search state
        self.search_results = None

        # Create input area
        self.input_area = InputArea(
            self.main_window.get_input_container(),
            on_add_task_callback=self.add_task_from_input,
            input_bg_color=self.settings_mgr.get_input_bg_color()
        )
        self.input_area.pack(fill=tk.X, padx=20, pady=15)

    def setup_shortcuts(self):
        """Setup keyboard shortcuts via ShortcutManager"""
        self.shortcut_mgr = ShortcutManager(self.root)

        # Undo/Redo (register both cases for cross-platform)
        self.shortcut_mgr.register_shortcut('<Control-z>', lambda e: self.undo_action(), "Undo")
        self.shortcut_mgr.register_shortcut('<Control-Z>', lambda e: self.undo_action())
        self.shortcut_mgr.register_shortcut('<Control-y>', lambda e: self.redo_action(), "Redo")
        self.shortcut_mgr.register_shortcut('<Control-Y>', lambda e: self.redo_action())
        self.shortcut_mgr.register_shortcut('<Control-Shift-z>', lambda e: self.redo_action())
        self.shortcut_mgr.register_shortcut('<Control-Shift-Z>', lambda e: self.redo_action())

        # Search
        self.shortcut_mgr.register_shortcut('<Control-f>', lambda e: self.search_bar.focus(), "Search")
        self.shortcut_mgr.register_shortcut('<Control-F>', lambda e: self.search_bar.focus())

        # Category switching: Ctrl+1-9 AND Alt+1-9 (fallback)
        for i in range(1, 10):
            self.shortcut_mgr.register_shortcut(
                f'<Control-Key-{i}>',
                lambda e, idx=i-1: self._handle_category_shortcut(idx),
                f"Switch to category {i}")
            self.shortcut_mgr.register_shortcut(
                f'<Control-{i}>',
                lambda e, idx=i-1: self._handle_category_shortcut(idx))
            self.shortcut_mgr.register_shortcut(
                f'<Alt-Key-{i}>',
                lambda e, idx=i-1: self._handle_category_shortcut(idx))
            self.shortcut_mgr.register_shortcut(
                f'<Alt-{i}>',
                lambda e, idx=i-1: self._handle_category_shortcut(idx))

        # Arrow navigation for 10+ categories
        self.shortcut_mgr.register_shortcut('<Control-Left>', lambda e: self._navigate_categories(-1), "Previous category")
        self.shortcut_mgr.register_shortcut('<Control-Right>', lambda e: self._navigate_categories(1), "Next category")
        self.shortcut_mgr.register_shortcut('<Control-Up>', lambda e: self._navigate_categories(-1))
        self.shortcut_mgr.register_shortcut('<Control-Down>', lambda e: self._navigate_categories(1))

        self.shortcut_mgr.bind_all()

        # Start reminder checker
        self.check_reminders()

    def _navigate_categories(self, direction):
        """Navigate to previous/next category (for 10+ categories support)"""
        try:
            if hasattr(self, 'input_area') and self.input_area.has_focus():
                return
        except (KeyError, AttributeError):
            pass

        categories = self.checklist.categories
        if not categories:
            return

        current_id = self.checklist.current_category_id

        # Find current category index
        current_idx = None
        for i, cat in enumerate(categories):
            if cat.id == current_id:
                current_idx = i
                break

        if current_idx is None:
            current_idx = 0

        # Calculate next index with wrap-around
        next_idx = (current_idx + direction) % len(categories)
        self.switch_category(categories[next_idx].id)

    def _handle_category_shortcut(self, idx):
        """Handle category switching shortcut, ignoring if input has focus"""
        try:
            if hasattr(self, 'input_area') and self.input_area.has_focus():
                return
        except (KeyError, AttributeError):
            pass
        self.switch_category_by_index(idx)

    def record_state(self, action_description=""):
        """Record current state before a change (Feature #1: Undo/Redo)"""
        self.undo_manager.record_state(self.checklist.to_dict(), action_description)

    def undo_action(self):
        """Undo the last action (Feature #1)"""
        previous_state = self.undo_manager.undo(self.checklist.to_dict())
        if previous_state:
            self.checklist = Checklist.from_dict(previous_state)
            self.save_data()
            self.refresh_ui()

    def redo_action(self):
        """Redo the last undone action (Feature #1)"""
        redo_state = self.undo_manager.redo(self.checklist.to_dict())
        if redo_state:
            self.checklist = Checklist.from_dict(redo_state)
            self.save_data()
            self.refresh_ui()

    def render_tasks(self):
        """Render tasks for current category"""
        # If search is active, render search results instead
        if self.search_bar.is_active():
            self.search_tasks(self.search_bar.get_query())
            return

        category = self.checklist.get_current_category()
        self.task_panel.render_tasks(category)

        if category:
            self.main_window.update_title(category.name)
        else:
            self.main_window.update_title("Select a category")

    def search_tasks(self, query):
        """Search tasks and display results (Feature #2)"""
        if not query or not query.strip():
            self.clear_search()
            return

        results = TaskSearcher.search_tasks(
            self.checklist.categories,
            query,
            category_id=self.checklist.current_category_id
        )

        self.search_results = results

        category = self.checklist.get_current_category()
        cat_name = category.name if category else "Tasks"
        self.main_window.update_title(f"🔍 Search in {cat_name}: {len(results)} result(s)")

        self._render_search_results(results, query)

    def _render_search_results(self, results, query):
        """Render search results in task panel"""
        for widget in self.task_panel.task_frame.winfo_children():
            widget.destroy()

        if not results:
            import tkinter as tk
            empty = tk.Label(self.task_panel.task_frame,
                           text=f"No tasks matching '{query}'",
                           bg='white', fg='#95a5a6',
                           font=('Segoe UI', 12))
            empty.pack(pady=50)
            return

        for result in results:
            self.task_panel._render_task(result['task_idx'], result['task'])

    def clear_search(self):
        """Clear search and show normal task list (Feature #2)"""
        self.search_results = None
        category = self.checklist.get_current_category()
        self.task_panel.render_tasks(category)

        if category:
            self.main_window.update_title(category.name)
        else:
            self.main_window.update_title("Select a category")

    def sort_tasks(self, sort_by):
        """Sort tasks in current category (Feature #9)"""
        category = self.checklist.get_current_category()
        if not category or not category.tasks:
            return

        self.record_state(f"Sort tasks by {sort_by}")

        if sort_by == 'smart':
            TaskSorter.sort_smart(category.tasks)
        else:
            TaskSorter.sort_tasks(category.tasks, sort_by)

        self.save_data()
        self.render_tasks()

    def switch_category(self, cat_id):
        """Switch to a different category"""
        self.checklist.current_category_id = cat_id
        self.sidebar.render_categories(self.checklist.categories,
                                       self.checklist.current_category_id)
        self.render_tasks()

    def switch_category_by_index(self, idx):
        """Switch category by index (for Ctrl+number shortcuts)"""
        cat = self.checklist.get_category_by_index(idx)
        if cat:
            self.switch_category(cat.id)

    def reorder_categories(self, from_idx, to_idx):
        """Reorder categories via drag-and-drop"""
        self.record_state("Reorder categories")
        self.checklist.reorder_categories(from_idx, to_idx)
        self.save_data()
        self.sidebar.render_categories(self.checklist.categories,
                                       self.checklist.current_category_id)

    def add_category_dialog(self):
        """Show dialog to add new category"""
        def on_add(name):
            self.record_state("Add category")
            new_id = self.checklist.get_next_category_id()
            self.checklist.add_category(Category(new_id, name))
            self.checklist.current_category_id = new_id
            self.save_data()
            self.refresh_ui()

        AddCategoryDialog(self.root, on_add)

    def delete_category(self, cat_id):
        """Delete a category"""
        if self.checklist.get_category_count() == 1:
            messagebox.showwarning("Cannot Delete",
                                  "Cannot delete the last category!")
            return

        if messagebox.askyesno("Delete Category",
                              "Delete this category and all its tasks?"):
            self.record_state("Delete category")
            self.checklist.remove_category(cat_id)
            if self.checklist.current_category_id == cat_id:
                if self.checklist.categories:
                    self.checklist.current_category_id = self.checklist.categories[0].id
                else:
                    self.checklist.current_category_id = None
            self.save_data()
            self.refresh_ui()

    def edit_category_dialog(self, cat_id, current_name):
        """Show dialog to edit category name"""
        def on_save(new_name):
            self.record_state("Edit category name")
            cat = self.checklist.get_category(cat_id)
            if cat:
                cat.name = new_name
            self.save_data()
            self.refresh_ui()

        EditCategoryDialog(self.root, current_name, on_save)

    def add_task_from_input(self):
        """Add task from input field"""
        text = self.input_area.get_text()
        if not text:
            return

        category = self.checklist.get_current_category()
        if category:
            self.record_state("Add task")
            category.add_task(Task(text))
            self.save_data()
            self.render_tasks()
            self.sidebar.render_categories(self.checklist.categories,
                                           self.checklist.current_category_id)
            self.input_area.clear()

    def toggle_task(self, idx):
        """Toggle task completion status"""
        category = self.checklist.get_current_category()
        if category and idx < len(category.tasks):
            self.record_state("Toggle task")
            category.tasks[idx].toggle_completion()
            self.save_data()
            self.render_tasks()

    def delete_task(self, idx):
        """Delete a task"""
        category = self.checklist.get_current_category()
        if category and idx < len(category.tasks):
            if messagebox.askyesno("Delete Task", "Delete this task?"):
                self.record_state("Delete task")
                category.remove_task(idx)
                self.save_data()
                self.render_tasks()
                self.sidebar.render_categories(self.checklist.categories,
                                               self.checklist.current_category_id)

    def edit_task_dialog(self, task_idx):
        """Show dialog to edit a task's text, priority, and due date"""
        category = self.checklist.get_current_category()
        if not category or task_idx >= len(category.tasks):
            return

        task = category.tasks[task_idx]
        current_text = task.text
        current_priority = task.priority
        current_due_date = task.due_date

        def on_save(new_text, priority=None, due_date=None):
            self.record_state("Edit task")
            task.text = new_text
            if priority is not None:
                task.priority = priority
            if due_date is not None or task.due_date is not None:
                task.due_date = due_date
            self.save_data()
            self.render_tasks()

        EditTaskDialog(self.root, current_text, on_save,
                      current_priority=current_priority,
                      current_due_date=current_due_date,
                      show_options=True)

    def clear_completed(self):
        """Clear all completed tasks"""
        category = self.checklist.get_current_category()
        if not category:
            return

        completed = category.get_completed_tasks()
        if not completed:
            messagebox.showinfo("No Tasks", "No completed tasks to clear!")
            return

        if messagebox.askyesno("Clear Completed",
                              f"Clear {len(completed)} completed task(s)?"):
            self.record_state("Clear completed tasks")
            category.clear_completed()
            self.save_data()
            self.render_tasks()
            self.sidebar.render_categories(self.checklist.categories,
                                           self.checklist.current_category_id)

    def add_subtask_dialog(self, task_idx):
        """Show dialog to add a sub-task"""
        def on_add(text):
            category = self.checklist.get_current_category()
            if category and task_idx < len(category.tasks):
                self.record_state("Add subtask")
                category.tasks[task_idx].add_subtask(Subtask(text))
                self.save_data()
                self.render_tasks()

        AddSubtaskDialog(self.root, on_add)

    def toggle_subtask(self, task_idx, subtask_idx):
        """Toggle sub-task completion status"""
        category = self.checklist.get_current_category()
        if category and task_idx < len(category.tasks):
            task = category.tasks[task_idx]
            if subtask_idx < len(task.subtasks):
                self.record_state("Toggle subtask")
                task.subtasks[subtask_idx].toggle_completion()
                self.save_data()
                self.render_tasks()

    def delete_subtask(self, task_idx, subtask_idx):
        """Delete a sub-task"""
        category = self.checklist.get_current_category()
        if category and task_idx < len(category.tasks):
            task = category.tasks[task_idx]
            if subtask_idx < len(task.subtasks):
                if messagebox.askyesno("Delete Sub-task", "Delete this sub-task?"):
                    self.record_state("Delete subtask")
                    task.remove_subtask(subtask_idx)
                    self.save_data()
                    self.render_tasks()

    def edit_subtask_dialog(self, task_idx, subtask_idx):
        """Show dialog to edit a subtask's text"""
        category = self.checklist.get_current_category()
        if not category or task_idx >= len(category.tasks):
            return

        task = category.tasks[task_idx]
        if subtask_idx >= len(task.subtasks):
            return

        current_text = task.subtasks[subtask_idx].text

        def on_save(new_text):
            self.record_state("Edit subtask")
            task.subtasks[subtask_idx].text = new_text
            self.save_data()
            self.render_tasks()

        EditTaskDialog(self.root, current_text, on_save, title="Edit Sub-task")

    def set_reminder_dialog(self, task_idx):
        """Show dialog to set a reminder for a task"""
        category = self.checklist.get_current_category()
        if not category or task_idx >= len(category.tasks):
            return

        task = category.tasks[task_idx]

        def on_set(reminder_iso):
            self.record_state("Set reminder")
            task.reminder = reminder_iso
            self.save_data()
            self.render_tasks()

        ReminderDialog(self.root, task.text, on_set, task.reminder)

    def check_reminders(self):
        """Check for due reminders and show notifications"""
        now = datetime.now()
        reminders_triggered = []
        corrupted_reminders = []

        for category in self.checklist.categories:
            for task in category.tasks:
                if task.reminder:
                    try:
                        reminder_time = datetime.fromisoformat(task.reminder)
                        if reminder_time <= now:
                            reminders_triggered.append({
                                'category': category.name,
                                'task': task.text,
                                'task_obj': task
                            })
                    except ValueError:
                        corrupted_reminders.append(task)

        # Clear any corrupted reminders
        for task in corrupted_reminders:
            task.reminder = None

        # Show notifications for triggered reminders
        for reminder_info in reminders_triggered:
            try:
                self.show_notification(
                    title=f"Reminder: {reminder_info['category']}",
                    message=reminder_info['task'][:100]
                )
            finally:
                reminder_info['task_obj'].reminder = None

        if reminders_triggered or corrupted_reminders:
            self.save_data()
            self.render_tasks()

        # Check again in 30 seconds
        self.root.after(30000, self.check_reminders)

    def show_notification(self, title, message):
        """Show a system notification (cross-platform)"""
        if HAS_PLYER:
            try:
                plyer_notification.notify(
                    title=title,
                    message=message,
                    app_name="Simple Checklist",
                    timeout=10
                )
                return
            except Exception:
                pass

        self.root.after(0, lambda: messagebox.showinfo(title, message))

    def export_markdown(self):
        """Export all tasks to Markdown file using MarkdownExporter"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")],
            initialfile=f"checklist-{datetime.now().strftime('%Y-%m-%d')}.md"
        )

        if not filename:
            return

        exporter = MarkdownExporter(self.checklist, self.storage.get_file_path())
        if exporter.export_to_file(filename):
            messagebox.showinfo("Export Complete",
                               f"Tasks exported to:\n{filename}")
        else:
            messagebox.showerror("Export Failed", "Failed to export checklist.")

    def save_data(self):
        """Save data via ChecklistStorage"""
        if not self.storage.save_checklist(self.checklist):
            messagebox.showerror("Error Saving Data", "Failed to save checklist.")

    def load_data(self):
        """Load data from JSON file with backup/recovery"""
        if not self.storage.file_exists():
            return

        # Create backup before loading in case file is corrupted
        backup_file = self.storage.get_file_path() + '.backup'
        try:
            file_path = self.storage.get_file_path()
            if os.path.getsize(file_path) > 0:
                shutil.copy2(file_path, backup_file)
        except (IOError, OSError):
            pass  # Backup creation is best-effort

        checklist = self.storage.load_checklist()
        if checklist:
            self.checklist = checklist
        else:
            # Try to recover from backup
            recovered = False
            if os.path.exists(backup_file):
                try:
                    original_path = self.storage.get_file_path()
                    self.storage.set_file_path(backup_file)
                    checklist = self.storage.load_checklist()
                    self.storage.set_file_path(original_path)
                    if checklist:
                        self.checklist = checklist
                        recovered = True
                        messagebox.showwarning("Data Recovery",
                                              "Original file was corrupted.\n\n"
                                              "Data has been restored from backup.")
                except Exception:
                    pass

            if not recovered:
                messagebox.showerror("Error Loading Data",
                                    "Failed to load checklist data.\n\n"
                                    "Starting with default categories.\n"
                                    f"A backup may exist at: {backup_file}")
                self.checklist = Checklist()

    def new_checklist(self):
        """Create a new checklist"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="new-checklist.json"
        )

        if not filename:
            return

        if messagebox.askyesno("New Checklist",
                              "Save current checklist before creating new?"):
            self.save_data()

        self.storage.set_file_path(filename)
        self.checklist = Checklist()
        self.init_default_categories()
        self.add_to_recent_files(filename)
        self.refresh_ui()
        self.main_window.update_window_title(filename)

    def open_checklist(self):
        """Open an existing checklist file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filename:
            self.load_checklist_file(filename)

    def load_checklist_file(self, filename):
        """Load a specific checklist file"""
        # Keep backup of current state in case load fails
        backup_checklist = copy.deepcopy(self.checklist)
        backup_file_path = self.storage.get_file_path()

        try:
            self.storage.set_file_path(filename)
            checklist = self.storage.load_checklist()

            if checklist is None:
                raise ValueError("Failed to parse checklist file")

            # Ensure current_category_id is valid
            if checklist.current_category_id is None or \
               checklist.get_category(checklist.current_category_id) is None:
                if checklist.categories:
                    checklist.current_category_id = checklist.categories[0].id
                else:
                    checklist.current_category_id = None

            self.checklist = checklist
            self.add_to_recent_files(filename)
            self.refresh_ui()
            self.main_window.update_window_title(filename)

        except Exception as e:
            # Restore previous state on error
            self.checklist = backup_checklist
            self.storage.set_file_path(backup_file_path)
            messagebox.showerror("Error",
                                f"Failed to load checklist:\n{str(e)}\n\nPrevious checklist has been restored.")
            self.refresh_ui()

    def save_checklist_as(self):
        """Save checklist to a new file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=os.path.basename(self.storage.get_file_path())
        )

        if filename:
            self.storage.set_file_path(filename)
            self.save_data()
            self.add_to_recent_files(filename)
            self.main_window.update_window_title(filename)
            messagebox.showinfo("Saved", f"Checklist saved to:\n{filename}")

    def add_to_recent_files(self, filename):
        """Add file to recent files list"""
        self.settings_mgr.add_recent_file(filename)
        self.main_window.update_recent_menu()

    def clear_recent_files(self):
        """Clear the recent files list"""
        self.settings_mgr.clear_recent_files()

    def change_input_color(self):
        """Change the color of the input box"""
        color = colorchooser.askcolor(
            title="Choose Input Box Color",
            initialcolor=self.settings_mgr.get_input_bg_color()
        )

        if color[1]:
            self.settings_mgr.set_input_bg_color(color[1])
            self.input_area.set_bg_color(color[1])


def main():
    root = tk.Tk()
    app = ChecklistApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
