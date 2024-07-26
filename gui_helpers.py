"""
@file gui_helpers.py
@brief Helper functions for creating and managing Tkinter GUI components.

This file contains utility functions that simplify the creation and management of Tkinter GUI components
for the GNSS Test Case Generator application. It includes functions to create and position label widgets,
set their text, and place them within the parent widget's grid layout. Additionally, it provides functions
to create button widgets, assign text labels and commands to them, and position them within the parent
widget using the pack layout manager. The file also includes a function to center the main application window,
calculating the appropriate screen position to ensure a balanced and user-friendly interface. By using these
helper functions, the main application code becomes more streamlined, readable, and consistent.
"""
import tkinter as tk


def create_label(parent, text, row, column, columnspan):
    """
    Creates a label widget and adds it to the parent widget. Labels display text or images on the screen.
    The function takes in the parent widget (where the label will be placed), the text for the label, and the grid
    parameters for positioning the label. It then creates the label, places it on the grid, and returns the label
    object for further use.

    Args:
        parent (tkinter object): Parent widget where the label is placed.
        text (str): Text displayed on the label.
        row (int), column (int): Position of the label in the grid of the parent widget.
        columnspan (int): Number of columns in the grid that the label spans.
    """
    label = tk.Label(parent, text=text)
    label.grid(row=row, column=column, columnspan=columnspan, padx=10, pady=10, sticky='w')
    return label


def create_button(parent, text, command):
    """
    Creates a button widget and adds it to the parent widget. Buttons are interactive elements that users can click
    to trigger actions. The function takes in the parent widget (where the button will be placed), the text for the
    button, and the command to be executed when the button is clicked. It then creates the button, packs it
    (which means it positions it within the parent widget), and returns the button object for further use.

    Args:
        parent (tkinter object): Parent widget where the button is placed.
        text (str): Text displayed on the button.
        command (function): Function executed when the button is clicked.
    """
    button = tk.Button(parent, text=text, command=command)
    button.pack(side=tk.LEFT, padx=5, pady=5)
    return button


def center_window(root):
    """
    Centers a tkinter window on the screen. It calculates the center position of the screen and the size of the window,
    and then positions the top-left corner of the window at the calculated center position. This is often done to make
    the GUI appear in a predictable location that is easy for the user to find, and to enhance the aesthetic appeal of
    the program by providing a balanced and symmetrical layout.

    Args:
        root (tkinter.Tk): Root window to be centered.
    """
    # Forces tkinter to immediately handle any pending tasks (known as "idle" tasks) to ensure that the window is fully
    # updated (including its size and position) before we try to center it.
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = root.winfo_width()
    window_height = root.winfo_height()
    position_x = (screen_width // 2) - (window_width // 2)
    position_y = (screen_height // 2) - (window_height // 2)
    # Sets the size and position of the window. The geometry method takes a string in the format 'widthxheight+x+y',
    # where width and height are the dimensions of the window, and x and y are the coordinates of the top-left corner
    # of the window. The + signs are literal plus signs, not addition operators.
    root.geometry(f'{window_width}x{window_height}+{position_x}+{position_y}')


class CustomMessageBox(tk.Toplevel):
    """
    @class CustomMessageBox
    @brief A custom message box with a specified icon.

    This class creates a custom message box that can display a message and an icon.
    It is used to replace the standard Tkinter messagebox for better customization.

    Args:
        master (tk.Tk): The root Tkinter window.
        title (str): The title of the message box.
        message (str): The message to display.
        icon_path (str): The file path to the icon image.
    """
    def __init__(self, master, title, message, icon_path):
        super().__init__(master)
        self.title(title)
        self.iconphoto(False, tk.PhotoImage(file=icon_path))
        self.configure(bg='#2c3e50')

        label = tk.Label(self, text=message, bg='#2c3e50', fg='white', wraplength=300, justify='center')
        label.pack(padx=20, pady=20, expand=True)

        self.update_idletasks()  # Ensure the label size is updated

        # Calculate the appropriate window size
        window_width = label.winfo_reqwidth() + 40
        window_height = label.winfo_reqheight() + 40
        self.geometry(f'{window_width}x{window_height}')

        # Center the window on the screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        position_x = (screen_width // 2) - (window_width // 2)
        position_y = (screen_height // 2) - (window_height // 2)
        self.geometry(f'{window_width}x{window_height}+{position_x}+{position_y}')

        self.transient(master)
        self.grab_set()
        master.wait_window(self)
