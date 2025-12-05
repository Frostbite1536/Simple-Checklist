"""
Simple Checklist - Desktop Version
A lightweight, keyboard-driven task manager with categories and Markdown export
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
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
        
        self.canvas.create_window((0, 0), window=self.task_frame, anchor='nw', width=680)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Input area
        input_frame = tk.Frame(right_container, bg='#fafafa')
        input_frame.pack(fill=tk.X, padx=20, pady=15)
        
        self.task_input = tk.Text(input_frame, height=3, 
                                 font=('Segoe UI', 11),
                                 relief=tk.FLAT, bg='white',
                                 borderwidth=2)
        self.task_input.pack(fill=tk.X)
        
        hints = tk.Label(input_frame, 
                        text="💡 Shift+Enter: New task | Enter: Add note line | Ctrl+1-9: Switch categories",
                        bg='#fafafa', fg='#7f8c8d',
                        font=('Segoe UI', 9))
        hints.pack(pady=5)
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Shift+Enter to add task
        self.task_input.bind('<Shift-Return>', lambda e: self.add_task_from_input())
        
        # Ctrl+1-9 to switch categories
        for i in range(1, 10):
            self.root.bind(f'<Control-Key-{i}>', 
                          lambda e, idx=i-1: self.switch_category_by_index(idx))
    
    def render_categories(self):
        """Render the category list"""
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
                          command=lambda c=cat['id']: self.switch_category(c))
            btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            del_btn = tk.Button(frame, text="×",
                              bg='#e74c3c', fg='white',
                              relief=tk.FLAT, width=3,
                              command=lambda c=cat['id']: self.delete_category(c))
            del_btn.pack(side=tk.RIGHT)
    
    def render_tasks(self):
        """Render tasks for current category"""
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
            
            text_style = {'font': ('Segoe UI', 11)}
            if task['completed']:
                text_style['fg'] = '#7f8c8d'
                text_style['overstrike'] = True
            
            task_text = tk.Label(main_row, text=task['text'],
                               bg='#f8f9fa', anchor='w',
                               **text_style)
            task_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Notes
            if task.get('notes'):
                notes_frame = tk.Frame(content, bg='#f8f9fa')
                notes_frame.pack(fill=tk.X, padx=20, pady=5)
                
                for note in task['notes']:
                    note_label = tk.Label(notes_frame, text=f"• {note}",
                                        bg='#f8f9fa', fg='#7f8c8d',
                                        font=('Segoe UI', 9),
                                        anchor='w')
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
        if idx < len(self.data['categories']):
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
            if name:
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
        
        entry.bind('<Return>', lambda e: add())
    
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
        text = self.task_input.get('1.0', tk.END).strip()
        if not text:
            return
        
        # Split by lines
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if not lines:
            return
        
        main_task = lines[0]
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
        """Export all tasks to Markdown file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")],
            initialfile=f"checklist-{datetime.now().strftime('%Y-%m-%d')}.md"
        )
        
        if not filename:
            return
        
        markdown = ""
        for category in self.data['categories']:
            markdown += f"# {category['name']}\n\n"
            
            if not category['tasks']:
                markdown += "_No tasks_\n\n"
            else:
                for task in category['tasks']:
                    checkbox = '[x]' if task['completed'] else '[ ]'
                    markdown += f"- {checkbox} {task['text']}\n"
                    
                    if task.get('notes'):
                        for note in task['notes']:
                            markdown += f"    - {note}\n"
                
                markdown += "\n"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        messagebox.showinfo("Export Complete", 
                           f"Tasks exported to:\n{filename}")
    
    def save_data(self):
        """Save data to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def load_data(self):
        """Load data from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.data = json.load(f)
            except:
                pass

def main():
    root = tk.Tk()
    app = ChecklistApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
