# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'libavtp'
copyright = '2024, Avnu'
author = 'Avnu'
release = 'v4.0.2'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["breathe", "exhale", "sphinx.ext.autosummary", "myst_parser"]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

# -- Breathe configuration ---------------------------------------------------
breathe_projects = {
    "libavtp": "./doxygen/xml"
}
breathe_default_project = "libavtp"

# -- Exhale configuration ---------------------------------------------------
exhale_args = {
    # These arguments are required
    "containmentFolder": "./exhale",
    "rootFileName": "libavtp_root.rst",
    "rootFileTitle": "libavtp_root",
    "doxygenStripFromPath": "..",
    # Suggested optional arguments
    "createTreeView": True,
    # TIP: if using the sphinx-bootstrap-theme, you need
    # "treeViewIsBootstrap": True,
    "exhaleExecutesDoxygen": True,
    "exhaleDoxygenStdin": "INPUT = libavtp"
}

# Tell sphinx what the primary language being documented is.
primary_domain = 'cpp'

# Tell sphinx what the pygments highlight language should be.
highlight_language = 'cpp'
