# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import datetime

import slash

year = datetime.date.today().year
project = "Slash"
copyright = f"{year}, Jesse Vogel"
author = "Jesse Vogel"
version = slash.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.intersphinx",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",  # NOTE: Make sure this is placed below "sphinx.ext.napoleon"
]

exclude_patterns = []

# -- Options for extensions --------------------------------------------------

autoclass_content = "init"
napoleon_include_init_with_doc = False
napoleon_include_special_with_doc = False
autodoc_typehints = "description"
typehints_use_signature = False
typehints_use_signature_return = True
always_use_bars_union = True

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_title = "Slash"
html_favicon = "static/favicon.png"
html_css_files = ["custom.css"]
html_static_path = ["static"]
html_show_sourcelink = False

# See: https://sphinx-rtd-theme.readthedocs.io/en/stable/configuring.html
html_theme_options = {
    "logo_only": False,
    "display_version": True,
    "prev_next_buttons_location": "bottom",
    "style_external_links": False,
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": True,
}
