"""
@file utilities.py
@brief Utility functions for GNSS Test Case Generator

This file contains a set of utility functions that support the GNSS Test Case Generator application. The functions
facilitate various essential tasks such as extracting datetime information from filenames, which helps in processing
files that follow a specific naming convention with embedded timestamps. They also include functionality for finding the
latest test case number in MATLAB files by scanning these files, ensuring that new test cases are sequentially numbered.
Additionally, the functions map NMEA files to observation files within a specified directory, crucial for correlating
GNSS data. The utilities provide methods to convert datetime objects to GPS week numbers, a format commonly used in GNSS
data analysis, and to extract and return the year and day of the year from datetime objects, often required for
date-specific GNSS calculations. Furthermore, the file includes a function to generate and append new test cases to
MATLAB files, automating the creation of test cases and integrating them into the existing database. Together,
these utility functions streamline the data preparation and test case generation processes for GNSS analysis, handling
file parsing, data extraction, and formatting tasks critical for the efficient operation of the
GNSS Test Case Generator application.
"""


import os
import re
from datetime import datetime, timedelta
from gps_time import GPSTime


def extract_datetime_from_filename(filename):
    """
    Extracts the date and time from the filename using a regular expression.
    The filename is expected to contain a timestamp in the format 'YYYY_MM_DD_HH_MM_SS'.
    The function uses regular expressions to identify and extract this timestamp.
    It then converts the timestamp into a datetime object, and calculates two additional datetime objects:
    one representing 3 hours before the extracted timestamp, and one representing 3 hours after.
    These three datetime objects are then returned as a tuple.
    If the filename does not contain a valid timestamp in the expected format, the function raises a ValueError.

    Args:
        filename (str): The filename string to extract the datetime from.

    Returns:
        tuple: A tuple containing the original datetime, the datetime 3 hours before, and the datetime 3 hours after.

    Raises:
        ValueError: If the filename format is invalid or does not contain the required datetime information.
    """
    # Define the regex pattern to match the datetime format in the filename
    pattern = r'(\d{4})_(\d{2})_(\d{2})_(\d{2})_(\d{2})_(\d{2})'
    # Search for the pattern in the filename
    match = re.search(pattern, filename)
    if match:
        # Extract the matched groups (year, month, day, hour, minute, second)
        year, month, day, hour, minute, second = match.groups()
        # Create a datetime object from the extracted values
        date_obj = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
        # Calculate the datetime 3 hours before the extracted datetime
        time_first = date_obj - timedelta(hours=3)
        # Calculate the datetime 3 hours after the extracted datetime
        time_last = date_obj + timedelta(hours=3)
        # Return the original datetime, and the calculated first and last datetimes
        return date_obj, time_first, time_last
    else:
        # Raise an error if the filename does not match the required format
        raise ValueError("Filename format is invalid or does not contain the required datetime information.")


def find_latest_case_number(matlab_file_path):
    """
    Finds the latest case number from the given MATLAB file. The function reads the file line by line, starting from the
    end, and looks for lines that start with the word 'case'. It then extracts the case number from the line and returns
    it as an integer. If the MATLAB file does not exist at the specified path, the function raises a RuntimeError with a
    specific error message. Any other exceptions that might occur during the file reading process are also caught and a
    RuntimeError is raised with the corresponding error message.

    Args:
        matlab_file_path (str): The path to the MATLAB file.

    Returns:
        int: The latest case number as an integer.

    Raises:
        RuntimeError: If the MATLAB file does not exist or if there is any other error reading the MATLAB file.
    """
    latest_case_number = 0

    try:
        with open(matlab_file_path, 'r') as file:
            lines = file.readlines()
            # Iterate over the lines in reverse order when finding the latest 'case' line.
            for line in reversed(lines):
                stripped_line = line.strip()
                if stripped_line.startswith('case'):
                    # Extract the case number from the line
                    latest_case_number = int(stripped_line.split()[1])
                    break
    except FileNotFoundError:
        # Catch the FileNotFoundError to provide a more specific error message when the MATLAB file does not exist
        raise RuntimeError(f"The MATLAB file at path {matlab_file_path} does not exist.")
    except Exception as e:
        # Catch any other exceptions that might occur during the file reading process
        # This is a catch-all for unexpected errors, which helps prevent the program from crashing unexpectedly
        raise RuntimeError(f"Error reading MATLAB file: {e}")

    return latest_case_number


def find_corresponding_files(data_directory):
    """
    Finds corresponding NMEA and observation files in the given directory. It first identifies the observation file
    extension by examining the year in the first NMEA file found. Then, it collects all NMEA and observation files in
    the directory. Finally, it creates a mapping from each NMEA file to its corresponding observation file,
    if one exists. If the specified directory does not exist, a FileNotFoundError is raised.

    Args:
        data_directory (str): The directory containing the data files.

    Returns:
        dict: A dictionary mapping NMEA file paths to their corresponding observation file paths.

    Raises:
        FileNotFoundError: If the specified directory does not exist.
    """
    try:
        # Attempt to list the files in the specified directory
        files = os.listdir(data_directory)
    except FileNotFoundError:
        # Catch the FileNotFoundError to provide a more specific error message when the directory does not exist
        raise FileNotFoundError(f"The directory {data_directory} does not exist.")

    nmea_files = {}
    observation_files = {}
    observation_extension = ''

    # Determine the observation file extension based on the year from the first NMEA file
    for filename in files:
        if filename.endswith('.nmea'):
            year = filename.split('_')[2]
            observation_extension = f"{year[-2:]}o"
            break

    # Collect NMEA and observation files
    for filename in files:
        if filename.endswith('.nmea'):
            nmea_files[filename] = os.path.join(data_directory, filename)
        elif filename.endswith(observation_extension):
            observation_files[filename] = os.path.join(data_directory, filename)

    # Map NMEA files to their corresponding observation files
    corresponding_files = {}
    for nmea_filename, nmea_file_path in nmea_files.items():
        observation_filename = nmea_filename.replace('.nmea', f'.{observation_extension}')
        if observation_filename in observation_files:
            corresponding_files[nmea_file_path] = observation_files[observation_filename]

    return corresponding_files


def get_gps_week_number(date_obj):
    """
    Converts a datetime object to a GPS week number using the GPS.from_datetime() method. If the conversion fails due to
    an error (most likely invalid datetime format), a RuntimeError will be raised.

    Args:
        date_obj (datetime): The datetime object to convert.

    Returns:
        int: The GPS week number.

    Raises:
        RuntimeError: If there is an error converting the datetime to GPS week number.
    """
    try:
        # Convert the datetime object to GPS time
        gps_time = GPSTime.from_datetime(date_obj)
        # Return the GPS week number
        return gps_time.week_number
    except Exception as e:
        # Raise an error if the conversion fails
        raise RuntimeError(f"Error converting datetime to GPS week number: {e}")


def get_year_and_day_of_year(date_obj):
    """
    Extracts the year and day of the year from a datetime object. If the extraction fails due to an error
    (e.g., invalid datetime format), a RuntimeError will be raised.

    Args:
        date_obj (datetime): The datetime object to extract from.

    Returns:
        tuple: A tuple containing the year and the day of the year.

    Raises:
        RuntimeError: If there is an error extracting the year and day of year.
    """
    try:
        # Extract the year from the datetime object
        year = date_obj.year
        # Extract the day of the year from the datetime object
        day_of_year = date_obj.timetuple().tm_yday
        # Return the year and day of the year
        return year, day_of_year
    except Exception as e:
        # Raise an error if extraction fails
        raise RuntimeError(f"Error extracting year and day of year from datetime: {e}")


def generate_test_case(time_first, time_last, nmea_file_path, observation_file_path, ephemeris_file_path,
                       orbit_file_path, matlab_file_path, case_number):
    """
    Generates a new test case and appends it to a MATLAB file. It first formats the start and end times,
    constructs the new test case, and reads the existing content of the MATLAB file. If the NMEA file is already
    included in any test case, the function returns False. Otherwise, it finds the position of the "end" keyword in
    the file, inserts the new test case before the "end" keyword, and writes the updated content back to the MATLAB file.
    If the MATLAB file does not exist at the specified path, a FileNotFoundError is raised.

    Args:
        time_first (datetime): The datetime object representing the start time (3 hours before the measurement).
        time_last (datetime): The datetime object representing the end time (3 hours after the measurement).
        nmea_file_path (str): The path to the NMEA file.
        observation_file_path (str): The path to the observation file.
        ephemeris_file_path (str): The path to the ephemeris file.
        orbit_file_path (str): The path to the orbit file.
        matlab_file_path (str): The path to the MATLAB file.
        case_number (int): The case number to be used in the new test case.

    Returns:
        bool: True if the test case is successfully added, False otherwise.

    Raises:
        FileNotFoundError: If the MATLAB file does not exist at the specified path.
    """
    # Convert the first and last time values to formatted lists of integers
    time_first_str = (f"{int(time_first.year)};{int(time_first.month)};{int(time_first.day)};{int(time_first.hour)};"
                      f"{int(time_first.minute)};{int(time_first.second)}")
    time_last_str = (f"{int(time_last.year)};{int(time_last.month)};{int(time_last.day)};{int(time_last.hour)};"
                     f"{int(time_last.minute)};{int(time_last.second)}")

    # Construct the new test case
    new_test_case = [
        f"\tcase {case_number}\n",
        f"\t\tinf.time.first=[{time_first_str}];\n",
        f"\t\tinf.time.last=[{time_last_str}];\n",
        f"\t\tnmeaFile='{nmea_file_path.replace(os.path.sep, '/')}';\n",
        f"\t\tfiles.ob='{observation_file_path.replace(os.path.sep, '/')}';\n",
        f"\t\tfiles.ep='{ephemeris_file_path.replace(os.path.sep, '/')}';\n",
        f"\t\tfiles.orbit='{orbit_file_path.replace(os.path.sep, '/')}';\n",
        "\n"
    ]

    try:
        # Read the existing content of the MATLAB file
        with open(matlab_file_path, 'r') as matlab_file:
            lines = matlab_file.readlines()
    except FileNotFoundError:
        # Catch the FileNotFoundError to provide a more specific error message when the directory does not exist
        raise FileNotFoundError(f"The MATLAB file at path {matlab_file_path} does not exist.")

    # If the NMEA file name was in the MATLAB file, it means that a test case corresponding to the data set exists, and
    # no duplicate test case should be created.
    nmea_file_exists = any(f"\t\tnmeaFile='{nmea_file_path.replace(os.path.sep, '/')}';\n"
                           in line for line in lines)
    if nmea_file_exists:
        return False

    # Find the position of the "end" keyword in the file
    end_index = len(lines) - 1
    for i, line in enumerate(reversed(lines)):
        if "end" in line:
            end_index -= i
            break

    # Insert the new test case before the "end" keyword
    lines = lines[:end_index] + new_test_case + lines[end_index:]

    # Write the updated content back to the MATLAB file
    with open(matlab_file_path, 'w') as matlab_file:
        matlab_file.writelines(lines)

    return True
