# Configuration file for the Sphinx documentation builder.
import os
import sys
import datetime

# Add the project root to the path so sphinx can find the modules
sys.path.insert(0, os.path.abspath('..'))

# Project information
project = 'Email Deliverability Library'
copyright = f'{datetime.datetime.now().year}, Innerkore'
author = 'Gagan (Innerkore)'

# The full version, including alpha/beta/rc tags
release = '0.1.2'

# Extensions
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx_rtd_theme',
    'myst_parser',  # For Markdown support
]

# Add mappings for intersphinx
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'requests': ('https://requests.readthedocs.io/en/latest/', None),
    'dnspython': ('https://dnspython.readthedocs.io/en/latest/', None),
}

# Templates path
templates_path = ['_templates']

# Pattern list that shouldn't be searched
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# HTML theme
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Theme options
html_theme_options = {
    'navigation_depth': 4,
    'titles_only': False,
    'logo_only': False,
}

# -- Extension configuration -------------------------------------------------

# Support for Markdown files
source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
}

# -- Napoleon settings ----------------------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# Last updated timestamp
html_last_updated_fmt = '%Y-%m-%d %H:%M:%S'