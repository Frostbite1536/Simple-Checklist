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
import json
import os
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
    ReminderDialog
)

# Try to import plyer for cross-platform notifications
try:
    from plyer import notification as plyer_notification
    HAS_PLYER = True
except ImportError:
    HAS_PLYER = False

# Import business logic
from src.models import Category, Task, Checklist
from src.persistence import Storage, Settings


class ChecklistApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Checklist")
        self.root.geometry("900x600")

        # Data
        self.data = {
            'categories': [],
            'current_category': None
        }
        self.data_file = os.path.join(os.path.expanduser('~'), '.simple_checklist.json')

        # Settings
        self.settings = {
            'input_bg_color': 'white',
            'recent_files': []
        }
        self.settings_file = os.path.join(os.path.expanduser('~'), '.simple_checklist_settings.json')
        self.load_settings()

        # Load data
        self.load_data()
        if not self.data['categories']:
            self.init_default_categories()

        # Setup UI components
        self.setup_ui()

        # Render initial state
        self.sidebar.render_categories(self.data['categories'],
                                       self.data['current_category'])
        self.render_tasks()

        # Keyboard shortcuts
        self.setup_shortcuts()

    def init_default_categories(self):
        """Initialize with default categories"""
        self.data['categories'] = [
            {'id': 1, 'name': 'Slack', 'tasks': []},
            {'id': 2, 'name': 'Discord', 'tasks': []},
            {'id': 3, 'name': 'Twitter', 'tasks': []},
            {'id': 4, 'name': 'Telegram', 'tasks': []},
            {'id': 5, 'name': 'General', 'tasks': []}
        ]
        self.data['current_category'] = 1
        self.save_data()

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
            'get_recent_files': lambda: self.settings['recent_files'],
            'on_load_recent_file': self.load_checklist_file,
            'on_clear_recent_files': self.clear_recent_files
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

        # Create input area
        self.input_area = InputArea(
            self.main_window.get_input_container(),
            on_add_task_callback=self.add_task_from_input,
            input_bg_color=self.settings['input_bg_color']
        )
        self.input_area.pack(fill=tk.X, padx=20, pady=15)

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Ctrl+1-9 to switch categories
        # Bug #11 fix: Check if input area has focus before processing shortcut
        for i in range(1, 10):
            self.root.bind(f'<Control-Key-{i}>',
                          lambda e, idx=i-1: self._handle_category_shortcut(idx))

        # Start reminder checker
        self.check_reminders()

    def _handle_category_shortcut(self, idx):
        """Handle category switching shortcut, ignoring if input has focus"""
        # Bug #11 fix: Don't switch categories if input area is focused
        try:
            focused_widget = self.root.focus_get()
            # Check if focus is on the input area's text widget
            if hasattr(self, 'input_area') and self.input_area.has_focus():
                return  # Ignore shortcut when input is focused
        except (KeyError, AttributeError):
            pass
        self.switch_category_by_index(idx)

    def render_tasks(self):
        """Render tasks for current category"""
        category = self.get_current_category()
        self.task_panel.render_tasks(category)

        if category:
            self.main_window.update_title(category['name'])
        else:
            self.main_window.update_title("Select a category")

    def get_current_category(self):
        """Get the currently selected category"""
        for cat in self.data['categories']:
            if cat['id'] == self.data['current_category']:
                return cat
        return None

    def switch_category(self, cat_id):
        """Switch to a different category"""
        self.data['current_category'] = cat_id
        self.sidebar.render_categories(self.data['categories'],
                                       self.data['current_category'])
        self.render_tasks()

    def switch_category_by_index(self, idx):
        """Switch category by index (for Ctrl+number shortcuts)"""
        if self.data['categories'] and 0 <= idx < len(self.data['categories']):
            self.switch_category(self.data['categories'][idx]['id'])

    def reorder_categories(self, from_idx, to_idx):
        """Reorder categories via drag-and-drop"""
        category = self.data['categories'].pop(from_idx)
        self.data['categories'].insert(to_idx, category)
        self.save_data()
        self.sidebar.render_categories(self.data['categories'],
                                       self.data['current_category'])

    def add_category_dialog(self):
        """Show dialog to add new category"""
        def on_add(name):
            new_id = max([c['id'] for c in self.data['categories']], default=0) + 1
            self.data['categories'].append({
                'id': new_id,
                'name': name,
                'tasks': []
            })
            self.data['current_category'] = new_id
            self.save_data()
            self.sidebar.render_categories(self.data['categories'],
                                           self.data['current_category'])
            self.render_tasks()

        AddCategoryDialog(self.root, on_add)

    def delete_category(self, cat_id):
        """Delete a category"""
        if len(self.data['categories']) == 1:
            messagebox.showwarning("Cannot Delete",
                                  "Cannot delete the last category!")
            return

        if messagebox.askyesno("Delete Category",
                              "Delete this category and all its tasks?"):
            self.data['categories'] = [c for c in self.data['categories']
                                      if c['id'] != cat_id]
            if self.data['current_category'] == cat_id:
                # Bug #5 fix: Add safety check before accessing [0]
                if self.data['categories']:
                    self.data['current_category'] = self.data['categories'][0]['id']
                else:
                    self.data['current_category'] = None
            self.save_data()
            self.sidebar.render_categories(self.data['categories'],
                                           self.data['current_category'])
            self.render_tasks()

    def edit_category_dialog(self, cat_id, current_name):
        """Show dialog to edit category name"""
        def on_save(new_name):
            for cat in self.data['categories']:
                if cat['id'] == cat_id:
                    cat['name'] = new_name
                    break
            self.save_data()
            self.sidebar.render_categories(self.data['categories'],
                                           self.data['current_category'])
            self.render_tasks()

        EditCategoryDialog(self.root, current_name, on_save)

    def add_task_from_input(self):
        """Add task from input field"""
        text = self.input_area.get_text()
        if not text:
            return

        category = self.get_current_category()
        if category:
            category['tasks'].append({
                'text': text,
                'notes': [],
                'completed': False,
                'created': datetime.now().isoformat()
            })
            self.save_data()
            self.render_tasks()
            self.sidebar.render_categories(self.data['categories'],
                                           self.data['current_category'])
            self.input_area.clear()

    def toggle_task(self, idx):
        """Toggle task completion status"""
        category = self.get_current_category()
        if category and idx < len(category['tasks']):
            category['tasks'][idx]['completed'] = not category['tasks'][idx]['completed']
            self.save_data()
            self.render_tasks()

    def delete_task(self, idx):
        """Delete a task"""
        category = self.get_current_category()
        if category and idx < len(category['tasks']):
            if messagebox.askyesno("Delete Task", "Delete this task?"):
                del category['tasks'][idx]
                self.save_data()
                self.render_tasks()
                self.sidebar.render_categories(self.data['categories'],
                                               self.data['current_category'])

    def edit_task_dialog(self, task_idx):
        """Show dialog to edit a task's text"""
        category = self.get_current_category()
        if not category or task_idx >= len(category['tasks']):
            return

        current_text = category['tasks'][task_idx]['text']

        def on_save(new_text):
            category['tasks'][task_idx]['text'] = new_text
            self.save_data()
            self.render_tasks()

        EditTaskDialog(self.root, current_text, on_save)

    def clear_completed(self):
        """Clear all completed tasks"""
        category = self.get_current_category()
        if not category:
            return

        completed = [t for t in category['tasks'] if t['completed']]
        if not completed:
            messagebox.showinfo("No Tasks", "No completed tasks to clear!")
            return

        if messagebox.askyesno("Clear Completed",
                              f"Clear {len(completed)} completed task(s)?"):
            category['tasks'] = [t for t in category['tasks'] if not t['completed']]
            self.save_data()
            self.render_tasks()
            self.sidebar.render_categories(self.data['categories'],
                                           self.data['current_category'])

    def add_subtask_dialog(self, task_idx):
        """Show dialog to add a sub-task"""
        def on_add(text):
            category = self.get_current_category()
            if category and task_idx < len(category['tasks']):
                if 'subtasks' not in category['tasks'][task_idx]:
                    category['tasks'][task_idx]['subtasks'] = []
                category['tasks'][task_idx]['subtasks'].append({
                    'text': text,
                    'completed': False
                })
                self.save_data()
                self.render_tasks()

        AddSubtaskDialog(self.root, on_add)

    def toggle_subtask(self, task_idx, subtask_idx):
        """Toggle sub-task completion status"""
        category = self.get_current_category()
        if category and task_idx < len(category['tasks']):
            task = category['tasks'][task_idx]
            if 'subtasks' in task and subtask_idx < len(task['subtasks']):
                task['subtasks'][subtask_idx]['completed'] = not task['subtasks'][subtask_idx]['completed']
                self.save_data()
                self.render_tasks()

    def delete_subtask(self, task_idx, subtask_idx):
        """Delete a sub-task"""
        category = self.get_current_category()
        if category and task_idx < len(category['tasks']):
            task = category['tasks'][task_idx]
            if 'subtasks' in task and subtask_idx < len(task['subtasks']):
                if messagebox.askyesno("Delete Sub-task", "Delete this sub-task?"):
                    del task['subtasks'][subtask_idx]
                    self.save_data()
                    self.render_tasks()

    def edit_subtask_dialog(self, task_idx, subtask_idx):
        """Show dialog to edit a subtask's text"""
        category = self.get_current_category()
        if not category or task_idx >= len(category['tasks']):
            return

        task = category['tasks'][task_idx]
        if 'subtasks' not in task or subtask_idx >= len(task['subtasks']):
            return

        current_text = task['subtasks'][subtask_idx]['text']

        def on_save(new_text):
            task['subtasks'][subtask_idx]['text'] = new_text
            self.save_data()
            self.render_tasks()

        EditTaskDialog(self.root, current_text, on_save, title="Edit Sub-task")

    def set_reminder_dialog(self, task_idx):
        """Show dialog to set a reminder for a task"""
        category = self.get_current_category()
        if not category or task_idx >= len(category['tasks']):
            return

        task = category['tasks'][task_idx]
        current_reminder = task.get('reminder')

        def on_set(reminder_iso):
            task['reminder'] = reminder_iso
            self.save_data()
            self.render_tasks()

        ReminderDialog(self.root, task['text'], on_set, current_reminder)

    def check_reminders(self):
        """Check for due reminders and show notifications"""
        now = datetime.now()
        reminders_triggered = []

        corrupted_reminders = []
        for category in self.data.get('categories', []):
            for task in category.get('tasks', []):
                reminder = task.get('reminder')
                if reminder:
                    try:
                        reminder_time = datetime.fromisoformat(reminder)
                        if reminder_time <= now:
                            reminders_triggered.append({
                                'category': category['name'],
                                'task': task['text'],
                                'task_obj': task
                            })
                    except ValueError:
                        # Bug #8 fix: Clear corrupted reminder data instead of silently ignoring
                        corrupted_reminders.append(task)

        # Clear any corrupted reminders
        for task in corrupted_reminders:
            task['reminder'] = None

        # Show notifications for triggered reminders
        # Bug #2 fix: Clear reminder in try-finally to ensure it's cleared even if notification fails
        for reminder_info in reminders_triggered:
            try:
                self.show_notification(
                    title=f"Reminder: {reminder_info['category']}",
                    message=reminder_info['task'][:100]
                )
            finally:
                # Clear the reminder regardless of notification success/failure
                reminder_info['task_obj']['reminder'] = None

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

        # Fallback: Show a tkinter message box
        # Use after to prevent blocking
        self.root.after(0, lambda: messagebox.showinfo(title, message))

    def export_markdown(self):
        """Export all tasks to Markdown file with timestamps"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")],
            initialfile=f"checklist-{datetime.now().strftime('%Y-%m-%d')}.md"
        )

        if not filename:
            return

        # Add timestamp header
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        markdown = f"# Checklist Export\n\n**Exported:** {timestamp}\n"
        markdown += f"**File:** {os.path.basename(self.data_file)}\n\n---\n\n"

        for category in self.data['categories']:
            markdown += f"## {category['name']}\n\n"

            if not category['tasks']:
                markdown += "_No tasks_\n\n"
            else:
                for task in category['tasks']:
                    checkbox = '[x]' if task['completed'] else '[ ]'
                    markdown += f"- {checkbox} {task['text']}\n"

                    # Export sub-tasks
                    if task.get('subtasks'):
                        for subtask in task['subtasks']:
                            sub_checkbox = '[x]' if subtask['completed'] else '[ ]'
                            markdown += f"  - {sub_checkbox} {subtask['text']}\n"

                    # Export notes
                    if task.get('notes'):
                        for note in task['notes']:
                            markdown += f"    - {note}\n"

                markdown += "\n"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(markdown)
            messagebox.showinfo("Export Complete",
                               f"Tasks exported to:\n{filename}")
        except (IOError, OSError) as e:
            messagebox.showerror("Export Failed",
                                f"Failed to export checklist:\n{str(e)}")

    def save_data(self):
        """Save data to JSON file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except (IOError, OSError) as e:
            messagebox.showerror("Error Saving Data",
                                f"Failed to save checklist:\n{str(e)}")

    def load_data(self):
        """Load data from JSON file"""
        if os.path.exists(self.data_file):
            # Bug #12 fix: Create backup before loading in case file is corrupted
            backup_file = self.data_file + '.backup'
            try:
                # Only create backup if file exists and is non-empty
                if os.path.getsize(self.data_file) > 0:
                    import shutil
                    shutil.copy2(self.data_file, backup_file)
            except (IOError, OSError):
                pass  # Backup creation is best-effort

            try:
                with open(self.data_file, 'r') as f:
                    self.data = json.load(f)
                # Migrate old data to ensure consistency
                self.migrate_data()
            except (json.JSONDecodeError, IOError, OSError, KeyError) as e:
                # Bug #12 fix: Try to recover from backup
                recovered = False
                if os.path.exists(backup_file):
                    try:
                        with open(backup_file, 'r') as f:
                            self.data = json.load(f)
                        self.migrate_data()
                        recovered = True
                        messagebox.showwarning("Data Recovery",
                                              f"Original file was corrupted:\n{str(e)}\n\n"
                                              "Data has been restored from backup.")
                    except (json.JSONDecodeError, IOError, OSError, KeyError):
                        pass  # Backup also corrupted

                if not recovered:
                    messagebox.showerror("Error Loading Data",
                                        f"Failed to load checklist data:\n{str(e)}\n\n"
                                        f"Starting with default categories.\n"
                                        f"A backup may exist at: {backup_file}")
                    self.data = {'categories': [], 'current_category': None}

    def migrate_data(self):
        """Migrate old data structures to current format"""
        # Ensure all subtasks have 'completed' key
        for category in self.data.get('categories', []):
            for task in category.get('tasks', []):
                if 'subtasks' in task:
                    for subtask in task['subtasks']:
                        if 'completed' not in subtask:
                            subtask['completed'] = False

    def save_settings(self):
        """Save settings to JSON file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except (IOError, OSError) as e:
            messagebox.showerror("Error Saving Settings",
                                f"Failed to save settings:\n{str(e)}")

    def load_settings(self):
        """Load settings from JSON file"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                    self.settings.update(loaded)
            except (json.JSONDecodeError, IOError, OSError):
                # If settings fail to load, use defaults silently
                # Settings are non-critical, so don't show error to user
                pass
        # Bug #3 fix: Clean up non-existent files from recent files list
        self.cleanup_recent_files()

    def cleanup_recent_files(self):
        """Remove non-existent files from recent files list"""
        if 'recent_files' in self.settings:
            original_count = len(self.settings['recent_files'])
            self.settings['recent_files'] = [
                f for f in self.settings['recent_files']
                if os.path.exists(f)
            ]
            # Save if any files were removed
            if len(self.settings['recent_files']) < original_count:
                self.save_settings()

    def new_checklist(self):
        """Create a new checklist"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="new-checklist.json"
        )

        if not filename:
            return  # User cancelled, don't clear data

        # Only ask to save after we know user didn't cancel
        if messagebox.askyesno("New Checklist",
                              "Save current checklist before creating new?"):
            self.save_data()

        self.data_file = filename
        self.data = {'categories': [], 'current_category': None}
        self.init_default_categories()
        self.add_to_recent_files(filename)
        self.sidebar.render_categories(self.data['categories'],
                                       self.data['current_category'])
        self.render_tasks()
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
        # Keep backup of current data in case load fails
        backup_data = self.data.copy()
        backup_file = self.data_file

        try:
            with open(filename, 'r') as f:
                loaded_data = json.load(f)

            # Validate the data structure
            if not isinstance(loaded_data, dict):
                raise ValueError("Invalid checklist format: root must be an object")

            if 'categories' not in loaded_data:
                raise ValueError("Invalid checklist format: missing 'categories' field")

            if not isinstance(loaded_data['categories'], list):
                raise ValueError("Invalid checklist format: 'categories' must be a list")

            # Ensure current_category exists and is valid
            if 'current_category' not in loaded_data or loaded_data['current_category'] is None:
                if loaded_data['categories']:
                    loaded_data['current_category'] = loaded_data['categories'][0].get('id', 1)
                else:
                    loaded_data['current_category'] = None

            self.data = loaded_data
            self.data_file = filename
            self.migrate_data()  # Ensure data consistency
            self.add_to_recent_files(filename)
            self.sidebar.render_categories(self.data['categories'],
                                           self.data['current_category'])
            self.render_tasks()
            self.main_window.update_window_title(filename)

        except (json.JSONDecodeError, IOError, OSError, ValueError) as e:
            # Restore previous state on error
            self.data = backup_data
            self.data_file = backup_file
            messagebox.showerror("Error",
                                f"Failed to load checklist:\n{str(e)}\n\nPrevious checklist has been restored.")
            # Re-render to ensure UI matches restored state
            self.sidebar.render_categories(self.data['categories'],
                                           self.data['current_category'])
            self.render_tasks()

    def save_checklist_as(self):
        """Save checklist to a new file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=os.path.basename(self.data_file)
        )

        if filename:
            self.data_file = filename
            self.save_data()
            self.add_to_recent_files(filename)
            self.main_window.update_window_title(filename)
            messagebox.showinfo("Saved", f"Checklist saved to:\n{filename}")

    def add_to_recent_files(self, filename):
        """Add file to recent files list"""
        if filename in self.settings['recent_files']:
            self.settings['recent_files'].remove(filename)
        self.settings['recent_files'].insert(0, filename)
        self.settings['recent_files'] = self.settings['recent_files'][:10]
        self.save_settings()
        self.main_window.update_recent_menu()

    def clear_recent_files(self):
        """Clear the recent files list"""
        self.settings['recent_files'] = []
        self.save_settings()

    def change_input_color(self):
        """Change the color of the input box"""
        color = colorchooser.askcolor(
            title="Choose Input Box Color",
            initialcolor=self.settings['input_bg_color']
        )

        if color[1]:  # color[1] is the hex color string
            self.settings['input_bg_color'] = color[1]
            self.input_area.set_bg_color(color[1])
            self.save_settings()


def main():
    root = tk.Tk()
    app = ChecklistApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
