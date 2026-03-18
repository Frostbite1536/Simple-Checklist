# Implementation Plan: 13 Missing Features for Simple Checklist

## Feature 1: Add Notes UI
**Goal:** Let users add, edit, and delete notes on tasks (data model already supports notes).

### Files to modify:
- `src/ui/task_panel.py` — Add a "📝" (add note) button to the task action button row; update `_render_notes()` to show edit/delete buttons per note
- `src/ui/dialogs.py` — Add `AddNoteDialog` (simple text input dialog, same pattern as `AddSubtaskDialog`) and `EditNoteDialog`
- `simple-checklist.py` — Add `add_note_dialog(task_idx)`, `edit_note_dialog(task_idx, note_idx)`, `delete_note(task_idx, note_idx)` methods; wire them into `TaskPanel` callbacks
- `src/ui/__init__.py` — Export new dialog classes

### Steps:
1. Create `AddNoteDialog` in `dialogs.py` — single-line `Entry` widget, Enter to submit, same validation pattern as `AddSubtaskDialog` but simpler
2. Create `EditNoteDialog` in `dialogs.py` — pre-fills with current note text, Enter to save
3. Add `on_add_note`, `on_edit_note`, `on_delete_note` callback parameters to `TaskPanel.__init__`
4. In `TaskPanel._render_task()`, add a "📝" button next to the existing "+" subtask button, calling `on_add_note(task_idx)`
5. In `TaskPanel._render_notes()`, add edit (✎) and delete (×) buttons next to each note, calling `on_edit_note(task_idx, note_idx)` and `on_delete_note(task_idx, note_idx)`
6. In `simple-checklist.py`, implement:
   - `add_note_dialog(task_idx)` — opens `AddNoteDialog`, calls `task.add_note(text)` on submit
   - `edit_note_dialog(task_idx, note_idx)` — opens `EditNoteDialog`, updates `task.notes[note_idx]`
   - `delete_note(task_idx, note_idx)` — confirms, pops `task.notes[note_idx]`
   - All three: `record_state()` → mutate → `save_data()` → `render_tasks()`
7. Wire callbacks into `TaskPanel` constructor in `setup_ui()`
8. Add unit tests in `tests/test_models.py` for `Task.add_note()` edge cases

---

## Feature 2: Reminder Polling Robustness
**Goal:** The reminder system works but has edge cases — make it robust by adding a missed-reminder catchup and ensuring the polling loop survives errors.

### Files to modify:
- `simple-checklist.py` — Harden `check_reminders()` method

### Steps:
1. Wrap the entire `check_reminders()` body in a try/except to ensure `root.after(30000, self.check_reminders)` always executes — currently an unhandled exception in the loop kills all future reminder checks
2. After loading data (`load_data()`), immediately call `check_reminders()` once synchronously before scheduling the loop — catches reminders that fired while the app was closed
3. Add a `self._reminder_after_id` field to track the `after()` return value so it can be cancelled on app exit if needed

---

## Feature 3: Markdown/CSV Import
**Goal:** Let users import tasks from Markdown (`.md`) or CSV (`.csv`) files.

### Files to modify:
- `src/features/export.py` → rename to `src/features/import_export.py` (or create `src/features/importer.py` alongside)
- `src/ui/main_window.py` — Add "Import" menu item under File
- `simple-checklist.py` — Add `import_tasks()` method
- `src/utils/constants.py` — Add `CSV` to `FileTypes`

### Steps:
1. Create `src/features/importer.py` with a `TaskImporter` class:
   - `import_from_markdown(file_path) -> List[Task]` — parse `- [ ] task` / `- [x] task` patterns; nested `  - [ ]` lines become subtasks; lines starting with `>` or `  •` become notes
   - `import_from_csv(file_path) -> List[Task]` — expect columns: `text`, `completed` (bool), `priority`, `due_date`; use `csv.DictReader`
2. Add `FileTypes.CSV` and `FileTypes.IMPORT_ALL` constants
3. In `MainWindow._setup_menu()`, add `file_menu.add_command(label="Import Tasks...", command=self._cb('on_import_tasks'))` between "Open" and "Save As"
4. In `simple-checklist.py`, add `import_tasks()`:
   - Open file dialog (`.md`, `.csv`, `.json`)
   - Detect format by extension
   - Parse into `List[Task]`
   - Show confirmation: "Import X tasks into category Y?"
   - `record_state()` → add tasks to current category → `save_data()` → `refresh_ui()`
5. Wire `'on_import_tasks': self.import_tasks` into the callbacks dict
6. Add `src/features/__init__.py` export
7. Unit tests in `tests/test_features.py`: test markdown parsing, CSV parsing, edge cases (empty files, malformed lines)

---

## Feature 4: Bulk Operations
**Goal:** Select multiple tasks and bulk delete/complete/uncomplete them.

### Files to modify:
- `src/ui/task_panel.py` — Add selection checkboxes and bulk action bar
- `simple-checklist.py` — Add bulk operation methods
- `src/ui/main_window.py` — Add Edit menu items for Select All / Deselect All

### Steps:
1. Add a `self.selection_mode` boolean and `self.selected_tasks: Set[int]` to `TaskPanel`
2. Add `toggle_selection_mode()` method that re-renders tasks with selection checkboxes (separate from completion checkboxes)
3. When selection mode is active, render a floating action bar at the top of the task panel with buttons: "Complete Selected", "Delete Selected", "Deselect All", "Cancel"
4. In `_render_task()`, when `self.selection_mode` is True, add a selection checkbox before the completion checkbox
5. In `simple-checklist.py`, add:
   - `bulk_complete(indices: List[int])` — `record_state()` → toggle each → `save_data()` → `refresh_ui()`
   - `bulk_delete(indices: List[int])` — confirm → `record_state()` → remove in reverse order → `save_data()` → `refresh_ui()`
   - `toggle_selection_mode()` — toggle panel mode
6. Add `Ctrl+A` shortcut to select all tasks (only when selection mode is active)
7. Add "Select Mode" item to Edit menu in `main_window.py`
8. Add `on_bulk_complete`, `on_bulk_delete` callback parameters to `TaskPanel`

---

## Feature 5: Task Drag-and-Drop Reordering
**Goal:** Let users reorder tasks within a category via drag-and-drop (same pattern as category drag-and-drop in sidebar).

### Files to modify:
- `src/ui/task_panel.py` — Add drag-and-drop handlers to task widgets
- `simple-checklist.py` — Add `reorder_tasks(from_idx, to_idx)` method

### Steps:
1. Add `self.on_reorder_task` callback parameter to `TaskPanel.__init__`
2. Add drag state tracking dict (same pattern as `Sidebar.drag_data`):
   ```python
   self.drag_data = {'source': None, 'index': None, 'start_y': None, 'dragging': False}
   ```
3. In `_render_task()`, bind `<Button-1>`, `<B1-Motion>`, `<ButtonRelease-1>` on the task_widget frame (the outermost frame per task)
4. Implement `_on_task_drag_start`, `_on_task_drag_motion`, `_on_task_drag_release` — mirror the sidebar's implementation:
   - Start: record source index and start_y
   - Motion: set dragging=True after 5px threshold, change cursor to `fleur`
   - Release: if dragging, find target index via y-position scan of task widgets; call `on_reorder_task(from_idx, to_idx)`
5. Store rendered task widget references in `self.task_widgets: List[dict]` for drop target detection
6. In `simple-checklist.py`, add `reorder_tasks(from_idx, to_idx)`:
   - `record_state("Reorder tasks")`
   - `category.tasks.insert(to_idx, category.tasks.pop(from_idx))`
   - `save_data()` → `render_tasks()`
7. Wire `on_reorder_task=self.reorder_tasks` into `TaskPanel` constructor

---

## Feature 6: Quick Filter Buttons
**Goal:** Add filter buttons (All / High Priority / Overdue / Completed) above the task list.

### Files to modify:
- `src/ui/task_panel.py` — Add filter bar above task list
- `simple-checklist.py` — Add filter state and rendering logic

### Steps:
1. Add a `FilterBar` section at the top of `TaskPanel.container` — a horizontal `Frame` with toggle buttons: "All", "High", "Overdue", "Pending", "Done"
2. Add `self.active_filter: str = 'all'` to `TaskPanel`
3. Add `on_filter_change` callback to `TaskPanel.__init__`
4. When a filter button is clicked, update `self.active_filter` and call `on_filter_change(filter_name)`
5. Highlight the active filter button (use `BTN_PRIMARY` color)
6. In `simple-checklist.py`, add `filter_tasks(filter_name)`:
   - Get current category tasks
   - Apply filter: `'high'` → `priority == 'high'`; `'overdue'` → `due_date < today`; `'pending'` → `not completed`; `'done'` → `completed`
   - Render only matching tasks (use `task_panel._render_task()` directly, similar to search rendering)
7. Store `self.active_filter` on the app to persist across category switches
8. When filter is active, show indicator in header title (e.g., "Work [High Priority]")

---

## Feature 7: Dark Mode / Theme Switching
**Goal:** Full app dark mode toggled from Settings menu.

### Files to modify:
- `src/utils/constants.py` — Add `DarkColors` class alongside existing `Colors`
- `src/persistence/settings.py` — Add `theme` setting
- `src/ui/main_window.py` — Add "Toggle Dark Mode" to Settings menu
- `src/ui/task_panel.py` — Accept theme colors
- `src/ui/sidebar.py` — Accept theme colors
- `src/ui/input_area.py` — Accept theme colors
- `src/ui/search_bar.py` — Accept theme colors
- `simple-checklist.py` — Add `toggle_theme()` method, pass theme to all components

### Steps:
1. Define `DarkColors` in `constants.py`:
   ```python
   SIDEBAR_BG = '#1a1a2e'
   SIDEBAR_ACTIVE = '#16213e'
   CONTENT_BG = '#0f3460'
   TASK_BG = '#1a1a2e'
   # ... etc
   ```
2. Add `ThemeManager` helper in `constants.py` that returns the right color set based on theme name
3. Add `'theme': 'light'` to `SettingsManager._get_default_settings()`
4. Add `get_theme()` / `set_theme()` methods to `SettingsManager`
5. Add `apply_theme(theme_colors)` methods to `TaskPanel`, `Sidebar`, `InputArea`, `SearchBar` — each updates its widget bg/fg colors
6. In `simple-checklist.py`, add `toggle_theme()`:
   - Toggle `self.settings_mgr.set_theme('dark'/'light')`
   - Call `apply_theme()` on all UI components
   - Re-render everything via `refresh_ui()`
7. Add "Toggle Dark Mode" command to Settings menu in `MainWindow._setup_menu()`, wired via `self._cb('on_toggle_theme')`
8. On startup, apply saved theme before rendering

---

## Feature 8: Auto-Backup on Load
**Goal:** Automatically create a timestamped backup when loading/opening a checklist file.

### Files to modify:
- `simple-checklist.py` — Call `backup_file()` in `load_data()` and `load_checklist_file()`
- `src/persistence/storage.py` — Add backup rotation (keep only last N backups)

### Steps:
1. In `ChecklistStorage`, add `rotate_backups(max_backups=5)` method:
   - Glob for `{file_path}.backup_*` files
   - Sort by modification time
   - Delete oldest files beyond `max_backups`
2. In `load_data()` (line 640), after the existing backup copy, call `self.storage.backup_file()` for a timestamped backup and `self.storage.rotate_backups()`
3. In `load_checklist_file()`, before switching files, call `self.storage.backup_file()` on the current file
4. Add constants: `Defaults.MAX_BACKUPS = 5`
5. Unit test: create multiple backup files, verify rotation keeps only 5

---

## Feature 9: Unsaved Changes Warning
**Goal:** Track dirty state and warn before discarding unsaved changes (close, new, open).

### Files to modify:
- `simple-checklist.py` — Add dirty flag, hook into `WM_DELETE_WINDOW`, check before new/open

### Steps:
1. Add `self._dirty = False` flag to `ChecklistApp.__init__`
2. In `save_data()`, set `self._dirty = False` after successful save
3. In `record_state()`, set `self._dirty = True`
4. Add `_on_close()` method:
   - If `self._dirty`: show "You have unsaved changes. Save before closing?" (Yes/No/Cancel)
     - Yes → save_data() → quit
     - No → quit
     - Cancel → return (don't close)
   - Else: quit
5. Bind `self.root.protocol("WM_DELETE_WINDOW", self._on_close)` in `__init__`
6. In `new_checklist()` and `open_checklist()`, check `self._dirty` before proceeding — show same dialog
7. Update window title to show `*` indicator when dirty: `self.root.title(f"{'*' if self._dirty else ''}Simple Checklist - ...")`

**Note:** The current app saves immediately after every change, so `_dirty` will almost always be False. This feature becomes meaningful once we have operations that don't auto-save, or if we make auto-save optional in the future.

---

## Feature 10: Recurring Tasks
**Goal:** Mark tasks as recurring (daily/weekly/monthly) so they auto-reset when completed.

### Files to modify:
- `src/models/task.py` — Add `recurrence` field
- `src/ui/dialogs.py` — Add recurrence selector to `EditTaskDialog`
- `src/ui/task_panel.py` — Show recurrence indicator
- `simple-checklist.py` — Handle recurrence on task completion

### Steps:
1. Add `recurrence: Optional[str] = None` to `Task.__init__` — values: `None`, `'daily'`, `'weekly'`, `'monthly'`
2. Add `VALID_RECURRENCES` constant and validation (same pattern as `VALID_PRIORITIES`)
3. Update `Task.to_dict()` / `Task.from_dict()` to serialize/deserialize `recurrence`
4. In `EditTaskDialog`, when `show_options=True`, add a recurrence dropdown below priority:
   - Options: None, Daily, Weekly, Monthly
   - Use `tk.OptionMenu` or radiobuttons
5. Update `EditTaskDialog._on_save()` to pass `recurrence` value
6. In `TaskPanel._render_task()`, show a recurrence icon (🔄) next to due date when `task.recurrence` is set
7. In `simple-checklist.py`, modify `toggle_task()`:
   - When completing a recurring task: instead of just toggling, reset `completed = False`, advance `due_date` by recurrence interval, keep the task
   - Show brief notification: "Recurring task reset — next due: {date}"
8. Add model tests for recurrence field serialization and due date advancement
9. Add `recurrence` to `from_dict` with safe fallback to None for existing data

---

## Feature 11: Ctrl+F Focus for Search Bar
**Goal:** The Ctrl+F shortcut is already registered but needs polish — ensure it works from any context and provides visual feedback.

### Files to modify:
- `simple-checklist.py` — Already wired, just needs minor improvements
- `src/ui/search_bar.py` — Add visual focus indicator

### Steps:
1. In `SearchBar.focus()`, add visual feedback: briefly flash the border color (e.g., set `highlightcolor` to green for 500ms, then back to blue)
2. In `setup_shortcuts()`, update the Ctrl+F handler to also select all existing search text when focusing (so typing immediately replaces the query)
3. Add `Escape` key binding at the root level to clear search and return focus to input area:
   ```python
   self.shortcut_mgr.register_shortcut('<Escape>', lambda e: self._escape_handler(), "Clear search / Cancel")
   ```
4. `_escape_handler()`: if search is active, clear it and focus input; otherwise, do nothing

---

## Feature 12: Help / About Dialog
**Goal:** Show keyboard shortcuts and app info in a dialog.

### Files to modify:
- `src/ui/dialogs.py` — Add `HelpDialog` class
- `src/ui/main_window.py` — Add Help menu
- `simple-checklist.py` — Wire help callback

### Steps:
1. Create `HelpDialog` in `dialogs.py`:
   - Modal `Toplevel`, ~500x400
   - Title: "Simple Checklist — Help"
   - Content: scrollable `Text` widget (read-only) populated from `ShortcutManager.create_help_text()`
   - Additional sections: "About", version info, link to repo
2. In `MainWindow._setup_menu()`, add a "Help" menu with "Keyboard Shortcuts..." and "About" commands
3. In `simple-checklist.py`, add `show_help_dialog()`:
   - Create help text from `self.shortcut_mgr.create_help_text()`
   - Open `HelpDialog` with the text
4. Wire `'on_show_help': self.show_help_dialog` into callbacks
5. Register `F1` shortcut to open help dialog

---

## Feature 13: Autosave
**Goal:** Optionally auto-save on a timer instead of only saving immediately after every change.

### Files to modify:
- `src/persistence/settings.py` — Add `autosave_interval` setting
- `simple-checklist.py` — Add autosave timer loop
- `src/ui/main_window.py` — Add "Autosave" toggle to Settings menu

### Steps:
1. Add `'autosave_enabled': True` and `'autosave_interval_seconds': 30` to default settings
2. In `simple-checklist.py`, add `_start_autosave()`:
   - If enabled, schedule `root.after(interval * 1000, self._autosave_tick)`
   - `_autosave_tick()`: if `self._dirty`, call `save_data()`; reschedule
3. Add `toggle_autosave()` method to toggle the setting and restart/stop the timer
4. In Settings menu, add checkbutton: "Autosave" with a checkmark when enabled
5. Store `self._autosave_after_id` to cancel on toggle

**Note:** Since the app currently saves after every mutation, autosave is only useful if we later add a "batch mode" or deferred-save option. For now, this provides the infrastructure and the UI toggle. The dirty flag from Feature 9 integrates directly — autosave only writes if dirty.

---

## Implementation Order (recommended)

Implement in dependency order, easiest wins first:

1. **Feature 11** (Ctrl+F polish) — Trivial, 15min
2. **Feature 12** (Help dialog) — Small, standalone, 30min
3. **Feature 1** (Notes UI) — Medium, fills an obvious gap, 1hr
4. **Feature 2** (Reminder robustness) — Small, important for reliability, 20min
5. **Feature 9** (Unsaved changes warning) — Small, important UX, 30min
6. **Feature 8** (Auto-backup rotation) — Small, uses existing code, 30min
7. **Feature 5** (Task drag-and-drop) — Medium, mirrors existing sidebar code, 1hr
8. **Feature 6** (Quick filters) — Medium, useful UX addition, 1hr
9. **Feature 3** (Import) — Medium, new module, 1.5hr
10. **Feature 4** (Bulk operations) — Medium-large, new UI pattern, 1.5hr
11. **Feature 10** (Recurring tasks) — Medium, model + UI + logic changes, 1.5hr
12. **Feature 13** (Autosave) — Small, but depends on Feature 9 (dirty flag), 30min
13. **Feature 7** (Dark mode) — Large, touches every UI file, 2hr

## Testing Strategy

Each feature gets tests added to the appropriate test file:
- Model changes → `tests/test_models.py`
- Feature modules (importer, sorter, etc.) → `tests/test_features.py`
- Integration/wiring → `tests/test_ui_integration.py`

All tests must pass (`python -m unittest discover -s tests`) before committing each feature.
