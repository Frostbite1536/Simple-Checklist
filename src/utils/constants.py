"""
Constants and configuration for Simple Checklist
Centralized location for all application constants
"""

import os


class Colors:
    """UI color scheme"""
    # Sidebar
    SIDEBAR_BG = '#2c3e50'
    SIDEBAR_ACTIVE = '#3498db'
    SIDEBAR_TEXT = 'white'

    # Main content
    CONTENT_BG = 'white'
    CONTENT_TEXT = '#2c3e50'

    # Tasks
    TASK_BG = '#f8f9fa'
    TASK_BORDER_ACTIVE = '#3498db'
    TASK_BORDER_COMPLETED = '#95a5a6'
    TASK_COMPLETED_TEXT = '#7f8c8d'

    # Buttons
    BTN_PRIMARY = '#3498db'
    BTN_SUCCESS = '#27ae60'
    BTN_DANGER = '#e74c3c'
    BTN_WARNING = '#e67e22'
    BTN_TEXT = 'white'

    # Other
    SEPARATOR = '#e0e0e0'
    HINT_TEXT = '#7f8c8d'
    EMPTY_TEXT = '#95a5a6'
    INPUT_AREA_BG = '#fafafa'
    DEFAULT_INPUT_BG = 'white'


class DarkColors:
    """Dark theme color scheme"""
    SIDEBAR_BG = '#1a1a2e'
    SIDEBAR_ACTIVE = '#16213e'
    SIDEBAR_TEXT = '#e0e0e0'

    CONTENT_BG = '#0f3460'
    CONTENT_TEXT = '#e0e0e0'

    TASK_BG = '#16213e'
    TASK_BORDER_ACTIVE = '#e94560'
    TASK_BORDER_COMPLETED = '#555555'
    TASK_COMPLETED_TEXT = '#888888'

    BTN_PRIMARY = '#e94560'
    BTN_SUCCESS = '#0a8754'
    BTN_DANGER = '#c0392b'
    BTN_WARNING = '#d35400'
    BTN_TEXT = 'white'

    SEPARATOR = '#333333'
    HINT_TEXT = '#999999'
    EMPTY_TEXT = '#777777'
    INPUT_AREA_BG = '#1a1a2e'
    DEFAULT_INPUT_BG = '#16213e'


class ThemeManager:
    """Returns the correct color set for a theme"""
    @staticmethod
    def get_colors(theme='light'):
        if theme == 'dark':
            return DarkColors
        return Colors


class UI:
    """UI dimensions and fonts"""
    # Window
    WINDOW_WIDTH = 900
    WINDOW_HEIGHT = 600
    WINDOW_TITLE = "Simple Checklist"

    # Sidebar
    SIDEBAR_WIDTH = 200

    # Fonts
    FONT_FAMILY = 'Segoe UI'
    FONT_TITLE = (FONT_FAMILY, 16, 'bold')
    FONT_SIDEBAR_TITLE = (FONT_FAMILY, 12, 'bold')
    FONT_CATEGORY = (FONT_FAMILY, 10)
    FONT_TASK = (FONT_FAMILY, 11)
    FONT_SUBTASK = (FONT_FAMILY, 10)
    FONT_NOTE = (FONT_FAMILY, 9)
    FONT_HINT = (FONT_FAMILY, 9)
    FONT_INPUT = (FONT_FAMILY, 11)
    FONT_EMPTY = (FONT_FAMILY, 14)
    FONT_EMPTY_SUB = (FONT_FAMILY, 12)

    # Category
    MAX_CATEGORY_NAME_LENGTH = 16

    # Padding
    PADDING_SMALL = 5
    PADDING_MEDIUM = 10
    PADDING_LARGE = 20

    # Input
    INPUT_HEIGHT = 3
    TASK_TEXT_WIDTH = 50
    SUBTASK_TEXT_WIDTH = 45


class Defaults:
    """Default values and settings"""
    # Default categories
    CATEGORIES = [
        {'id': 1, 'name': 'Slack', 'tasks': []},
        {'id': 2, 'name': 'Discord', 'tasks': []},
        {'id': 3, 'name': 'Twitter', 'tasks': []},
        {'id': 4, 'name': 'Telegram', 'tasks': []},
        {'id': 5, 'name': 'General', 'tasks': []}
    ]

    # Settings
    INPUT_BG_COLOR = Colors.DEFAULT_INPUT_BG
    MAX_RECENT_FILES = 10
    MAX_BACKUPS = 5

    # Export
    EXPORT_DATE_FORMAT = '%Y-%m-%d'
    EXPORT_TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'


class Paths:
    """File paths"""
    # Data files
    DEFAULT_CHECKLIST_FILE = os.path.join(
        os.path.expanduser('~'),
        '.simple_checklist.json'
    )
    SETTINGS_FILE = os.path.join(
        os.path.expanduser('~'),
        '.simple_checklist_settings.json'
    )


class Shortcuts:
    """Keyboard shortcuts"""
    ADD_TASK = '<Shift-Return>'
    NEWLINE = '<Return>'
    CATEGORY_1 = '<Control-Key-1>'
    CATEGORY_2 = '<Control-Key-2>'
    CATEGORY_3 = '<Control-Key-3>'
    CATEGORY_4 = '<Control-Key-4>'
    CATEGORY_5 = '<Control-Key-5>'
    CATEGORY_6 = '<Control-Key-6>'
    CATEGORY_7 = '<Control-Key-7>'
    CATEGORY_8 = '<Control-Key-8>'
    CATEGORY_9 = '<Control-Key-9>'
    # Undo/Redo
    UNDO = '<Control-z>'
    REDO = '<Control-y>'
    REDO_ALT = '<Control-Shift-z>'
    # Search
    SEARCH = '<Control-f>'
    # Navigation
    PREV_CATEGORY = '<Control-Left>'
    NEXT_CATEGORY = '<Control-Right>'


class Messages:
    """User-facing messages"""
    # Hints
    HINT_TEXT = "💡 Shift+Enter: New task | Ctrl+Z: Undo | Ctrl+F: Search | Ctrl+1-9: Switch categories"

    # Empty states
    NO_CATEGORY_SELECTED = "No category selected"
    NO_TASKS = "No tasks yet\nStart typing below to add your first task!"
    NO_RECENT_FILES = "(No recent files)"

    # Confirmations
    DELETE_TASK = "Delete this task?"
    DELETE_SUBTASK = "Delete this sub-task?"
    DELETE_CATEGORY = "Delete this category and all its tasks?"
    CLEAR_COMPLETED = "Clear {} completed task(s)?"
    SAVE_BEFORE_NEW = "Save current checklist before creating new?"

    # Warnings
    CANNOT_DELETE_LAST_CATEGORY = "Cannot delete the last category!"
    NO_COMPLETED_TASKS = "No completed tasks to clear!"

    # Success
    EXPORT_COMPLETE = "Tasks exported to:\n{}"
    CHECKLIST_SAVED = "Checklist saved to:\n{}"

    # Errors
    LOAD_ERROR = "Failed to load checklist:\n{}"

    # Titles
    CATEGORY_SIDEBAR_TITLE = "📋 Categories"
    ADD_CATEGORY_BTN = "+ Add Category"
    EXPORT_BTN = "📥 Export MD"
    CLEAR_DONE_BTN = "🗑️ Clear Done"


class FileTypes:
    """File type filters for dialogs"""
    JSON = [("JSON files", "*.json"), ("All files", "*.*")]
    MARKDOWN = [("Markdown files", "*.md"), ("All files", "*.*")]
    CSV = [("CSV files", "*.csv"), ("All files", "*.*")]
    IMPORT_ALL = [("Supported files", "*.md *.csv"), ("Markdown files", "*.md"),
                  ("CSV files", "*.csv"), ("All files", "*.*")]
