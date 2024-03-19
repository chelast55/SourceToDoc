from os import system

# TODO: (through argparse?)
project_name: str = "libavtp"
project_author: str = "Avnu"
project_release_version: str = "v4.0.2"
project_year: str = "2024"
html_theme: str = "alabaster" # "sphinx_rtd_theme"
doxygen_path: str = "doxygen"
sphinx_path: str = "sphinx"

if __name__ == '__main__':
    # setup doxygen
    #system("doxygen -g Doxyfile.in")
    # TODO: (automatically) modify Doxyfile.in with min. the following:
    # PROJECT_NAME = project name (through argparse?)
    # GENERATE_HTML = NO
    # GENERATE_XML = YES
    # INPUT = path to project to document (through argparse?)
    # RECURSIVE = YES
    # OUTPUT_DIRECTORY = doxygen or something like temp/doxygen

    # setup sphinx+breathe config
    conf_content: list[str] = [
        f"# Configuration file for the Sphinx documentation builder.\n",
        f"#\n",
        f"# For the full list of built-in configuration values, see the documentation:\n",
        f"# https://www.sphinx-doc.org/en/master/usage/configuration.html\n",
        f"\n",
        f"# -- Project information -----------------------------------------------------\n",
        f"# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information\n",
        f"\n",
        f"project = '{project_name}'\n",
        f"copyright = '{project_year}, {project_author}'\n",
        f"author = '{project_author}'\n",
        f"release = '{project_release_version}'\n",
        f"\n",
        f"# -- General configuration ---------------------------------------------------\n",
        f"# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration\n",
        f"\n",
        f'extensions = ["breathe", "exhale", "sphinx.ext.autosummary", "myst_parser"]\n',
        f"\n",
        f"templates_path = ['_templates']\n",
        f"exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']\n",
        f"\n",
        f"\n",
        f"\n",
        f"# -- Options for HTML output -------------------------------------------------\n",
        f"# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output\n",
        f"\n",
        f"html_theme = '{html_theme}'\n",
        f"html_static_path = ['_static']\n",
        f'\n',
        f'# -- Breathe configuration ---------------------------------------------------\n',
        "breathe_projects = {\n",
        f'    "{project_name}": "./{doxygen_path}/xml"\n',
        "}\n",
        f'breathe_default_project = "{project_name}"\n',
        f'\n',
        f'# -- Exhale configuration ---------------------------------------------------\n',
        'exhale_args = {\n',
        f'    # These arguments are required\n',
        f'    "containmentFolder": "./exhale",\n',
        f'    "rootFileName": "{project_name}_root.rst",\n',
        f'    "rootFileTitle": "{project_name}_root",\n',
        f'    "doxygenStripFromPath": "..",\n',
        f'    # Suggested optional arguments\n',
        f'    "createTreeView": True,\n',
        f'    # TIP: if using the sphinx-bootstrap-theme, you need\n',
        f'    # "treeViewIsBootstrap": True,\n',
        f'    "exhaleExecutesDoxygen": True,\n',
        f'    "exhaleDoxygenStdin": "INPUT = libavtp"\n'
        '}\n',
        f'\n',
        f"# Tell sphinx what the primary language being documented is.\n",
        f"primary_domain = 'cpp'\n",
        f'\n',
        f"# Tell sphinx what the pygments highlight language should be.\n",
        f"highlight_language = 'cpp'\n"
    ]
    with open("conf.py", 'w+') as conf_file:
        conf_file.writelines(conf_content)

    # generate doxygen documentation
    #print("\n--------------------")
    #print("Generate doxygen...")
    #system("doxygen Doxyfile.in")

    # setup RST
    #print("\n--------------------")
    #print("Generate breath-apidoc filelist...")
    #system(f"breathe-apidoc -o . {doxygen_path}/xml")

    # generate sphinx documentation from doxygen output
    print("\n--------------------")
    print("Generate sphinx...")
    system(f"sphinx-build -b html . {sphinx_path}/")

