# 🛰️ GNSS Test Case Generator

The GNSS Test Case Generator automates the creation of GNSS test cases by downloading, processing, and correlating ephemeris and orbit files with measurement data, generating test cases in MATLAB format.

## 🌟 Features

- 📥 **Download and decompress ephemeris and orbit files.**
- 🛠️ **Generate test cases using correlated GNSS data.**
- 🖥️ **User-friendly GUI with logs and progress tracking.**

## 📋 Prerequisites

- **Python 3.6 or higher**
- **Additional Required Python packages:**
  - `requests`
  - `gps-time`

## 💻 Installation 

1. **Clone the Repository:**

    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2. **Install Required Packages:**

    ```bash
    pip install requests gps-time
    ```

## 🚀 Usage

1. **Run the Application:**

    ```bash
    python main.py
    ```

2. **Using the GUI:**

    - **Welcome Window:** Set the default test case file path and data directory, then proceed.
    - **Main Window:** Select the data directory if not already set, and click “Write” to start processing and generating test cases.

## 🙏 Acknowledgments

- The icon was made by Freepik from [www.flaticon.com](https://www.flaticon.com).
- The code was primarily generated using ChatGPT-4o, with additional editing, reviewing, and design contributions by me.