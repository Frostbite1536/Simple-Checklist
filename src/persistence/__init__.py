"""
Persistence layer for Simple Checklist
Handles data storage, retrieval, and settings management
"""

from .storage import ChecklistStorage
from .settings import SettingsManager

__all__ = ['ChecklistStorage', 'SettingsManager']
