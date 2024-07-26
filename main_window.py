"""
@file main_window.py
@brief Implements the main user interface and core functionality for the GNSS Test Case Generator application.

This module contains the GNSSTestCaseGenerator class, which is responsible for
initializing the main application window, setting up the graphical user interface (GUI),
and handling the primary operations of the GNSS Test Case Generator. This includes
configuring user inputs, managing data processing, displaying progress, and providing
detailed logs of the application's actions.
"""
import time
import threading
import tkinter as tk
import os
from tkinter import filedialog, ttk
from utilities import (
    extract_datetime_from_filename,
    find_latest_case_number,
    find_corresponding_files,
    get_gps_week_number,
    get_year_and_day_of_year,
    generate_test_case
)
from file_operations import download_ephemeris_file, download_orbit_file
from gui_helpers import create_label, create_button, center_window, CustomMessageBox


class GNSSTestCaseGenerator:
    def __init__(self, master, welcome_window, default_data_directory="", default_test_case_file_path=""):
        """
        Initializes the GNSSTestCaseGenerator class.

        Parameters:
            master (tk.Toplevel): The main window of the application.
            welcome_window (tk.Toplevel): The welcome window instance for managing transitions.
            default_data_directory (str): The default directory path for data files.
            default_test_case_file_path (str): The default file path for test cases.

        This constructor sets up the initial state of the main window, including the default paths,
        initializes the GUI components, and centers the main window on the screen.
        """
        self.master = master
        self.welcome_window = welcome_window
        self.default_data_directory = default_data_directory
        self.default_test_case_file_path = default_test_case_file_path
        # Initialize a flag to indicate whether the detail section is visible or not.
        self.details_visible = False
        # Initialize a list to store log messages for the running process.
        self.log_messages = []
        # Set up the GUI components and layout.
        self._setup_gui()
        # Center the main window on the screen.
        center_window(self.master)
        # Set the window icon
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        self.master.iconphoto(False, tk.PhotoImage(file=icon_path))

    def _setup_gui(self):
        """
        Sets up the main GUI components and layout for the GNSS Test Case Generator application.

        This function initializes the main window's title, sets up the behavior for the window close event,
        and calls helper methods to create and configure various GUI elements including labels, entry fields,
        buttons, a progress bar, and a detail section.
        """
        self.master.title("GNSS Test Case Generator")
        # Handle the closing event through on_closing function when the user attempts to close the window.
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        self._setup_labels()
        self._setup_entry_and_buttons()
        self._setup_progress_bar()
        self._setup_action_buttons()
        self._create_detail_section()

    def _setup_labels(self):
        """
        Sets up and positions labels in the main window using a grid layout.

        This function uses the create_label helper to add:
        - A label indicating the test case file path.
        - A label for the measured data directory.
        """
        self.test_case_label = create_label(self.master, f"Write test case to {self.default_test_case_file_path}", 0, 0, 3)
        self.data_directory_label = create_label(self.master, "Measured Data Directory:", 1, 0, 1)

    def _setup_entry_and_buttons(self):
        """
        Sets up the entry field and browse button for the data directory.

        This function creates a frame containing:
        - An entry field for the data directory path, pre-filled with the default directory.
        - A browse button ("...") to open a file dialog for selecting the data directory.

        The browse button is positioned slightly farther from the entry field to improve the layout,
        and the right edge of the browse button aligns with the right edge of the progress bar and write button.
        """
        self.entry_button_frame = tk.Frame(self.master)
        self.entry_button_frame.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky='ew')

        self.data_directory_entry = tk.Entry(self.entry_button_frame, width=70)
        self.data_directory_entry.grid(row=0, column=0, padx=(0, 5), pady=0, sticky='ew')
        self.data_directory_entry.insert(0, self.default_data_directory)

        self.browse_data_button = tk.Button(self.entry_button_frame, text="...", command=self.browse_data_directory)
        self.browse_data_button.grid(row=0, column=1, padx=10, pady=0, sticky='ew')
        self.browse_data_button.config(width=3)

    def _setup_progress_bar(self):
        """
        Sets up the progress bar for tracking processing status.

        This function creates a status label and a progress bar.
        The status label provides textual feedback about the current status of the processing,
        while the progress bar visually indicates the progress of the ongoing operations.
        """
        self.progress_bar = ttk.Progressbar(self.master, orient="horizontal", mode="determinate")
        self.progress_bar.grid(row=3, column=0, columnspan=3, padx=15, pady=10, sticky='ew')

    def _setup_action_buttons(self):
        """
        Sets up the action buttons (Cancel and Write) in the main window.

        This function creates a frame containing:
        - A Cancel button to abort the process and return to the welcome window.
        - A Write button to start data processing.

        The buttons are positioned in the grid layout and adjusted for better appearance.
        """
        self.button_frame = tk.Frame(self.master)
        self.button_frame.grid(row=4, column=2, padx=10, pady=10, sticky='e')

        self.cancel_button = create_button(self.button_frame, "Cancel", self.cancel)
        self.cancel_button.config(width=10)
        self.write_button = create_button(self.button_frame, "Write", self.process_data)
        self.write_button.config(width=10, bg='skyblue')

    def _create_detail_section(self):
        """
        Creates the detail section with a toggle button.

        This function sets up a section in the main window that can be toggled to show or hide detailed log messages.
        The section includes:
        - A toggle button to show or hide the details.
        - A text widget to display detailed log messages, with lines dynamically adjusting based on the content.
        - Vertical and horizontal scrollbars for navigating the text widget content.

        The toggle button is made to be the same size as the Cancel and Write buttons for consistency.
        """
        self.detail_frame = tk.Frame(self.master)
        self.detail_frame.grid(row=4, column=0, padx=10, pady=10, sticky='w')

        self.toggle_button = tk.Button(self.detail_frame, text="▼ Details", command=self.toggle_details)
        self.toggle_button.config(width=10)
        self.toggle_button.pack(side=tk.LEFT, padx=5)

        # Use default font, set height for 10 lines of text
        self.detail_text = tk.Text(self.master, wrap="word", height=10)
        self.detail_text.grid(row=5, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')
        self.detail_text.grid_remove()

        self.detail_vertical_scrollbar = ttk.Scrollbar(self.master, orient="vertical", command=self.detail_text.yview)
        self.detail_vertical_scrollbar.grid(row=5, column=3, sticky='ns')
        self.detail_text['yscrollcommand'] = self.detail_vertical_scrollbar.set
        self.detail_vertical_scrollbar.grid_remove()

        self.detail_horizontal_scrollbar = ttk.Scrollbar(self.master, orient="horizontal", command=self.detail_text.xview)
        self.detail_horizontal_scrollbar.grid(row=6, column=0, columnspan=3, sticky='ew')
        self.detail_text['xscrollcommand'] = self.detail_horizontal_scrollbar.set
        self.detail_horizontal_scrollbar.grid_remove()

    def browse_data_directory(self):
        """
        Opens a file dialog to select the data directory.

        This function prompts the user with a directory selection dialog. If a directory is selected,
        it updates the entry field with the selected directory path and sets the default data directory
        to the chosen path.
        """
        initial_dir = self.data_directory_entry.get() or self.default_data_directory
        directory = filedialog.askdirectory(initialdir=initial_dir)
        if directory:
            self.data_directory_entry.delete(0, tk.END)
            self.data_directory_entry.insert(0, directory)

    def cancel(self):
        """
        Handles the cancel action to hide the main window and show the welcome window.

        This function is called when the user clicks the Cancel button. It hides the current main
        window and makes the welcome window visible again, allowing the user to return to the
        initial setup screen.
        """
        self.master.withdraw()
        self.welcome_window.deiconify()

    def process_data(self):
        """
        @brief Starts the data processing in a separate thread.

        This method initiates the data processing routine by disabling the action buttons
        to prevent unwanted user interactions, and then starts a background thread to
        handle the processing. It logs messages for each step and updates the progress bar.

        The method performs the following steps:
        - Disables the "Write" and "Cancel" buttons.
        - Starts a new thread for processing data.
        - Finds corresponding data files in the specified directory.
        - Extracts necessary information from filenames.
        - Downloads required ephemeris and orbit files.
        - Generates test cases and logs the results.
        - Updates the progress bar.

        If no data files are found, it logs an appropriate message. It also handles any
        exceptions during the processing and logs error messages accordingly.
        """

        # Clear the detail window messages
        self.detail_text.delete(1.0, tk.END)
        self.log_messages.clear()

        data_directory = self.data_directory_entry.get()
        test_case_file_path = self.default_test_case_file_path

        # Disable buttons to prevent unwanted user actions during processing
        self.write_button.config(state="disabled")
        self.cancel_button.config(state="disabled")

        def process():
            """
            @brief Handles the data processing in a background thread.

            This function performs the core processing logic, including file discovery,
            data extraction, file downloads, and test case generation. It logs messages
            for each step and updates the progress bar.

            The function performs the following steps:
            - Searches for corresponding data files in the specified directory.
            - Extracts date and time information from filenames.
            - Downloads ephemeris and orbit files based on the extracted information.
            - Generates test cases using the extracted data and downloaded files.
            - Logs the success or failure of each test case generation.
            - Updates the progress bar.

            If no corresponding files are found, it logs a message indicating this.
            """
            total_generated_test_cases = 0
            # Find corresponding files in the specified data directory
            corresponding_files = find_corresponding_files(data_directory)
            if not corresponding_files:
                self.log_message("No data files found in the specified directory.")
            # Determine the next available case number by finding the latest case number
            case_number = find_latest_case_number(test_case_file_path) + 1
            self.progress_bar["maximum"] = len(corresponding_files)

            for idx, (nmea_file_path, observation_file_path) in enumerate(corresponding_files.items()):
                try:
                    # Extract date and time information from the NMEA filename
                    date_obj, time_first, time_last = extract_datetime_from_filename(nmea_file_path)
                    # Get GPS week number based on the extracted date
                    gps_week = get_gps_week_number(date_obj)
                    # Get the year and day of the year based on the extracted date
                    year, day_of_year = get_year_and_day_of_year(date_obj)
                    # Download the required ephemeris file
                    ephemeris_file_path = download_ephemeris_file(data_directory, year, day_of_year)
                    # Download the required orbit file
                    orbit_file_path = download_orbit_file(data_directory, gps_week, year, day_of_year)

                    # Generate a test case using the extracted and downloaded data
                    success = generate_test_case(
                        time_first, time_last, nmea_file_path, observation_file_path,
                        ephemeris_file_path, orbit_file_path, test_case_file_path, case_number
                    )
                    data_filepath = os.path.basename(data_directory)

                    if success:
                        # Log a success message if the test case is generated successfully
                        self.log_message(
                            f"Test case {case_number} of {date_obj.strftime('%d/%m/%Y %H:%M:%S')} in {data_filepath} "
                            f"generated successfully."
                        )
                        case_number += 1
                        total_generated_test_cases += 1
                    else:
                        # Log a failure message if the test case generation fails
                        self.log_message(
                            f"Test case of {date_obj.strftime('%d/%m/%Y %H:%M:%S')} in {data_filepath} "
                            f"generated unsuccessfully."
                        )
                except Exception as e:
                    # Log any exceptions that occur during the processing
                    error_message = f"Error processing {nmea_file_path}: {e}"
                    self.log_message(error_message)
                finally:
                    # Update the progress bar value and add a small delay
                    self.progress_bar["value"] = idx + 1
                    time.sleep(0.5)

            if total_generated_test_cases == 0:
                self.log_message("0 test cases written.")

            # Re-enable the action buttons after processing is complete
            self.write_button.config(state="normal")
            self.cancel_button.config(state="normal")

        # Start the process function in a new thread to avoid blocking the main UI thread
        threading.Thread(target=process).start()

    def toggle_details(self):
        """
        @brief Toggles the visibility of the detail text area.

        This method shows or hides the detailed log messages area. If no log messages are present,
        it logs a message indicating that 0 test cases were written. The method also adjusts the
        window size accordingly when toggling the visibility of the details.

        The method performs the following steps:
        - Checks if there are log messages; if not, logs "0 test cases written."
        - Toggles the visibility of the detail text widget and scrollbars.
        - Updates the window size to fit the detailed log or revert to the original size.
        """
        if not self.log_messages:
            self.log_message("0 test cases written.")

        if self.details_visible:
            # Hide the detail text area and scrollbars
            self.detail_text.grid_remove()
            self.detail_vertical_scrollbar.grid_remove()
            self.detail_horizontal_scrollbar.grid_remove()
            self.toggle_button.config(text="▼ Details")
            self.master.geometry("")
        else:
            # Show the detail text area and scrollbars
            self.detail_text.grid()
            self.detail_vertical_scrollbar.grid()
            self.detail_horizontal_scrollbar.grid()
            self.toggle_button.config(text="▲ Details")
            self.update_detail_text()
            self.master.update_idletasks()
            new_height = self.detail_text.winfo_reqheight() + 200
            new_width = max(self.master.winfo_reqwidth(), self.detail_text.winfo_reqwidth() + 40)
            self.master.geometry(f"{new_width}x{new_height}")
        self.details_visible = not self.details_visible

    def update_detail_text(self):
        """
        @brief Updates the detail text widget with logged messages.

        This method clears the existing text in the detail text widget and inserts the current log messages.
        It ensures that the widget scrolls to the end to show the latest messages and adjusts the width of
        the text widget to fit the longest line of text.
        """
        self.detail_text.delete(1.0, tk.END)  # Clear the existing text
        for message in self.log_messages:
            self.detail_text.insert(tk.END, message + "\n")
        self.detail_text.see(tk.END)

        # Adjust the width of the Text widget to fit the longest line of text
        longest_line_length = max(len(line) for line in self.log_messages)
        self.detail_text.config(width=longest_line_length)

    def log_message(self, message):
        """
        @brief Logs a message to the log list.

        This method appends a given message to the list of log messages, which are displayed
        in the detail text area when the details are toggled on.

        @param message The message to log.
        """
        self.log_messages.append(message)

    def on_closing(self):
        """
        @brief Handles the closing event.

        This method is called when the window close button is clicked. It calls the exit_program
        function to close the application.
        """
        self.exit_program()

    def exit_program(self):
        """
        @brief Exits the application.

        This method quits and destroys the main Tkinter window, effectively closing the application.
        """
        self.master.quit()
        self.master.destroy()
