"""Script to set up Sphinx documentation."""
import os
import subprocess
import sys

def setup_sphinx_docs():
    # Create docs directory
    os.makedirs("docs", exist_ok=True)
    os.makedirs("docs/source", exist_ok=True)
    
    # Run sphinx-quickstart
    os.chdir("docs")
    subprocess.run([
        "sphinx-quickstart",
        "--sep",
        "--project=Email Deliverability",
        "--author=Your Company",
        "--release=0.1.0",
        "--language=en",
        "-v", "0.1.0",
        "--suffix=.rst",
        "--master=index",
        "--ext-autodoc",
        "--ext-viewcode",
        "--ext-todo",
        "--extensions=sphinx.ext.autodoc,sphinx.ext.viewcode,sphinx.ext.napoleon,sphinx.ext.todo",
        "source"
    ])
    os.chdir("..")
    
    # Copy over content
    print("Documentation scaffold created. Now run 'python -m pip install sphinx sphinx-rtd-theme' to install dependencies.")
    print("Then run 'cd docs && make html' to build the HTML documentation.")

if __name__ == "__main__":
    setup_sphinx_docs()