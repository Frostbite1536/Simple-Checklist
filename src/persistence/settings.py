"""
Settings management for Simple Checklist
Handles user preferences and application settings
"""

import json
import os
from typing import List, Optional, Dict, Any

from ..utils.constants import Paths, Defaults


class SettingsManager:
    """Manages user settings and preferences"""

    def __init__(self, settings_file: Optional[str] = None):
        """
        Initialize settings manager

        Args:
            settings_file: Path to the settings JSON file (uses default if None)
        """
        self.settings_file = settings_file or Paths.SETTINGS_FILE
        self.settings = self._get_default_settings()
        self.load_settings()

    def _get_default_settings(self) -> Dict[str, Any]:
        """
        Get default settings

        Returns:
            Dictionary of default settings
        """
        return {
            'input_bg_color': Defaults.INPUT_BG_COLOR,
            'recent_files': []
        }

    def load_settings(self) -> bool:
        """
        Load settings from file

        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(self.settings_file):
            return False

        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                loaded_settings = json.load(f)
                self.settings.update(loaded_settings)
            return True
        except Exception as e:
            print(f"Error loading settings: {e}")
            return False

    def save_settings(self) -> bool:
        """
        Save settings to file

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False

    def get_input_bg_color(self) -> str:
        """
        Get the input box background color

        Returns:
            Color string (hex or name)
        """
        return self.settings.get('input_bg_color', Defaults.INPUT_BG_COLOR)

    def set_input_bg_color(self, color: str) -> None:
        """
        Set the input box background color

        Args:
            color: Color string (hex or name)
        """
        self.settings['input_bg_color'] = color
        self.save_settings()

    def get_recent_files(self) -> List[str]:
        """
        Get the list of recent files

        Returns:
            List of file paths
        """
        return self.settings.get('recent_files', [])

    def add_recent_file(self, file_path: str) -> None:
        """
        Add a file to the recent files list

        Args:
            file_path: Path to add
        """
        recent_files = self.get_recent_files()

        # Remove if already exists
        if file_path in recent_files:
            recent_files.remove(file_path)

        # Add to beginning
        recent_files.insert(0, file_path)

        # Keep only max allowed
        recent_files = recent_files[:Defaults.MAX_RECENT_FILES]

        self.settings['recent_files'] = recent_files
        self.save_settings()

    def remove_recent_file(self, file_path: str) -> bool:
        """
        Remove a file from the recent files list

        Args:
            file_path: Path to remove

        Returns:
            True if removed, False if not found
        """
        recent_files = self.get_recent_files()

        if file_path in recent_files:
            recent_files.remove(file_path)
            self.settings['recent_files'] = recent_files
            self.save_settings()
            return True

        return False

    def clear_recent_files(self) -> None:
        """Clear all recent files"""
        self.settings['recent_files'] = []
        self.save_settings()

    def get_recent_files_existing(self) -> List[str]:
        """
        Get recent files that still exist on the filesystem

        Returns:
            List of existing file paths
        """
        return [f for f in self.get_recent_files() if os.path.exists(f)]

    def cleanup_recent_files(self) -> int:
        """
        Remove non-existent files from recent files list

        Returns:
            Number of files removed
        """
        recent_files = self.get_recent_files()
        existing_files = [f for f in recent_files if os.path.exists(f)]
        removed_count = len(recent_files) - len(existing_files)

        if removed_count > 0:
            self.settings['recent_files'] = existing_files
            self.save_settings()

        return removed_count

    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value by key

        Args:
            key: Setting key
            default: Default value if key not found

        Returns:
            Setting value or default
        """
        return self.settings.get(key, default)

    def set_setting(self, key: str, value: Any) -> None:
        """
        Set a setting value

        Args:
            key: Setting key
            value: Setting value
        """
        self.settings[key] = value
        self.save_settings()

    def reset_to_defaults(self) -> None:
        """Reset all settings to default values"""
        self.settings = self._get_default_settings()
        self.save_settings()

    def get_all_settings(self) -> Dict[str, Any]:
        """
        Get all settings

        Returns:
            Dictionary of all settings
        """
        return self.settings.copy()

    def import_settings(self, settings_dict: Dict[str, Any]) -> None:
        """
        Import settings from a dictionary

        Args:
            settings_dict: Dictionary of settings to import
        """
        self.settings.update(settings_dict)
        self.save_settings()

    def export_settings(self) -> Dict[str, Any]:
        """
        Export settings to a dictionary

        Returns:
            Dictionary of current settings
        """
        return self.get_all_settings()
