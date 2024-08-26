from shutil import which
from os import chdir, system
from pathlib import Path

from sourcetodoc.common.Config import Config
from sourcetodoc.common.helpers import delete_directory_if_exists


def run_doc_gen(config: Config):
    """
    Run the documentation generation part of the toolchain.

    Parameters
    ----------
    config: Config
        Initialized instance of common.Config containing configuration for the toolchain
    """
    # check if a README file was found
    if config.readme_file_path is not None:
        print(f"README found at {config.readme_file_path}")
    else:
        print(f"Could not find a file easily identifiable as a \"README\" :/")

    # delete artifacts from prior builds and ensure paths exist TODO: move to end as cleanup, when debugging is done
    delete_directory_if_exists(config.doc_path_abs)
    config.doc_path_abs.mkdir(parents=True, exist_ok=True)
    config.doxygen_path.mkdir(parents=True, exist_ok=True)
    chdir(config.out_path)

    # check non-python requirements
    default_dot = which("dot")
    if default_dot is None:
        raise OSError("dot (graphviz) was not found in PATH")
    default_doxygen = which("doxygen")
    if default_doxygen is None:
        raise OSError("doxygen was not found in PATH")
    if config.args.dg_html_theme == "doxygen-awesome" and not config.doxygen_stylesheet_path.is_file():
        raise OSError(
            "The stylesheet for doxygen-awesome was not found at its expected path. Try:\n$ git submodule update --init")

    if config.args.apidoc_toolchain == "doxygen-only":
        # generate config file for Doxygen
        with open(Path("Doxyfile.in"), "w+") as doxyfile:
            doxyfile.write(config.DOXYFILE_CONTENT)

        # run doxygen
        system("doxygen Doxyfile.in")

    elif config.args.apidoc_toolchain == "sphinx-based":
        # this path is only here for reference and may be (partially) broken
        # region sphinx-based
        print("!!! Disclaimer: Using sphinx-based is currently not recommended and may not work at all.")

        config.sphinx_path.mkdir(parents=True, exist_ok=True)
        config.exhale_containment_path_abs.mkdir(parents=True, exist_ok=True)

        # generate config files for sphinx+breathe+exhale+doxygen
        with open(Path("index.rst"), "w+") as index_rst_file:
            index_rst_file.write(config.INDEX_RST_CONTENT)
        with open(Path("conf.py"), "w+") as conf_py_file:
            conf_py_file.write(config.CONF_PY_CONTENT + config.CONF_PY_EXHALE_EXTENSION)

        # run sphinx+breath+exhale+doxygen
        print("\n--------------------")
        print("Generate sphinx...")
        system(f"sphinx-build -b html . {config.sphinx_path}")

        # exhale output post processings
        # TODO: implement
        # delete_directory_if_exists(exhale_containment_path)  # DEBUG
        # delete_directory_if_exists(sphinx_path / Path("doc"))  # DEBUG
        # system(f"breathe-apidoc -o {exhale_containment_path} -m {str(doxygen_path / Path("xml"))}")  # DEBUG

        # adjust sphinx config for second run
        with open(Path("conf.py"), "w+") as conf_py_file:
            conf_py_file.write(config.CONF_PY_CONTENT)

        # run sphinx again
        # maybe some cleanup is necessary?
        # system(f"sphinx-build -b html . {sphinx_path}")

        # endregion sphinx-based