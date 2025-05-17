# Configuration file for the Sphinx documentation builder.

import os
import sys

# Add the 'src' directory to sys.path, regardless of where Sphinx is run from
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# -- Project information -----------------------------------------------------

project = 'Agentic AI: An Exploratory And Functional Approach'
copyright = '2025, Alejandro Martinez Esquivias'
author = 'Alejandro Martinez Esquivias'
release = '1.0'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',  # Optional: automatic type hint rendering
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Autodoc default settings ------------------------------------------------

autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
    'private-members': False,
    'special-members': '__init__',
}

# -- Napoleon settings for Google-style docstrings ---------------------------

napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_use_param = True
napoleon_use_rtype = True
