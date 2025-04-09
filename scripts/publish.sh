#!/bin/bash
set -e  # Exit on error

# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Install required tools
pip install --upgrade pip wheel twine build

# Build the package
python -m build

# Check package
twine check dist/*

# Ask for confirmation
read -p "Upload to PyPI? (y/N): " UPLOAD
if [[ $UPLOAD == "y" || $UPLOAD == "Y" ]]; then
    # Upload to PyPI
    twine upload dist/*
    echo "Package published to PyPI successfully!"
else
    echo "Upload cancelled."
fi
