import os
import sys

def prepare_deployment():
    """
    Prepare the app directory for deployment
    """
    print("Preparing deployment...")

    # Get the current directory (app)
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Check if iflow_matcher.py exists
    if not os.path.exists(os.path.join(current_dir, "iflow_matcher.py")):
        print("Error: iflow_matcher.py not found!")
        return False

    # Check if all required files exist
    required_files = ["app.py", "Procfile", "requirements.txt", "iflow_matcher.py"]
    for file in required_files:
        if not os.path.exists(os.path.join(current_dir, file)):
            print(f"Error: Required file {file} not found!")
            return False

    print("All required files found.")
    print("Deployment preparation completed successfully!")
    return True

if __name__ == "__main__":
    if prepare_deployment():
        print("Ready for deployment!")
        sys.exit(0)
    else:
        print("Deployment preparation failed!")
        sys.exit(1)
