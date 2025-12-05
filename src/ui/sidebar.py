"""
Category sidebar component for Simple Checklist
Displays categories with drag-and-drop reordering support
"""

import tkinter as tk


class Sidebar:
    """Category sidebar with drag-and-drop reordering"""

    def __init__(self, parent, on_category_click, on_category_delete,
                 on_add_category, on_category_reorder):
        """
        Initialize the sidebar

        Args:
            parent: Parent widget
            on_category_click: Callback function(cat_id) when category is clicked
            on_category_delete: Callback function(cat_id) when delete is clicked
            on_add_category: Callback function() when add category button is clicked
            on_category_reorder: Callback function(from_idx, to_idx) when categories are reordered
        """
        self.on_category_click = on_category_click
        self.on_category_delete = on_category_delete
        self.on_add_category = on_add_category
        self.on_category_reorder = on_category_reorder

        # Drag and drop state
        self.drag_data = {
            'source': None,
            'index': None,
            'start_y': None,
            'dragging': False
        }

        # Create sidebar frame
        self.frame = tk.Frame(parent, bg='#2c3e50', width=200)
        self.frame.pack_propagate(False)

        # Sidebar title
        title_label = tk.Label(self.frame, text="📋 Categories",
                              bg='#2c3e50', fg='white',
                              font=('Segoe UI', 12, 'bold'),
                              pady=15)
        title_label.pack(fill=tk.X)

        # Categories container
        self.category_frame = tk.Frame(self.frame, bg='#2c3e50')
        self.category_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        # Add category button
        add_cat_btn = tk.Button(self.frame, text="+ Add Category",
                               bg='#3498db', fg='white',
                               relief=tk.FLAT, pady=8,
                               command=self.on_add_category)
        add_cat_btn.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

    def pack(self, **kwargs):
        """Pack the sidebar frame"""
        self.frame.pack(**kwargs)

    def grid(self, **kwargs):
        """Grid the sidebar frame"""
        self.frame.grid(**kwargs)

    def render_categories(self, categories, current_category_id):
        """
        Render the category list

        Args:
            categories: List of category dictionaries with 'id', 'name', and 'tasks'
            current_category_id: ID of the currently selected category
        """
        # Clear existing widgets
        for widget in self.category_frame.winfo_children():
            widget.destroy()

        # Create category buttons
        for idx, cat in enumerate(categories):
            is_active = cat['id'] == current_category_id

            frame = tk.Frame(self.category_frame,
                           bg='#3498db' if is_active else '#2c3e50')
            frame.pack(fill=tk.X, pady=3)

            btn = tk.Button(frame,
                          text=f"{cat['name']} ({len(cat['tasks'])})",
                          bg='#3498db' if is_active else '#2c3e50',
                          fg='white', relief=tk.FLAT,
                          anchor='w', padx=10, pady=8,
                          font=('Segoe UI', 10),
                          cursor='hand2')
            btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Bind drag-and-drop events
            btn.bind('<Button-1>',
                    lambda e, i=idx, c=cat['id']: self._on_drag_start(e, i, c))
            btn.bind('<B1-Motion>', self._on_drag_motion)
            btn.bind('<ButtonRelease-1>',
                    lambda e, i=idx, c=cat['id']: self._on_drag_release(e, i, c))

            # Delete button
            del_btn = tk.Button(frame, text="×",
                              bg='#e74c3c', fg='white',
                              relief=tk.FLAT, width=3,
                              command=lambda c=cat['id']: self.on_category_delete(c))
            del_btn.pack(side=tk.RIGHT)

    def _on_drag_start(self, event, index, cat_id):
        """Start dragging a category"""
        self.drag_data['source'] = event.widget
        self.drag_data['index'] = index
        self.drag_data['cat_id'] = cat_id
        self.drag_data['start_y'] = event.y_root
        self.drag_data['dragging'] = False

    def _on_drag_motion(self, event):
        """Handle drag motion"""
        if self.drag_data['source'] and self.drag_data['start_y'] is not None:
            # If moved more than 5 pixels, consider it a drag
            if abs(event.y_root - self.drag_data['start_y']) > 5:
                self.drag_data['dragging'] = True
                self.drag_data['source'].config(cursor='fleur')

    def _on_drag_release(self, event, target_index, cat_id):
        """Handle drop event to reorder categories or switch category"""
        source_index = self.drag_data['index']

        if self.drag_data['dragging'] and source_index is not None and source_index != target_index:
            # It was a drag - reorder categories
            self.on_category_reorder(source_index, target_index)
        elif not self.drag_data['dragging']:
            # It was a click - switch category
            self.on_category_click(cat_id)

        # Reset drag data
        if self.drag_data['source']:
            self.drag_data['source'].config(cursor='hand2')
        self.drag_data = {
            'source': None,
            'index': None,
            'start_y': None,
            'dragging': False
        }
