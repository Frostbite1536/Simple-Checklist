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

### UI Features
- Clean, modern interface with category sidebar
- Visual task completion indicators
- Color-coded task states
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
- **Ctrl+1-9**: Quickly switch between categories (1 for first category, 2 for second, etc.)
- **Enter**: Add a new line in the task input (for task notes)

### Managing Tasks
- **Add a task**: Type in the input box and press `Shift+Enter`
- **Add sub-tasks**: Click the `+` button next to any task to add nested checklist items
- **Complete a task**: Check the checkbox next to the task
- **Delete a task**: Click the `×` button on the right side of the task
- **Select/Copy text**: Click and drag to select any task or sub-task text, then copy with Ctrl+C

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

## Changelog

### Version 2.0 (Current)
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
