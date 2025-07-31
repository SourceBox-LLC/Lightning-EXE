import flet as ft
import os
import threading
import subprocess
import tempfile
import shutil
import requests
import zipfile
import re
import sys
import venv
from pull_repo import clone_github_repo
import cmd_args_helper


class LightningEXEFlet:
    def __init__(self):
        # Initialize state variables
        self.env_vars = []  # List to store environment variables as (key, value) tuples
        self.cmd_args = ""
        self.extra_packages = ""
        self.input_type = "file"
        self.source_path = ""
        self.main_file = ""
        self.output_dir = ""
        self.onefile = True
        self.console = True
        self.detected_special = False
        self.detected_framework = None
        self.experimental_mode_enabled = False
        
        # UI references
        self.page = None
        self.status_text = None
        self.progress_bar = None
        self.build_button = None
        
    def main(self, page: ft.Page):
        self.page = page
        page.title = "Lightning EXE"
        page.theme_mode = ft.ThemeMode.DARK
        page.window_width = 800
        page.window_height = 700
        page.window_min_width = 700
        page.window_min_height = 600
        page.padding = 20
        
        # Create the main UI
        self.create_ui()
        
    def create_ui(self):
        # Header section with reset button
        header = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.FLASH_ON, size=40, color=ft.Colors.PURPLE_400),
                ft.Column([
                    ft.Text("Lightning EXE", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_400),
                    ft.Text("Convert projects to executable files instantly", size=14, color=ft.Colors.GREY_400)
                ], spacing=2, expand=True),
                ft.ElevatedButton(
                    text="Reset",
                    icon=ft.Icons.REFRESH,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.ORANGE_600,
                        color=ft.Colors.WHITE,
                        padding=ft.padding.all(10)
                    ),
                    on_click=self.reset_application,
                    tooltip="Reset all fields and start over"
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.only(bottom=20)
        )
        
        # Create tabs for different sections
        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Input Source",
                    icon=ft.Icons.SOURCE,
                    content=self.create_input_tab()
                ),
                ft.Tab(
                    text="Build Options", 
                    icon=ft.Icons.SETTINGS,
                    content=self.create_options_tab()
                ),
                ft.Tab(
                    text="Advanced",
                    icon=ft.Icons.TUNE,
                    content=self.create_advanced_tab()
                )
            ],
            expand=True
        )
        
        # Status and build section
        status_section = self.create_status_section()
        
        # Add all components to page
        self.page.add(
            header,
            ft.Divider(),
            tabs,
            ft.Divider(),
            status_section
        )
        
    def create_input_tab(self):
        # Input type selection with better spacing
        self.input_type_group = ft.RadioGroup(
            content=ft.Column([
                ft.Radio(value="file", label="Python File"),
                ft.Radio(value="folder", label="Project Folder"),
                ft.Radio(value="github", label="GitHub Repository")
            ], spacing=10),
            value="file",
            on_change=self.on_input_type_change
        )
        
        # Source path input
        self.source_path_field = ft.TextField(
            label="Source Path",
            hint_text="Select a Python file, folder, or enter GitHub URL",
            expand=True,
            on_change=self.on_source_path_change,
            value=""
        )
        
        self.browse_button = ft.ElevatedButton(
            text="Browse",
            icon=ft.Icons.FOLDER_OPEN,
            on_click=self.browse_source,
            width=100
        )
        
        source_row = ft.Row([
            self.source_path_field,
            self.browse_button
        ], spacing=10)
        
        # Main file selection (for folders and GitHub)
        self.main_file_field = ft.TextField(
            label="Main Python File",
            hint_text="e.g., main.py, app.py",
            visible=False,
            on_change=self.on_main_file_change,
            value=""
        )
        
        # Create the main content with proper structure
        content_column = ft.Column([
            ft.Container(
                content=ft.Column([
                    ft.Text("Select Source Type", size=16, weight=ft.FontWeight.BOLD),
                    self.input_type_group,
                ], spacing=10),
                padding=ft.padding.all(10),
                border=ft.border.all(1, ft.Colors.OUTLINE),
                border_radius=8
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("Source Location", size=16, weight=ft.FontWeight.BOLD),
                    source_row,
                    self.main_file_field,
                ], spacing=10),
                padding=ft.padding.all(10),
                border=ft.border.all(1, ft.Colors.OUTLINE),
                border_radius=8
            )
        ], spacing=20)
        
        return ft.Container(
            content=content_column,
            padding=20,
            expand=True
        )
        
    def create_options_tab(self):
        # Output directory
        self.output_dir_field = ft.TextField(
            label="Output Directory",
            hint_text="Where to save the executable",
            expand=True,
            on_change=self.on_output_dir_change,
            value=""
        )
        
        output_browse_button = ft.ElevatedButton(
            text="Browse",
            icon=ft.Icons.FOLDER_OPEN,
            on_click=self.browse_output_dir
        )
        
        output_row = ft.Row([
            self.output_dir_field,
            output_browse_button
        ], spacing=10)
        
        # Build options
        self.onefile_checkbox = ft.Checkbox(
            label="Create single executable file (--onefile)",
            value=True,
            on_change=self.on_onefile_change
        )
        
        self.console_checkbox = ft.Checkbox(
            label="Show console window",
            value=True,
            on_change=self.on_console_change
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Output Settings", size=16, weight=ft.FontWeight.BOLD),
                output_row,
                ft.Divider(),
                ft.Text("Build Options", size=16, weight=ft.FontWeight.BOLD),
                self.onefile_checkbox,
                self.console_checkbox,
            ], spacing=15),
            padding=20
        )
        
    def create_advanced_tab(self):
        # Environment Variables section
        env_vars_section = ft.ExpansionTile(
            title=ft.Text("Environment Variables"),
            subtitle=ft.Text("Add environment variables to your executable"),
            controls=[
                self.create_env_vars_content()
            ]
        )
        
        # Command Line Arguments section
        self.cmd_args_field = ft.TextField(
            label="Command Line Arguments",
            hint_text="Additional arguments to pass to your application",
            multiline=True,
            min_lines=2,
            max_lines=4,
            on_change=self.on_cmd_args_change
        )
        
        # Extra Packages section
        self.extra_packages_field = ft.TextField(
            label="Extra Packages",
            hint_text="Additional packages to include (comma-separated)",
            on_change=self.on_extra_packages_change
        )
        
        return ft.Container(
            content=ft.Column([
                env_vars_section,
                ft.Divider(),
                ft.Text("Command Line Arguments", size=16, weight=ft.FontWeight.BOLD),
                self.cmd_args_field,
                ft.Divider(),
                ft.Text("Extra Packages", size=16, weight=ft.FontWeight.BOLD),
                self.extra_packages_field,
            ], spacing=15, scroll=ft.ScrollMode.AUTO),
            padding=20
        )
        
    def create_env_vars_content(self):
        self.env_vars_list = ft.Column(spacing=10)
        
        # Add new env var controls
        self.new_env_key = ft.TextField(label="Key", width=200)
        self.new_env_value = ft.TextField(label="Value", width=300)
        add_env_button = ft.ElevatedButton(
            text="Add",
            icon=ft.Icons.ADD,
            on_click=self.add_env_var
        )
        
        add_env_row = ft.Row([
            self.new_env_key,
            self.new_env_value,
            add_env_button
        ], spacing=10)
        
        return ft.Column([
            add_env_row,
            ft.Divider(),
            self.env_vars_list
        ], spacing=10)
        
    def create_status_section(self):
        # Status text area
        self.status_text = ft.TextField(
            label="Build Status",
            multiline=True,
            min_lines=8,
            max_lines=8,
            read_only=True,
            value="Ready to build executable...",
        )
        
        # Progress bar
        self.progress_bar = ft.ProgressBar(
            width=400,
            visible=False
        )
        
        # Build button
        self.build_button = ft.ElevatedButton(
            text="Build Executable",
            icon=ft.Icons.BUILD,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.PURPLE_600,
                color=ft.Colors.WHITE,
                padding=ft.padding.all(15)
            ),
            on_click=self.start_build
        )
        
        return ft.Container(
            content=ft.Column([
                self.status_text,
                self.progress_bar,
                ft.Row([
                    self.build_button
                ], alignment=ft.MainAxisAlignment.CENTER)
            ], spacing=15),
            padding=20
        )
        
    # Event handlers
    def on_input_type_change(self, e):
        self.input_type = e.control.value
        print(f"Input type changed to: {self.input_type}")
        
        # Show/hide main file field for folder and GitHub options
        if self.input_type in ["folder", "github"]:
            self.main_file_field.visible = True
            if self.input_type == "github":
                self.source_path_field.hint_text = "Enter GitHub repository URL"
                self.source_path_field.label = "GitHub Repository URL"
                self.browse_button.visible = False
            else:
                self.source_path_field.hint_text = "Select project folder"
                self.source_path_field.label = "Project Folder"
                self.browse_button.visible = True
        else:
            self.main_file_field.visible = False
            self.source_path_field.hint_text = "Select a Python file"
            self.source_path_field.label = "Python File"
            self.browse_button.visible = True
            
        # Clear the current value when switching types
        self.source_path_field.value = ""
        self.main_file_field.value = ""
        self.source_path = ""
        self.main_file = ""
        
        self.page.update()
        
    def on_source_path_change(self, e):
        self.source_path = e.control.value
        print(f"Source path changed to: {self.source_path}")
        
    def on_main_file_change(self, e):
        self.main_file = e.control.value
        
    def on_output_dir_change(self, e):
        self.output_dir = e.control.value
        
    def on_onefile_change(self, e):
        self.onefile = e.control.value
        
    def on_console_change(self, e):
        self.console = e.control.value
        
    def on_cmd_args_change(self, e):
        self.cmd_args = e.control.value
        
    def on_extra_packages_change(self, e):
        self.extra_packages = e.control.value
        
    def browse_source(self, e):
        def file_result(e: ft.FilePickerResultEvent):
            print(f"File picker result: {e.files}")
            if e.files:
                selected_path = e.files[0].path
                print(f"Selected file: {selected_path}")
                self.source_path_field.value = selected_path
                self.source_path = selected_path
                self.page.update()
                print(f"Updated field value: {self.source_path_field.value}")
                
        def folder_result(e: ft.FilePickerResultEvent):
            print(f"Folder picker result: {e.path}")
            if e.path:
                selected_path = e.path
                print(f"Selected folder: {selected_path}")
                self.source_path_field.value = selected_path
                self.source_path = selected_path
                self.page.update()
                print(f"Updated field value: {self.source_path_field.value}")
            
        if self.input_type == "file":
            file_picker = ft.FilePicker(on_result=file_result)
            self.page.overlay.append(file_picker)
            self.page.update()
            file_picker.pick_files(
                dialog_title="Select Python file",
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["py"]
            )
        else:  # folder
            folder_picker = ft.FilePicker(on_result=folder_result)
            self.page.overlay.append(folder_picker)
            self.page.update()
            folder_picker.get_directory_path(dialog_title="Select project folder")
            
    def browse_output_dir(self, e):
        def result(e: ft.FilePickerResultEvent):
            if e.path:
                self.output_dir_field.value = e.path
                self.output_dir = e.path
                self.page.update()
                
        file_picker = ft.FilePicker(on_result=result)
        self.page.overlay.append(file_picker)
        self.page.update()
        file_picker.get_directory_path(dialog_title="Select output directory")
        
    def add_env_var(self, e):
        key = self.new_env_key.value.strip()
        value = self.new_env_value.value.strip()
        
        if key and value:
            self.env_vars.append((key, value))
            
            # Create a row for the new environment variable
            env_var_row = ft.Row([
                ft.Text(f"{key}:", width=150, weight=ft.FontWeight.BOLD),
                ft.Text(value, expand=True),
                ft.IconButton(
                    icon=ft.Icons.DELETE,
                    icon_color=ft.Colors.RED_400,
                    tooltip="Remove",
                    on_click=lambda e, k=key: self.remove_env_var(k)
                )
            ])
            
            self.env_vars_list.controls.append(env_var_row)
            
            # Clear input fields
            self.new_env_key.value = ""
            self.new_env_value.value = ""
            
            self.page.update()
            
    def remove_env_var(self, key):
        # Remove from list
        self.env_vars = [(k, v) for k, v in self.env_vars if k != key]
        
        # Rebuild the UI list
        self.env_vars_list.controls.clear()
        for k, v in self.env_vars:
            env_var_row = ft.Row([
                ft.Text(f"{k}:", width=150, weight=ft.FontWeight.BOLD),
                ft.Text(v, expand=True),
                ft.IconButton(
                    icon=ft.Icons.DELETE,
                    icon_color=ft.Colors.RED_400,
                    tooltip="Remove",
                    on_click=lambda e, key=k: self.remove_env_var(key)
                )
            ])
            self.env_vars_list.controls.append(env_var_row)
            
        self.page.update()
        
    def reset_application(self, e):
        """Reset all form fields and application state"""
        try:
            # Reset all state variables
            self.env_vars = []
            self.cmd_args = ""
            self.extra_packages = ""
            self.input_type = "file"
            self.source_path = ""
            self.main_file = ""
            self.output_dir = ""
            self.onefile = True
            self.console = True
            self.detected_special = False
            self.detected_framework = None
            self.experimental_mode_enabled = False
            
            # Reset UI fields
            if hasattr(self, 'source_path_field'):
                self.source_path_field.value = ""
                self.source_path_field.label = "Source Path"
                self.source_path_field.hint_text = "Select a Python file, folder, or enter GitHub URL"
                
            if hasattr(self, 'main_file_field'):
                self.main_file_field.value = ""
                self.main_file_field.visible = False
                
            if hasattr(self, 'output_dir_field'):
                self.output_dir_field.value = ""
                
            if hasattr(self, 'onefile_checkbox'):
                self.onefile_checkbox.value = True
                
            if hasattr(self, 'console_checkbox'):
                self.console_checkbox.value = True
                
            if hasattr(self, 'cmd_args_field'):
                self.cmd_args_field.value = ""
                
            if hasattr(self, 'extra_packages_field'):
                self.extra_packages_field.value = ""
                
            if hasattr(self, 'new_env_key'):
                self.new_env_key.value = ""
                
            if hasattr(self, 'new_env_value'):
                self.new_env_value.value = ""
                
            # Reset input type radio group
            if hasattr(self, 'input_type_group'):
                self.input_type_group.value = "file"
                
            # Clear environment variables list
            if hasattr(self, 'env_vars_list'):
                self.env_vars_list.controls.clear()
                
            # Reset status
            if hasattr(self, 'status_text'):
                self.status_text.value = "Ready to build executable..."
                
            # Hide progress bar
            if hasattr(self, 'progress_bar'):
                self.progress_bar.visible = False
                
            # Re-enable build button
            if hasattr(self, 'build_button'):
                self.build_button.disabled = False
                
            # Show browse button
            if hasattr(self, 'browse_button'):
                self.browse_button.visible = True
                
            self.update_status("Application reset successfully! Ready for new build.", "success")
            self.page.update()
            
        except Exception as ex:
            self.update_status(f"Error during reset: {str(ex)}", "error")
        
    def update_status(self, message, status_type="info"):
        """Update the status text area with new message"""
        current_text = self.status_text.value
        timestamp = __import__('datetime').datetime.now().strftime("%H:%M:%S")
        
        status_icons = {
            "info": "ℹ️",
            "success": "✅", 
            "warning": "⚠️",
            "error": "❌"
        }
        
        icon = status_icons.get(status_type, "ℹ️")
        new_line = f"[{timestamp}] {icon} {message}"
        
        if current_text.strip() == "Ready to build executable...":
            self.status_text.value = new_line
        else:
            self.status_text.value = current_text + "\n" + new_line
            
        self.page.update()
        
    def start_build(self, e):
        """Start the build process in a separate thread"""
        if not self.validate_inputs():
            return
            
        # Disable build button and show progress
        self.build_button.disabled = True
        self.progress_bar.visible = True
        self.page.update()
        
        # Start build in separate thread
        build_thread = threading.Thread(target=self.build_executable)
        build_thread.daemon = True
        build_thread.start()
        
    def validate_inputs(self):
        """Validate user inputs before building"""
        if not self.source_path:
            self.update_status("Please select a source file, folder, or GitHub URL", "error")
            return False
            
        if self.input_type in ["folder", "github"] and not self.main_file:
            self.update_status("Please specify the main Python file", "error")
            return False
            
        if not self.output_dir:
            self.update_status("Please select an output directory", "error")
            return False
            
        return True
        
    def build_executable(self):
        """Main build process - runs in separate thread"""
        try:
            self.update_status("Starting build process...", "info")
            
            # Prepare source
            if self.input_type == "file":
                source_file = self.source_path
                source_dir = os.path.dirname(source_file)
            elif self.input_type == "folder":
                source_dir = self.source_path
                source_file = os.path.join(source_dir, self.main_file)
            else:  # github
                self.update_status("Cloning GitHub repository...", "info")
                temp_dir = tempfile.mkdtemp()
                source_dir = self.download_github_repo(self.source_path, temp_dir)
                source_file = os.path.join(source_dir, self.main_file)
                
            if not os.path.exists(source_file):
                raise Exception(f"Main file not found: {source_file}")
                
            self.update_status(f"Source file: {source_file}", "info")
            
            # Create output directory
            os.makedirs(self.output_dir, exist_ok=True)
            
            # Run PyInstaller
            self.update_status("Running PyInstaller...", "info")
            self.run_pyinstaller(source_file, self.output_dir)
            
            self.update_status("Build completed successfully! 🎉", "success")
            
        except Exception as e:
            self.update_status(f"Build failed: {str(e)}", "error")
        finally:
            # Re-enable build button and hide progress
            self.build_button.disabled = False
            self.progress_bar.visible = False
            self.page.update()
            
    def parse_requirements_file(self, requirements_path):
        """Parse a requirements.txt file and return a list of package names"""
        packages = []
        try:
            with open(requirements_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    # Skip -r or -f flags
                    if line.startswith('-r') or line.startswith('-f') or line.startswith('--'):
                        continue
                    # Extract package name (remove version specifiers)
                    package_name = re.split(r'[>=<!=~]', line)[0].strip()
                    # Remove any extra characters
                    package_name = re.sub(r'[\[\]\s].*$', '', package_name)
                    if package_name:
                        packages.append(package_name)
        except Exception as e:
            self.update_status(f"Warning: Could not parse {requirements_path}: {e}", "warning")
        return packages
            
    def download_github_repo(self, github_url, dest_dir):
        """Clone a GitHub repository using git"""
        try:
            repo_dir = os.path.join(dest_dir, "repo")
            clone_github_repo(github_url, repo_dir)
            return repo_dir
        except Exception as e:
            raise Exception(f"Error cloning GitHub repository: {str(e)}")
            
    def run_pyinstaller(self, source_file, output_dir, python_exe=None, custom_cmd=None):
        """Run PyInstaller to create an executable"""
        if python_exe is None:
            python_exe = sys.executable
            
        # Check if PyInstaller is installed
        try:
            version_check = subprocess.run(
                [python_exe, "-m", "PyInstaller", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            self.update_status(f"Found PyInstaller version: {version_check.stdout.strip()}")
        except (subprocess.SubprocessError, FileNotFoundError):
            self.update_status("Installing PyInstaller...", "info")
            try:
                subprocess.run([python_exe, "-m", "pip", "install", "pyinstaller"], check=True)
            except subprocess.CalledProcessError:
                raise Exception("Failed to install PyInstaller")
                
        # Auto-detect and install dependencies from requirements.txt
        project_dir = os.path.dirname(source_file)
        requirements_files = []
        
        # Look for requirements files in the project directory
        for req_file in ["requirements.txt", "requirements.pip", "reqs.txt"]:
            req_path = os.path.join(project_dir, req_file)
            if os.path.exists(req_path):
                requirements_files.append(req_path)
                
        if requirements_files:
            self.update_status(f"Found requirements files: {', '.join([os.path.basename(f) for f in requirements_files])}", "info")
            
            # Parse and install requirements
            all_packages = set()
            for req_file in requirements_files:
                packages = self.parse_requirements_file(req_file)
                all_packages.update(packages)
                
            if all_packages:
                self.update_status(f"Installing {len(all_packages)} dependencies...", "info")
                try:
                    # Install all requirements
                    for req_file in requirements_files:
                        subprocess.run([python_exe, "-m", "pip", "install", "-r", req_file], 
                                     check=True, capture_output=True, text=True)
                    self.update_status("Dependencies installed successfully", "success")
                except subprocess.CalledProcessError as e:
                    self.update_status(f"Warning: Some dependencies may not have installed: {e}", "warning")
        else:
            self.update_status("No requirements.txt file found in project directory", "info")
                
        # Prepare PyInstaller command
        cmd = [
            python_exe, "-m", "PyInstaller",
            "--distpath", output_dir,
            "--workpath", os.path.join(output_dir, "build"),
            "--specpath", output_dir
        ]
        
        # Add onefile/onedir option
        if self.onefile:
            cmd.append("--onefile")
        else:
            cmd.append("--onedir")
            
        # Add console/no-console option
        if not self.console:
            cmd.append("--windowed")
            
        # Add hidden imports for required modules
        cmd.extend(["--hidden-import", "dotenv"])
        
        # Add dependencies from requirements.txt as hidden imports
        if requirements_files:
            all_packages = set()
            for req_file in requirements_files:
                packages = self.parse_requirements_file(req_file)
                all_packages.update(packages)
            
            for package in all_packages:
                cmd.extend(["--hidden-import", package])
                self.update_status(f"Adding hidden import: {package}")
                
            # Also try to collect data files for common packages that need them
            data_packages = ['pygame', 'tkinter', 'PIL', 'numpy', 'scipy', 'matplotlib']
            for package in all_packages:
                if package.lower() in [p.lower() for p in data_packages]:
                    cmd.extend(["--collect-all", package])
                    self.update_status(f"Collecting all files for: {package}")
        
        # Add environment variables if defined
        if self.env_vars:
            env_vars_str = "{" + ", ".join([f"'{k}': '{v}'" for k, v in self.env_vars]) + "}"
            cmd.extend(["--add-data", f"env_vars.py:."])
            
            # Create temporary env_vars.py file
            env_vars_dir = os.path.dirname(source_file)
            env_vars_path = os.path.join(env_vars_dir, "env_vars.py")
            
            with open(env_vars_path, "w") as f:
                f.write(f"# Environment variables for Lightning EXE\n")
                f.write(f"import os\n\n")
                f.write(f"_env_vars = {env_vars_str}\n\n")
                f.write(f"def init_env_vars():\n")
                f.write(f"    for key, value in _env_vars.items():\n")
                f.write(f"        os.environ[key] = value\n\n")
                f.write(f"init_env_vars()\n")
                
        # Add extra packages
        if self.extra_packages:
            packages = [pkg.strip() for pkg in self.extra_packages.split(",") if pkg.strip()]
            for pkg in packages:
                cmd.extend(["--hidden-import", pkg])
                
        # Add command line arguments
        if self.cmd_args:
            # Parse and add command line arguments using cmd_args_helper
            try:
                args = cmd_args_helper.parse_args(self.cmd_args)
                cmd.extend(args)
            except Exception as e:
                self.update_status(f"Warning: Could not parse command line arguments: {e}", "warning")
                
        # Add the source file
        cmd.append(source_file)
        
        # Run PyInstaller
        self.update_status(f"Running command: {' '.join(cmd)}", "info")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True
        )
        
        # Stream output
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                self.update_status(output.strip())
                
        rc = process.poll()
        if rc != 0:
            raise Exception(f"PyInstaller failed with return code {rc}")


def main(page: ft.Page):
    app = LightningEXEFlet()
    app.main(page)


if __name__ == "__main__":
    ft.app(target=main)
