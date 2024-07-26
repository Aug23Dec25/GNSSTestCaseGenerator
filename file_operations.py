"""
@file file_operations.py
@brief Functions for downloading and decompressing files for GNSS Test Case Generator

This file contains functions to download and decompress ephemeris and orbit files
required for the GNSS Test Case Generator. It handles fetching files from specified URLs
or FTP servers, decompressing them, and saving them in the specified output directory.
These functions are essential for preparing the data files needed to generate GNSS test cases.
"""

import os
import requests
import gzip
import shutil
import ftplib


def download_and_decompress(url, output_directory, filename):
    """
    Downloads and decompresses a file from the given URL. Fetches a compressed file from a specified URL,
    saves it to a given directory, and decompresses it. If the decompressed file already exists, skips the download step.
    In case of a download or decompression error, raises a RuntimeError with an appropriate message.

    Args:
        url (str): The URL to download the file from.
        output_directory (str): The directory to save the downloaded file.
        filename (str): The name of the file to save.

    Returns:
        str: The path to the decompressed file.

    Raises:
        RuntimeError: If there is an error downloading or decompressing the file.
    """
    gz_file_path = os.path.join(output_directory, filename)
    # The compressed file has a .gz extension, to get the path of the decompressed file,
    # remove the last three characters from the filename.
    decompressed_file_path = os.path.join(output_directory, filename[:-3])

    # If the decompressed file already exists, return its path without downloading it again.
    if os.path.exists(decompressed_file_path):
        return decompressed_file_path

    # Tries to establish a connection to the server that hosts the file. If there's an error,
    # catch the error and terminate the process.
    try:
        # Sends a GET request to the specified URL. The argument stream=True means that the response content should be
        # streamed (i.e., delivered and processed incrementally) rather than downloaded all at once.
        # This is useful when dealing with large files.
        response = requests.get(url, stream=True)
        # Checks the HTTP status code of the response. If the status code indicates an error (e.g., 404 Not Found),
        # an exception will be raised. If the status code indicates success (e.g., 200 OK), the program
        # will be progressed.
        response.raise_for_status()
    # Catches any errors related to the process of establishing a connection to the server.
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error downloading file from URL '{url}': {e}")

    # After successfully establishing a connection to the server, try to download the file.
    try:
        # Opens the compressed file in binary write mode.
        with open(gz_file_path, 'wb') as file:
            # This loop iterates over the content of the server's response in chunks of 8192 bytes (or 8 KB).
            # On each iteration, it writes a chunk of data to the file.
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
    # Catches any errors related to I/O operations (e.g., reading or writing files).
    except IOError as e:
        raise RuntimeError(f"Error writing downloaded file to '{gz_file_path}': {e}")

    # Opens the compressed file in binary read mode.
    with gzip.open(gz_file_path, 'rb') as f_in:
        # Creates a new file with the name of the decompressed file and opens it in binary read mode.
        # Then, decompressing by writing all the data from the decompressed file to the new file.
        with open(decompressed_file_path, 'wb') as f_out:
            # Copies the data from one file object to another.
            shutil.copyfileobj(f_in, f_out)

    # After downloading and decompressing the needed file, removes the compressed file to save storage space.
    if os.path.exists(gz_file_path):
        os.remove(gz_file_path)

    return decompressed_file_path


def download_ephemeris_file(output_directory, year, day_of_year):
    """
    Downloads and decompresses an ephemeris file from a specified URL. Constructs the URL for the ephemeris file based
    on the given year and day of the year. Uses the download_and_decompress function to fetch and decompress the file.
    Raises a RuntimeError if any error occurs during the download or decompression process.

    Args:
        output_directory (str): The directory to save the downloaded file.
        year (int): The year of the file to download.
        day_of_year (int): The day of the year of the file to download.

    Returns:
        str: The path to the decompressed ephemeris file.

    Raises:
        RuntimeError: If there is an error downloading or decompressing the file.
    """
    # Constructs the URL for the ephemeris file based on the year and day of year
    url = (f"https://igs.bkg.bund.de/root_ftp/IGS/BRDC/{year}/{day_of_year:03d}/BRDM00DLR_S_{year}"
           f"{day_of_year:03d}0000_01D_MN.rnx.gz")
    # Extracts the last part of the URL to construct the file name.
    filename = url.split('/')[-1]

    try:
        return download_and_decompress(url, output_directory, filename)
    except RuntimeError as e:
        raise RuntimeError(f"Error in downloading or decompressing ephemeris file for year {year} "
                           f"and day {day_of_year}: {e}")


def download_orbit_file(output_directory, gps_week, year, day_of_year):
    """
    Downloads and decompresses an orbit file from a specified FTP server given the date of the measurement.
    Connects to an FTP server, navigates to the appropriate directory based on the GPS week,
    and downloads the specified orbit file. Decompresses the file and saves it to the given directory.
    Raises a RuntimeError if any error occurs during the download or decompression process.

    Args:
        output_directory (str): The directory to save the downloaded file.
        gps_week (int): The GPS week number for the downloading file.
        year (int): The year of the downloading file.
        day_of_year (int): The day of the year of the downloading file.

    Returns:
        str: The path to the decompressed orbit file.

    Raises:
        RuntimeError: If there is an error downloading or decompressing the file.
    """
    # Defines the FTP server
    ftp_host = "ftp.gfz-potsdam.de"
    # Constructs the name of the directory for the week of the orbit file that corresponds to the measured data.
    # The IGS20 standard should be preferred because it provides higher precision and accuracy and also supports
    # multiple satellite systems.
    week_directory_igs20 = f"{gps_week}_IGS20"
    # Constructs the name of the compressed orbit file.
    filename = f"GBM0MGXRAP_{year}{day_of_year:03d}0000_01D_05M_ORB.SP3.gz"
    # Defines the full file path of the compressed orbit file.
    gz_file_path = os.path.join(output_directory, filename)
    # Defines the full file path of the decompressed orbit file.
    sp3_file_path = os.path.join(output_directory, filename[:-3])

    # If the decompressed orbit file already exists, return the path of the file.
    if os.path.exists(sp3_file_path):
        return sp3_file_path

    try:
        # Creates a new FTP client session. This is the first step in the process of connecting to the FTP server.
        ftp = ftplib.FTP(ftp_host)
        # Logs into the FTP server anonymously (by default).
        ftp.login()
        ftp.cwd("GNSS" + os.path.sep + "products" + os.path.sep + "mgex")

        # Checks if the directory for the specific GPS week exists on the server. nlst() method retrieves a list of
        # all the filenames in the cwd on the server.
        if week_directory_igs20 not in ftp.nlst():
            raise FileNotFoundError(f"FTP week directory '{week_directory_igs20}' not found on server '{ftp_host}'.")

        # If the directory for the GPS week does exist, change the cwd to that directory.
        ftp.cwd(week_directory_igs20)

        try:
            # Opens the compressed file in binary write mode. 'with' statement ensures that the file is properly closed
            # after it is no longer needed.
            with open(gz_file_path, 'wb') as file:
                # Sends a RETR command to the FTP server to download the file named `filename`. The syntax of this
                # command must be exactly "RETR {filename}". The server will send the file as a stream of bytes.
                # For each block of bytes received from the server, call the `file.write` method to write the block
                # to the file.
                ftp.retrbinary(f"RETR {filename}", file.write)
        # Catches "permanent" errors during an FTP operation (response code in the range of 500-599), which are
        # typically caused by issues that won't be resolved by retrying the operation. Examples include situations where
        # the requested file doesn't exist on the server, the user doesn't have permission to access the file,
        # or the command sent is not recognized by the server.
        except ftplib.error_perm as e:
            raise RuntimeError(f"FTP error downloading file '{filename}' from server '{ftp_host}': {e}")

        # Opens the compressed file in binary read mode.
        with gzip.open(gz_file_path, 'rb') as f_in:
            # Opens (or create) the decompressed file in binary write mode.
            with open(sp3_file_path, 'wb') as f_out:
                # Copies the contents of the compressed file to the decompressed file.
                shutil.copyfileobj(f_in, f_out)

        # After downloading and decompressing the file, remove the compressed file to save storage space.
        if os.path.exists(gz_file_path):
            os.remove(gz_file_path)

        return sp3_file_path
    # Catches any exception that is either a known FTP error (e.g., error_reply, error_temp, error_perm, etc.)
    # or any other Python Exception.
    except (ftplib.all_errors, Exception) as e:
        raise RuntimeError(f"Error downloading orbit file for GPS week {gps_week}, year {year}, day {day_of_year} from "
                           f"server '{ftp_host}': {e}")
