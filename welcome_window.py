"""
@file welcome_window.py
@brief Welcome window for the GNSS Test Case Generator.

This file defines the WelcomeWindow class, which provides the initial GUI for setting up the GNSS Test Case Generator
application. The welcome window allows users to set the default test case file path and the default data directory before
proceeding to the main application window. The GUI components include buttons for these actions, a help button, and
necessary event handlers for smooth user interaction.

The class ensures that the necessary paths are set before proceeding, and provides a help section for user guidance.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os
from main_window import GNSSTestCaseGenerator
from gui_helpers import center_window, CustomMessageBox


class WelcomeWindow:
    """
    @class WelcomeWindow
    @brief Class to create and manage the welcome window for the GNSS Test Case Generator application.

    This class provides methods to set up the GUI, handle user interactions, and navigate to the main application
    window. It includes options to set the default test case file path and the default data directory, ensuring these
    are set before proceeding.
    """

    def __init__(self, master: tk.Toplevel):
        """
        @brief Initializes the WelcomeWindow class.

        Args:
            master (tk.Tk): The root Tkinter window.
        """
        self.master = master
        self.default_data_directory = ""
        self.default_test_case_file_path = ""
        self.config_file = 'config.json'
        self.icon_path = os.path.join(os.path.dirname(__file__), "icon.png")

        self.load_config()

        self._setup_gui()

    def load_config(self):
        """
        @brief Loads the configuration file to get the last selected paths.

        This function reads the configuration file if it exists and sets the default paths accordingly.
        """
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as config_file:
                config = json.load(config_file)
                self.default_data_directory = config.get('default_data_directory', "")
                self.default_test_case_file_path = config.get('default_test_case_file_path', "")

    def save_config(self, key, value):
        """
        @brief Saves the given path to the configuration file.

        Args:
            key (str): The configuration key to update.
            value (str): The value to save.
        """
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as config_file:
                config = json.load(config_file)
        else:
            config = {}

        config[key] = value

        with open(self.config_file, 'w') as config_file:
            json.dump(config, config_file)

    def _setup_gui(self):
        """
        @brief Sets up the GUI components and layout for the welcome window.

        This function initializes the window settings, creates the button frame, and sets the window size and icon.
        It also calls the function to create the buttons within the frame.
        """
        self.master.title("GNSS Test Case Generator")
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.master.configure(bg='#b3cde0')

        # Set window size to be optimal for a 13.3-inch laptop screen
        self.master.geometry('350x264')

        # Set the app icon
        self.master.iconphoto(False, tk.PhotoImage(file=self.icon_path))

        # Create a frame for the buttons
        button_frame = tk.Frame(self.master, bg='#b3cde0')
        button_frame.place(relwidth=1, relheight=1)

        self._create_buttons(button_frame)

    def _create_buttons(self, parent):
        """
        @brief Creates and positions buttons in the welcome window.

        This function sets up buttons for setting the test case file path, data directory, proceeding to the main
        application, and displaying help. Each button is created with a specific background color and added to the
        parent frame.

        Args:
            parent (tkinter object): Parent widget where the buttons are placed.
        """
        self._create_button(parent, "Set Default Test Case File Path", self.set_default_test_case_file, '#6497b1')
        self._create_button(parent, "Set Default Data Directory", self.set_default_data_directory, '#005b96')
        self._create_button(parent, "Proceed", self.proceed, '#03396c')
        self._create_button(parent, "Help", self.show_help, '#011f4b')

    def _create_button(self, parent, text, command, bg_color):
        """
        @brief Helper function to create a button.

        Args:
            parent (tkinter object): Parent widget where the button is placed.
            text (str): The text to display on the button.
            command (function): The function to call when the button is clicked.
            bg_color (str): The background color of the button.

        Returns:
            button (tk.Button): The created button object.
        """
        button = tk.Button(parent, text=text, command=command, bg=bg_color, fg='white', activebackground='#34495e',
                           activeforeground='white', font=("Helvetica", 12, "bold"), bd=0, padx=10, pady=10, height=2)
        button.pack(pady=0, fill='x', padx=0)
        return button

    def set_default_test_case_file(self):
        """
        @brief Opens a file dialog to select the default test case file.

        This function allows the user to choose a MATLAB file for the test cases.
        The selected file path is stored for later use and saved to the configuration file.
        """
        initial_dir = os.path.dirname(self.default_test_case_file_path) if self.default_test_case_file_path else ""
        filepath = filedialog.askopenfilename(
            initialdir=initial_dir,
            filetypes=[("MATLAB files", "*.m")],
            title="Choose a MATLAB file for the test case"
        )
        if filepath:
            self.default_test_case_file_path = filepath
            self.save_config('default_test_case_file_path', self.default_test_case_file_path)
            print(f"Default test case file path set to: {self.default_test_case_file_path}")  # Debug print

    def set_default_data_directory(self):
        """
        @brief Opens a file dialog to select the default data directory.

        This function allows the user to choose a directory where data files are stored.
        The selected directory path is stored for later use and saved to the configuration file.
        """
        initial_dir = self.default_data_directory if self.default_data_directory else ""
        directory = filedialog.askdirectory(initialdir=initial_dir, title="Choose the default data directory")
        if directory:
            self.default_data_directory = directory
            self.save_config('default_data_directory', self.default_data_directory)
            print(f"Default data directory set to: {self.default_data_directory}")  # Debug print

    def proceed(self):
        """
        @brief Proceeds to the main application window.

        This function checks if both the default test case file path and the default data directory are set.
        If not, it shows a warning message. Otherwise, it opens the main application window.
        """
        if not self.default_test_case_file_path or not self.default_data_directory:
            CustomMessageBox(self.master, "Missing Information",
                             "Please set both the default test case file path and the default data directory "
                             "before proceeding.",
                             self.icon_path)
            return

        self.master.withdraw()  # Hide the welcome window
        root = tk.Toplevel(self.master)
        GNSSTestCaseGenerator(root, self.master, self.default_data_directory, self.default_test_case_file_path)
        center_window(root)

    def show_help(self):
        """
        @brief Displays the help message in a centered window.

        This function opens a new window with help information, explaining how to use the welcome window's features.
        """
        help_window = tk.Toplevel(self.master)
        help_window.title("Help")
        help_window.configure(bg='#2c3e50')

        # Set the app icon for the help window
        help_window.iconphoto(False, tk.PhotoImage(file=self.icon_path))

        help_label = tk.Label(help_window, text=(
            "Use 'Set Default Test Case File Path' to choose the MATLAB file for writing test cases. "
            "This file is typically set once at the start and can be changed by returning to this window. "
            "'Set Default Data Directory' to specify where your data files are stored. "
            "After setting both paths, press 'Proceed' to continue."
        ), bg='#2c3e50', fg='white', wraplength=300, justify='left')
        help_label.pack(padx=20, pady=20)

        # Center the help window
        center_window(help_window)

    def on_closing(self):
        """
        @brief Handles the closing event.

        This function is called when the window close button is clicked. It calls the exit_program function to
        close the application.
        """
        self.exit_program()

    def exit_program(self):
        """
        @brief Exits the application.

        This function quits and destroys the main Tkinter window, effectively closing the application.
        """
        self.master.quit()
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = WelcomeWindow(root)
    root.mainloop()
