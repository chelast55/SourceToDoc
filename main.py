from os import chdir, system
from pathlib import Path
from argparse import Namespace

from sourcetodoc.helpers import delete_directory_if_exists
from sourcetodoc.cli.ConfiguredParser import ConfiguredParser

# configurable variables
project_name: str = "libavtp"
project_author: str = "Avnu"
project_release_version: str = "v4.0.2"
project_year: str = "2024"

html_theme: str = "sphinx_rtd_theme"
exhale_root_file_name: str = f"root_{project_name}"

# Paths (sphinx-based)
generated_docs_main_path: Path = Path("out")  # Path conf.py will be placed, everything Sphinx related is rel. to it
project_path: Path = generated_docs_main_path.parent.absolute() / Path(project_name)
doxygen_awesome_submodule_path: Path \
    = generated_docs_main_path.parent.absolute() / Path("submodules") / Path("doxygen-awesome-css")

doc_path: Path = Path("doc") / Path(project_name)  # TODO: option to reverse those with a CLI parameter
doc_path_abs: Path = generated_docs_main_path.absolute() / doc_path
doc_source_path: Path = doc_path / Path("src")
doc_source_path_abs: Path = doc_path_abs / Path("src")
doxygen_path: Path = doc_source_path_abs / Path("doxygen")
sphinx_path: Path = doc_path_abs  # Sphinx (or rather its index.html) is the "main artifact"
exhale_containment_path: Path = doc_source_path / Path("exhale")
exhale_containment_path_abs: Path = doc_source_path_abs / Path("exhale")
exhale_include_path: Path = doc_path / exhale_containment_path
graphviz_dot_path: Path = Path(r"C:\Program Files\Graphviz\bin\dot.exe")  # TODO: this needs to be addressed
stylesheet_path: Path = doxygen_awesome_submodule_path / Path("doxygen-awesome.css")

DOXYFILE_CONTENT: str = f"""
    INPUT = {str(project_path).replace('\\', '\\\\')}
    # OPTIMIZE_OUTPUT_FOR_C  = YES
    EXTRACT_ALL = YES
    EXTRACT_PRIVATE = YES
    EXTRACT_PRIV_VIRTUAL   = YES
    EXTRACT_PACKAGE        = YES
    EXTRACT_STATIC         = YES
    EXTRACT_LOCAL_METHODS  = YES
    EXTRACT_ANON_NSPACES   = YES
    SORT_MEMBERS_CTORS_1ST = YES
    GENERATE_HTML = YES  # DEBUG
    XML_PROGRAMLISTING = YES
    XML_NS_MEMB_FILE_SCOPE = YES
    GENERATE_AUTOGEN_DEF   = YES # EXPERIMENTAL
    MACRO_EXPANSION        = YES
    HIDE_UNDOC_RELATIONS   = YES
    GENERATE_TREEVIEW = YES
    HAVE_DOT = YES
    CLASS_GRAPH = YES
    COLLABORATION_GRAPH = YES
    UML_LOOK = YES
    UML_LIMIT_NUM_FIELDS   = 50
    DOT_UML_DETAILS = YES
    TEMPLATE_RELATIONS     = YES
    INCLUDE_GRAPH = YES
    INCLUDED_BY_GRAPH = YES
    CALL_GRAPH = YES
    CALLER_GRAPH = YES
    GRAPHICAL_HIERARCHY = YES
    DIRECTORY_GRAPH = YES
    DOT_IMAGE_FORMAT = svg
    INTERACTIVE_SVG = YES
    DOT_PATH = {str(graphviz_dot_path).replace('\\', '\\\\') if not graphviz_dot_path is None else ""}
    DOT_MULTI_TARGETS      = YES
    HTML_STYLESHEET = {str(stylesheet_path).replace('\\', '\\\\')}
    HTML_COLORSTYLE = LIGHT  # required with Doxygen >= 1.9.5
    GENERATE_LATEX = NO
    RECURSIVE = YES
"""

INDEX_RST_CONTENT: str = f"""
Welcome to {project_name}'s documentation!
============================{"="*len(project_name)}
    
.. toctree::
    :maxdepth: 2
    :caption: Contents:

    {str(exhale_containment_path).replace('\\', '/') + "/" + exhale_root_file_name}

Only to proof that graphs are included and until this is properly handled with exhale

.. doxygenindex::
    :allow-dot-graphs:

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
"""

CONF_PY_CONTENT: str = f"""
# Configuration file for the Sphinx documentation builder.

# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
from pathlib import Path
from exhale import utils as exhale_utils

project = "{project_name}"
copyright = "{project_year}, {project_author}"
author = "{project_author}"
release = "{project_release_version}"

project_path: Path = Path(r"{str(project_path)}")
doxygen_path: Path = Path(r"{str(doxygen_path)}")
sphinx_path: Path = Path(r"{str(sphinx_path)}")
exhale_path: Path = Path(r"{str(exhale_containment_path)}")
graphviz_dot_path: Path = Path(r"{str(graphviz_dot_path)}")
        
graphviz_output_format = "svg"
# graphviz_dot_args = ["-Gbgcolor=#FF00FF", "-Ncolor=#ffffff", "-Ecolor=#00ff00"]
graphviz_dot = str(graphviz_dot_path)

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "{html_theme}"

extensions = ["sphinx.ext.graphviz", "sphinx.ext.autodoc", "sphinx.ext.autosummary", "myst_parser"]
"""

CONF_PY_EXHALE_EXTENSION = f"""
# -- Additional configuration ---------------------------------------------------

extensions += ["breathe", "exhale"]

def specifications_for_kind(kind):
    \"\"\"
    For a given input ``kind``, return the list of reStructuredText specifications
    for the associated Breathe directive.
    \"\"\"
    # Change the defaults for .. doxygenclass:: and .. doxygenstruct::
    if kind == "class" or kind == "struct" or kind == "file":
        print("Doxygenclass or struct encountered and overriting")
        return [
            ":members:",
            ":protected-members:",
            ":private-members:",
            ":undoc-members:",
            ":allow-dot-graphs:"
        ]
    # An empty list signals to Exhale to use the defaults
    else:
        print("Something else encountered")
        return []
        
# -- Breathe configuration ---------------------------------------------------
breathe_projects = {{
    "{project_name}": str(doxygen_path / Path("xml"))
}}
breathe_default_project = "{project_name}"
primary_domain = "cpp"
highlight_language="cpp"

# -- Exhale configuration ---------------------------------------------------
exhale_args = {{
    # These arguments are required
    "containmentFolder": str(exhale_path.absolute()),
    "rootFileName": "{exhale_root_file_name}.rst",
    "rootFileTitle": "{project_name} API",
    "doxygenStripFromPath": str(sphinx_path.absolute()),
    "fullToctreeMaxDepth": 1,
    # Suggested optional arguments
    "createTreeView": True,
    # TIP: if using the sphinx-bootstrap-theme, you need
    #"treeViewIsBootstrap": True,
    "exhaleExecutesDoxygen": True,
    "exhaleDoxygenStdin": {DOXYFILE_CONTENT},
    "verboseBuild": True, # DEBUG
    "generateBreatheFileDirectives": True, # DEBUG
    "customSpecificationsMapping": exhale_utils.makeCustomSpecificationsMapping(specifications_for_kind)
}}

"""

if __name__ == "__main__":
    # parse arguments
    args = ConfiguredParser().parse_args()
    project_name = args.project_name
    project_author = args.project_author
    project_release_version = args.project_release_version
    project_year = args.project_year

    # delete artifacts from prior builds and ensure paths exist TODO: move to end as cleenup, when debugging is done
    delete_directory_if_exists(doc_path_abs)
    doc_path_abs.mkdir(parents=True, exist_ok=True)
    doxygen_path.mkdir(parents=True, exist_ok=True)
    sphinx_path.mkdir(parents=True, exist_ok=True)
    exhale_containment_path_abs.mkdir(parents=True, exist_ok=True)
    if not graphviz_dot_path.exists(): raise OSError("dot.exe not found at given path")
    chdir(generated_docs_main_path)

    if args.apidoc_toolchain == "doxygen-only":
        # set paths for doxygen
        project_path = generated_docs_main_path / Path(args.project_name)

        # generate config file for Doxygen
        with open(Path("Doxyfile.in"), "w+") as doxyfile:
            doxyfile.write(DOXYFILE_CONTENT)

        # run doxygen
        system("doxygen Doxyfile.in")

    elif args.apidoc_toolchain == "sphinx-based":
        # this path is only here for reference and may be (partially) broken
        print("!!! Disclaimer: Using sphinx-based is currently not recommended and may not work at all.")

        # generate config files for sphinx+breathe+exhale+doxygen
        with open(Path("index.rst"), "w+") as index_rst_file:
            index_rst_file.write(INDEX_RST_CONTENT)
        with open(Path("conf.py"), "w+") as conf_py_file:
            conf_py_file.write(CONF_PY_CONTENT + CONF_PY_EXHALE_EXTENSION)

        # run sphinx+breath+exhale+doxygen
        print("\n--------------------")
        print("Generate sphinx...")
        system(f"sphinx-build -b html . {sphinx_path}")

        # exhale output post processings
        # TODO: implement
        #delete_directory_if_exists(exhale_containment_path)  # DEBUG
        #delete_directory_if_exists(sphinx_path / Path("doc"))  # DEBUG
        #system(f"breathe-apidoc -o {exhale_containment_path} -m {str(doxygen_path / Path("xml"))}")  # DEBUG

        # adjust sphinx config for second run
        with open(Path("conf.py"), "w+") as conf_py_file:
            conf_py_file.write(CONF_PY_CONTENT)

        # run sphinx again
        # maybe some cleanup is necessary?
        #system(f"sphinx-build -b html . {sphinx_path}")
