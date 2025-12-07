"""
Search bar component for Simple Checklist
Provides search input with real-time filtering
"""

import tkinter as tk


class SearchBar:
    """Search bar widget with real-time search capabilities"""

    def __init__(self, parent, on_search_callback, on_clear_callback=None):
        """
        Initialize the search bar

        Args:
            parent: Parent widget
            on_search_callback: Callback function(query) called on each keystroke
            on_clear_callback: Callback function() called when search is cleared
        """
        self.on_search_callback = on_search_callback
        self.on_clear_callback = on_clear_callback

        # Create the search frame
        self.frame = tk.Frame(parent, bg='white')

        # Search icon and label
        search_label = tk.Label(self.frame, text="🔍 Search:",
                               bg='white', fg='#7f8c8d',
                               font=('Segoe UI', 10))
        search_label.pack(side=tk.LEFT, padx=(0, 5))

        # Search entry
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search_change)

        self.search_entry = tk.Entry(self.frame, textvariable=self.search_var,
                                     font=('Segoe UI', 10), width=25,
                                     relief=tk.SOLID, borderwidth=1,
                                     highlightthickness=1,
                                     highlightcolor='#3498db',
                                     highlightbackground='#bdc3c7')
        self.search_entry.pack(side=tk.LEFT, padx=5)

        # Clear button
        self.clear_btn = tk.Button(self.frame, text="×",
                                  bg='#95a5a6', fg='white',
                                  relief=tk.FLAT, width=2,
                                  font=('Segoe UI', 10, 'bold'),
                                  command=self.clear)
        self.clear_btn.pack(side=tk.LEFT, padx=2)

        # Escape key to clear
        self.search_entry.bind('<Escape>', lambda e: self.clear())

        # Initially hide clear button
        self._update_clear_button_visibility()

    def _on_search_change(self, *args):
        """Handle search text changes"""
        query = self.search_var.get()
        self._update_clear_button_visibility()
        if self.on_search_callback:
            self.on_search_callback(query)

    def _update_clear_button_visibility(self):
        """Show/hide clear button based on search content"""
        if self.search_var.get():
            self.clear_btn.config(bg='#e74c3c')
        else:
            self.clear_btn.config(bg='#95a5a6')

    def clear(self):
        """Clear the search field"""
        self.search_var.set("")
        if self.on_clear_callback:
            self.on_clear_callback()

    def get_query(self):
        """Get the current search query"""
        return self.search_var.get().strip()

    def pack(self, **kwargs):
        """Pack the search bar frame"""
        self.frame.pack(**kwargs)

    def grid(self, **kwargs):
        """Grid the search bar frame"""
        self.frame.grid(**kwargs)

    def focus(self):
        """Set focus to the search entry"""
        self.search_entry.focus()

    def is_active(self):
        """Check if there's an active search"""
        return bool(self.search_var.get().strip())
