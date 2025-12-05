#!/usr/bin/env python3
"""
Cross-platform launcher for Simple Checklist
Automatically detects the platform and launches the application with appropriate settings
"""

import sys
import os
import platform
import subprocess

def main():
    """Launch Simple Checklist with platform-specific configurations"""

    system = platform.system()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_script = os.path.join(script_dir, 'simple-checklist.py')

    # Check if the main script exists
    if not os.path.exists(app_script):
        print(f"Error: Could not find simple-checklist.py in {script_dir}")
        sys.exit(1)

    # Platform-specific configurations
    if system == 'Windows':
        print("Launching Simple Checklist on Windows...")
        # On Windows, use pythonw to avoid console window
        try:
            subprocess.Popen(['pythonw', app_script])
        except FileNotFoundError:
            # Fall back to python if pythonw is not available
            subprocess.Popen(['python', app_script])

    elif system == 'Darwin':  # macOS
        print("Launching Simple Checklist on macOS...")
        # On macOS, use python3
        subprocess.Popen(['python3', app_script])

    elif system == 'Linux':
        print("Launching Simple Checklist on Linux...")
        # On Linux, use python3
        subprocess.Popen(['python3', app_script])

    else:
        print(f"Warning: Unknown platform '{system}', attempting to launch anyway...")
        subprocess.Popen([sys.executable, app_script])

    print("Simple Checklist launched successfully!")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error launching Simple Checklist: {e}")
        input("Press Enter to exit...")
        sys.exit(1)
