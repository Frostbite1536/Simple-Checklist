# Complete Refactor Plan: Unify Architecture & Enable All Features

## Goal

Refactor `ChecklistApp` to use the existing model/persistence/feature classes as its
backbone, eliminating ~1,000 lines of duplicated logic while enabling every feature
the dead code provides. Every current feature and functionality must remain working.

---

## Architecture Overview

### Current State
```
ChecklistApp (981 lines, god class)
  ├── self.data = raw dicts          # bypasses models
  ├── self.settings = raw dicts      # bypasses SettingsManager
  ├── json.dump / json.load          # bypasses ChecklistStorage
  ├── inline markdown export         # bypasses MarkdownExporter
  ├── self.root.bind(...)            # bypasses ShortcutManager
  ├── Sidebar has own drag-drop      # bypasses DragDropManager
  ├── TaskSearcher (uses dicts)      # correct, but tied to dict format
  └── TaskSorter (uses dicts)        # correct, but tied to dict format
```

### Target State
```
ChecklistApp (slim coordinator, ~500 lines)
  ├── self.checklist = Checklist     # model objects throughout
  ├── self.settings_mgr = SettingsManager
  ├── self.storage = ChecklistStorage
  ├── self.exporter = MarkdownExporter
  ├── self.shortcut_mgr = ShortcutManager
  ├── self.undo_manager = UndoManager (already used)
  ├── TaskSearcher (updated for model objects)
  └── TaskSorter (updated for model objects)

UI Components (updated to accept model objects)
  ├── Sidebar.render_categories(categories: List[Category], current_id)
  ├── TaskPanel.render_tasks(category: Optional[Category])
  ├── TaskPanel._render_task(idx, task: Task)
  └── (all other UI unchanged - callbacks remain the same)
```

---

## Refactor Phases

### Phase 1: Update Models (Low Risk)

Ensure model classes handle all data the app needs. Fix known bugs.

#### 1a. Fix list aliasing in `Task.from_dict()`

**File:** `src/models/task.py`
```python
# Line 201 — Change:
notes=data.get('notes', []),
# To:
notes=list(data.get('notes', [])),
```

Note: `Category.from_dict()` is safe — it creates new `Task` objects via a list
comprehension, so no aliasing at the category level. The bug is only in `Task`
passing the `notes` list reference from the source dict without copying.

#### 1b. `to_dict()` changes are NOT needed

After review, changing UI components to use attribute access (Phase 2) eliminates
the need for `to_dict()` to always include all fields. The only remaining consumers
of `to_dict()` are:

- **Undo/redo** (serializes for snapshot — Phase 6e): `Checklist.from_dict()` already
  handles missing fields with defaults, so the compact format works fine.
- **Persistence** (save to JSON — Phase 4a): Compact format is actually preferable
  for smaller file sizes.
- **Tests**: The existing `test_to_dict` tests verify the current conditional behavior.
  Changing it would break those tests for no benefit.

**Decision:** Keep `to_dict()` as-is. The UI layer will use attribute access directly
on model objects (Phase 2), so it never calls `to_dict()` at all.

#### 1c. Add data migration support to `Checklist.from_dict()`

**File:** `src/models/checklist.py` — The current `from_dict` trusts all data.
Add the validation logic currently in `ChecklistApp.migrate_data()` so loading
corrupt/old data through models also gets cleaned up.

---

### Phase 2: Update UI to Accept Model Objects (Medium Risk)

The UI currently accesses dict keys like `task['text']`, `cat['id']`. We need to
change these to attribute access: `task.text`, `cat.id`.

#### 2a. Update `Sidebar.render_categories()`

**File:** `src/ui/sidebar.py`

Change all dict access to attribute access:
- `cat['id']` → `cat.id`
- `cat['name']` → `cat.name`
- `len(cat['tasks'])` → `cat.get_task_count()` (or `len(cat.tasks)`)

The method signature stays the same: `render_categories(categories, current_category_id)`,
but `categories` becomes `List[Category]` instead of `List[dict]`.

#### 2b. Update `TaskPanel.render_tasks()` and `_render_task()`

**File:** `src/ui/task_panel.py`

`render_tasks()` checks `if not category:` (line 131) which correctly handles `None`
(Category objects are always truthy). Then accesses `category['tasks']` (line 138) —
change to `category.tasks`.

In `_render_task()`, change all dict access to attribute access. The file uses a mix
of direct bracket access and `.get()` with defaults:

Direct access (will crash if key missing — but attributes always exist on model):
- `task['completed']` → `task.completed` (lines 170, 186, 194, 274)
- `task['text']` → `task.text` (lines 251, 256, 268)

`.get()` access (optional fields — attributes always exist on model with defaults):
- `task.get('priority', 'medium')` → `task.priority` (line 163)
- `task.get('due_date')` → `task.due_date` (line 273)
- `task.get('reminder') is not None` → `task.reminder is not None` (line 207)
- `task.get('subtasks')` → `task.subtasks` (lines 301-302; truthy check still works — empty list is falsy)
- `task.get('notes')` → `task.notes` (lines 305-306; same truthy check)

For subtasks in `_render_subtasks()`:
- `subtask['text']` → `subtask.text`
- `subtask['completed']` → `subtask.completed`

#### 2c. Verify all dialogs still work

Dialogs accept simple values (strings, callbacks) — no changes needed. They don't
access data dicts directly.

---

### Phase 3: Update Features for Model Objects (Medium Risk)

#### 3a. Update `TaskSearcher` to work with model objects

**File:** `src/features/search.py`

Change `search_tasks()` to accept `List[Category]` instead of `List[dict]`.
The method uses a mix of direct bracket access and `.get()`:

Direct bracket access (in result dict construction):
- `cat['id']` → `cat.id` (line 48)
- `cat['name']` → `cat.name` (line 49)

`.get()` access with defaults:
- `cat.get('tasks', [])` → `cat.tasks` (line 37)
- `task.get('text', '').lower()` → `task.text.lower()` (line 46)
- `task.get('completed', False)` → `task.completed` (line 39)
- `task.get('subtasks', [])` → `task.subtasks` (line 58)
- `subtask.get('text', '').lower()` → `subtask.text.lower()` (line 59)
- `task.get('notes', [])` → `task.notes` (line 72)

Category filtering:
- `c['id'] == category_id` → `c.id == category_id` (line 32)

Search results will return `Task` objects instead of dicts:
```python
results.append({
    'category_id': cat.id,
    'category_name': cat.name,
    'task_idx': task_idx,
    'task': task,  # Now a Task object
    'match_type': 'task'
})
```

Also update `filter_by_status()` and `filter_by_reminder()`:
- `t.get('completed', False)` → `t.completed`
- `t.get('reminder')` → `t.reminder`

#### 3b. Update `TaskSorter` to work with model objects

**File:** `src/features/task_sorting.py`

Change `.get()` calls to attribute access:
- `t.get('created', '')` → `t.created or ''`
- `t.get('due_date', '9999-12-31')` → `t.due_date or '9999-12-31'`
- `t.get('priority', 'medium')` → `t.priority`
- `t.get('completed', False)` → `t.completed`
- `t.get('text', '').lower()` → `t.text.lower()`

The sort operates in-place on `category.tasks` which is a list of Task objects.

---

### Phase 4: Wire Up Persistence Layer (Medium Risk)

#### 4a. Replace inline JSON I/O with `ChecklistStorage`

**File:** `simple-checklist.py`

Replace `self.data_file` + `json.dump/load` with:
```python
self.storage = ChecklistStorage(file_path)
```

**`save_data()`** simplifies to:
```python
def save_data(self):
    if not self.storage.save_checklist(self.checklist):
        messagebox.showerror("Error Saving Data", "Failed to save checklist.")
```

**`load_data()`** keeps its extra logic that `ChecklistStorage.load_checklist()` lacks:
- Pre-load backup via `shutil.copy2` (the app currently does this at line 742)
- Backup recovery if load fails (lines 754-764)
- Messagebox warnings on corruption/recovery
- Fallback to `self.storage.create_default_checklist()`

```python
def load_data(self):
    if not self.storage.file_exists():
        return
    # Create backup before loading (existing logic)
    self.storage.backup_file("backup")
    checklist = self.storage.load_checklist()
    if checklist:
        self.checklist = checklist
    else:
        # Try recovery from backup (keep existing recovery logic)
        ...
```

Note: `ChecklistStorage.load_checklist()` internally calls `Checklist.from_dict()`,
which gains migration logic in Phase 1c. But the backup-before-load, backup-recovery,
and messagebox feedback must stay in `ChecklistApp`.

**`load_checklist_file(filename)`** keeps its validation and rollback logic:
- Validates root is dict, has 'categories' list (lines 897-903)
- Keeps backup of previous data for rollback on failure (line 889)
- This validation should move into `ChecklistStorage` or `Checklist.from_dict()`

**File path changes** (`new_checklist`, `open_checklist`, `save_checklist_as`):
Use `self.storage.set_file_path(new_path)` instead of `self.data_file = new_path`.
Access via `self.storage.get_file_path()` instead of `self.data_file`.

#### 4b. Replace inline settings with `SettingsManager`

**File:** `simple-checklist.py`

Replace `self.settings` + `self.settings_file` with:
```python
self.settings_mgr = SettingsManager()
```

- `self.settings['input_bg_color']` → `self.settings_mgr.get_input_bg_color()`
- `self.settings['recent_files']` → `self.settings_mgr.get_recent_files()`
- `save_settings()` → `self.settings_mgr.save_settings()`
- `load_settings()` → constructor handles it
- `cleanup_recent_files()` → `self.settings_mgr.cleanup_recent_files()`
- `add_to_recent_files()` → `self.settings_mgr.add_recent_file()`
- `change_input_color()` → `self.settings_mgr.set_input_bg_color()`

---

### Phase 5: Wire Up Feature Classes (Low Risk)

#### 5a. Replace inline markdown export with `MarkdownExporter`

**File:** `simple-checklist.py`

Replace the 45-line `export_markdown()` method with:
```python
def export_markdown(self):
    filename = filedialog.asksaveasfilename(...)
    if not filename:
        return
    exporter = MarkdownExporter(self.checklist, self.storage.get_file_path())
    if exporter.export_to_file(filename):
        messagebox.showinfo("Export Complete", f"Tasks exported to:\n{filename}")
    else:
        messagebox.showerror("Export Failed", "Failed to export checklist.")
```

Also remove `ChecklistStorage.export_to_markdown()` and `_generate_markdown()` since
`MarkdownExporter` is the canonical export implementation.

#### 5b. Add new export features to menu

**File:** `src/ui/main_window.py`

Add Export submenu with:
- Export All (existing)
- Export Current Category
- Export Completed Tasks Only
- Export Pending Tasks Only
- Export Preview (show in dialog before writing)

New callbacks in `ChecklistApp`:
```python
def export_current_category(self):
    ...
    exporter.export_category(self.checklist.current_category_id, filename)

def export_completed_only(self):
    ...
    exporter.export_completed_only(filename)

def export_pending_only(self):
    ...
    exporter.export_pending_only(filename)
```

#### 5c. Wire up `ShortcutManager`

**File:** `simple-checklist.py`

Replace the manual `self.root.bind(...)` calls in `setup_shortcuts()` with
`ShortcutManager`. Note: `DefaultShortcuts` only registers `add_task` (Shift+Return)
and category switching (Ctrl+1-9). All other shortcuts must be registered manually:

```python
self.shortcut_mgr = ShortcutManager(self.root)

# Undo/Redo (register both cases for cross-platform)
self.shortcut_mgr.register_shortcut('<Control-z>', lambda e: self.undo_action(), "Undo")
self.shortcut_mgr.register_shortcut('<Control-Z>', lambda e: self.undo_action(), "Undo")
self.shortcut_mgr.register_shortcut('<Control-y>', lambda e: self.redo_action(), "Redo")
self.shortcut_mgr.register_shortcut('<Control-Y>', lambda e: self.redo_action(), "Redo")
self.shortcut_mgr.register_shortcut('<Control-Shift-z>', lambda e: self.redo_action(), "Redo")
self.shortcut_mgr.register_shortcut('<Control-Shift-Z>', lambda e: self.redo_action(), "Redo")

# Search
self.shortcut_mgr.register_shortcut('<Control-f>', lambda e: self.search_bar.focus(), "Search")
self.shortcut_mgr.register_shortcut('<Control-F>', lambda e: self.search_bar.focus(), "Search")

# Category switching: Ctrl+1-9 AND Alt+1-9 (fallback for systems where Ctrl+N fails)
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
self.shortcut_mgr.register_shortcut('<Control-Up>', lambda e: self._navigate_categories(-1), "Previous category")
self.shortcut_mgr.register_shortcut('<Control-Down>', lambda e: self._navigate_categories(1), "Next category")

self.shortcut_mgr.bind_all()
```

Note: Only register descriptions for the "primary" binding of each shortcut (e.g.,
`<Control-z>` gets "Undo" but `<Control-Z>` and Alt fallbacks get no description)
so `create_help_text()` doesn't show duplicates.

Add Help > Keyboard Shortcuts menu item in `MainWindow._setup_menu()`:
```python
def show_shortcuts_help(self):
    help_text = self.shortcut_mgr.create_help_text()
    messagebox.showinfo("Keyboard Shortcuts", help_text)
```

#### 5d. Evaluate `DragDropManager`

The Sidebar's built-in drag-and-drop works well and includes UI-specific logic
(5px drag threshold, cursor changes, drop target detection based on widget positions)
that the DragDropManager doesn't have.

**Decision:** Keep the Sidebar's drag-drop implementation. Remove `DragDropManager`
from `src/features/` since it's a less capable duplicate. If needed in the future,
the Sidebar code can be extracted into a proper UI-aware drag manager.

---

### Phase 6: Refactor `ChecklistApp` (High Risk, Careful)

This is the core refactor — changing `ChecklistApp` from dict-based to model-based.

#### 6a. Change data store from dict to `Checklist`

Replace:
```python
self.data = {'categories': [], 'current_category': None}
```
With:
```python
self.checklist = Checklist()
```

#### 6b. Update all category operations

| Current (dict) | New (model) |
|---|---|
| `self.data['categories']` | `self.checklist.categories` |
| `self.data['current_category']` | `self.checklist.current_category_id` |
| `self.data['current_category'] = cat_id` | `self.checklist.current_category_id = cat_id` (direct assignment — see note below) |
| `self.get_current_category()` (manual loop) | `self.checklist.get_current_category()` |
| `max([c['id'] for c in ...]) + 1` | `self.checklist.get_next_category_id()` |
| `self.data['categories'].append({...})` | `self.checklist.add_category(Category(...))` |
| `self.data['categories'] = [c for c if ...]` | `self.checklist.remove_category(cat_id)` |
| `self.data['categories'].pop(i)` + `.insert(j)` | `self.checklist.reorder_categories(i, j)` |

**Note on `set_current_category` vs direct assignment:** `Checklist.set_current_category(cat_id)`
validates the ID exists and returns `False` if not found. The current app unconditionally sets
`self.data['current_category'] = cat_id` in `switch_category()`. Use direct assignment
(`self.checklist.current_category_id = cat_id`) in `switch_category()` to match current behavior,
since callers already guarantee valid IDs. Use `set_current_category()` only where validation
is wanted (e.g., `load_checklist_file` where data comes from external files).

#### 6c. Update all task operations

| Current (dict) | New (model) |
|---|---|
| `category['tasks'].append({...})` | `category.add_task(Task(...))` |
| `del category['tasks'][idx]` | `category.remove_task(idx)` |
| `category['tasks'][idx]['completed'] = ...` | `category.tasks[idx].toggle_completion()` |
| `category['tasks'][idx]['text'] = ...` | `category.tasks[idx].text = new_text` |
| `category['tasks'] = [t for t if not completed]` | `category.clear_completed()` |

#### 6d. Update all subtask operations

| Current (dict) | New (model) |
|---|---|
| `task['subtasks'].append({...})` | `task.add_subtask(Subtask(...))` |
| `del task['subtasks'][idx]` | `task.remove_subtask(idx)` |
| `task['subtasks'][idx]['completed'] = not ...` | `task.subtasks[idx].toggle_completion()` |
| `task['subtasks'][idx]['text'] = ...` | `task.subtasks[idx].text = new_text` |

#### 6e. Update undo/redo

Currently: `self.undo_manager.record_state(self.data)` saves the raw dict.

New approach: `self.undo_manager.record_state(self.checklist.to_dict())` serializes
to dict for the snapshot. On undo/redo, reconstruct:
```python
def undo_action(self):
    previous = self.undo_manager.undo(self.checklist.to_dict())
    if previous:
        self.checklist = Checklist.from_dict(previous)
        self.save_data()
        self.refresh_ui()
```

This preserves the existing deep-copy behavior (UndoManager already deepcopies).

#### 6f. Update search integration

Search results contain Task objects now. `_render_search_results` passes them to
`TaskPanel._render_task()` which now expects Task objects (updated in Phase 2b).

#### 6g. Update sort integration

`TaskSorter.sort_tasks(category.tasks, ...)` sorts `List[Task]` in-place — works
directly after Phase 3b.

#### 6h. Update reminder checking

```python
for category in self.checklist.categories:
    for task in category.tasks:
        if task.reminder:
            reminder_time = datetime.fromisoformat(task.reminder)
            ...
            task.reminder = None  # Clear triggered reminder
```

#### 6i. Update `init_default_categories()`

Replace dict creation with:
```python
def init_default_categories(self):
    self.checklist = self.storage.create_default_checklist()
    self.save_data()
```

#### 6j. Create `refresh_ui()` helper

Many methods repeat the same UI update pattern. Extract to:
```python
def refresh_ui(self):
    """Refresh sidebar and task panel to match current data."""
    self.sidebar.render_categories(self.checklist.categories,
                                    self.checklist.current_category_id)
    self.render_tasks()
```

---

### Phase 7: Remove Dead Code & Consolidate (Low Risk)

#### 7a. Remove `ChecklistStorage.export_to_markdown()` and `_generate_markdown()`
Replaced by `MarkdownExporter`. Also remove `test_export_to_markdown` from
`tests/test_persistence.py` (it tests the removed methods).

#### 7b. Remove `DragDropManager` class
Sidebar has its own drag-drop. Remove `src/features/drag_drop.py`.
Update `src/features/__init__.py` to remove the `DragDropManager` import.
Also remove the entire `TestDragDropManager` class from `tests/test_features.py`
(~85 lines of tests for the removed class).

#### 7c. Remove backward-compatibility aliases
**File:** `src/persistence/__init__.py` — Remove `Storage = ChecklistStorage` and
`Settings = SettingsManager`. Note: `simple-checklist.py` imports these aliases at
line 43 (`from src.persistence import Storage, Settings`). Update that import to
use the real class names, or defer this removal until Phase 6 when those imports
are rewritten anyway.

#### 7c-ii. Update `src/features/__init__.py` exports
Add `TaskSearcher`, `TaskSorter`, and `UndoManager` to the package exports so
all feature classes are accessible via `from src.features import ...`.

#### 7d. Centralize `MAX_CATEGORY_NAME_LENGTH`
Move to `src/utils/constants.py` as `UI.MAX_CATEGORY_NAME_LENGTH = 16`.
Update `src/ui/sidebar.py` and `src/ui/dialogs.py` to import from there.

#### 7e. Fix `_on_mousewheel` identical branches
**Files:** `src/ui/sidebar.py`, `src/ui/task_panel.py`

Replace:
```python
if abs(event.delta) >= 120:
    direction = -1 if event.delta > 0 else 1
else:
    direction = -1 if event.delta > 0 else 1
```
With:
```python
if abs(event.delta) >= 120:
    units = int(-event.delta / 120) * 3  # Windows: normalize 120→1 unit
else:
    units = -event.delta * 3              # macOS: delta is already ±1
self.canvas.yview_scroll(units, 'units')
```

#### 7f. Extract shared mousewheel logic

Create `src/ui/scrollable_mixin.py` (or a utility function) with the
bind/unbind/mousewheel logic used by both Sidebar and TaskPanel.

---

### Phase 8: Update Tests (Critical)

#### 8a. Update existing model/persistence/feature tests

Since `to_dict()` is NOT being changed (Phase 1b revised), existing `test_to_dict`
tests in `test_models.py` will continue passing as-is.

Tests that WILL break and need updating:
- `test_export_to_markdown` in `test_persistence.py` — removed method (Phase 7a)
- `TestDragDropManager` in `test_features.py` — removed class (Phase 7b)
- `TestMarkdownExporter` in `test_features.py` — still valid, no changes needed
- `TestShortcutManager` in `test_features.py` — still valid, no changes needed

Tests that need attention for Phase 3 changes:
- Any future tests for `TaskSearcher` and `TaskSorter` must use model objects
  (Task/Category) instead of raw dicts as input.

#### 8b. Add tests for `TaskSearcher`
Test search across categories, single category, case insensitivity, match types,
filtering by status, filtering by reminder. Use Task/Category objects as input.

#### 8c. Add tests for `TaskSorter`
Test each sort mode (created, due_date, priority, completion, a-z, smart).
Test reverse sorting. Test empty lists and missing fields.

#### 8d. Add tests for `UndoManager`
Test record_state, undo, redo, can_undo/can_redo, clear, max_history enforcement,
redo stack cleared on new action, description tracking.

#### 8e. Add integration tests for `ChecklistApp`
Test the key flows using mocked Tkinter:
- Add/delete/edit category
- Add/delete/toggle/edit task
- Add/delete/toggle subtask
- Undo/redo cycle
- Save/load cycle via ChecklistStorage
- Search and clear search
- Sort tasks
- Export via MarkdownExporter
- Reminder checking

---

### Phase 9: Use Constants Throughout (Low Risk, Optional)

Replace hardcoded values in UI files with constants from `src/utils/constants.py`:
- Colors: `'#2c3e50'` → `Colors.SIDEBAR_BG`
- Fonts: `('Segoe UI', 12, 'bold')` → `UI.FONT_SIDEBAR_TITLE`
- Strings: `"No tasks yet..."` → `Messages.NO_TASKS`
- Dimensions: `width=200` → `UI.SIDEBAR_WIDTH`

This is cosmetic but improves maintainability.

---

## New Features Enabled After Refactor

| Feature | Source | How Exposed |
|---|---|---|
| Export current category only | `MarkdownExporter.export_category()` | Export submenu |
| Export completed tasks only | `MarkdownExporter.export_completed_only()` | Export submenu |
| Export pending tasks only | `MarkdownExporter.export_pending_only()` | Export submenu |
| Export preview before write | `MarkdownExporter.get_export_preview()` | Export submenu (shows dialog) |
| Export statistics in header | `MarkdownExporter._generate_header()` | Automatic in all exports |
| Keyboard shortcuts help | `ShortcutManager.create_help_text()` | Help > Keyboard Shortcuts menu |
| Per-category completion % | `Category.get_completion_percentage()` | Sidebar display (optional) |
| Full task completion check | `Task.is_fully_completed()` | Visual indicator (optional) |
| Checklist-wide statistics | `MarkdownExporter.get_statistics()` | Status bar or info dialog (optional) |

---

## Execution Order & Risk Management

| Phase | Risk | Testable After? | Rollback Complexity |
|---|---|---|---|
| 1. Update Models | Low | Yes (existing tests) | Trivial |
| 2. Update UI for models | Medium | Yes (manual UI test) | Medium |
| 3. Update Features | Medium | Yes (unit tests) | Low |
| 4. Wire Persistence | Medium | Yes (save/load test) | Medium |
| 5. Wire Features | Low | Yes (export/shortcuts) | Low |
| 6. Refactor ChecklistApp | High | Yes (full integration) | Hard — do incrementally |
| 7. Remove Dead Code | Low | Yes (all tests) | Trivial (git revert) |
| 8. Update Tests | None | Yes (tests pass) | N/A |
| 9. Use Constants | Low | Yes (visual check) | Trivial |

**Phase 6 should be done method-by-method**, running the test suite after each change.
The recommended order within Phase 6 is:
1. Change data store (6a)
2. Update init/default categories (6i)
3. Update persistence calls (load_data → storage, save_data → storage)
4. Update category operations
5. Update task operations
6. Update subtask operations
7. Update undo/redo
8. Update search
9. Update sort
10. Update reminders
11. Update file operations (new/open/save-as)
12. Extract refresh_ui helper (6j)

---

## Files Modified Summary

| File | Changes |
|---|---|
| `src/models/task.py` | Fix notes aliasing in `from_dict()` |
| `src/models/checklist.py` | Add migration logic to `from_dict()` |
| `src/ui/sidebar.py` | Dict access → attribute access, use constant import |
| `src/ui/task_panel.py` | Dict access → attribute access, fix mousewheel |
| `src/ui/main_window.py` | Add Export submenu, Help menu |
| `src/ui/dialogs.py` | Use constant import |
| `src/features/search.py` | Dict access → attribute access on Task/Category |
| `src/features/task_sorting.py` | Dict access → attribute access on Task |
| `src/features/shortcuts.py` | No changes (already correct) |
| `src/features/export.py` | No changes (already works with model objects) |
| `src/features/undo_manager.py` | No changes (already correct) |
| `src/features/__init__.py` | Remove DragDropManager, add TaskSearcher/TaskSorter/UndoManager |
| `src/persistence/storage.py` | Remove `export_to_markdown`, `_generate_markdown` |
| `src/persistence/__init__.py` | Remove backward-compat aliases (after Phase 6 import update) |
| `src/utils/constants.py` | Add `MAX_CATEGORY_NAME_LENGTH` |
| `simple-checklist.py` | Major refactor — model-based architecture |
| `tests/test_models.py` | No changes needed (`to_dict` behavior unchanged) |
| `tests/test_features.py` | Remove DragDropManager tests, add UndoManager/Searcher/Sorter tests |
| `tests/test_persistence.py` | Remove `test_export_to_markdown` |
| `tests/test_ui_integration.py` | Add ChecklistApp integration tests |

## Files Removed

| File | Reason |
|---|---|
| `src/features/drag_drop.py` | Sidebar has its own superior implementation |
