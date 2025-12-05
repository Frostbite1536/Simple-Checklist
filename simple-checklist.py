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
from tkinter import ttk, messagebox, filedialog, colorchooser
import json
import os
from datetime import datetime

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

        # Drag and drop state
        self.drag_data = {'source': None, 'index': None, 'start_y': None, 'dragging': False}

        # Load data
        self.load_data()
        if not self.data['categories']:
            self.init_default_categories()

        # Setup UI
        self.setup_ui()
        self.render_categories()
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
        """Create the UI layout"""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Checklist", command=self.new_checklist)
        file_menu.add_command(label="Open Checklist...", command=self.open_checklist)
        file_menu.add_command(label="Save As...", command=self.save_checklist_as)
        file_menu.add_separator()

        # Recent files submenu
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Recent Files", menu=self.recent_menu)
        self.update_recent_menu()

        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Change Input Box Color", command=self.change_input_color)

        # Main container
        main_container = tk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar (left)
        sidebar = tk.Frame(main_container, bg='#2c3e50', width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # Sidebar title
        title_label = tk.Label(sidebar, text="📋 Categories", 
                              bg='#2c3e50', fg='white', 
                              font=('Segoe UI', 12, 'bold'),
                              pady=15)
        title_label.pack(fill=tk.X)
        
        # Categories listbox
        self.category_frame = tk.Frame(sidebar, bg='#2c3e50')
        self.category_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        # Add category button
        add_cat_btn = tk.Button(sidebar, text="+ Add Category",
                               bg='#3498db', fg='white',
                               relief=tk.FLAT, pady=8,
                               command=self.add_category_dialog)
        add_cat_btn.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        # Right side (main content)
        right_container = tk.Frame(main_container, bg='white')
        right_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Header
        header = tk.Frame(right_container, bg='white', height=60)
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
                              command=self.export_markdown)
        export_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = tk.Button(btn_frame, text="🗑️ Clear Done",
                             bg='#e74c3c', fg='white',
                             relief=tk.FLAT, padx=12, pady=6,
                             command=self.clear_completed)
        clear_btn.pack(side=tk.LEFT)
        
        # Separator
        separator = tk.Frame(right_container, height=1, bg='#e0e0e0')
        separator.pack(fill=tk.X)
        
        # Tasks area (scrollable)
        task_container = tk.Frame(right_container, bg='white')
        task_container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas for scrolling
        self.canvas = tk.Canvas(task_container, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(task_container, orient='vertical', 
                                 command=self.canvas.yview)
        
        self.task_frame = tk.Frame(self.canvas, bg='white')
        self.task_frame.bind('<Configure>',
                           lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))

        self.canvas_window = self.canvas.create_window((0, 0), window=self.task_frame, anchor='nw')
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Update canvas width when window resizes
        self.canvas.bind('<Configure>', self.on_canvas_resize)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Input area
        input_frame = tk.Frame(right_container, bg='#fafafa')
        input_frame.pack(fill=tk.X, padx=20, pady=15)

        self.task_input = tk.Text(input_frame, height=3,
                                 font=('Segoe UI', 11),
                                 relief=tk.FLAT, bg=self.settings['input_bg_color'],
                                 borderwidth=2)
        self.task_input.pack(fill=tk.X)

        hints = tk.Label(input_frame,
                        text="💡 Shift+Enter: New task | Enter: New line | Ctrl+1-9: Switch categories",
                        bg='#fafafa', fg='#7f8c8d',
                        font=('Segoe UI', 9))
        hints.pack(pady=5)
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Shift+Enter to add task
    def add_task_handler(e):
                self.add_task_from_input()
                return 'break'

            self.task_input.bind('<Shift-Return>', add_task_handler)

        # Ctrl+1-9 to switch categories
        for i in range(1, 10):
            self.root.bind(f'<Control-Key-{i}>',
                          lambda e, idx=i-1: self.switch_category_by_index(idx))

    def on_canvas_resize(self, event):
        """Update canvas window width when canvas is resized"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def render_categories(self):
        """Render the category list with drag-and-drop support"""
        # Clear existing
        for widget in self.category_frame.winfo_children():
            widget.destroy()

        # Create category buttons
        for idx, cat in enumerate(self.data['categories']):
            is_active = cat['id'] == self.data['current_category']

            frame = tk.Frame(self.category_frame,
                           bg='#3498db' if is_active else '#2c3e50')
            frame.pack(fill=tk.X, pady=3)

            btn = tk.Button(frame,
                          text=f"{cat['name']} ({len(cat['tasks'])})",
                          bg='#3498db' if is_active else '#2c3e50',
                          fg='white', relief=tk.FLAT,
                          anchor='w', padx=10, pady=8,
                          font=('Segoe UI', 10),
                          cursor='hand2')
            btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Bind drag-and-drop events (no command - handled in release)
            btn.bind('<Button-1>', lambda e, i=idx, c=cat['id']: self.on_drag_start(e, i, c))
            btn.bind('<B1-Motion>', self.on_drag_motion)
            btn.bind('<ButtonRelease-1>', lambda e, i=idx, c=cat['id']: self.on_drag_release(e, i, c))

            del_btn = tk.Button(frame, text="×",
                              bg='#e74c3c', fg='white',
                              relief=tk.FLAT, width=3,
                              command=lambda c=cat['id']: self.delete_category(c))
            del_btn.pack(side=tk.RIGHT)
    
    def render_tasks(self):
        """Render tasks for current category with sub-tasks support"""
        # Clear existing
        for widget in self.task_frame.winfo_children():
            widget.destroy()

        category = self.get_current_category()
        if not category:
            empty = tk.Label(self.task_frame, text="No category selected",
                           bg='white', fg='#95a5a6',
                           font=('Segoe UI', 14))
            empty.pack(pady=50)
            return

        self.title_label.config(text=category['name'])

        if not category['tasks']:
            empty = tk.Label(self.task_frame,
                           text="No tasks yet\nStart typing below to add your first task!",
                           bg='white', fg='#95a5a6',
                           font=('Segoe UI', 12))
            empty.pack(pady=50)
            return

        # Render each task
        for idx, task in enumerate(category['tasks']):
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

            # Checkbox and text
            main_row = tk.Frame(content, bg='#f8f9fa')
            main_row.pack(fill=tk.X)

            var = tk.BooleanVar(value=task['completed'])
            cb = tk.Checkbutton(main_row, variable=var, bg='#f8f9fa',
                              command=lambda i=idx: self.toggle_task(i))
            cb.pack(side=tk.LEFT)

            text_style = {'font': ('Segoe UI', 11), 'cursor': 'xterm'}
            if task['completed']:
                text_style['fg'] = '#7f8c8d'
                text_style['overstrike'] = True

            # Use Text widget for selectable/copyable text
            task_text = tk.Text(main_row, height=1,
                              bg='#f8f9fa', relief=tk.FLAT,
                              wrap=tk.WORD, **text_style)
            task_text.insert('1.0', task['text'])
            task_text.config(state=tk.DISABLED)
            task_text.pack(side=tk.LEFT, fill=tk.X, expand=True)

            # Add sub-task button
            add_sub_btn = tk.Button(main_row, text="+",
                                   bg='#3498db', fg='white',
                                   relief=tk.FLAT, width=2,
                                   command=lambda i=idx: self.add_subtask_dialog(i))
            add_sub_btn.pack(side=tk.RIGHT, padx=2)

            # Sub-tasks (nested checklist items)
            if task.get('subtasks'):
                subtasks_frame = tk.Frame(content, bg='#f8f9fa')
                subtasks_frame.pack(fill=tk.X, padx=20, pady=5)

                for sub_idx, subtask in enumerate(task['subtasks']):
                    sub_row = tk.Frame(subtasks_frame, bg='#f8f9fa')
                    sub_row.pack(fill=tk.X, pady=2)

                    sub_var = tk.BooleanVar(value=subtask['completed'])
                    sub_cb = tk.Checkbutton(sub_row, variable=sub_var, bg='#f8f9fa',
                                          command=lambda i=idx, si=sub_idx: self.toggle_subtask(i, si))
                    sub_cb.pack(side=tk.LEFT)

                    sub_text_style = {'font': ('Segoe UI', 10), 'cursor': 'xterm'}
                    if subtask['completed']:
                        sub_text_style['fg'] = '#7f8c8d'
                        sub_text_style['overstrike'] = True

                    sub_text = tk.Text(sub_row, height=1,
                                     bg='#f8f9fa', relief=tk.FLAT,
                                     wrap=tk.WORD, **sub_text_style)
                    sub_text.insert('1.0', f"↳ {subtask['text']}")
                    sub_text.config(state=tk.DISABLED)
                    sub_text.pack(side=tk.LEFT, fill=tk.X, expand=True)

                    # Delete sub-task button
                    del_sub_btn = tk.Button(sub_row, text="×",
                                          bg='#e67e22', fg='white',
                                          relief=tk.FLAT, width=2,
                                          command=lambda i=idx, si=sub_idx: self.delete_subtask(i, si))
                    del_sub_btn.pack(side=tk.RIGHT)

            # Notes
            if task.get('notes'):
                notes_frame = tk.Frame(content, bg='#f8f9fa')
                notes_frame.pack(fill=tk.X, padx=20, pady=5)

                for note in task['notes']:
                    note_label = tk.Label(notes_frame, text=f"• {note}",
                                        bg='#f8f9fa', fg='#7f8c8d',
                                        font=('Segoe UI', 9),
                                        anchor='w', cursor='xterm')
                    note_label.pack(fill=tk.X)

            # Delete button
            del_btn = tk.Button(task_widget, text="×",
                              bg='#e74c3c', fg='white',
                              relief=tk.FLAT, width=3,
                              command=lambda i=idx: self.delete_task(i))
            del_btn.pack(side=tk.RIGHT, padx=5)
    
    def get_current_category(self):
        """Get the currently selected category"""
        for cat in self.data['categories']:
            if cat['id'] == self.data['current_category']:
                return cat
        return None
    
    def switch_category(self, cat_id):
        """Switch to a different category"""
        self.data['current_category'] = cat_id
        self.render_categories()
        self.render_tasks()
    
    def switch_category_by_index(self, idx):
        """Switch category by index (for Ctrl+number shortcuts)"""
        if self.data['categories'] and 0 <= idx < len(self.data['categories']):
            self.switch_category(self.data['categories'][idx]['id'])
    
    def add_category_dialog(self):
        """Show dialog to add new category"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Category")
        dialog.geometry("300x120")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Category name:").pack(pady=10)
        
        entry = tk.Entry(dialog, font=('Segoe UI', 11))
        entry.pack(pady=5, padx=20, fill=tk.X)
        entry.focus()
        
        def add():
            name = entry.get().strip()
            if not name:
                messagebox.showwarning("Invalid Input", "Category name cannot be empty!")
                return
            new_id = max([c['id'] for c in self.data['categories']], default=0) + 1
            self.data['categories'].append({
                'id': new_id,
                'name': name,
                'tasks': []
            })
            self.data['current_category'] = new_id
            self.save_data()
            self.render_categories()
            self.render_tasks()
            dialog.destroy()
        
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Add", command=add).pack(side=tk.LEFT, padx=5)

        def on_return(e):
            add()
            return 'break'

        entry.bind('<Return>', on_return)
    
    def delete_category(self, cat_id):
        """Delete a category"""
        if len(self.data['categories']) == 1:
            messagebox.showwarning("Cannot Delete", "Cannot delete the last category!")
            return
        
        if messagebox.askyesno("Delete Category", 
                              "Delete this category and all its tasks?"):
            self.data['categories'] = [c for c in self.data['categories'] 
                                      if c['id'] != cat_id]
            if self.data['current_category'] == cat_id:
                self.data['current_category'] = self.data['categories'][0]['id']
            self.save_data()
            self.render_categories()
            self.render_tasks()
    
    def add_task_from_input(self):
        """Add task from input field"""
        # Get text and explicitly strip to handle Text widget's trailing newline
        text = self.task_input.get('1.0', tk.END).strip()
        if not text:
            return

        # Split by lines and filter empty lines
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if not lines:
            return

        main_task = lines[0]
        if not main_task:
            return

        notes = lines[1:] if len(lines) > 1 else []

        category = self.get_current_category()
        if category:
            category['tasks'].append({
                'text': main_task,
                'notes': notes,
                'completed': False,
                'created': datetime.now().isoformat()
            })
            self.save_data()
            self.render_tasks()
            self.render_categories()
            self.task_input.delete('1.0', tk.END)
    
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
                self.render_categories()
    
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
            self.render_categories()
    
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
            try:
                with open(self.data_file, 'r') as f:
                    self.data = json.load(f)
# Migrate old data to ensure consistency
                self.migrate_data()
            except (json.JSONDecodeError, IOError, OSError, KeyError) as e:
                messagebox.showerror("Error Loading Data",
                                    f"Failed to load checklist data:\n{str(e)}\n\nStarting with default categories.")
                self.data = {'categories': [], 'current_category': None}
>>>>>>> main

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

    # Drag and Drop Methods
    def on_drag_start(self, event, index, cat_id):
        """Start dragging a category"""
        self.drag_data['source'] = event.widget
        self.drag_data['index'] = index
        self.drag_data['cat_id'] = cat_id
        self.drag_data['start_y'] = event.y_root
        self.drag_data['dragging'] = False

    def on_drag_motion(self, event):
        """Handle drag motion"""
        if self.drag_data['source'] and self.drag_data['start_y'] is not None:
            # If moved more than 5 pixels, consider it a drag
            if abs(event.y_root - self.drag_data['start_y']) > 5:
                self.drag_data['dragging'] = True
                self.drag_data['source'].config(cursor='fleur')

    def on_drag_release(self, event, target_index, cat_id):
        """Handle drop event to reorder categories or switch category"""
        source_index = self.drag_data['index']

        if self.drag_data['dragging'] and source_index is not None and source_index != target_index:
            # It was a drag - reorder categories
            category = self.data['categories'].pop(source_index)
            self.data['categories'].insert(target_index, category)
            self.save_data()
            self.render_categories()
        elif not self.drag_data['dragging']:
            # It was a click - switch category
            self.switch_category(cat_id)

        # Reset drag data
        if self.drag_data['source']:
            self.drag_data['source'].config(cursor='hand2')
        self.drag_data = {'source': None, 'index': None, 'start_y': None, 'dragging': False}

    # Sub-task Methods
    def add_subtask_dialog(self, task_idx):
        """Show dialog to add a sub-task"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Sub-task")
        dialog.geometry("400x120")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Sub-task:").pack(pady=10)

        entry = tk.Entry(dialog, font=('Segoe UI', 11))
        entry.pack(pady=5, padx=20, fill=tk.X)
        entry.focus()

        def add():
            text = entry.get().strip()
            if not text:
                messagebox.showwarning("Invalid Input", "Sub-task text cannot be empty!")
                return
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
                dialog.destroy()

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Add", command=add).pack(side=tk.LEFT, padx=5)

        def on_return(e):
            add()
            return 'break'

        entry.bind('<Return>', on_return)

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

    # File Management Methods
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
        if messagebox.askyesno("New Checklist", "Save current checklist before creating new?"):
            self.save_data()

        self.data_file = filename
        self.data = {'categories': [], 'current_category': None}
        self.init_default_categories()
        self.add_to_recent_files(filename)
        self.render_categories()
        self.render_tasks()
        self.root.title(f"Simple Checklist - {os.path.basename(filename)}")

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
            self.render_categories()
            self.render_tasks()
            self.root.title(f"Simple Checklist - {os.path.basename(filename)}")
            
        except (json.JSONDecodeError, IOError, OSError, ValueError) as e:
            # Restore previous state on error
            self.data = backup_data
            self.data_file = backup_file
            messagebox.showerror("Error", f"Failed to load checklist:\n{str(e)}\n\nPrevious checklist has been restored.")
            # Re-render to ensure UI matches restored state
            self.render_categories()
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
            self.root.title(f"Simple Checklist - {os.path.basename(filename)}")
            messagebox.showinfo("Saved", f"Checklist saved to:\n{filename}")

    def add_to_recent_files(self, filename):
        """Add file to recent files list"""
        if filename in self.settings['recent_files']:
            self.settings['recent_files'].remove(filename)
        self.settings['recent_files'].insert(0, filename)
        self.settings['recent_files'] = self.settings['recent_files'][:10]  # Keep only 10 recent files
        self.save_settings()
        self.update_recent_menu()

    def update_recent_menu(self):
        """Update the recent files menu"""
        self.recent_menu.delete(0, tk.END)
        if not self.settings['recent_files']:
            self.recent_menu.add_command(label="(No recent files)", state=tk.DISABLED)
        else:
            has_valid_files = False
            for filepath in self.settings['recent_files']:
                if os.path.exists(filepath):
                    has_valid_files = True
                    self.recent_menu.add_command(
                        label=os.path.basename(filepath),
                        command=lambda f=filepath: self.load_checklist_file(f)
                    )
                else:
                    # Show non-existent files as disabled with indicator
                    self.recent_menu.add_command(
                        label=f"{os.path.basename(filepath)} (missing)",
                        state=tk.DISABLED
                    )

            # Add separator and clear option if there are any files
            if self.settings['recent_files']:
                self.recent_menu.add_separator()
                self.recent_menu.add_command(
                    label="Clear Recent Files",
                    command=self.clear_recent_files
                )

    def clear_recent_files(self):
        """Clear the recent files list"""
        if messagebox.askyesno("Clear Recent Files", "Clear all recent files from the list?"):
            self.settings['recent_files'] = []
            self.save_settings()
            self.update_recent_menu()

    # Settings Methods
    def change_input_color(self):
        """Change the color of the input box"""
        color = colorchooser.askcolor(
            title="Choose Input Box Color",
            initialcolor=self.settings['input_bg_color']
        )

        if color[1]:  # color[1] is the hex color string
            self.settings['input_bg_color'] = color[1]
            self.task_input.config(bg=color[1])
            self.save_settings()

def main():
    root = tk.Tk()
    app = ChecklistApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
