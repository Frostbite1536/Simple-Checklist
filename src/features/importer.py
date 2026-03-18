"""
Task Importer for Simple Checklist
Supports importing tasks from Markdown and CSV files
"""

import csv
import re
from typing import List

from ..models.task import Task, Subtask


class TaskImporter:
    """Import tasks from various file formats"""

    @staticmethod
    def import_from_markdown(file_path: str) -> List[Task]:
        """
        Import tasks from a Markdown file.

        Supported patterns:
        - [ ] task text       -> incomplete task
        - [x] task text       -> completed task
          - [ ] subtask       -> subtask (indented)
          > note text         -> note on previous task
          • note text         -> note on previous task

        Args:
            file_path: Path to the Markdown file

        Returns:
            List of Task objects
        """
        tasks = []
        current_task = None

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.rstrip('\n\r')

                # Subtask pattern (indented checkbox)
                subtask_match = re.match(
                    r'^[ \t]+[-*]\s*\[([ xX])\]\s+(.+)', line)
                if subtask_match and current_task:
                    completed = subtask_match.group(1).lower() == 'x'
                    text = subtask_match.group(2).strip()
                    if text:
                        try:
                            current_task.add_subtask(
                                Subtask(text, completed=completed))
                        except ValueError:
                            pass
                    continue

                # Top-level task pattern
                task_match = re.match(
                    r'^[-*]\s*\[([ xX])\]\s+(.+)', line)
                if task_match:
                    completed = task_match.group(1).lower() == 'x'
                    text = task_match.group(2).strip()
                    if text:
                        try:
                            current_task = Task(text, completed=completed)
                            tasks.append(current_task)
                        except ValueError:
                            current_task = None
                    continue

                # Note patterns (blockquote or bullet)
                note_match = re.match(
                    r'^[ \t]+(>|[•·])\s*(.+)', line)
                if note_match and current_task:
                    note_text = note_match.group(2).strip()
                    if note_text:
                        current_task.add_note(note_text)
                    continue

        return tasks

    @staticmethod
    def import_from_csv(file_path: str) -> List[Task]:
        """
        Import tasks from a CSV file.

        Expected columns: text, completed, priority, due_date
        Only 'text' is required.

        Args:
            file_path: Path to the CSV file

        Returns:
            List of Task objects
        """
        tasks = []

        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                text = row.get('text', '').strip()
                if not text:
                    continue

                completed_str = row.get('completed', 'false').strip().lower()
                completed = completed_str in ('true', '1', 'yes', 'x')

                priority = row.get('priority', 'medium').strip().lower()
                if priority not in ('low', 'medium', 'high'):
                    priority = 'medium'

                due_date = row.get('due_date', '').strip() or None

                try:
                    task = Task(text, completed=completed,
                               priority=priority, due_date=due_date)
                    tasks.append(task)
                except ValueError:
                    continue

        return tasks

    @staticmethod
    def import_file(file_path: str) -> List[Task]:
        """
        Auto-detect format and import tasks.

        Args:
            file_path: Path to the file

        Returns:
            List of Task objects
        """
        lower = file_path.lower()
        if lower.endswith('.csv'):
            return TaskImporter.import_from_csv(file_path)
        elif lower.endswith('.md') or lower.endswith('.markdown'):
            return TaskImporter.import_from_markdown(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
