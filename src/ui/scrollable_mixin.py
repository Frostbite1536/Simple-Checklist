"""
Scrollable widget utilities
Shared mousewheel binding/unbinding logic for scrollable panels
"""


def bind_mousewheel(canvas, frame):
    """Bind mousewheel scrolling to canvas and its content frame"""
    canvas.bind('<MouseWheel>', lambda e: _on_mousewheel(canvas, e))
    canvas.bind('<Button-4>', lambda e: _on_mousewheel_linux(canvas, e))
    canvas.bind('<Button-5>', lambda e: _on_mousewheel_linux(canvas, e))
    frame.bind('<MouseWheel>', lambda e: _on_mousewheel(canvas, e))
    frame.bind('<Button-4>', lambda e: _on_mousewheel_linux(canvas, e))
    frame.bind('<Button-5>', lambda e: _on_mousewheel_linux(canvas, e))


def unbind_mousewheel(canvas, frame):
    """Unbind mousewheel scrolling from canvas and its content frame"""
    canvas.unbind('<MouseWheel>')
    canvas.unbind('<Button-4>')
    canvas.unbind('<Button-5>')
    frame.unbind('<MouseWheel>')
    frame.unbind('<Button-4>')
    frame.unbind('<Button-5>')


def _on_mousewheel(canvas, event):
    """Handle mousewheel scroll (Windows/Mac)"""
    if abs(event.delta) >= 120:
        units = int(-event.delta / 120) * 3
    else:
        units = -event.delta * 3
    canvas.yview_scroll(units, 'units')


def _on_mousewheel_linux(canvas, event):
    """Handle mousewheel scroll (Linux)"""
    if event.num == 4:
        canvas.yview_scroll(-3, 'units')
    elif event.num == 5:
        canvas.yview_scroll(3, 'units')
