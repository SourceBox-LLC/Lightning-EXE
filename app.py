import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import subprocess
import cmd_args_helper
import tempfile
import shutil
import requests
import zipfile
import re
from pull_repo import clone_github_repo
import sys
import venv

class LightningEXE:
    def __init__(self, root):
        self.root = root
        self.root.title("Lightning EXE")
        self.root.geometry("700x600")
        
        # Initialize environment variables list
        self.env_vars = []  # List to store environment variables as (key, value) tuples
        
        # Initialize command line arguments
        self.cmd_args_var = tk.StringVar()
        
        # Initialize extra packages
        self.extra_packages_var = tk.StringVar()
        
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
        
        # ===== ADVANCED OPTIONS SECTION =====
        advanced_frame = ttk.Frame(main_notebook, padding=15)
        main_notebook.add(advanced_frame, text=" Advanced ")
        
        # Create a notebook inside the advanced tab for sub-sections
        advanced_notebook = ttk.Notebook(advanced_frame)
        advanced_notebook.pack(fill=tk.BOTH, expand=True)
        
        # ===== ENVIRONMENT VARIABLES SECTION (now in Advanced tab) =====
        env_vars_frame = ttk.Frame(advanced_notebook, padding=15)
        advanced_notebook.add(env_vars_frame, text=" Environment Variables ")
        
        # ===== COMMAND LINE ARGUMENTS SECTION =====
        cmd_args_frame = ttk.Frame(advanced_notebook, padding=15)
        advanced_notebook.add(cmd_args_frame, text=" Command Line Arguments ")
        
        # Command Line Arguments explanation
        cmd_args_label = ttk.Label(cmd_args_frame, 
                               text="Add command-line arguments that will be passed to your script:", 
                               font=("Segoe UI", 10))
        cmd_args_label.pack(anchor=tk.W, pady=(0, 10))
        
        cmd_hint = ttk.Label(cmd_args_frame, 
                           text="For scripts that require arguments (e.g. 'python main.py add 5 3'), add them here.",
                           foreground=self.accent2_color, font=("Segoe UI", 9))
        cmd_hint.pack(anchor=tk.W, pady=(0, 15))
        
        # Example box
        example_frame = ttk.LabelFrame(cmd_args_frame, text="Example", padding=10)
        example_frame.pack(fill=tk.X, pady=(0, 15))
        
        example_text = (
            "# For a script with command:", 
            "python main.py add 5 3", 
            "", 
            "# Enter in the field below:", 
            "add 5 3"
        )
        
        for line in example_text:
            ttk.Label(example_frame, text=line, font=("Consolas", 9)).pack(anchor=tk.W)
        
        # Command arguments entry
        args_entry_frame = ttk.Frame(cmd_args_frame)
        args_entry_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(args_entry_frame, text="Command Arguments:").pack(anchor=tk.W, pady=(0, 5))
        
        self.cmd_args_var = tk.StringVar()
        cmd_args_entry = ttk.Entry(args_entry_frame, textvariable=self.cmd_args_var, width=60)
        cmd_args_entry.pack(fill=tk.X, pady=5)
        
        # Note about how arguments are used
        note_frame = ttk.Frame(cmd_args_frame)
        note_frame.pack(fill=tk.X, pady=10)
        
        note_label = ttk.Label(
            note_frame,
            text="Note: Arguments will be passed to the script when the executable is run.",
            font=("Segoe UI", 9, "italic")
        )
        note_label.pack(anchor=tk.W)
        
        # ===== EXTRA PACKAGES SECTION =====
        packages_frame = ttk.Frame(advanced_notebook, padding=15)
        advanced_notebook.add(packages_frame, text=" Extra Packages ")
        
        # Extra Packages explanation
        packages_label = ttk.Label(packages_frame, 
                               text="Specify additional packages to include in your executable:", 
                               font=("Segoe UI", 10))
        packages_label.pack(anchor=tk.W, pady=(0, 10))
        
        pkg_hint = ttk.Label(packages_frame, 
                           text="List packages separated by commas (e.g., 'pandas,numpy,matplotlib').",
                           foreground=self.accent2_color, font=("Segoe UI", 9))
        pkg_hint.pack(anchor=tk.W, pady=(0, 15))
        
        # Example box
        pkg_example_frame = ttk.LabelFrame(packages_frame, text="Example", padding=10)
        pkg_example_frame.pack(fill=tk.X, pady=(0, 15))
        
        pkg_example_text = (
            "# Common data science packages:", 
            "pandas,numpy,matplotlib,scipy", 
            "", 
            "# Common web packages:", 
            "flask,requests,beautifulsoup4"
        )
        
        for line in pkg_example_text:
            ttk.Label(pkg_example_frame, text=line, font=("Consolas", 9)).pack(anchor=tk.W)
        
        # Extra packages entry
        packages_entry_frame = ttk.Frame(packages_frame)
        packages_entry_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(packages_entry_frame, text="Extra Packages:").pack(anchor=tk.W, pady=(0, 5))
        
        self.extra_packages_var = tk.StringVar()
        packages_entry = ttk.Entry(packages_entry_frame, textvariable=self.extra_packages_var, width=60)
        packages_entry.pack(fill=tk.X, pady=5)
        
        # Note about how packages are used
        pkg_note_frame = ttk.Frame(packages_frame)
        pkg_note_frame.pack(fill=tk.X, pady=10)
        
        pkg_note_label = ttk.Label(
            pkg_note_frame,
            text="Note: These packages will be explicitly included in your executable. Only add packages your app actually uses.",
            font=("Segoe UI", 9, "italic")
        )
        pkg_note_label.pack(anchor=tk.W)
        
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
        
        # Environment Variables
        env_vars_label = ttk.Label(env_vars_frame, 
                                text="Add environment variables that will be included in the executable:", 
                                font=("Segoe UI", 10))
        env_vars_label.pack(anchor=tk.W, pady=(0, 10))
        
        env_hint = ttk.Label(env_vars_frame, 
                           text="These variables will be available to your application at runtime, similar to .env files.",
                           foreground=self.accent2_color, font=("Segoe UI", 9))
        env_hint.pack(anchor=tk.W, pady=(0, 15))
        
        # Frame for adding new variables
        add_var_frame = ttk.Frame(env_vars_frame)
        add_var_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(add_var_frame, text="Variable Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.new_var_key = tk.StringVar()
        key_entry = ttk.Entry(add_var_frame, textvariable=self.new_var_key, width=20)
        key_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(add_var_frame, text="Value:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.new_var_value = tk.StringVar()
        value_entry = ttk.Entry(add_var_frame, textvariable=self.new_var_value, width=40)
        value_entry.grid(row=0, column=3, padx=5, pady=5, sticky=tk.EW)
        
        add_btn = ttk.Button(add_var_frame, text="Add", command=self.add_env_var, width=10)
        add_btn.grid(row=0, column=4, padx=5, pady=5)
        
        # Frame for listing variables
        list_frame = ttk.LabelFrame(env_vars_frame, text="Defined Variables", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create a frame with a scrollbar for the variables list
        var_scroll_frame = ttk.Frame(list_frame)
        var_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(var_scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create a canvas for scrolling
        self.env_canvas = tk.Canvas(var_scroll_frame, bg=self.bg_color, highlightthickness=0)
        self.env_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure the scrollbar
        scrollbar.config(command=self.env_canvas.yview)
        self.env_canvas.config(yscrollcommand=scrollbar.set)
        
        # Create a frame inside the canvas to hold the variables
        self.env_list_frame = ttk.Frame(self.env_canvas)
        self.env_canvas_window = self.env_canvas.create_window((0, 0), window=self.env_list_frame, anchor=tk.NW)
        
        # Configure the canvas to resize with the frame
        self.env_list_frame.bind('<Configure>', lambda e: self.env_canvas.configure(scrollregion=self.env_canvas.bbox('all')))
        self.env_canvas.bind('<Configure>', self._resize_env_canvas)
        
        # Empty state label
        self.empty_env_label = ttk.Label(self.env_list_frame, text="No environment variables defined", 
                                     foreground=self.accent2_color, font=("Segoe UI", 10, "italic"))
        self.empty_env_label.pack(pady=20)
        
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
            venv_dir = None
            venv_python = sys.executable  # Default to current python
            
            try:
                # Process based on input type
                if input_type == "file":
                    # For single file, we can directly use it
                    self.update_status("Using single Python file as source...", "info")
                    source_file = path
                    project_dir = os.path.dirname(path)
                elif input_type == "folder":
                    # For folder, copy the contents to the temp directory
                    self.update_status("Copying project files...", "info")
                    self.copy_directory(path, temp_dir)
                    source_file = os.path.join(temp_dir, main_file)
                    project_dir = temp_dir
                    self.update_status(f"Project files copied. Using '{main_file}' as entry point.", "info")
                elif input_type == "github":
                    # For GitHub, clone the repository
                    self.update_status("Connecting to GitHub...", "info")
                    repo_dir = self.download_github_repo(path, temp_dir)
                    if not repo_dir or not os.path.exists(repo_dir):
                        raise Exception("Failed to clone GitHub repository")
                    self.update_status(f"GitHub repository cloned successfully. Using '{main_file}' as entry point.", "info")
                    source_file = os.path.join(repo_dir, main_file)
                    project_dir = repo_dir
                
                # --- NEW LOGIC: Use requirements.txt if present ---
                requirements_path = os.path.join(project_dir, "requirements.txt")
                if os.path.isfile(requirements_path):
                    self.update_status("requirements.txt found. Creating virtual environment and installing dependencies...", "info")
                    venv_dir = os.path.join(temp_dir, "venv_build")
                    venv.create(venv_dir, with_pip=True)
                    if sys.platform.startswith("win"):
                        venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
                    else:
                        venv_python = os.path.join(venv_dir, "bin", "python")
                    # Install requirements
                    pip_cmd = [venv_python, "-m", "pip", "install", "-r", requirements_path]
                    proc = subprocess.run(pip_cmd, capture_output=True, text=True)
                    if proc.returncode != 0:
                        raise Exception(f"Failed to install requirements:\n{proc.stdout}\n{proc.stderr}")
                    self.update_status("Dependencies installed in build environment.", "info")
                    # Always install pyinstaller in the venv
                    self.update_status("Installing PyInstaller in build environment...", "info")
                    pip_pyinstaller = [venv_python, "-m", "pip", "install", "pyinstaller"]
                    proc2 = subprocess.run(pip_pyinstaller, capture_output=True, text=True)
                    if proc2.returncode != 0:
                        raise Exception(f"Failed to install PyInstaller in build venv:\n{proc2.stdout}\n{proc2.stderr}")
                    self.update_status("PyInstaller installed in build environment.", "info")
                else:
                    self.update_status("No requirements.txt found in project. Using system environment.", "warning")
                
                # Run PyInstaller using the venv's python if venv was created
                self.update_status("Starting PyInstaller build process...", "info")
                self.run_pyinstaller(source_file, output_dir, python_exe=venv_python)
                
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
    
    def run_pyinstaller(self, source_file, output_dir, python_exe=None):
        """Run PyInstaller to create an executable"""
        if python_exe is None:
            python_exe = sys.executable
        # Check if PyInstaller is already installed and available
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
        
        # Prepare PyInstaller command
        cmd = [
            python_exe, "-m", "PyInstaller",
            "--distpath", output_dir,
            "--workpath", os.path.join(output_dir, "build"),
            "--specpath", output_dir
        ]
        
        # Add onefile/onedir option
        if self.onefile_var.get():
            cmd.append("--onefile")
        else:
            cmd.append("--onedir")
        
        # Add console/no-console option
        if not self.console_var.get():
            cmd.append("--windowed")
            
        # Add hidden imports for required modules
        cmd.extend(["--hidden-import", "dotenv"])
        
        # Add environment variables if defined
        if self.env_vars:
            env_vars_str = "{" + ", ".join([f"'{k}': '{v}'" for k, v in self.env_vars]) + "}"
            cmd.extend(["--add-data", f"env_vars.py:."]) 
            
            # Create a temporary env_vars.py file with the environment variables
            env_vars_dir = os.path.dirname(source_file)
            env_vars_path = os.path.join(env_vars_dir, "env_vars.py")
            
            with open(env_vars_path, "w") as f:
                f.write(f"# Environment variables for Lightning EXE\n")
                f.write(f"# This file is automatically generated\n\n")
                f.write(f"import os\n\n")
                f.write(f"# Set environment variables\n")
                f.write(f"_env_vars = {env_vars_str}\n\n")
                f.write(f"def init_env_vars():\n")
                f.write(f"    for key, value in _env_vars.items():\n")
                f.write(f"        os.environ[key] = value\n\n")
                f.write(f"# Initialize environment variables when imported\n")
                f.write(f"init_env_vars()\n")
            
            # Create a hook for the application entry point to load environment variables
            hook_dir = os.path.join(env_vars_dir, "hooks")
            os.makedirs(hook_dir, exist_ok=True)
            hook_path = os.path.join(hook_dir, "hook-env_vars.py")
            
            with open(hook_path, "w") as f:
                f.write("# PyInstaller hook to ensure env_vars is imported\n")
                f.write("from PyInstaller.utils.hooks import collect_data_files\n\n")
                f.write("# Force env_vars module to be included\n")
                f.write("hiddenimports = ['env_vars']\n")
            
            # Add hook path to PyInstaller command
            cmd.extend(["--additional-hooks-dir", hook_dir])
            
            # Inject import into the source file or its directory
            self.inject_env_vars_import(source_file)
        
        # Check if we have command line arguments
        if self.cmd_args_var.get().strip():
            # Create a wrapper script to handle command line arguments
            wrapper_path = cmd_args_helper.create_wrapper_script(
                source_file, 
                self.cmd_args_var.get().strip()
            )
            
            # Use wrapper as the entry point
            cmd.append(wrapper_path)
            
            # Add original script directory to PyInstaller's path so imports work
            cmd.extend(["--paths", os.path.dirname(source_file)])
            
            self.update_status(f"Using command-line arguments: {self.cmd_args_var.get().strip()}", "info")
        else:
            # Add source file directly if no command-line arguments
            cmd.append(source_file)
        
        # Execute PyInstaller
        self.update_status("Running PyInstaller...", "info")
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # Set a timeout for the process
            try:
                stdout, _ = process.communicate(timeout=300)  # 5 minute timeout
                
                if process.returncode != 0:
                    raise Exception(f"PyInstaller failed with exit code {process.returncode}\n{stdout}")
                
            except subprocess.TimeoutExpired:
                process.kill()
                raise Exception("PyInstaller process timed out after 5 minutes")
                
        except Exception as e:
            raise Exception(f"Error running PyInstaller: {str(e)}")
    
    def add_env_var(self):
        """Add a new environment variable to the list"""
        key = self.new_var_key.get().strip()
        value = self.new_var_value.get().strip()
            
        if not key:
            messagebox.showerror("Error", "Variable name cannot be empty")
            return
                
        # Check if key already exists
        for i, (k, _) in enumerate(self.env_vars):
            if k == key:
                # Update existing key
                self.env_vars[i] = (key, value)
                self.refresh_env_vars_list()
                self.new_var_key.set("")
                self.new_var_value.set("")
                return
            
        # Add new key-value pair
        self.env_vars.append((key, value))
        self.refresh_env_vars_list()
            
        # Clear inputs
        self.new_var_key.set("")
        self.new_var_value.set("")
    
    def remove_env_var(self, key):
        """Remove an environment variable from the list"""
        self.env_vars = [(k, v) for k, v in self.env_vars if k != key]
        self.refresh_env_vars_list()
    
    def refresh_env_vars_list(self):
        """Refresh the displayed list of environment variables"""
        # Clear all widgets in the list frame
        for widget in self.env_list_frame.winfo_children():
            widget.destroy()
            
        if not self.env_vars:
            # Show empty state
            self.empty_env_label = ttk.Label(self.env_list_frame, text="No environment variables defined", 
                                        foreground=self.accent2_color, font=("Segoe UI", 10, "italic"))
            self.empty_env_label.pack(pady=20)
            return
            
        # Create a header row
        header_frame = ttk.Frame(self.env_list_frame)
        header_frame.pack(fill=tk.X, padx=5, pady=(5, 10))
            
        ttk.Label(header_frame, text="Variable", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, padx=(5, 15))
        ttk.Label(header_frame, text="Value", font=("Segoe UI", 10, "bold")).grid(row=0, column=1, padx=(5, 15))
            
        # Add a separator
        sep = ttk.Separator(self.env_list_frame, orient="horizontal")
        sep.pack(fill=tk.X, pady=5)
            
        # Add each environment variable
        for key, value in self.env_vars:
            var_frame = ttk.Frame(self.env_list_frame)
            var_frame.pack(fill=tk.X, padx=5, pady=2)
                
            ttk.Label(var_frame, text=key).grid(row=0, column=0, padx=(5, 15), pady=5, sticky=tk.W)
            ttk.Label(var_frame, text=value).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
                
            remove_btn = ttk.Button(var_frame, text="✕", width=3,
                                  command=lambda k=key: self.remove_env_var(k))
            remove_btn.grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
    
    def _resize_env_canvas(self, event):
        """Resize the canvas width to fit the parent"""
        canvas_width = event.width
        self.env_canvas.itemconfig(self.env_canvas_window, width=canvas_width)
    
    def inject_env_vars_import(self, source_file):
        """Inject the env_vars import into the source file or directory"""
        # If the source file is within a directory, create an __init__.py file
        dir_path = os.path.dirname(source_file)
        init_file = os.path.join(dir_path, "__init__.py")
            
        # Check if __init__.py already exists
        if not os.path.exists(init_file):
            # Create a basic __init__.py file
            with open(init_file, "w") as f:
                f.write("# __init__.py for Lightning EXE environment variables\n")
                f.write("try:\n")
                f.write("    import env_vars\n")
                f.write("except ImportError:\n")
                f.write("    pass\n")


if __name__ == "__main__":
    import sys
        
    # Check Python version
    if sys.version_info < (3, 6):
        print("Python 3.6 or higher is required")
        sys.exit(1)
        
    # Create and run the application
    root = tk.Tk()
    app = LightningEXE(root)
    
    # Set a custom icon if available
    try:
        root.iconbitmap("lightning_icon.ico")
    except:
        pass
    
    root.mainloop()
