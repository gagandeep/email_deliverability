#!/usr/bin/env python3
"""Script to build and publish the package to PyPI."""
import subprocess
import os
import sys

def run_command(command):
    """Run a shell command and print output."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(f"Output: {result.stdout}")
    
    if result.stderr:
        print(f"Error: {result.stderr}")
    
    if result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)
    
    return result

def main():
    """Build and publish the package to PyPI."""
    # Ensure we're in the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(os.path.join(script_dir, '..'))
    
    # Clean build directories
    print("Cleaning build directories...")
    for directory in ['build', 'dist', '*.egg-info']:
        run_command(f"rm -rf {directory}")
    
    # Install/upgrade required packages
    print("Installing build dependencies...")
    run_command("pip install --upgrade pip setuptools wheel twine==6.0.1")
    
    # Build the package
    print("Building package...")
    run_command("python setup.py sdist bdist_wheel")
    
    # Check the distribution
    print("Checking distribution...")
    run_command("twine check dist/*")
    
    # Upload to TestPyPI first
    upload_to_test = input("Upload to TestPyPI first? (y/n): ").lower() == 'y'
    if upload_to_test:
        print("Uploading to TestPyPI...")
        run_command("twine upload --repository-url https://test.pypi.org/legacy/ dist/*")
        
        # Provide instruction to install from TestPyPI
        package_name = "email_deliverability"  # Get this from setup.py
        print(f"\nTo test the package from TestPyPI, run:")
        print(f"pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple {package_name}")
    
    # Upload to PyPI
    upload_to_pypi = input("Upload to PyPI? (y/n): ").lower() == 'y'
    if upload_to_pypi:
        print("Uploading to PyPI...")
        run_command("twine upload dist/*")
        print("\nPackage published to PyPI successfully!")

if __name__ == "__main__":
    main()