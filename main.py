"""
@file main.py
@brief Entry point for the GNSS Test Case Generator application.

This script serves as the entry point for the GNSS Test Case Generator application.
It initializes the main Tkinter root window, creates and displays the welcome window,
centers the welcome window on the screen, and starts the Tkinter main event loop.

To launch the GNSS Test Case Generator application, simply run this script.
"""
import tkinter as tk
from welcome_window import WelcomeWindow
from gui_helpers import center_window

# The code within this block only runs if this script is executed directly
if __name__ == "__main__":
    # Create the main Tkinter root window, which serves as the primary container for the entire application
    root = tk.Tk()
    # Hide the root window initially because it is empty
    root.withdraw()

    # Create the welcome window as a top-level window, making it a child of the root window
    welcome_window = tk.Toplevel(root)
    # Initialize the WelcomeWindow class with the newly created top-level window
    WelcomeWindow(welcome_window)

    # Center the welcome window on the screen
    center_window(welcome_window)

    # Start the Tkinter main event loop to keep the application running
    root.mainloop()
