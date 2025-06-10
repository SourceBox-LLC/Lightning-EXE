import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import subprocess
import tempfile
import shutil
import requests
import zipfile
import re
from pull_repo import clone_github_repo

class LightningEXE:
    def __init__(self, root):
        self.root = root
        self.root.title("Lightning EXE")
        self.root.geometry("700x600")
        
        # Define color scheme
        self.bg_color = "#1e1e2e"  # Dark blue-purple background
        self.accent_color = "#cba6f7"  # Light purple accent
        self.accent2_color = "#89b4fa"  # Light blue secondary accent
        self.text_color = "#cdd6f4"  # Light blue-gray text
        self.highlight_color = "#f38ba8"  # Soft pink highlight
        self.success_color = "#a6e3a1"  # Soft green for success
        
        # Configure the root window
        self.root.configure(bg=self.bg_color)
        
        # Make window resizable
        self.root.minsize(700, 600)
        
        # Set application style
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Configure styles for various widgets
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("TLabel", background=self.bg_color, foreground=self.text_color, font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", background=self.bg_color, foreground=self.accent_color, font=("Segoe UI", 24, "bold"))
        self.style.configure("Subheader.TLabel", background=self.bg_color, foreground=self.accent2_color, font=("Segoe UI", 12))
        
        # Button styles
        self.style.configure("TButton", background=self.accent_color, foreground=self.bg_color, font=("Segoe UI", 10, "bold"),
                            borderwidth=0, focusthickness=3, focuscolor=self.accent2_color)
        self.style.map("TButton", background=[("active", self.accent2_color), ("pressed", self.highlight_color)])
        
        # Primary action button style
        self.style.configure("Accent.TButton", background=self.accent_color, foreground=self.bg_color, font=("Segoe UI", 12, "bold"))
        self.style.map("Accent.TButton", background=[("active", self.highlight_color)])
        
        # Radiobutton styles
        self.style.configure("TRadiobutton", background=self.bg_color, foreground=self.text_color, font=("Segoe UI", 10))
        self.style.map("TRadiobutton", background=[("active", self.bg_color)],
                        indicatorcolor=[("selected", self.accent_color), ("!selected", self.text_color)])
        
        # Checkbutton styles
        self.style.configure("TCheckbutton", background=self.bg_color, foreground=self.text_color, font=("Segoe UI", 10))
        self.style.map("TCheckbutton", background=[("active", self.bg_color)])
        
        # Entry style
        self.style.configure("TEntry", fieldbackground="#313244", foreground=self.text_color, bordercolor=self.accent2_color, 
                           lightcolor=self.accent2_color, darkcolor=self.accent2_color)
        
        # Progressbar style
        self.style.configure("TProgressbar", background=self.accent_color, troughcolor="#313244", bordercolor=self.bg_color,
                           lightcolor=self.accent_color, darkcolor=self.accent_color)
        
        # Separator style
        self.style.configure("TSeparator", background=self.accent2_color)
        
        # LabelFrame style
        self.style.configure("TLabelframe", background=self.bg_color, foreground=self.text_color, bordercolor=self.accent2_color)
        self.style.configure("TLabelframe.Label", background=self.bg_color, foreground=self.accent2_color, font=("Segoe UI", 10, "bold"))
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main container with padding
        container = ttk.Frame(self.root, padding="20")
        container.pack(fill=tk.BOTH, expand=True)
        
        # Header section with logo and title
        header_frame = ttk.Frame(container)
        header_frame.pack(fill=tk.X, pady=(10, 20))
        
        # Add lightning bolt icon (text-based)
        icon_label = ttk.Label(header_frame, text="⚡", font=("Segoe UI", 36), style="Header.TLabel")
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Title and description in vertical stack next to icon
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)
        
        title_label = ttk.Label(title_frame, text="Lightning EXE", style="Header.TLabel")
        title_label.pack(anchor=tk.W)
        
        desc_label = ttk.Label(title_frame, text="Convert projects to executable files instantly", style="Subheader.TLabel")
        desc_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Add separator below header
        sep = ttk.Separator(container, orient="horizontal")
        sep.pack(fill=tk.X, pady=(0, 20))
        
        # Main content area - using a notebook for better organization
        main_notebook = ttk.Notebook(container)
        main_notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Configure notebook style
        self.style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        self.style.configure("TNotebook.Tab", background="#313244", foreground=self.text_color, padding=[10, 5], font=("Segoe UI", 9))
        self.style.map("TNotebook.Tab", background=[("selected", self.accent_color)], 
                       foreground=[("selected", self.bg_color)])
        
        # ===== INPUT SECTION =====
        input_frame = ttk.Frame(main_notebook, padding=15)
        main_notebook.add(input_frame, text=" Input Source ")
        
        # Input type selection with custom radio buttons
        input_type_frame = ttk.LabelFrame(input_frame, text="Select Source Type", padding=10)
        input_type_frame.pack(fill=tk.X, pady=(5, 15))
        
        self.input_type = tk.StringVar(value="file")
        
        # Use grid layout with proper spacing
        input_types_grid = ttk.Frame(input_type_frame)
        input_types_grid.pack(fill=tk.X, padx=5, pady=5)
        
        file_rb = ttk.Radiobutton(input_types_grid, text="Python File", variable=self.input_type, 
                                value="file", command=self.update_input_type)
        file_rb.grid(row=0, column=0, sticky=tk.W, padx=20, pady=10)
        
        folder_rb = ttk.Radiobutton(input_types_grid, text="Project Folder", variable=self.input_type, 
                                  value="folder", command=self.update_input_type)
        folder_rb.grid(row=0, column=1, sticky=tk.W, padx=20, pady=10)
        
        github_rb = ttk.Radiobutton(input_types_grid, text="GitHub Repository", variable=self.input_type, 
                                  value="github", command=self.update_input_type)
        github_rb.grid(row=0, column=2, sticky=tk.W, padx=20, pady=10)
        
        # Source selection frame
        source_frame = ttk.LabelFrame(input_frame, text="Source Location", padding=10)
        source_frame.pack(fill=tk.X, pady=10)
        
        # Dynamic content frame for input selection
        self.input_frame_content = ttk.Frame(source_frame, padding=5)
        self.input_frame_content.pack(fill=tk.X)
        
        # Path entry and browse button (default for file)
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(self.input_frame_content, textvariable=self.path_var, width=60)
        self.path_entry.grid(row=0, column=0, padx=5, pady=10, sticky=tk.EW)
        
        self.browse_button = ttk.Button(self.input_frame_content, text="Browse", command=self.browse_file, width=12)
        self.browse_button.grid(row=0, column=1, padx=5, pady=10)
        
        # Main file selection (hidden by default, shown for folder/GitHub)
        self.main_file_frame = ttk.Frame(input_frame)
        self.main_file_frame.pack(fill=tk.X, pady=10)
        self.main_file_frame.pack_forget()  # Hidden by default
        
        main_file_label_frame = ttk.LabelFrame(self.main_file_frame, text="Main Python File", padding=10)
        main_file_label_frame.pack(fill=tk.X)
        
        main_file_hint = ttk.Label(main_file_label_frame, 
                                 text="Specify the main Python file that should be executed (e.g., main.py, app.py)")
        main_file_hint.pack(anchor=tk.W, pady=(0, 10))
        
        main_file_entry_frame = ttk.Frame(main_file_label_frame)
        main_file_entry_frame.pack(fill=tk.X)
        
        self.main_file_var = tk.StringVar()
        main_file_entry = ttk.Entry(main_file_entry_frame, textvariable=self.main_file_var, width=30)
        main_file_entry.pack(side=tk.LEFT, padx=5, pady=5, expand=True, fill=tk.X)
        
        # ===== OUTPUT OPTIONS SECTION =====
        options_frame = ttk.Frame(main_notebook, padding=15)
        main_notebook.add(options_frame, text=" Build Options ")
        
        # Output directory
        output_dir_frame = ttk.LabelFrame(options_frame, text="Output Location", padding=10)
        output_dir_frame.pack(fill=tk.X, pady=(5, 15))
        
        output_dir_hint = ttk.Label(output_dir_frame, 
                                  text="Select where the executable will be saved")
        output_dir_hint.pack(anchor=tk.W, pady=(0, 10))
        
        output_dir_entry_frame = ttk.Frame(output_dir_frame)
        output_dir_entry_frame.pack(fill=tk.X)
        
        self.output_dir_var = tk.StringVar()
        output_dir_entry = ttk.Entry(output_dir_entry_frame, textvariable=self.output_dir_var, width=60)
        output_dir_entry.pack(side=tk.LEFT, padx=5, pady=5, expand=True, fill=tk.X)
        
        output_dir_button = ttk.Button(output_dir_entry_frame, text="Browse", command=self.browse_output_dir, width=12)
        output_dir_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Build options section
        packaging_frame = ttk.LabelFrame(options_frame, text="Packaging Options", padding=10)
        packaging_frame.pack(fill=tk.X, pady=15)
        
        # Option descriptions with icons
        self.onefile_var = tk.BooleanVar(value=True)
        onefile_frame = ttk.Frame(packaging_frame)
        onefile_frame.pack(fill=tk.X, pady=10)
        
        onefile_check = ttk.Checkbutton(onefile_frame, text="Create Single File Executable", 
                                      variable=self.onefile_var)
        onefile_check.pack(side=tk.LEFT)
        
        onefile_info = ttk.Label(onefile_frame, text="(Easier distribution, slower startup time)")
        onefile_info.pack(side=tk.LEFT, padx=10)
        
        self.console_var = tk.BooleanVar(value=False)
        console_frame = ttk.Frame(packaging_frame)
        console_frame.pack(fill=tk.X, pady=10)
        
        console_check = ttk.Checkbutton(console_frame, text="Show Console Window", 
                                      variable=self.console_var)
        console_check.pack(side=tk.LEFT)
        
        console_info = ttk.Label(console_frame, text="(Shows command output, useful for debugging)")
        console_info.pack(side=tk.LEFT, padx=10)
        
        # Build section
        build_frame = ttk.Frame(container, padding=(0, 10))
        build_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Progress bar and status
        progress_frame = ttk.Frame(build_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, mode='indeterminate')
        self.progress.pack(fill=tk.X)
        
        status_frame = ttk.Frame(progress_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        status_icon = ttk.Label(status_frame, text="ℹ️", foreground=self.accent2_color)
        status_icon.pack(side=tk.LEFT)
        
        self.status_var = tk.StringVar(value="Ready to build")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(side=tk.LEFT, padx=5)
        
        # Build button
        self.build_button = ttk.Button(
            build_frame, 
            text="⚡ BUILD EXECUTABLE", 
            command=self.build_executable, 
            style="Accent.TButton",
            padding=(20, 10)
        )
        self.build_button.pack(pady=10)
        
        # Initialize UI based on default selection
        self.update_input_type()
    
    def update_input_type(self):
        # Clear the frame
        for widget in self.input_frame_content.winfo_children():
            widget.destroy()
        
        input_type = self.input_type.get()
        
        if input_type == "file":
            # Path entry and browse button for file
            self.path_var = tk.StringVar()
            
            file_label = ttk.Label(self.input_frame_content, text="Select Python File:")
            file_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=(5, 0))
            
            input_row = ttk.Frame(self.input_frame_content)
            input_row.grid(row=1, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=5)
            
            self.path_entry = ttk.Entry(input_row, textvariable=self.path_var, width=60)
            self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
            
            self.browse_button = ttk.Button(input_row, text="Browse", command=self.browse_file, width=12)
            self.browse_button.pack(side=tk.RIGHT)
            
            # Hide main file option
            self.main_file_frame.pack_forget()
        
        elif input_type == "folder":
            # Path entry and browse button for folder
            self.path_var = tk.StringVar()
            
            folder_label = ttk.Label(self.input_frame_content, text="Select Project Folder:")
            folder_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=(5, 0))
            
            input_row = ttk.Frame(self.input_frame_content)
            input_row.grid(row=1, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=5)
            
            self.path_entry = ttk.Entry(input_row, textvariable=self.path_var, width=60)
            self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
            
            self.browse_button = ttk.Button(input_row, text="Browse", command=self.browse_folder, width=12)
            self.browse_button.pack(side=tk.RIGHT)
            
            # Show main file option
            self.main_file_frame.pack(fill=tk.X, pady=10)
        
        elif input_type == "github":
            # GitHub URL entry
            gh_label = ttk.Label(self.input_frame_content, text="Enter GitHub Repository URL:")
            gh_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=(5, 0))
            
            gh_hint = ttk.Label(self.input_frame_content, 
                               text="Example: https://github.com/username/repository",
                               foreground=self.accent2_color, font=("Segoe UI", 8))
            gh_hint.grid(row=1, column=0, sticky=tk.W, padx=5, pady=(0, 10))
            
            self.path_var = tk.StringVar()
            self.path_entry = ttk.Entry(self.input_frame_content, textvariable=self.path_var, width=60)
            self.path_entry.grid(row=2, column=0, padx=5, pady=5, sticky=tk.EW)
            
            # Show main file option
            self.main_file_frame.pack(fill=tk.X, pady=10)
    
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Python File",
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        if file_path:
            self.path_var.set(file_path)
    
    def browse_folder(self):
        folder_path = filedialog.askdirectory(title="Select Project Folder")
        if folder_path:
            self.path_var.set(folder_path)
    
    def browse_output_dir(self):
        output_dir = filedialog.askdirectory(title="Select Output Directory")
        if output_dir:
            self.output_dir_var.set(output_dir)
    
    def validate_inputs(self):
        input_type = self.input_type.get()
        path = self.path_var.get().strip()
        
        if not path:
            messagebox.showerror("Error", "Please provide a valid input path")
            return False
        
        # Validate based on input type
        if input_type == "file" and not path.endswith('.py'):
            messagebox.showerror("Error", "Selected file must be a Python file (.py)")
            return False
        
        if input_type == "github":
            # Simple GitHub URL validation
            if not (path.startswith("https://github.com/") or path.startswith("http://github.com/")):
                messagebox.showerror("Error", "Please enter a valid GitHub repository URL")
                return False
            
            # Additional validation could be added here
        
        # Check if main file is specified for folder/github
        if input_type in ("folder", "github") and not self.main_file_var.get().strip():
            messagebox.showerror("Error", "Please specify the main Python file")
            return False
        
        # Validate output directory
        output_dir = self.output_dir_var.get().strip()
        if not output_dir:
            messagebox.showerror("Error", "Please specify an output directory")
            return False
        
        if not os.path.isdir(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create output directory: {str(e)}")
                return False
        
        return True
    
    def build_executable(self):
        if not self.validate_inputs():
            return
        
        # Disable the build button and show progress
        self.build_button.configure(state="disabled")
        self.progress.start(10)  # Smoother animation
        
        # Reset status display to show building
        self.update_status("Initializing build process...", "info")
        
        # Start the build process in a separate thread
        build_thread = threading.Thread(target=self.run_build_process)
        build_thread.daemon = True
        build_thread.start()
    
    def run_build_process(self):
        try:
            input_type = self.input_type.get()
            path = self.path_var.get().strip()
            output_dir = self.output_dir_var.get().strip()
            main_file = self.main_file_var.get().strip()
            
            # Create a temporary directory for processing
            self.update_status("Preparing build environment...", "info")
            temp_dir = tempfile.mkdtemp()
            
            try:
                # Process based on input type
                if input_type == "file":
                    # For single file, we can directly use it
                    self.update_status("Using single Python file as source...", "info")
                    source_file = path
                    
                elif input_type == "folder":
                    # For folder, copy the contents to the temp directory
                    self.update_status("Copying project files...", "info")
                    self.copy_directory(path, temp_dir)
                    source_file = os.path.join(temp_dir, main_file)
                    self.update_status(f"Project files copied. Using '{main_file}' as entry point.", "info")
                    
                elif input_type == "github":
                    # For GitHub, clone the repository
                    self.update_status("Connecting to GitHub...", "info")
                    repo_dir = self.download_github_repo(path, temp_dir)
                    if not repo_dir or not os.path.exists(repo_dir):
                        raise Exception("Failed to clone GitHub repository")
                    
                    self.update_status(f"GitHub repository cloned successfully. Using '{main_file}' as entry point.", "info")
                    source_file = os.path.join(repo_dir, main_file)
                
                # Run PyInstaller
                self.update_status("Starting PyInstaller build process...", "info")
                self.run_pyinstaller(source_file, output_dir)
                
                # Build completed successfully
                self.update_status("Build completed successfully!", "success")
                
                # Calculate executable path to show in message
                if self.onefile_var.get():
                    exe_name = os.path.splitext(os.path.basename(source_file))[0] + ".exe"
                    exe_path = os.path.join(output_dir, exe_name)
                    success_msg = f"Executable created successfully!\n\nLocation: {exe_path}"
                else:
                    exe_dir = os.path.splitext(os.path.basename(source_file))[0]
                    exe_path = os.path.join(output_dir, exe_dir)
                    success_msg = f"Executable folder created successfully!\n\nLocation: {exe_path}"
                
                messagebox.showinfo("Success", success_msg)
                
            finally:
                # Clean up temporary directory
                try:
                    self.update_status("Cleaning up temporary files...", "info")
                    shutil.rmtree(temp_dir)
                except Exception:
                    pass
        
        except Exception as e:
            error_msg = str(e)
            self.update_status(f"Error: {error_msg}", "error")
            messagebox.showerror("Error", f"Failed to build executable:\n\n{error_msg}")
        
        finally:
            # Re-enable the build button and stop progress
            self.root.after(0, lambda: self.build_button.configure(state="normal"))
            self.root.after(0, self.progress.stop)
    
    def update_status(self, message, status_type="info"):
        """Update the status bar with message and appropriate styling
        
        Args:
            message: The status message to display
            status_type: One of 'info', 'success', 'warning', 'error'
        """
        def _update():
            # Set message text
            self.status_var.set(message)
            
            # Set appropriate icon and color based on status_type
            status_icon = status_frame.winfo_children()[0]
            if status_type == "info":
                status_icon.configure(text="ℹ️", foreground=self.accent2_color)
            elif status_type == "success":
                status_icon.configure(text="✅", foreground=self.success_color)
            elif status_type == "warning":
                status_icon.configure(text="⚠️", foreground=self.highlight_color)
            elif status_type == "error":
                status_icon.configure(text="❌", foreground=self.highlight_color)
        
        # Schedule the update on the main thread
        status_frame = self.progress.master.winfo_children()[1]
        self.root.after(0, _update)
    
    def copy_directory(self, src, dst):
        """Copy the contents of src directory to dst directory"""
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                os.makedirs(d, exist_ok=True)
                self.copy_directory(s, d)
            else:
                shutil.copy2(s, d)
    
    def download_github_repo(self, github_url, dest_dir):
        """Clone a GitHub repository using git"""
        try:
            # Create a subdirectory for the repository
            repo_dir = os.path.join(dest_dir, "repo")
            
            # Call the clone_github_repo function from pull_repo.py
            clone_github_repo(github_url, repo_dir)
            
            return repo_dir
        except Exception as e:
            raise Exception(f"Error cloning GitHub repository: {str(e)}")
    
    def run_pyinstaller(self, source_file, output_dir):
        """Run PyInstaller to create an executable"""
        # Check if PyInstaller is already installed and available
        try:
            # Check if PyInstaller is already installed by running a simple version check
            version_check = subprocess.run(
                [sys.executable, "-m", "PyInstaller", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            self.update_status(f"Found PyInstaller version: {version_check.stdout.strip()}")
        except (subprocess.SubprocessError, FileNotFoundError):
            # If PyInstaller is not installed or the check fails, try to install it
            self.update_status("Installing PyInstaller...")
            try:
                install_result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "pyinstaller"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if install_result.returncode != 0:
                    error_msg = install_result.stderr or "Unknown error during installation"
                    raise Exception(f"Failed to install PyInstaller: {error_msg}")
            except subprocess.TimeoutExpired:
                raise Exception("PyInstaller installation timed out. Please install it manually: pip install pyinstaller")
            except Exception as e:
                raise Exception(f"Failed to install PyInstaller: {str(e)}")
        
        # Prepare PyInstaller command
        self.update_status("Configuring PyInstaller...")
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--distpath", output_dir,
            "--workpath", os.path.join(output_dir, "build")
        ]
        
        # Add options
        if self.onefile_var.get():
            cmd.append("--onefile")
        else:
            cmd.append("--onedir")
        
        if not self.console_var.get():
            cmd.append("--noconsole")
        
        # Add the source file
        cmd.append(source_file)
        
        # Run PyInstaller
        self.update_status("Running PyInstaller to build executable...")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5 minute timeout
            
            if result.returncode != 0:
                error_message = result.stderr or "Unknown error"
                raise Exception(f"PyInstaller failed: {error_message}")
                
            self.update_status("PyInstaller completed successfully!")
        except subprocess.TimeoutExpired:
            raise Exception("PyInstaller build process timed out. The build may be too complex or your system may be under heavy load.")
        except Exception as e:
            if "No module named 'PyInstaller'" in str(e):
                raise Exception("PyInstaller is not installed correctly. Please install it manually: pip install pyinstaller")
            raise

if __name__ == "__main__":
    import sys
    
    # Check Python version
    if sys.version_info < (3, 6):
        print("Python 3.6 or higher is required!")
        sys.exit(1)
    
    # Make sure we have the sys module available globally
    # since it's needed by run_pyinstaller
    root = tk.Tk()
    app = LightningEXE(root)
    
    # Set a custom icon if available
    try:
        root.iconbitmap("lightning_icon.ico")
    except:
        pass
    
    root.mainloop()
