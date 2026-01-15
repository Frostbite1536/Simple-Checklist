# Simple-Checklist

A lightweight, keyboard-driven task manager with categories, nested sub-tasks, and advanced features for productivity enthusiasts.

## Features

### Core Features
- **Category Management**: Organize tasks into customizable categories
- **Nested Sub-tasks**: Create sub-checklist items within any task with independent checkboxes
- **Drag-and-Drop**: Easily reorder categories by dragging them in the sidebar
- **Markdown Export**: Export all tasks with timestamps to beautifully formatted Markdown files
- **Multiple Checklist Files**: Load and manage different checklist JSON files for various projects
- **Customizable Interface**: Change the color of the text input box to match your preferences
- **Text Selection**: Easily select and copy checklist item text
- **Keyboard Shortcuts**: Navigate and manage tasks without touching the mouse

### Advanced Features
- **Undo/Redo**: Full undo/redo support (Ctrl+Z / Ctrl+Y) for all task operations
- **Search & Filter**: Real-time search across tasks, subtasks, and notes (Ctrl+F)
- **Task Sorting**: Sort tasks by priority, due date, creation date, completion status, or alphabetically
- **Smart Sort**: Intelligent sorting that prioritizes incomplete high-priority tasks with upcoming due dates
- **Task Priority**: Set priority levels (Low, Medium, High) with color-coded indicators
- **Due Dates**: Add due dates to tasks with visual overdue/upcoming warnings
- **Task Reminders**: Set time-based reminders with system notifications

### UI Features
- Clean, modern interface with category sidebar
- Visual task completion indicators
- Color-coded priority borders (Red=High, Orange=Medium, Green=Low)
- Due date indicators with overdue warnings
- Scrollable task lists
- Responsive layout

## Installation

### Requirements
- Python 3.6 or higher
- tkinter (usually comes with Python)

### Quick Start

#### Using the Cross-Platform Launcher (Recommended)
```bash
# On Linux/macOS
./launch.py

# On Windows (double-click or run)
python launch.py
```

#### Direct Launch
```bash
python simple-checklist.py
```

## Usage

### Getting Started
1. Launch the application using `launch.py` or run `simple-checklist.py` directly
2. Select or create a category from the sidebar
3. Type your task in the input box at the bottom
4. Press `Shift+Enter` to add the task

### Keyboard Shortcuts
- **Shift+Enter**: Add a new task
- **Ctrl+1-9** or **Alt+1-9**: Quickly switch between categories (1 for first category, 2 for second, etc.)
- **Ctrl+Left/Right Arrow**: Navigate to previous/next category (useful for 10+ categories)
- **Ctrl+Z**: Undo last action
- **Ctrl+Y** or **Ctrl+Shift+Z**: Redo last undone action
- **Ctrl+F**: Focus search bar
- **Enter**: Add a new line in the task input (for task notes)
- **Escape**: Clear search (when search bar is focused)

### Managing Tasks
- **Add a task**: Type in the input box and press `Shift+Enter`
- **Add sub-tasks**: Click the `+` button next to any task to add nested checklist items
- **Complete a task**: Check the checkbox next to the task
- **Edit a task**: Click the `✎` button to edit text, set priority, and add due date
- **Delete a task**: Click the `×` button on the right side of the task
- **Set a reminder**: Click the `🔔` button to set a timed reminder
- **Select/Copy text**: Click and drag to select any task or sub-task text, then copy with Ctrl+C

### Task Priority & Due Dates
- **Setting Priority**: When editing a task, choose Low (green), Medium (orange), or High (red) priority
- **Setting Due Date**: Enter a date in YYYY-MM-DD format when editing a task
- **Visual Indicators**: Tasks show colored left borders based on priority
- **Due Date Warnings**:
  - Overdue tasks show "⚠️ Overdue"
  - Tasks due today show "📌 Due Today"
  - Tasks due within 3 days show "📌 Due in Xd"

### Searching & Sorting
- **Search**: Use the search bar (Ctrl+F) to find tasks by text, subtask content, or notes
- **Sort Menu**: Use the Sort menu to organize tasks:
  - **Smart Sort** (Recommended): Incomplete first, then by priority, then by due date
  - **By Priority**: High to Low priority
  - **By Due Date**: Earliest first
  - **By Creation Date**: Oldest first
  - **Alphabetically**: A to Z
  - **By Completion Status**: Incomplete first

### Managing Categories
- **Add a category**: Click the `+ Add Category` button in the sidebar
- **Switch categories**: Click on a category name or use `Ctrl+1-9` shortcuts
- **Reorder categories**: Click and drag a category button to reorder them
- **Delete a category**: Click the `×` button next to the category name

### Working with Multiple Checklists
- **Create New**: `File → New Checklist` - Create a fresh checklist in a new JSON file
- **Open Existing**: `File → Open Checklist...` - Load a different checklist file
- **Save As**: `File → Save As...` - Save current checklist to a new file
- **Recent Files**: `File → Recent Files` - Quickly access your recent checklist files

### Exporting
- Click `📥 Export MD` to save all tasks to a Markdown file
- Exports include:
  - Timestamp of export
  - All categories and their tasks
  - Sub-tasks with proper indentation
  - Task completion status
  - Notes associated with tasks

### Customization
- **Change Input Box Color**: `Settings → Change Input Box Color`
  - Choose any color for the task input box background
  - Settings are automatically saved

### Clearing Completed Tasks
- Click `🗑️ Clear Done` to remove all completed tasks from the current category

## Data Storage

### Checklist Data
- Default location: `~/.simple_checklist.json`
- Can be saved to any location using `File → Save As...`
- Format: JSON with categories, tasks, sub-tasks, and notes

### Settings
- Location: `~/.simple_checklist_settings.json`
- Stores:
  - Input box color preference
  - Recent files list (up to 10 files)

### Data Structure
```json
{
  "categories": [
    {
      "id": 1,
      "name": "Category Name",
      "tasks": [
        {
          "text": "Main task",
          "completed": false,
          "created": "2025-12-05T10:30:00",
          "priority": "high",
          "due_date": "2025-12-10",
          "reminder": "2025-12-10T09:00:00",
          "subtasks": [
            {
              "text": "Sub-task 1",
              "completed": false
            }
          ],
          "notes": ["Additional note"]
        }
      ]
    }
  ],
  "current_category": 1
}
```

**Task Fields:**
- `text` (required): The task description
- `completed` (required): Boolean completion status
- `created` (auto): ISO timestamp of when the task was created
- `priority` (optional): "low", "medium", or "high" (default: "medium")
- `due_date` (optional): Date in YYYY-MM-DD format
- `reminder` (optional): ISO datetime for reminder notification
- `subtasks` (optional): Array of subtask objects
- `notes` (optional): Array of note strings

## Platform Support

The application works on:
- **Windows** - Full support with native UI
- **macOS** - Full support with native UI
- **Linux** - Full support with GTK/Qt themes

The `launch.py` script automatically detects your platform and launches with appropriate settings.

## Tips and Tricks

1. **Multi-line tasks**: Press `Enter` (not Shift+Enter) to add notes to your task before submitting
2. **Quick category switching**: Use `Ctrl+1` through `Ctrl+9` to instantly switch between your first 9 categories
3. **Drag categories**: Organize your categories by priority - drag them up or down in the sidebar
4. **Sub-tasks for complex items**: Break down large tasks into smaller, manageable sub-tasks
5. **Multiple checklists**: Use different JSON files for work, personal, and project-specific tasks
6. **Recent files**: Access your recent checklists quickly from the File menu
7. **Markdown export**: Export before major changes as a backup, or to share progress with others
8. **Custom colors**: Set different input colors for different types of work sessions

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is open source and available under the MIT License.

## Architecture

### Modular Design (v3.0+)

Simple Checklist features a clean, modular architecture that separates concerns and makes the codebase maintainable and extensible.

```
simple-checklist/
├── simple-checklist.py      # Main application entry point
├── launch.py                # Cross-platform launcher
├── src/
│   ├── models/              # Data models
│   │   ├── task.py          # Task and Subtask classes
│   │   ├── category.py      # Category class
│   │   └── checklist.py     # Checklist management
│   ├── persistence/         # Data persistence
│   │   ├── storage.py       # ChecklistStorage for JSON I/O
│   │   └── settings.py      # SettingsManager for user preferences
│   ├── features/            # Feature modules
│   │   ├── undo_manager.py  # Undo/Redo state management
│   │   ├── search.py        # Task search and filtering
│   │   ├── task_sorting.py  # Task sorting algorithms
│   │   ├── drag_drop.py     # Drag-and-drop manager
│   │   ├── export.py        # Markdown exporter
│   │   └── shortcuts.py     # Keyboard shortcut manager
│   ├── ui/                  # UI components (tkinter)
│   │   ├── main_window.py   # Main application window
│   │   ├── sidebar.py       # Category sidebar component
│   │   ├── task_panel.py    # Task display panel
│   │   ├── input_area.py    # Task input component
│   │   ├── search_bar.py    # Search bar component
│   │   └── dialogs.py       # Dialog windows
│   └── utils/               # Utility functions
│       └── constants.py     # Application constants
└── tests/                   # Comprehensive test suite
    ├── test_models.py
    ├── test_persistence.py
    ├── test_features.py
    └── test_ui_integration.py
```

### Architecture Benefits

- **Separation of Concerns**: UI, business logic, and data persistence are cleanly separated
- **Testability**: 121 automated tests with 100% pass rate
- **Maintainability**: Small, focused modules that are easy to understand and modify
- **Extensibility**: Easy to add new features or swap UI frameworks
- **Reusability**: Components can be used independently

### For Developers

See [DEVELOPER.md](DEVELOPER.md) for detailed documentation on:
- Module architecture and design patterns
- API documentation for each component
- Adding new features
- Running tests
- Contributing guidelines

## Testing

Simple Checklist has a comprehensive test suite with 121 automated tests:

```bash
# Run all tests
python -m unittest discover tests -v

# Run specific test file
python -m unittest tests.test_models
python -m unittest tests.test_features
python -m unittest tests.test_persistence
python -m unittest tests.test_ui_integration
```

**Test Coverage:**
- Model Layer: 20 tests
- Feature Modules: 38 tests
- Persistence Layer: 37 tests
- Integration Tests: 26 tests

All tests pass with 100% success rate (excluding 6 environment-dependent UI tests).

## Changelog

### Version 3.1 (Current)
- **Undo/Redo Support**: Full undo/redo for all task operations (Ctrl+Z / Ctrl+Y)
- **Search & Filter**: Real-time search across tasks, subtasks, and notes (Ctrl+F)
- **Task Sorting**: Multiple sort options including Smart Sort
- **Task Priority**: Low/Medium/High priority levels with visual indicators
- **Due Dates**: Add due dates with overdue/upcoming warnings
- **Task Reminders**: Time-based reminders with system notifications
- **Enhanced Navigation**: Ctrl+Arrow keys for 10+ categories, Alt+1-9 fallback shortcuts
- Updated documentation to reflect all new features

### Version 3.0
- **Major refactor to modular architecture**
- Extracted UI components into separate modules
- Added comprehensive test suite (121 tests)
- Improved code organization and maintainability
- 37% reduction in main file size
- Full backward compatibility with v2.0 data
- Enhanced documentation for developers

### Version 2.0
- Added nested sub-tasks with independent checkboxes
- Implemented drag-and-drop category reordering
- Added customizable input box colors
- Created cross-platform launcher script
- Added timestamps to Markdown exports
- Implemented multiple checklist file support with recent files menu
- Made all text selectable and copyable
- Enhanced data structure to support new features

### Version 1.0
- Initial release
- Basic task and category management
- Markdown export
- Keyboard shortcuts
- Note support
