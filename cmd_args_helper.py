"""
Helper module for handling command-line arguments in Lightning EXE.
"""
import os
import sys

def create_wrapper_script(source_file, args):
    """
    Create a wrapper script that passes command-line arguments to the main script.
    
    Args:
        source_file: Path to the original Python script
        args: Command-line arguments to pass to the script
    
    Returns:
        Path to the created wrapper script
    """
    wrapper_dir = os.path.dirname(source_file)
    wrapper_path = os.path.join(wrapper_dir, "_lightning_exe_wrapper.py")
    
    with open(wrapper_path, "w") as f:
        f.write("# Wrapper script created by Lightning EXE to handle command-line arguments\n")
        f.write("import sys\n")
        f.write("import os\n\n")
        
        # Get the original script name without path
        script_name = os.path.basename(source_file)
        
        # Define the command-line arguments
        if args:
            f.write(f"# Set command-line arguments\n")
            f.write(f"sys.argv = ['{script_name}'")
            
            # Parse and add each argument
            for arg in args.split():
                f.write(f", '{arg}'")
            
            f.write("]\n\n")
        
        # Get full path to the original script
        f.write(f"# Execute the original script directly\n")
        f.write(f"script_dir = os.path.dirname(os.path.abspath(__file__))\n")
        f.write(f"original_script = os.path.join(script_dir, '{script_name}')\n")
        f.write(f"sys.path.insert(0, script_dir)\n\n")
        
        # Execute the original script with exec
        f.write(f"try:\n")
        f.write(f"    with open(original_script, 'r') as script_file:\n")
        f.write(f"        script_content = script_file.read()\n")
        f.write(f"    # Use globals as namespace to ensure script runs in the main context\n")
        f.write(f"    namespace = globals()\n")
        f.write(f"    namespace['__file__'] = original_script\n")
        f.write(f"    exec(script_content, namespace)\n")
        f.write(f"except Exception as e:\n")
        f.write(f"    print(f\"Error running '{script_name}': {{e}}\")\n")
        f.write(f"    import traceback\n")
        f.write(f"    traceback.print_exc()\n")
        f.write(f"    input(\"Press Enter to exit...\")\n")
        f.write(f"    sys.exit(1)\n")
    
    return wrapper_path
