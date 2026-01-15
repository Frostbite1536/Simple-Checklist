# API Reference

Quick reference for Simple Checklist modules and classes.

## Models (`src/models/`)

### Subtask

```python
from src.models.task import Subtask

# Create
subtask = Subtask(text: str, completed: bool = False)

# Methods
subtask.toggle_completion() -> None
data = subtask.to_dict() -> dict
subtask = Subtask.from_dict(data: dict) -> Subtask

# Properties
subtask.text: str
subtask.completed: bool
```

### Task

```python
from src.models.task import Task

# Create
task = Task(
    text: str,
    completed: bool = False,
    notes: list = None,
    subtasks: list = None,
    created: str = None,           # ISO format timestamp (auto-generated)
    priority: str = 'medium',      # 'low', 'medium', 'high'
    due_date: str = None,          # YYYY-MM-DD format
    reminder: str = None           # ISO datetime format
)

# Methods
task.toggle_completion() -> None
task.add_subtask(subtask: Subtask) -> None
task.remove_subtask(index: int) -> Subtask | None
task.add_note(note: str) -> None
task.get_subtask_count() -> int
task.get_completed_subtask_count() -> int
task.is_fully_completed() -> bool
data = task.to_dict() -> dict
task = Task.from_dict(data: dict) -> Task

# Properties
task.text: str
task.completed: bool
task.notes: list
task.subtasks: list
task.created: str
task.priority: str        # 'low', 'medium', or 'high'
task.due_date: str | None # YYYY-MM-DD format
task.reminder: str | None # ISO datetime format
```

### Category

```python
from src.models.category import Category

# Create
category = Category(id: int, name: str)

# Methods
category.add_task(task: Task) -> None
task = category.remove_task(index: int) -> Task | None
task = category.get_task(index: int) -> Task | None
category.get_task_count() -> int
category.get_completed_tasks() -> list[Task]
category.get_pending_tasks() -> list[Task]
category.clear_completed() -> int  # Returns count removed
category.get_completion_percentage() -> float
data = category.to_dict() -> dict
category = Category.from_dict(data: dict) -> Category

# Properties
category.id: int
category.name: str
category.tasks: list[Task]
```

### Checklist

```python
from src.models.checklist import Checklist

# Create
checklist = Checklist()

# Methods
checklist.add_category(category: Category) -> None
cat = checklist.remove_category(cat_id: int) -> Category | None
cat = checklist.get_category(cat_id: int) -> Category | None
cat = checklist.get_category_by_index(index: int) -> Category | None
cat = checklist.get_current_category() -> Category | None
checklist.set_current_category(cat_id: int) -> bool
checklist.get_category_count() -> int
checklist.get_next_category_id() -> int
checklist.reorder_categories(from_idx: int, to_idx: int) -> bool
checklist.get_total_task_count() -> int
checklist.get_total_completed_count() -> int
data = checklist.to_dict() -> dict
checklist = Checklist.from_dict(data: dict) -> Checklist

# Properties
checklist.categories: list[Category]
checklist.current_category_id: int | None
```

---

## Persistence (`src/persistence/`)

### ChecklistStorage

```python
from src.persistence.storage import ChecklistStorage

# Create
storage = ChecklistStorage(file_path: str = None)

# Methods
storage.save_checklist(checklist: Checklist) -> bool
checklist = storage.load_checklist() -> Checklist | None
storage.file_exists() -> bool
storage.set_file_path(file_path: str) -> None
storage.get_file_path() -> str
checklist = storage.create_default_checklist() -> Checklist
storage.export_to_markdown(checklist: Checklist, filename: str) -> bool
storage.backup_file(suffix: str = None) -> bool
storage.get_file_size() -> int
storage.get_last_modified() -> datetime | None
```

### SettingsManager

```python
from src.persistence.settings import SettingsManager

# Create
settings = SettingsManager(file_path: str = None)

# Methods
settings.get_input_bg_color() -> str
settings.set_input_bg_color(color: str) -> None
settings.add_recent_file(filepath: str) -> None
files = settings.get_recent_files() -> list[str]
files = settings.get_recent_files_existing() -> list[str]
settings.remove_recent_file(filepath: str) -> bool
settings.clear_recent_files() -> None
count = settings.cleanup_recent_files() -> int
value = settings.get_setting(key: str, default: any = None) -> any
settings.set_setting(key: str, value: any) -> None
all = settings.get_all_settings() -> dict
settings.reset_to_defaults() -> None
data = settings.export_settings() -> dict
settings.import_settings(data: dict) -> None
```

---

## Features (`src/features/`)

### UndoManager

```python
from src.features.undo_manager import UndoManager

# Create
undo_manager = UndoManager(max_history: int = 20)

# Methods
undo_manager.record_state(state: dict, action_description: str = "") -> None
previous = undo_manager.undo(current_state: dict) -> dict | None
redo_state = undo_manager.redo(current_state: dict) -> dict | None
undo_manager.can_undo() -> bool
undo_manager.can_redo() -> bool
undo_manager.get_undo_description() -> str | None
undo_manager.get_redo_description() -> str | None
undo_manager.clear() -> None
```

### TaskSearcher

```python
from src.features.search import TaskSearcher

# Static methods
results = TaskSearcher.search_tasks(
    categories: list,         # List of category dicts
    query: str,               # Search query
    category_id: int = None,  # Limit to specific category
    include_completed: bool = True
) -> list[dict]
# Returns: [{'category_id': int, 'category_name': str, 'task_idx': int,
#            'task': dict, 'match_type': str}, ...]

filtered = TaskSearcher.filter_by_status(
    tasks: list,
    completed: bool = None    # None=all, True=completed, False=pending
) -> list[dict]

filtered = TaskSearcher.filter_by_reminder(
    tasks: list,
    has_reminder: bool = True
) -> list[dict]
```

### TaskSorter

```python
from src.features.task_sorting import TaskSorter

# Class constant
TaskSorter.PRIORITY_ORDER  # {'high': 0, 'medium': 1, 'low': 2}

# Static methods
TaskSorter.sort_tasks(
    tasks: list,
    sort_by: str = 'created',  # 'created', 'due_date', 'priority', 'completion', 'a-z'
    reverse: bool = False
) -> list

TaskSorter.sort_smart(tasks: list) -> list
# Sorts: incomplete first, then priority (high→low), then due date (earliest first)
```

### DragDropManager

```python
from src.features.drag_drop import DragDropManager

# Create
manager = DragDropManager(
    checklist: Checklist,
    on_reorder: callable
)

# Methods
manager.start_drag(index: int) -> None
manager.end_drag(target_index: int) -> bool
manager.reset_drag() -> None
manager.is_dragging() -> bool
index = manager.get_drag_source_index() -> int | None
manager.validate_reorder(from_idx: int, to_idx: int) -> bool
preview = manager.get_reorder_preview(from_idx: int, to_idx: int) -> list[str] | None
```

### MarkdownExporter

```python
from src.features.export import MarkdownExporter

# Create
exporter = MarkdownExporter(
    checklist: Checklist,
    source_file: str = ""
)

# Methods
markdown = exporter.export_to_string(include_metadata: bool = True) -> str
exporter.export_to_file(filename: str, include_metadata: bool = True) -> bool
exporter.export_category(cat_id: int, filename: str) -> bool
exporter.export_completed_only(filename: str) -> bool
exporter.export_pending_only(filename: str) -> bool
preview = exporter.get_export_preview(max_lines: int = 20) -> str
stats = exporter.get_statistics() -> dict
```

### ShortcutManager

```python
from src.features.shortcuts import ShortcutManager

# Create
manager = ShortcutManager(root_widget: tk.Widget)

# Methods
manager.register_shortcut(
    key_sequence: str,
    callback: callable,
    description: str = ""
) -> None
manager.unregister_shortcut(
    key_sequence: str,
    callback: callable = None
) -> bool
manager.bind_all() -> None
manager.unbind_all() -> None
manager.set_root_widget(widget: tk.Widget) -> None
manager.is_registered(key_sequence: str) -> bool
count = manager.get_shortcut_count() -> int
shortcuts = manager.get_all_shortcuts() -> dict
help_text = manager.create_help_text() -> str
manager.clear_all() -> None
```

### DefaultShortcuts

```python
from src.features.shortcuts import DefaultShortcuts

# Static methods
DefaultShortcuts.register_task_shortcuts(
    manager: ShortcutManager,
    callbacks: dict
) -> None

DefaultShortcuts.register_category_shortcuts(
    manager: ShortcutManager,
    switch_category_func: callable
) -> None

DefaultShortcuts.register_all_defaults(
    manager: ShortcutManager,
    task_callbacks: dict,
    switch_category_func: callable
) -> None
```

---

## UI Components (`src/ui/`)

### MainWindow

```python
from src.ui import MainWindow

# Create
callbacks = {
    'on_new_checklist': callable,
    'on_open_checklist': callable,
    'on_save_as': callable,
    'on_exit': callable,
    'on_change_color': callable,
    'on_export_markdown': callable,
    'on_clear_completed': callable,
    'get_recent_files': callable,
    'on_load_recent_file': callable,
    'on_clear_recent_files': callable
}
window = MainWindow(root: tk.Tk, callbacks: dict)

# Methods
container = window.get_sidebar_container() -> tk.Frame
container = window.get_task_panel_container() -> tk.Frame
container = window.get_input_container() -> tk.Frame
window.update_title(title: str) -> None
window.update_window_title(filename: str) -> None
window.update_recent_menu() -> None
```

### Sidebar

```python
from src.ui import Sidebar

# Create
sidebar = Sidebar(
    parent: tk.Widget,
    on_category_click: callable,     # (cat_id: int) -> None
    on_category_delete: callable,    # (cat_id: int) -> None
    on_add_category: callable,       # () -> None
    on_category_reorder: callable    # (from_idx: int, to_idx: int) -> None
)

# Methods
sidebar.pack(**kwargs) -> None
sidebar.grid(**kwargs) -> None
sidebar.render_categories(
    categories: list[dict],
    current_category_id: int
) -> None
```

### TaskPanel

```python
from src.ui import TaskPanel

# Create
panel = TaskPanel(
    parent: tk.Widget,
    on_toggle_task: callable,        # (task_idx: int) -> None
    on_delete_task: callable,        # (task_idx: int) -> None
    on_add_subtask: callable,        # (task_idx: int) -> None
    on_toggle_subtask: callable,     # (task_idx: int, subtask_idx: int) -> None
    on_delete_subtask: callable      # (task_idx: int, subtask_idx: int) -> None
)

# Methods
panel.pack(**kwargs) -> None
panel.grid(**kwargs) -> None
panel.render_tasks(category: dict | None) -> None
```

### InputArea

```python
from src.ui import InputArea

# Create
input_area = InputArea(
    parent: tk.Widget,
    on_add_task_callback: callable,  # () -> None
    input_bg_color: str = 'white'
)

# Methods
input_area.pack(**kwargs) -> None
input_area.grid(**kwargs) -> None
text = input_area.get_text() -> str
input_area.clear() -> None
input_area.set_bg_color(color: str) -> None
input_area.focus() -> None
```

### SearchBar

```python
from src.ui import SearchBar

# Create
search_bar = SearchBar(
    parent: tk.Widget,
    on_search_callback: callable,   # (query: str) -> None
    on_clear_callback: callable     # () -> None
)

# Methods
search_bar.pack(**kwargs) -> None
query = search_bar.get_query() -> str
search_bar.clear() -> None
search_bar.is_active() -> bool
search_bar.focus() -> None
```

### AddCategoryDialog

```python
from src.ui import AddCategoryDialog

# Create (automatically shows dialog)
dialog = AddCategoryDialog(
    parent: tk.Widget,
    on_add_callback: callable  # (name: str) -> None
)
```

### EditCategoryDialog

```python
from src.ui import EditCategoryDialog

# Create (automatically shows dialog)
dialog = EditCategoryDialog(
    parent: tk.Widget,
    current_name: str,
    on_save_callback: callable  # (new_name: str) -> None
)
```

### AddSubtaskDialog

```python
from src.ui import AddSubtaskDialog

# Create (automatically shows dialog)
dialog = AddSubtaskDialog(
    parent: tk.Widget,
    on_add_callback: callable  # (text: str) -> None
)
```

### EditTaskDialog

```python
from src.ui import EditTaskDialog

# Create (automatically shows dialog)
dialog = EditTaskDialog(
    parent: tk.Widget,
    current_text: str,
    on_save_callback: callable,  # (text: str, priority: str, due_date: str|None) -> None
    current_priority: str = 'medium',  # 'low', 'medium', 'high'
    current_due_date: str = None,      # YYYY-MM-DD
    show_options: bool = True          # Show priority/due date fields
)
```

### ReminderDialog

```python
from src.ui import ReminderDialog

# Create (automatically shows dialog)
dialog = ReminderDialog(
    parent: tk.Widget,
    task_text: str,
    on_set_callback: callable,   # (reminder_iso: str) -> None
    current_reminder: str = None # ISO datetime format
)
```

---

## Data Structures

### Category Dictionary (for UI rendering)

```python
{
    'id': int,           # Unique category ID
    'name': str,         # Category name
    'tasks': list[dict]  # List of task dictionaries
}
```

### Task Dictionary (for UI rendering)

```python
{
    'text': str,                    # Task text
    'completed': bool,              # Completion status
    'notes': list[str],             # Optional notes
    'subtasks': list[dict],         # Optional subtasks
    'created': str,                 # ISO timestamp
    'priority': str,                # 'low', 'medium', 'high' (default: 'medium')
    'due_date': str | None,         # YYYY-MM-DD format
    'reminder': str | None          # ISO datetime format
}
```

### Subtask Dictionary

```python
{
    'text': str,        # Subtask text
    'completed': bool   # Completion status
}
```

---

## Common Patterns

### Loading and Saving Data

```python
from src.persistence.storage import ChecklistStorage
from src.models.checklist import Checklist

# Load
storage = ChecklistStorage('/path/to/file.json')
checklist = storage.load_checklist()

if checklist is None:
    checklist = storage.create_default_checklist()

# Modify
category = checklist.get_category(1)
from src.models.task import Task
category.add_task(Task("New task"))

# Save
storage.save_checklist(checklist)
```

### Converting Between Formats

```python
# Checklist object → Dictionary (for UI or JSON)
data = checklist.to_dict()

# Dictionary → Checklist object
checklist = Checklist.from_dict(data)

# Old format compatibility
if 'categories' in old_data:
    # Can be used directly with to_dict/from_dict
    checklist = Checklist.from_dict(old_data)
```

### Exporting to Markdown

```python
from src.features.export import MarkdownExporter

exporter = MarkdownExporter(checklist, source_file="my_list.json")

# Get markdown string
markdown = exporter.export_to_string(include_metadata=True)

# Save to file
exporter.export_to_file("export.md")

# Export only completed
exporter.export_completed_only("done.md")
```

### Managing Settings

```python
from src.persistence.settings import SettingsManager

settings = SettingsManager()

# Get/set color
color = settings.get_input_bg_color()
settings.set_input_bg_color('#FFEECC')

# Manage recent files
settings.add_recent_file('/path/to/checklist.json')
recent = settings.get_recent_files()  # Max 10, newest first
```

---

## Error Handling

### File Operations

```python
try:
    storage.save_checklist(checklist)
except (IOError, OSError) as e:
    # Handle file write error
    print(f"Failed to save: {e}")

try:
    checklist = storage.load_checklist()
except (json.JSONDecodeError, IOError, OSError) as e:
    # Handle file read error or invalid JSON
    print(f"Failed to load: {e}")
    checklist = storage.create_default_checklist()
```

### Category/Task Access

```python
# Always check for None
category = checklist.get_category(cat_id)
if category is None:
    # Category doesn't exist
    return

task = category.get_task(task_idx)
if task is None:
    # Task doesn't exist
    return
```

---

*For detailed usage examples and guides, see [DEVELOPER.md](DEVELOPER.md)*

---

*Last updated: January 2026*
*Version: 3.1*
