import os
import shutil
import subprocess

def clone_github_repo(github_url, repo_dir):
    """
    Clone a GitHub repository to the specified directory.
    
    Args:
        github_url (str): The URL of the GitHub repository to clone
        repo_dir (str): The directory where to clone the repository
        
    Returns:
        bool: True if successful, raises exception otherwise
        
    Raises:
        Exception: If any error occurs during the process
    """
    # Clean up if repo directory already exists
    if os.path.exists(repo_dir):
        try:
            # First try to update if it's a git repo
            if os.path.exists(os.path.join(repo_dir, '.git')):
                print(f"Repository directory already exists. Attempting to update...")
                current_dir = os.getcwd()
                try:
                    # Try to update the repo
                    os.chdir(repo_dir)
                    subprocess.run(["git", "fetch", "--all"], check=True)
                    subprocess.run(["git", "reset", "--hard", "origin/main"], check=True)
                    print("Repository updated successfully!")
                    os.chdir(current_dir)
                    return True
                except subprocess.CalledProcessError:
                    # If update fails, fall back to deleting and cloning
                    os.chdir(current_dir)
                    print("Couldn't update repository. Removing and cloning fresh...")
                    shutil.rmtree(repo_dir)
                except Exception as e:
                    # Make sure we return to the original directory
                    os.chdir(current_dir)
                    raise e
            else:
                # Not a git repo, just remove it
                print(f"Removing existing directory {repo_dir}...")
                shutil.rmtree(repo_dir)
        except Exception as e:
            print(f"Warning handling existing repository: {e}")
            # Continue even if we couldn't handle the old repo
    
    # Create a new empty repo directory
    try:
        os.makedirs(repo_dir, exist_ok=True)
    except Exception as e:
        error_msg = f"Could not create repository directory: {str(e)}"
        print(f"Error: {error_msg}")
        raise Exception(error_msg)
    
    try:
        # Clone the repository
        print(f"Cloning {github_url} into '{repo_dir}'...")
        subprocess.run(["git", "clone", github_url, repo_dir], check=True)
        print("Repository cloned successfully!")
        return True
    except subprocess.CalledProcessError as e:
        error_msg = f"Failed to clone repository. Make sure the URL is correct and you have git installed. Command returned: {e}"
        print(f"Error: {error_msg}")
        raise subprocess.CalledProcessError(e.returncode, e.cmd, e.output, e.stderr, error_msg)
    except Exception as e:
        error_msg = f"An unexpected error occurred during cloning: {str(e)}"
        print(f"Error: {error_msg}")
        raise Exception(error_msg)
