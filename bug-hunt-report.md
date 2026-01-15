# Bug Hunt Report - Simple Checklist
**Date:** 2025-12-30
**QA Framework:** qa-prompt.md (Strict Analysis-Only Mode)

---

## Executive Summary

Conducted systematic bug hunt following strict inclusion/exclusion criteria. Analyzed all UI components, feature modules, and persistence layer for concrete, reproducible UI/UX bugs.

**Bugs Found:** 2
**Confidence:** Both HIGH

---

## Bug #1: Task Text Truncation with Long Single-Line Text

**Short Description:**
Long task text without newlines gets truncated when displayed, hiding content from user.

**Exact Location:**
`src/ui/task_panel.py:TaskPanel._render_task()` (lines 244-252)

**Trigger Condition:**
1. Create a task with 200+ characters of text without newline characters
2. Example: "This is a very long task description that contains important details about a project deliverable that needs to be completed by the end of the quarter and includes multiple requirements such as documentation updates, code reviews, stakeholder meetings..."

**Observable Failure:**
- Text widget height is calculated as: `line_count = task['text'].count('\n') + 1`
- For text with no newlines, line_count = 1
- Text widget created with `height=1` and `wrap=tk.WORD`
- Text wraps to 3-4 visual lines due to word wrapping
- Only first wrapped line is visible in the widget
- User cannot see full task text without editing the task

**Code Evidence:**
```python
# Line 244-245
line_count = task['text'].count('\n') + 1

# Line 248-252
task_text = tk.Text(main_row, height=line_count,
                  bg='#f8f9fa', relief=tk.FLAT,
                  wrap=tk.WORD, **text_style)
task_text.insert('1.0', task['text'])
task_text.config(state=tk.DISABLED)
```

**Impact:**
- Users cannot see their full task descriptions
- Critical task details are hidden
- Affects productivity and task management effectiveness
- No scrollbar or resize option to view hidden text

**Confidence Level:** **HIGH**
Deterministic failure with concrete reproduction steps. User-visible and frustrating.

---

## Bug #2: Input Text Added to Wrong Category After Category Switch

**Short Description:**
When user types task text but switches category before submitting, task is silently added to the new category instead of the original one.

**Exact Location:**
- Category switching: `simple-checklist.py:ChecklistApp.switch_category()` (lines 364-369)
- Task addition: `simple-checklist.py:ChecklistApp.add_task_from_input()` (lines 441-460)

**Trigger Condition:**
1. User selects "Work" category
2. User types "Finish quarterly report" in input box at bottom
3. User clicks "Personal" category in sidebar (or uses Ctrl+2)
4. User presses Shift+Enter to submit task
5. Task "Finish quarterly report" is added to "Personal" category, NOT "Work"

**Observable Failure:**
- No warning or indication that category changed while typing
- Input text persists across category switches
- Task silently added to currently selected category, not the category user was viewing when they started typing
- User discovers task in wrong category later, causing confusion

**Code Evidence:**
```python
# switch_category() doesn't clear or warn about input text
def switch_category(self, cat_id):
    self.data['current_category'] = cat_id
    self.sidebar.render_categories(...)
    self.render_tasks()
    # No interaction with input_area

# add_task_from_input() uses current category at time of submission
def add_task_from_input(self):
    text = self.input_area.get_text()
    category = self.get_current_category()  # Gets currently selected category
    if category:
        category['tasks'].append({...})
```

**Impact:**
- Tasks end up in wrong categories
- Users waste time searching for misplaced tasks
- Undermines trust in the application's task organization
- Particularly affects users who multitask or get interrupted
- No undo warning makes it easy to miss the error

**Confidence Level:** **HIGH**
Deterministic behavior with realistic user workflow. Breaks user mental model that tasks belong to the category they were viewing when typing started.

---

## Analysis Summary

### Bugs Excluded (Examples)

The following potential issues were examined but **excluded** per QA criteria:

- **Performance with large task counts**: No measured regression (exclusion: performance optimization)
- **Memory growth in undo stack**: Bounded at 20 states, acceptable limit (exclusion: speculative edge case)
- **Timezone handling in reminders**: Architectural limitation, not UI/UX bug (exclusion: architectural opinion)
- **Duplicate category IDs via manual JSON editing**: Outside app control (exclusion: hypothetical)
- **Input not clearing on category switch**: Same as Bug #2 but from different angle

### Stop Conditions Assessment

**Rule A (Diminishing Returns):** NOT MET
- First pass produced 2 HIGH-confidence bugs
- Continue monitoring if requested

**Rule B (Speculation Detection):** NOT MET
- No speculative triggers identified
- All bugs have concrete reproduction steps

**Rule C (Stability Confirmation):** NOT MET
- 2 qualifying bugs found, not zero

### Recommendation

**Address both bugs before next release.**

Bug #1 is a visual defect affecting data visibility.
Bug #2 is a workflow confusion causing data integrity issues (tasks in wrong categories).

Both have deterministic reproduction steps and clear user impact.

---

## Testing Methodology

- ✅ Reviewed all UI components (`src/ui/*.py`)
- ✅ Reviewed feature modules (`src/features/*.py`)
- ✅ Reviewed persistence layer (`src/persistence/*.py`)
- ✅ Reviewed main application logic (`simple-checklist.py`)
- ✅ Traced state management through undo/redo operations
- ✅ Traced search functionality across category switches
- ✅ Examined error handling and edge cases
- ✅ Verified dialog modal behavior
- ✅ Checked keyboard shortcut conflicts

**Total files analyzed:** 15+ Python files
**Lines of code reviewed:** ~3,500+
**Time spent:** Comprehensive systematic review
