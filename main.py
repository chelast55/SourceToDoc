from os import chdir, system
from pathlib import Path
from argparse import Namespace
import shutil
from typing import Optional

from sourcetodoc.common.Config import Config
from sourcetodoc.docstring.cli import run_comment_converter
from sourcetodoc.helpers import delete_directory_if_exists
from sourcetodoc.cli.ConfiguredParser import ConfiguredParser
from sourcetodoc.testcoverage.cover_meson import *


if __name__ == "__main__":
    parser: ConfiguredParser = ConfiguredParser()
    config = Config()
    config.args = parser.parse_args()
    config.initialize()

    # general stuff
    if not config.project_path.exists():
        raise OSError(f"No project at {config.project_path}. Path does not exist :/")

    # docstring preprocessing
    if config.args.converter is not None:
        print("\nComment Conversion:\n")
        run_comment_converter(parser, config.project_path, **vars(config.args))

    # documentation generation
    if config.args.disable_doc_gen:
        print("\nDocumentation Generation:\n")

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
        default_dot = shutil.which("dot")
        if default_dot is None:
            parser.error("dot (graphviz) was not found in PATH")
        default_doxygen = shutil.which("doxygen")
        if default_doxygen is None:
            parser.error("doxygen was not found in PATH")
        if config.args.dg_html_theme == "doxygen-awesome" and not config.doxygen_stylesheet_path.is_file():
            parser.error("The stylesheet for doxygen-awesome was not found at its expected path. Try:\n$ git submodule update --init")

        if config.args.apidoc_toolchain == "doxygen-only":
            # generate config file for Doxygen
            with open(Path("Doxyfile.in"), "w+") as doxyfile:
                doxyfile.write(config.DOXYFILE_CONTENT)

            # run doxygen
            system("doxygen Doxyfile.in")

        elif config.args.apidoc_toolchain == "sphinx-based":
            # this path is only here for reference and may be (partially) broken
            #region sphinx-based
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
            #delete_directory_if_exists(exhale_containment_path)  # DEBUG
            #delete_directory_if_exists(sphinx_path / Path("doc"))  # DEBUG
            #system(f"breathe-apidoc -o {exhale_containment_path} -m {str(doxygen_path / Path("xml"))}")  # DEBUG

            # adjust sphinx config for second run
            with open(Path("conf.py"), "w+") as conf_py_file:
                conf_py_file.write(config.CONF_PY_CONTENT)

            # run sphinx again
            # maybe some cleanup is necessary?
            #system(f"sphinx-build -b html . {sphinx_path}")

            #endregion sphinx-based
    
    # coverage
    if config.args.disable_test_cov:
        print("\nTest Coverage Evaluation:\n")
        chdir(config.root_path)
        if config.args.tc_coverage_type == "meson":
            # TODO: allocate variables like project_path (the inline-if)
            meson_build_location: Path = config.project_path
            build_folder_name: Path = Path("build")
            keep_build_folder: bool = False
            meson_setup_args: list[str] = []
            if config.args.tc_meson_build_location is not None:
                meson_build_location = Path(config.args.tc_meson_build_location)
            if config.args.tc_build_folder_name is not None:
                build_folder_name = config.args.tc_build_folder_name
            if config.args.tc_keep_build_folder is not None:
                keep_build_folder = config.args.tc_keep_build_folder
            if config.args.tc_meson_setup_args is not None:
                # TODO: str to list or change meson_setup_args in yaml to list if possible
                pass
            run_meson(meson_build_location, build_folder_name, keep_build_folder, meson_setup_args)
