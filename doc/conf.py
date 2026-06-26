# -*- coding: utf-8 -*-
#
# lewis documentation build configuration file, created by
# sphinx-quickstart on Wed Nov  9 16:42:53 2016.
import os
import sys

sys.path.insert(0, os.path.abspath("../lewis"))


# -- General configuration ------------------------------------------------
extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    # and making summary tables at the top of API docs
    "sphinx.ext.autosummary",
    # This can parse google style docstrings
    "sphinx.ext.napoleon",
    # For linking to external sphinx documentation
    "sphinx.ext.intersphinx",
    # Add links to source code in API docs
    "sphinx.ext.viewcode",
]
templates_path = ["_templates"]
# General information about the project.
project = "lewis"
language = "en"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
# -- Options for HTML output ---------------------------------------------
suppress_warnings = ["docutils"]
html_theme = "sphinx_rtd_theme"
html_logo = "resources/logo/lewis-logo.png"
html_context = {
    "display_github": True,  # Integrate GitHub
    "github_user": "ISISComputingGroup",  # Username
    "github_repo": "lewis",  # Repo name
    "github_version": "main",  # Version
    "conf_py_path": "/doc/",  # Path in the checkout to the docs root
}

autoclass_content = "both"
myst_heading_anchors = 3

napoleon_google_docstring = False
napoleon_numpy_docstring = True
