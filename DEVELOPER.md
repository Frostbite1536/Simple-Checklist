# Developer Documentation

Welcome to the Simple Checklist developer documentation! This guide will help you understand the architecture, contribute to the project, and extend its functionality.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Module Documentation](#module-documentation)
- [Development Setup](#development-setup)
- [Adding New Features](#adding-new-features)
- [Testing Guide](#testing-guide)
- [Code Style](#code-style)
- [Contributing](#contributing)

---

## Architecture Overview

Simple Checklist follows a **layered architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────┐
│         User Interface (UI)             │
│     (tkinter components)                │
├─────────────────────────────────────────┤
│       Application Layer                 │
│    (simple-checklist.py)                │
├─────────────────────────────────────────┤
│         Feature Modules                 │
│  (drag-drop, export, shortcuts)         │
├─────────────────────────────────────────┤
│         Business Logic                  │
│    (models: Task, Category)             │
├─────────────────────────────────────────┤
│      Persistence Layer                  │
│   (storage, settings)                   │
└─────────────────────────────────────────┘
```

### Design Principles

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Dependency Injection**: Components receive dependencies through constructors
3. **Callback Pattern**: UI components communicate with app logic via callbacks
4. **Data-Driven**: All state is stored in data structures, making testing easy
5. **Backward Compatibility**: New versions maintain compatibility with old data formats

---

## Module Documentation

### Models Layer (`src/models/`)

Defines the core data structures and business logic.

#### `task.py`

**Classes:**
- `Subtask`: Represents a nested checklist item
- `Task`: Represents a main task with optional subtasks, notes, priority, due date, and reminder

**Key Methods:**
```python
# Subtask
subtask = Subtask("Buy milk", completed=False)
subtask.toggle_completion()
data = subtask.to_dict()

# Task with all optional fields
task = Task(
    "Complete project",
    notes=["Important"],
    priority='high',           # 'low', 'medium', 'high'
    due_date='2025-12-31',     # YYYY-MM-DD format
    reminder='2025-12-30T09:00:00'  # ISO datetime
)
task.add_subtask(Subtask("Write code"))
task.toggle_completion()
count = task.get_subtask_count()
is_done = task.is_fully_completed()  # True if task and all subtasks done

# Properties
task.priority    # 'low', 'medium', or 'high' (default: 'medium')
task.due_date    # Date string or None
task.reminder    # ISO datetime string or None
task.created     # Auto-generated ISO timestamp
```

#### `category.py`

**Class:** `Category`

Manages a collection of tasks within a category.

**Key Methods:**
```python
category = Category(1, "Work")
category.add_task(Task("Task 1"))
category.remove_task(0)

# Query tasks
completed = category.get_completed_tasks()
pending = category.get_pending_tasks()
percentage = category.get_completion_percentage()

# Bulk operations
count = category.clear_completed()  # Returns number removed
```

#### `checklist.py`

**Class:** `Checklist`

Root container managing multiple categories.

**Key Methods:**
```python
checklist = Checklist()
checklist.add_category(Category(1, "Work"))
checklist.set_current_category(1)

# Get categories
current = checklist.get_current_category()
category = checklist.get_category(1)

# Reordering
checklist.reorder_categories(0, 2)  # Move first to third position

# Statistics
total_tasks = checklist.get_total_task_count()
completed = checklist.get_total_completed_count()
```

---

### Persistence Layer (`src/persistence/`)

Handles data loading, saving, and settings management.

#### `storage.py`

**Class:** `ChecklistStorage`

Manages JSON file I/O for checklist data.

**Key Methods:**
```python
storage = ChecklistStorage("/path/to/checklist.json")

# Save/Load
storage.save_checklist(checklist)
loaded = storage.load_checklist()

# File operations
exists = storage.file_exists()
size = storage.get_file_size()
last_mod = storage.get_last_modified()

# Backup
storage.backup_file("backup_20250101")

# Export
storage.export_to_markdown(checklist, "export.md")

# Create default
default = storage.create_default_checklist()
```

#### `settings.py`

**Class:** `SettingsManager`

Manages application settings and preferences.

**Key Methods:**
```python
settings = SettingsManager("/path/to/settings.json")

# Input color
settings.set_input_bg_color('#FF0000')
color = settings.get_input_bg_color()

# Recent files
settings.add_recent_file('/path/to/checklist.json')
recent = settings.get_recent_files()  # Max 10, most recent first
settings.remove_recent_file('/path/to/old.json')
settings.clear_recent_files()

# Generic settings
settings.set_setting('custom_key', 'value')
value = settings.get_setting('custom_key', default='default')

# Bulk operations
all_settings = settings.get_all_settings()
exported = settings.export_settings()
settings.import_settings(exported)
settings.reset_to_defaults()
```

---

### Feature Modules (`src/features/`)

Specialized functionality that can be used independently.

#### `undo_manager.py`

**Class:** `UndoManager`

Manages undo/redo state history for the application.

**Key Methods:**
```python
undo_manager = UndoManager(max_history=20)

# Record state before a change
undo_manager.record_state(current_data, "Add task")

# Undo/Redo operations
previous_state = undo_manager.undo(current_data)  # Returns state to restore
redo_state = undo_manager.redo(current_data)      # Returns state to redo

# Query
can_undo = undo_manager.can_undo()
can_redo = undo_manager.can_redo()
description = undo_manager.get_undo_description()

# Clear history
undo_manager.clear()
```

#### `search.py`

**Class:** `TaskSearcher`

Provides search and filtering across tasks.

**Key Methods:**
```python
# Search tasks across categories
results = TaskSearcher.search_tasks(
    categories,           # List of category dicts
    query,                # Search query string
    category_id=None,     # Optional: limit to specific category
    include_completed=True  # Include completed tasks in results
)
# Returns: [{'category_id': 1, 'category_name': 'Work', 'task_idx': 0, 'task': {...}, 'match_type': 'task'}, ...]

# Filter by status
completed_tasks = TaskSearcher.filter_by_status(tasks, completed=True)
pending_tasks = TaskSearcher.filter_by_status(tasks, completed=False)

# Filter by reminder
tasks_with_reminders = TaskSearcher.filter_by_reminder(tasks, has_reminder=True)
```

#### `task_sorting.py`

**Class:** `TaskSorter`

Provides various sorting options for tasks.

**Key Methods:**
```python
# Sort by specific criteria
TaskSorter.sort_tasks(tasks, sort_by='created', reverse=False)
# sort_by options: 'created', 'due_date', 'priority', 'completion', 'a-z'

# Smart sort (recommended)
# Sorts: incomplete first, then by priority (high→low), then by due date (earliest first)
TaskSorter.sort_smart(tasks)

# Priority order constant
TaskSorter.PRIORITY_ORDER  # {'high': 0, 'medium': 1, 'low': 2}
```

#### `drag_drop.py`

**Class:** `DragDropManager`

Manages drag-and-drop state for category reordering.

**Key Methods:**
```python
def on_reorder_callback():
    print("Categories reordered!")

manager = DragDropManager(checklist, on_reorder_callback)

# Drag flow
manager.start_drag(0)  # Start dragging category at index 0
is_dragging = manager.is_dragging()
manager.end_drag(2)  # Drop at index 2

# Preview
preview = manager.get_reorder_preview(0, 2)  # ['Cat2', 'Cat3', 'Cat1']

# Validation
valid = manager.validate_reorder(0, 2)

# Reset
manager.reset_drag()
```

#### `export.py`

**Class:** `MarkdownExporter`

Exports checklist data to Markdown format.

**Key Methods:**
```python
exporter = MarkdownExporter(checklist, source_file="/path/to/file.json")

# Export all
markdown = exporter.export_to_string(include_metadata=True)
success = exporter.export_to_file("output.md")

# Export filtered
exporter.export_category(1, "work_tasks.md")
exporter.export_completed_only("completed.md")
exporter.export_pending_only("pending.md")

# Preview
preview = exporter.get_export_preview(max_lines=10)

# Statistics
stats = exporter.get_statistics()
# Returns: {'categories': 3, 'total_tasks': 15, 'completed_tasks': 5, ...}
```

#### `shortcuts.py`

**Class:** `ShortcutManager`

Manages keyboard shortcuts with tkinter widgets.

**Key Methods:**
```python
manager = ShortcutManager(root_widget)

# Register shortcuts
def save_handler(event):
    print("Saving...")
    return 'break'  # Prevent default behavior

manager.register_shortcut('<Control-s>', save_handler, "Save")
manager.register_shortcut('<Control-o>', open_handler, "Open")

# Bind to widgets
manager.bind_all()

# Query
is_registered = manager.is_registered('<Control-s>')
count = manager.get_shortcut_count()
all_shortcuts = manager.get_all_shortcuts()  # Dict of key: description

# Help text
help_text = manager.create_help_text()  # Formatted help string

# Cleanup
manager.unregister_shortcut('<Control-s>')
manager.unbind_all()
manager.clear_all()
```

**Helper Class:** `DefaultShortcuts`

Provides common shortcut sets:

```python
# Register task shortcuts
DefaultShortcuts.register_task_shortcuts(manager, {
    'add_task': add_task_handler
})

# Register category shortcuts
DefaultShortcuts.register_category_shortcuts(manager, switch_category_func)

# Register all defaults
DefaultShortcuts.register_all_defaults(
    manager,
    task_callbacks={'add_task': add_task_handler},
    switch_category_func=switch_category_func
)
```

---

### UI Components (`src/ui/`)

Modular UI components built with tkinter.

#### `main_window.py`

**Class:** `MainWindow`

Main application window coordinator.

**Constructor:**
```python
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

main_window = MainWindow(root, callbacks)
```

**Key Methods:**
```python
# Get containers for other components
sidebar_container = main_window.get_sidebar_container()
task_panel_container = main_window.get_task_panel_container()
input_container = main_window.get_input_container()

# Update UI
main_window.update_title("Work Tasks")
main_window.update_window_title("/path/to/checklist.json")
main_window.update_recent_menu()
```

#### `sidebar.py`

**Class:** `Sidebar`

Category sidebar with drag-and-drop support.

**Constructor:**
```python
sidebar = Sidebar(
    parent_widget,
    on_category_click=self.switch_category,
    on_category_delete=self.delete_category,
    on_add_category=self.add_category_dialog,
    on_category_reorder=self.reorder_categories
)
sidebar.pack(fill=tk.BOTH, expand=True)
```

**Key Methods:**
```python
# Render categories
categories = [
    {'id': 1, 'name': 'Work', 'tasks': [...]},
    {'id': 2, 'name': 'Personal', 'tasks': [...]}
]
sidebar.render_categories(categories, current_category_id=1)
```

#### `task_panel.py`

**Class:** `TaskPanel`

Scrollable task display panel.

**Constructor:**
```python
task_panel = TaskPanel(
    parent_widget,
    on_toggle_task=self.toggle_task,
    on_delete_task=self.delete_task,
    on_add_subtask=self.add_subtask_dialog,
    on_toggle_subtask=self.toggle_subtask,
    on_delete_subtask=self.delete_subtask
)
task_panel.pack(fill=tk.BOTH, expand=True)
```

**Key Methods:**
```python
# Render tasks for a category
category = {'name': 'Work', 'tasks': [...]}
task_panel.render_tasks(category)

# Render with None shows "No category selected"
task_panel.render_tasks(None)
```

#### `input_area.py`

**Class:** `InputArea`

Task input component with keyboard shortcuts.

**Constructor:**
```python
input_area = InputArea(
    parent_widget,
    on_add_task_callback=self.add_task_from_input,
    input_bg_color='white'
)
input_area.pack(fill=tk.X, padx=20, pady=15)
```

**Key Methods:**
```python
# Get input text
text = input_area.get_text()

# Clear input
input_area.clear()

# Set background color
input_area.set_bg_color('#FFEECC')

# Set focus
input_area.focus()
```

#### `search_bar.py`

**Class:** `SearchBar`

Real-time search bar component.

**Constructor:**
```python
search_bar = SearchBar(
    parent_widget,
    on_search_callback=self.search_tasks,   # (query: str) -> None
    on_clear_callback=self.clear_search     # () -> None
)
search_bar.pack(fill=tk.X, padx=20, pady=(10, 0))
```

**Key Methods:**
```python
# Get current query
query = search_bar.get_query()

# Clear search
search_bar.clear()

# Check if search is active
if search_bar.is_active():
    print("Search in progress")

# Set focus
search_bar.focus()
```

#### `dialogs.py`

**Classes:** `AddCategoryDialog`, `AddSubtaskDialog`, `EditTaskDialog`, `EditCategoryDialog`, `ReminderDialog`

Modal dialogs for user input.

**Usage:**
```python
def on_category_added(name):
    print(f"Adding category: {name}")

dialog = AddCategoryDialog(parent_window, on_category_added)

def on_subtask_added(text):
    print(f"Adding subtask: {text}")

dialog = AddSubtaskDialog(parent_window, on_subtask_added)

# Edit task with priority and due date
def on_task_saved(new_text, priority, due_date):
    print(f"Task: {new_text}, Priority: {priority}, Due: {due_date}")

dialog = EditTaskDialog(
    parent_window, current_text, on_task_saved,
    current_priority='medium',
    current_due_date='2025-12-31',
    show_options=True  # Show priority and due date fields
)

# Set reminder
def on_reminder_set(reminder_iso):
    print(f"Reminder set for: {reminder_iso}")

dialog = ReminderDialog(parent_window, task_text, on_reminder_set, current_reminder=None)
```

---

## Development Setup

### Prerequisites

- Python 3.6 or higher
- tkinter (usually included with Python)
- Git

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/Simple-Checklist.git
cd Simple-Checklist

# Run tests to verify setup
python -m unittest discover tests -v

# Launch the application
python simple-checklist.py
```

### Project Structure

```
Simple-Checklist/
├── simple-checklist.py          # Main application
├── launch.py                    # Cross-platform launcher
├── README.md                    # User documentation
├── DEVELOPER.md                 # This file
├── PHASE6_TESTING_REPORT.md    # Testing documentation
├── src/                         # Source modules
│   ├── models/                  # Data models
│   ├── persistence/             # Data storage
│   ├── features/                # Feature modules
│   ├── ui/                      # UI components
│   └── utils/                   # Utilities
└── tests/                       # Test suite
    ├── test_models.py
    ├── test_persistence.py
    ├── test_features.py
    └── test_ui_integration.py
```

---

## Adding New Features

### Step 1: Choose the Right Layer

- **Model Layer**: Adding new data structures or business logic
- **Persistence Layer**: New storage formats or settings
- **Feature Module**: Standalone functionality (export formats, etc.)
- **UI Component**: New visual elements or interactions

### Step 2: Create the Module

Example: Adding a CSV export feature

```python
# src/features/csv_export.py

"""CSV export functionality for Simple Checklist"""

import csv
from datetime import datetime

class CSVExporter:
    """Export checklist to CSV format"""

    def __init__(self, checklist):
        self.checklist = checklist

    def export_to_file(self, filename):
        """Export all tasks to CSV file"""
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Category', 'Task', 'Completed', 'Created'])

            for category in self.checklist.categories:
                for task in category.tasks:
                    writer.writerow([
                        category.name,
                        task.text,
                        'Yes' if task.completed else 'No',
                        task.created
                    ])

        return True
```

### Step 3: Add Tests

```python
# tests/test_csv_export.py

import unittest
import tempfile
import os
from src.features.csv_export import CSVExporter
from src.models import Checklist, Category, Task

class TestCSVExporter(unittest.TestCase):
    def test_export_to_file(self):
        checklist = Checklist()
        cat = Category(1, "Work")
        cat.add_task(Task("Task 1"))
        checklist.add_category(cat)

        exporter = CSVExporter(checklist)

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        temp_file.close()

        try:
            result = exporter.export_to_file(temp_file.name)
            self.assertTrue(result)
            self.assertTrue(os.path.exists(temp_file.name))
        finally:
            os.unlink(temp_file.name)
```

### Step 4: Integrate into Application

```python
# In simple-checklist.py

from src.features.csv_export import CSVExporter

class ChecklistApp:
    def export_csv(self):
        """Export checklist to CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )

        if filename:
            # Convert old data format to Checklist object if needed
            # or use existing checklist object
            exporter = CSVExporter(self.checklist)
            if exporter.export_to_file(filename):
                messagebox.showinfo("Success", f"Exported to {filename}")
```

### Step 5: Update Documentation

- Add feature to README.md
- Document API in DEVELOPER.md
- Add to changelog

---

## Testing Guide

### Running Tests

```bash
# Run all tests
python -m unittest discover tests -v

# Run specific test file
python -m unittest tests.test_models -v

# Run specific test class
python -m unittest tests.test_models.TestTask -v

# Run specific test method
python -m unittest tests.test_models.TestTask.test_add_subtask -v
```

### Writing Tests

Follow these patterns:

#### Model Tests

```python
class TestNewModel(unittest.TestCase):
    def setUp(self):
        """Create test fixtures"""
        self.model = NewModel("test")

    def test_creation(self):
        """Test object creation"""
        self.assertEqual(self.model.name, "test")

    def test_method(self):
        """Test specific method"""
        result = self.model.do_something()
        self.assertTrue(result)
```

#### Integration Tests

```python
class TestFeatureIntegration(unittest.TestCase):
    def test_end_to_end_flow(self):
        """Test complete workflow"""
        # Create objects
        checklist = Checklist()
        storage = ChecklistStorage()

        # Perform operations
        checklist.add_category(Category(1, "Test"))
        storage.save_checklist(checklist)

        # Verify results
        loaded = storage.load_checklist()
        self.assertEqual(loaded.get_category_count(), 1)
```

### Test Coverage Goals

- **Models**: Test all public methods, edge cases, serialization
- **Persistence**: Test save/load, error handling, file operations
- **Features**: Test core functionality, error cases, integration
- **UI**: Test component APIs, callbacks, state management

---

## Code Style

### General Guidelines

- **PEP 8**: Follow Python's style guide
- **Docstrings**: Use docstrings for all classes and public methods
- **Type Hints**: Optional but encouraged for complex functions
- **Comments**: Explain "why", not "what"
- **Naming**: Use descriptive names (e.g., `calculate_completion_percentage` not `calc_pct`)

### Example Code Style

```python
"""
Module description here
Explain what this module does
"""

import tkinter as tk
from typing import List, Optional


class MyComponent:
    """
    Brief component description

    Detailed description of the component's purpose and usage.
    """

    def __init__(self, parent: tk.Widget, callback: callable):
        """
        Initialize the component

        Args:
            parent: Parent tkinter widget
            callback: Function to call on events
        """
        self.parent = parent
        self.callback = callback
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI (private method)"""
        # Implementation here
        pass

    def public_method(self, param: str) -> bool:
        """
        Public method description

        Args:
            param: Parameter description

        Returns:
            True if successful, False otherwise
        """
        # Implementation here
        return True
```

---

## Contributing

### Contribution Workflow

1. **Fork** the repository
2. **Create a branch** for your feature: `git checkout -b feature/my-feature`
3. **Write code** following the style guide
4. **Add tests** for new functionality
5. **Run tests** to ensure nothing breaks: `python -m unittest discover tests`
6. **Commit** with clear messages: `git commit -m "Add CSV export feature"`
7. **Push** to your fork: `git push origin feature/my-feature`
8. **Create a Pull Request** with description of changes

### Pull Request Guidelines

- Clear description of what the PR does
- Reference any related issues
- Ensure all tests pass
- Update documentation if adding features
- Keep PRs focused (one feature per PR)

### Code Review Process

- Maintainers will review within 1-2 weeks
- Address feedback in additional commits
- Once approved, PR will be merged
- Your contribution will be added to the changelog

---

## Advanced Topics

### Swapping UI Frameworks

The modular architecture makes it easy to swap UI frameworks:

1. Create new UI modules (e.g., `src/ui_qt/` for PyQt)
2. Implement same component APIs
3. Update imports in `simple-checklist.py`
4. Business logic remains unchanged

### Adding New Data Fields

To add new fields to tasks:

1. Update `Task` class in `src/models/task.py`
2. Add to `to_dict()` and `from_dict()` methods
3. Update `migrate_data()` in storage for compatibility
4. Add UI elements to display/edit the field
5. Update tests

### Performance Optimization

- Use generators for large datasets
- Implement lazy loading for task rendering
- Cache frequently accessed data
- Profile with cProfile for bottlenecks

### Internationalization

To add i18n support:

1. Extract all UI strings to constants
2. Create translation dictionaries
3. Add language selection setting
4. Update UI components to use translated strings

---

## Resources

- **Python Documentation**: https://docs.python.org/3/
- **tkinter Documentation**: https://docs.python.org/3/library/tkinter.html
- **PEP 8 Style Guide**: https://www.python.org/dev/peps/pep-0008/
- **unittest Documentation**: https://docs.python.org/3/library/unittest.html

---

## Getting Help

- **Issues**: Create an issue on GitHub for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact maintainers for sensitive topics

---

## License

This project is licensed under the MIT License. See LICENSE file for details.

---

*Last updated: January 2026*
*Version: 3.1*
