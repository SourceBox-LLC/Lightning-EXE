# Lightning EXE Documentation

Welcome to the Lightning EXE documentation! This application allows you to convert Python projects into executable files effortlessly. Below, you will find detailed information about the features of the application and instructions on how to use it effectively.

## Table of Contents
- [Features](#features)
- [Getting Started](#getting-started)
  - [Requirements](#requirements)
  - [Installation](#installation)
- [Using Lightning EXE](#using-lightning-exe)
  - [Input Source Selection](#input-source-selection)
  - [Output Options](#output-options)
  - [Building the Executable](#building-the-executable)
- [Error Handling and Troubleshooting](#error-handling-and-troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features
- **Multiple Input Sources**: Choose to convert a single Python file, a project folder, or a GitHub repository.
- **Customizable Output Options**: Select where to save the executable and whether to create a single-file executable or a directory.
- **User-Friendly Interface**: Built with Tkinter for a clean and intuitive GUI.
- **Progress Tracking**: View real-time progress and status updates during the build process.
- **Automatic Dependency Management**: Automatically installs PyInstaller if not present.

## Getting Started

### Requirements
- Python 3.6 or higher
- Git (for cloning GitHub repositories)
- Tkinter (comes pre-installed with standard Python installations)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/lightning-exe.git
   cd lightning-exe
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

## Using Lightning EXE

### Input Source Selection
When you launch Lightning EXE, you will be presented with options to select the source of your Python project. You can choose from the following:

- **Python File**: Select a single `.py` file.
- **Project Folder**: Select a folder containing your Python project.
- **GitHub Repository**: Enter the URL of a GitHub repository.

#### Selecting Input Source
1. In the **Input Source** tab, choose your input type using the radio buttons.
2. Depending on your selection, the corresponding input field will be displayed for you to provide the file path or URL.

### Output Options
In the **Build Options** tab, you can configure where the executable will be saved and how it will be packaged.

1. **Output Location**: Specify the directory where the executable will be stored.
2. **Packaging Options**:
   - **Create Single File Executable**: Check this box to bundle everything into a single executable file.
   - **Show Console Window**: Check this box if you want to see console output during execution, useful for debugging.

### Building the Executable
Once you have configured the input and output options:

1. Click the **⚡ BUILD EXECUTABLE** button.
2. The progress bar will indicate the build status, and you will receive notifications upon completion or if any errors occur.

## Error Handling and Troubleshooting
- **Invalid Input Path**: Ensure that the path provided is correct and accessible.
- **Python File Requirement**: If you select a file, it must have a `.py` extension.
- **GitHub URL Validation**: Make sure you enter a valid GitHub repository URL.
- **Output Directory Issues**: Ensure the output directory exists or the application can create it.

If you encounter any issues, please refer to the messages displayed in the status area for guidance.

## Contributing
We welcome contributions! If you would like to contribute to Lightning EXE, please fork the repository, make your changes, and submit a pull request. Ensure that your code adheres to the existing style and includes relevant tests.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

---

Thank you for using Lightning EXE! We hope this documentation helps you get started and make the most of the application. If you have any questions or feedback, feel free to reach out!