"""
Persistence layer for Simple Checklist
Handles data storage, retrieval, and settings management
"""

from .storage import ChecklistStorage
from .settings import SettingsManager

# Aliases for backward compatibility
Storage = ChecklistStorage
Settings = SettingsManager

__all__ = ['ChecklistStorage', 'SettingsManager', 'Storage', 'Settings']
