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

---

## Packaging FastAPI and Streamlit Apps (Important Limitations)

Lightning EXE aims to make any Python app instantly executable. However, some web frameworks (notably **FastAPI/Uvicorn** and **Streamlit**) use dynamic imports and subprocesses that are not always compatible with PyInstaller or similar tools.

### What to Expect
- **Most apps** (console, Tkinter, PyQt, Pygame, Flask, etc.) work out of the box.
- **FastAPI and Streamlit apps** may require special handling and may not work with zero configuration.

### What Lightning EXE Does
- **Automated Detection:** If your project or custom command uses FastAPI/Uvicorn or Streamlit, Lightning EXE will warn you before building.
- **Experimental Mode:** You can enable this in the Advanced tab. Lightning EXE will attempt to patch the environment to improve compatibility, but this may not work for all apps.

### Known Issues
- Running `uvicorn main:app` or `streamlit run app.py` in an EXE may result in errors like:
  - `Error loading ASGI app. Could not import module "main".`
- This is due to how PyInstaller bundles code and how these frameworks import your app.

### Workarounds
- **Recommended:** Use a programmatic entrypoint for FastAPI (requires a small code change):
  ```python
  import uvicorn
  import main
  if __name__ == "__main__":
      uvicorn.run(main.app, host="127.0.0.1", port=8000)
  ```
  Set this script as your main file in Lightning EXE.
- **Try One-Dir Mode:** Sometimes, building as a folder (not a single file) helps. You can select this in the build options.
- **Experimental Mode:** Enable this in the Advanced tab to let Lightning EXE patch the environment. This is not guaranteed to work for all web apps.

### Summary Table
| Framework/Command         | Works with EXE? | Notes/Workaround                |
|--------------------------|-----------------|---------------------------------|
| Console/Tkinter/PyQt/etc | ✅              | Works out of the box            |
| Flask                    | ✅              | Works out of the box            |
| FastAPI (`uvicorn main:app`) | ❌          | Use programmatic entrypoint     |
| Streamlit (`streamlit run app.py`) | ❌   | Experimental, may need tweaks   |

### Why This Happens
These frameworks use dynamic imports and subprocesses that expect a normal Python environment. PyInstaller bundles code in a way that can break these assumptions. This is a limitation of Python packaging tools, not Lightning EXE specifically.

For more details and troubleshooting, see the [Lightning EXE Troubleshooting Guide](#) (coming soon).

---

Thank you for using Lightning EXE! We hope this documentation helps you get started and make the most of the application. If you have any questions or feedback, feel free to reach out!