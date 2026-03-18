# Implementation Plan: 13 Missing Features for Simple Checklist

## Audit Summary

This plan has been audited against the actual codebase. Key corrections made:

1. **Feature 1:** Removed unnecessary `EditNoteDialog` — reuse existing `EditTaskDialog` with `title="Edit Note"` (same pattern used for subtask editing). Added specific line references.
2. **Feature 2:** Removed incorrect claim that `check_reminders()` needs an initial synchronous call — it's already called at startup (line 204). Added suggestion to move it out of `setup_shortcuts()`.
3. **Feature 3:** Removed dangerous suggestion to rename `export.py` — would break two import sites. Only the `importer.py` approach is correct.
4. **Feature 4:** Noted that the Edit menu's Undo/Redo still uses old `callbacks.get()` pattern instead of `_cb()` — should be fixed alongside.
5. **Feature 5:** Added critical caveat — drag events must bind to a dedicated drag handle, NOT the entire task frame, because task frames contain `tk.Text` (needs mouse for text selection) and `tk.Button` (needs click events).
6. **Feature 6:** Clarified filter bar placement — must be packed BEFORE the canvas inside `TaskPanel.container`.
7. **Feature 7:** Clarified that `apply_theme()` only needs to update persistent containers; per-task colors are re-applied on `refresh_ui()`. `dialogs.py` and `scrollable_mixin.py` don't need changes.
8. **Feature 8:** Distinguished the two existing backup mechanisms (crash-recovery `.backup` vs timestamped `backup_file()`). Noted `backup_file()` exists but is never called.
9. **Feature 9:** Expanded caveat — `_dirty` flag is effectively always False under current immediate-save pattern. Only clears `_dirty` on save success.
10. **Feature 10:** Added handling for recurring tasks with no `due_date`. Updated `EditTaskDialog` callback signature. Added `from_dict` clamping pattern.
11. **Feature 11:** Documented Escape key binding interaction — `SearchBar` already binds Escape locally (line 54), root-level binding won't conflict due to tkinter event ordering.
12. **Features 9+13:** Noted these are no-ops until per-operation `save_data()` calls are removed.

---

## Feature 1: Add Notes UI
**Goal:** Let users add, edit, and delete notes on tasks (data model already supports notes).

### Files to modify:
- `src/ui/task_panel.py` — Add a "📝" (add note) button to the task action button row (line 187, next to the "+" subtask button); update `_render_notes()` (line 342) to show edit/delete buttons per note
- `src/ui/dialogs.py` — Add `AddNoteDialog` (simple text input dialog, same pattern as `AddSubtaskDialog`)
- `simple-checklist.py` — Add `add_note_dialog(task_idx)`, `edit_note_dialog(task_idx, note_idx)`, `delete_note(task_idx, note_idx)` methods; wire them into `TaskPanel` callbacks
- `src/ui/__init__.py` — Export `AddNoteDialog`

### Steps:
1. Create `AddNoteDialog` in `dialogs.py` — single-line `Entry` widget, Enter to submit, same validation pattern as `AddSubtaskDialog` but simpler
2. For editing notes, reuse the existing `EditTaskDialog` with `title="Edit Note"` (same pattern used at line 542 of simple-checklist.py for editing subtasks — no need for a separate `EditNoteDialog` class)
3. Add `on_add_note`, `on_edit_note`, `on_delete_note` callback parameters to `TaskPanel.__init__` (follows existing pattern of optional callbacks like `on_edit_task=None` at line 29)
4. In `TaskPanel._render_task()`, add a "📝" button next to the existing "+" subtask button (line 188), calling `on_add_note(task_idx)`
5. In `TaskPanel._render_notes()` (line 342), add edit (✎) and delete (×) buttons next to each note label, calling `on_edit_note(task_idx, note_idx)` and `on_delete_note(task_idx, note_idx)` — mirror the subtask button pattern from `_render_subtasks()` (line 303-324)
6. In `simple-checklist.py`, implement:
   - `add_note_dialog(task_idx)` — opens `AddNoteDialog`, calls `task.add_note(text)` on submit
   - `edit_note_dialog(task_idx, note_idx)` — opens `EditTaskDialog(title="Edit Note")`, updates `task.notes[note_idx]`
   - `delete_note(task_idx, note_idx)` — confirms, pops `task.notes[note_idx]`
   - All three: `record_state()` → mutate → `save_data()` → `render_tasks()`
7. Wire callbacks into `TaskPanel` constructor in `setup_ui()` (line 139-149 of simple-checklist.py)
8. Export `AddNoteDialog` from `src/ui/__init__.py` (line 6) and import it in `simple-checklist.py` (line 21-31)
9. Add unit tests in `tests/test_models.py` for `Task.add_note()` edge cases

---

## Feature 2: Reminder Polling Robustness
**Goal:** The reminder system works but has edge cases — make it robust by adding a missed-reminder catchup and ensuring the polling loop survives errors.

### Files to modify:
- `simple-checklist.py` — Harden `check_reminders()` method

### Steps:
1. Wrap the entire `check_reminders()` body (lines 562-596) in a try/except/finally to ensure `root.after(30000, self.check_reminders)` at line 599 always executes — currently an unhandled exception (e.g., a malformed task object) in the iteration loop kills all future reminder checks permanently
2. The initial call already happens at line 204 (`self.check_reminders()` in `setup_shortcuts()`), which both checks and schedules. No additional synchronous call needed. However, verify it catches reminders that fired while the app was closed — it does, since it checks `reminder_time <= now` (line 571)
3. Add a `self._reminder_after_id` field to store the return value of `root.after()` so it can be cancelled via `root.after_cancel()` on app exit or when switching checklist files
4. Move the `self.check_reminders()` call out of `setup_shortcuts()` into the end of `__init__`, since it's not a keyboard shortcut concern — it's a background timer

---

## Feature 3: Markdown/CSV Import
**Goal:** Let users import tasks from Markdown (`.md`) or CSV (`.csv`) files.

### Files to modify:
- `src/features/importer.py` — New file (do NOT rename `export.py` — it's imported by `src/features/__init__.py` line 6 and `simple-checklist.py` line 50)
- `src/features/__init__.py` — Add `TaskImporter` to imports and `__all__`
- `src/ui/main_window.py` — Add "Import Tasks..." menu item under File
- `simple-checklist.py` — Add `import_tasks()` method, import `TaskImporter`
- `src/utils/constants.py` — Add `CSV` and `IMPORT_ALL` to `FileTypes`

### Steps:
1. Create `src/features/importer.py` with a `TaskImporter` class:
   - `import_from_markdown(file_path) -> List[Task]` — parse `- [ ] task` / `- [x] task` patterns; nested `  - [ ]` lines become subtasks; lines starting with `>` or `  •` become notes
   - `import_from_csv(file_path) -> List[Task]` — expect columns: `text`, `completed` (bool), `priority`, `due_date`; use `csv.DictReader`
2. Add `FileTypes.CSV` and `FileTypes.IMPORT_ALL` constants
3. In `MainWindow._setup_menu()`, add `file_menu.add_command(label="Import Tasks...", command=self._cb('on_import_tasks'))` between "Open Checklist..." (line 76) and "Save As..." (line 78)
4. In `simple-checklist.py`, add `import_tasks()`:
   - Open file dialog (`.md`, `.csv`, `.json`)
   - Detect format by extension
   - Parse into `List[Task]`
   - Show confirmation: "Import X tasks into category Y?"
   - `record_state()` → add tasks to current category → `save_data()` → `refresh_ui()`
5. Wire `'on_import_tasks': self.import_tasks` into the callbacks dict (line 98 of simple-checklist.py)
6. Add `from .importer import TaskImporter` to `src/features/__init__.py` and add `'TaskImporter'` to `__all__`
7. Unit tests in `tests/test_features.py`: test markdown parsing (`- [ ] task`, `- [x] done`, nested subtasks, notes), CSV parsing (valid/invalid rows), edge cases (empty files, missing columns, BOM encoding)

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
6. Add `Ctrl+A` shortcut to select all tasks (only when selection mode is active). Register via `self.shortcut_mgr.register_shortcut()` in `setup_shortcuts()`
7. Add "Select Mode" item to Edit menu in `main_window.py` (line 91, after the existing Undo/Redo items). Note: the Edit menu's Undo/Redo commands (lines 93-98) still use the old `self.callbacks.get('on_undo', lambda: None)` pattern instead of `self._cb()` — fix this inconsistency while adding the Select Mode item
8. Add `on_bulk_complete`, `on_bulk_delete`, `on_toggle_selection` callback parameters to `TaskPanel.__init__`

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
3. In `_render_task()`, add a drag handle element (e.g., a `⠿` or `≡` label on the left side, before the priority border). Bind `<Button-1>`, `<B1-Motion>`, `<ButtonRelease-1>` on the drag handle only — NOT the entire task_widget frame, because that frame contains `tk.Text` widgets (which need mouse events for text selection) and `tk.Button` widgets (which need click events). Binding on the whole frame would conflict with both.
4. Implement `_on_task_drag_start`, `_on_task_drag_motion`, `_on_task_drag_release` — mirror the sidebar's implementation (lines 203-284 of sidebar.py):
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
1. Add a `FilterBar` frame inside `TaskPanel.container`, packed BEFORE the canvas (line 67 of task_panel.py). This places the filter buttons above the scrollable task list but within the task panel component. Alternatively, it could go in the `task_panel_container` in `simple-checklist.py` (between the search bar at line 136 and the task panel at line 150), but keeping it inside `TaskPanel` is better encapsulation. Buttons: "All", "High", "Overdue", "Pending", "Done"
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
5. Add `apply_theme(theme_colors)` methods to `TaskPanel`, `Sidebar`, `InputArea`, `SearchBar`, and `MainWindow` — each updates its container/frame bg/fg colors. Note: `TaskPanel` and `Sidebar` re-create child widgets on each render via `render_tasks()`/`render_categories()`, so `apply_theme()` only needs to update the persistent container colors; per-task colors will be picked up on the next `refresh_ui()` call. `dialogs.py` doesn't need `apply_theme()` since dialogs are created fresh each time. `scrollable_mixin.py` has no colors.
6. In `simple-checklist.py`, add `toggle_theme()`:
   - Toggle `self.settings_mgr.set_theme('dark'/'light')`
   - Call `apply_theme()` on all UI components (MainWindow, Sidebar, TaskPanel, InputArea, SearchBar)
   - Re-render everything via `refresh_ui()`
7. Add "Toggle Dark Mode" command to Settings menu in `MainWindow._setup_menu()` (line 119), wired via `self._cb('on_toggle_theme')`
8. On startup in `setup_ui()`, read saved theme via `self.settings_mgr.get_theme()` and pass theme colors to all component constructors before the first `refresh_ui()` call

---

## Feature 8: Auto-Backup on Load
**Goal:** Automatically create a timestamped backup when loading/opening a checklist file.

### Files to modify:
- `simple-checklist.py` — Call `backup_file()` in `load_data()` and `load_checklist_file()`
- `src/persistence/storage.py` — Add backup rotation (keep only last N backups)

### Important context:
There are currently TWO separate backup mechanisms that must not be confused:
- **Crash-recovery backup** (line 646-652 of simple-checklist.py): copies the file to a fixed `.backup` path via `shutil.copy2()` before loading. This is a single rolling file used for corruption recovery.
- **Timestamped backup** (`storage.backup_file()` at line 117 of storage.py): creates files like `file.json.backup_20260318_120000` for version history. This method exists but is NEVER called anywhere in the app.

### Steps:
1. In `ChecklistStorage`, add `rotate_backups(max_backups=5)` method:
   - Use `glob.glob(f"{self.file_path}.backup_*")` to find timestamped backups
   - Sort by modification time (`os.path.getmtime`)
   - Delete oldest files beyond `max_backups` via `os.remove()`
2. In `load_data()` (line 640), after the existing crash-recovery copy (line 650), also call `self.storage.backup_file()` for a timestamped version-history backup, then `self.storage.rotate_backups()`. Keep both mechanisms — the crash-recovery `.backup` is a fast single-file safety net; the timestamped backups are user-facing history.
3. In `load_checklist_file()` (line 713), before switching to the new file, call `self.storage.backup_file()` on the CURRENT file so the user has a restore point
4. Add `Defaults.MAX_BACKUPS = 5` to `constants.py` (line 91, after `MAX_RECENT_FILES`)
5. Import `glob` in `storage.py`
6. Unit test: create 7 backup files with different timestamps, call `rotate_backups(5)`, verify only the 5 newest remain

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

**Important caveat:** The current app calls `save_data()` immediately after every mutation (the pattern is always `record_state()` → mutate → `save_data()` → `render_tasks()`). This means `_dirty` is set to True by `record_state()` and immediately cleared by `save_data()` in the same synchronous call chain. The dirty flag will effectively NEVER be True when `_on_close()` runs, making this feature a no-op under current behavior.

This becomes meaningful only if:
- We later add a deferred-save mode (Feature 13 could enable this)
- We remove the immediate `save_data()` calls from individual operations
- A `save_data()` call fails (returns False), in which case we should NOT clear `_dirty`

For now, implement it correctly so the infrastructure is ready, and ensure `save_data()` only clears `_dirty` on success.

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
7. In `simple-checklist.py`, modify `toggle_task()` (line 422):
   - When completing a recurring task (i.e., `task.recurrence is not None` and task is being marked complete):
     - If `task.due_date` exists: advance it by the recurrence interval (daily=+1 day, weekly=+7, monthly=+1 month via `dateutil.relativedelta` or manual month math) and keep `completed = False`
     - If `task.due_date` is None: set `due_date` to today + interval (need a starting point to recur from)
     - Show brief notification: "Recurring task reset — next due: {date}"
   - When un-completing a recurring task (toggle back): just toggle normally, no special handling
8. Update `EditTaskDialog._on_save()` (line 228 of dialogs.py): currently it passes `(new_text, priority, due_date)` — it now needs to also pass `recurrence`. Update the callback signature in `simple-checklist.py:edit_task_dialog.on_save()` (line 454) to accept the 4th parameter
9. Add `VALID_RECURRENCES = (None, 'daily', 'weekly', 'monthly')` in `task.py` alongside `VALID_PRIORITIES`. In `Task.__init__`, validate `recurrence in VALID_RECURRENCES`. In `Task.from_dict`, clamp invalid values to None (same pattern as priority clamping at line 200)
10. Add model tests for recurrence field serialization, due date advancement (with and without existing due_date), and `from_dict` clamping of invalid recurrence values

---

## Feature 11: Ctrl+F Focus for Search Bar
**Goal:** The Ctrl+F shortcut is already registered but needs polish — ensure it works from any context and provides visual feedback.

### Files to modify:
- `simple-checklist.py` — Already wired, just needs minor improvements
- `src/ui/search_bar.py` — Add visual focus indicator

### Steps:
1. In `SearchBar.focus()` (line 91 of search_bar.py), add visual feedback: briefly flash the border color (e.g., `self.search_entry.config(highlightcolor='#27ae60')`, then `self.search_entry.after(500, lambda: self.search_entry.config(highlightcolor='#3498db'))`)
2. In `SearchBar.focus()`, also select all existing search text so typing immediately replaces the query: `self.search_entry.select_range(0, tk.END)`
3. Add `Escape` key binding at the root level in `setup_shortcuts()` to clear search and return focus to input area. **Caveat:** `SearchBar` already binds Escape locally on the entry widget (line 54 of search_bar.py: `self.search_entry.bind('<Escape>', lambda e: self.clear())`). The root-level binding will NOT conflict because tkinter processes widget-level bindings before root-level ones. The local binding clears the search text; the root-level handler can additionally move focus to the input area:
   ```python
   self.shortcut_mgr.register_shortcut('<Escape>', lambda e: self._escape_handler(), "Clear search / Cancel")
   ```
4. `_escape_handler()`: if `self.search_bar.is_active()`, call `self.search_bar.clear()` and `self.input_area.focus()`; otherwise, do nothing. This is safe even when the search entry has focus, because the local Escape binding fires first (clearing the text), and then this root handler fires (moving focus)

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

**Note:** Since the app currently saves after every mutation (see Feature 9 caveat), autosave is only useful if we later add a deferred-save mode where `save_data()` calls are removed from individual operations. For now, this provides the infrastructure and the UI toggle. The dirty flag from Feature 9 integrates directly — `_autosave_tick()` only writes if `self._dirty` is True. To make Features 9 and 13 actually functional, a follow-up task would remove the per-operation `save_data()` calls and rely solely on autosave + explicit save.

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
