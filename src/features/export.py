"""
Markdown Exporter
Handles exporting checklists to various formats
"""

import os
from datetime import datetime
from typing import Optional, Dict, Any
from ..models.checklist import Checklist
from ..models.category import Category
from ..models.task import Task
from ..utils.constants import Defaults


class MarkdownExporter:
    """Exports checklists to Markdown format with various options"""

    def __init__(self, checklist: Checklist, source_file: Optional[str] = None):
        """
        Initialize exporter

        Args:
            checklist: Checklist to export
            source_file: Optional source file path for metadata
        """
        self.checklist = checklist
        self.source_file = source_file

    def export_to_string(self, include_metadata: bool = True) -> str:
        """
        Export checklist to Markdown string

        Args:
            include_metadata: Whether to include header metadata

        Returns:
            Markdown formatted string
        """
        parts = []

        if include_metadata:
            parts.append(self._generate_header())

        for category in self.checklist.categories:
            parts.append(self._format_category(category))

        return '\n'.join(parts)

    def export_to_file(self, file_path: str, include_metadata: bool = True) -> bool:
        """
        Export checklist to Markdown file

        Args:
            file_path: Path to save the markdown file
            include_metadata: Whether to include header metadata

        Returns:
            True if successful, False otherwise
        """
        try:
            content = self.export_to_string(include_metadata)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error exporting to file: {e}")
            return False

    def _generate_header(self) -> str:
        """
        Generate header metadata

        Returns:
            Header string
        """
        timestamp = datetime.now().strftime(Defaults.EXPORT_TIMESTAMP_FORMAT)
        header = "# Checklist Export\n\n"
        header += f"**Exported:** {timestamp}\n"

        if self.source_file:
            header += f"**File:** {os.path.basename(self.source_file)}\n"

        # Add statistics
        total_tasks = self.checklist.get_total_task_count()
        completed_tasks = self.checklist.get_total_completed_count()
        completion_pct = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        header += f"**Total Tasks:** {total_tasks}\n"
        header += f"**Completed:** {completed_tasks} ({completion_pct:.1f}%)\n"
        header += f"**Categories:** {self.checklist.get_category_count()}\n"
        header += "\n---\n\n"

        return header

    def _format_category(self, category: Category) -> str:
        """
        Format a category as Markdown

        Args:
            category: Category to format

        Returns:
            Markdown string for the category
        """
        lines = [f"## {category.name}\n"]

        if not category.tasks:
            lines.append("_No tasks_\n")
        else:
            # Add category statistics
            completed = len(category.get_completed_tasks())
            total = category.get_task_count()
            pct = category.get_completion_percentage()
            lines.append(f"**Progress:** {completed}/{total} tasks ({pct:.1f}% complete)\n")

            for task in category.tasks:
                lines.append(self._format_task(task))

        lines.append("")  # Empty line after category
        return '\n'.join(lines)

    def _format_task(self, task: Task, indent: int = 0) -> str:
        """
        Format a task as Markdown

        Args:
            task: Task to format
            indent: Indentation level

        Returns:
            Markdown string for the task
        """
        indent_str = '  ' * indent
        checkbox = '[x]' if task.completed else '[ ]'
        lines = [f"{indent_str}- {checkbox} {task.text}"]

        # Add subtasks
        if task.subtasks:
            for subtask in task.subtasks:
                sub_checkbox = '[x]' if subtask.completed else '[ ]'
                lines.append(f"{indent_str}  - {sub_checkbox} {subtask.text}")

        # Add notes
        if task.notes:
            for note in task.notes:
                lines.append(f"{indent_str}    - {note}")

        return '\n'.join(lines)

    def export_category(self, category_id: int, file_path: str) -> bool:
        """
        Export a single category to file

        Args:
            category_id: ID of category to export
            file_path: Path to save the file

        Returns:
            True if successful, False otherwise
        """
        category = self.checklist.get_category(category_id)
        if not category:
            return False

        try:
            content = f"# {category.name}\n\n"
            content += self._format_category(category)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error exporting category: {e}")
            return False

    def export_completed_only(self, file_path: str) -> bool:
        """
        Export only completed tasks

        Args:
            file_path: Path to save the file

        Returns:
            True if successful, False otherwise
        """
        try:
            timestamp = datetime.now().strftime(Defaults.EXPORT_TIMESTAMP_FORMAT)
            content = f"# Completed Tasks\n\n**Exported:** {timestamp}\n\n---\n\n"

            for category in self.checklist.categories:
                completed_tasks = category.get_completed_tasks()
                if completed_tasks:
                    content += f"## {category.name}\n\n"
                    for task in completed_tasks:
                        content += self._format_task(task) + "\n"
                    content += "\n"

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error exporting completed tasks: {e}")
            return False

    def export_pending_only(self, file_path: str) -> bool:
        """
        Export only pending (incomplete) tasks

        Args:
            file_path: Path to save the file

        Returns:
            True if successful, False otherwise
        """
        try:
            timestamp = datetime.now().strftime(Defaults.EXPORT_TIMESTAMP_FORMAT)
            content = f"# Pending Tasks\n\n**Exported:** {timestamp}\n\n---\n\n"

            for category in self.checklist.categories:
                pending_tasks = category.get_pending_tasks()
                if pending_tasks:
                    content += f"## {category.name}\n\n"
                    for task in pending_tasks:
                        content += self._format_task(task) + "\n"
                    content += "\n"

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error exporting pending tasks: {e}")
            return False

    def get_export_preview(self, max_lines: int = 20) -> str:
        """
        Get a preview of the export

        Args:
            max_lines: Maximum number of lines to include

        Returns:
            Preview string
        """
        full_export = self.export_to_string()
        lines = full_export.split('\n')

        if len(lines) <= max_lines:
            return full_export

        preview_lines = lines[:max_lines]
        preview_lines.append(f"\n... ({len(lines) - max_lines} more lines)")
        return '\n'.join(preview_lines)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get export statistics

        Returns:
            Dictionary of statistics
        """
        total_tasks = self.checklist.get_total_task_count()
        completed_tasks = self.checklist.get_total_completed_count()

        # Count subtasks
        total_subtasks = 0
        completed_subtasks = 0
        for category in self.checklist.categories:
            for task in category.tasks:
                total_subtasks += task.get_subtask_count()
                completed_subtasks += task.get_completed_subtask_count()

        return {
            'categories': self.checklist.get_category_count(),
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': total_tasks - completed_tasks,
            'completion_percentage': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            'total_subtasks': total_subtasks,
            'completed_subtasks': completed_subtasks,
            'export_timestamp': datetime.now().isoformat()
        }
