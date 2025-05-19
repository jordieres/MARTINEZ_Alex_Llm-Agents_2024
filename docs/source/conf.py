# Configuration file for the Sphinx documentation builder.

import os
import sys
import yaml

def load_env_from_yaml(config_path):
    """Load environment variables from a YAML file."""
    if not os.path.isfile(config_path):
        print(f"[INFO] Configuration file {config_path} not found. Skipping...")
        return

    with open(config_path, 'r') as file:
        try:
            config = yaml.safe_load(file)
        except yaml.YAMLError as e:
            print(f"[ERROR] Failed to parse YAML: {e}")
            return

    # Flatten nested dictionaries if needed, or assume flat structure
    for key, value in config.items():
        # Only set if not already in the environment
        os.environ.setdefault(key, str(value))

# Usage example
CONFIG_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../config.yaml'))
load_env_from_yaml(CONFIG_FILE_PATH)
# ------------------- Normal conf.py


# Add the 'src' directory to sys.path, regardless of where Sphinx is run from
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'src')))

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
    'sphinx_autodoc_typehints',
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
    'private-members': True,
    'special-members': '__init__',
    'inherited-members': True,
    'show-inheritance': True,
}

# -- Napoleon settings for Google-style docstrings ---------------------------

napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
