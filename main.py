from os import chdir

from sourcetodoc.cli.ConfiguredParser import ConfiguredParser
from sourcetodoc.common.Config import Config
from sourcetodoc.docstring.cli import run_comment_converter
from sourcetodoc.docgen.doc_gen import run_documentation_generation
from sourcetodoc.testcoverage.cover_meson import *
from sourcetodoc.testcoverage.cover_cmake import *
from sourcetodoc.testcoverage.linker import *


if __name__ == "__main__":
    parser: ConfiguredParser = ConfiguredParser()
    config = Config(parser.parse_args())

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
        run_documentation_generation(config)
    
    # coverage
    if config.args.disable_test_cov:
        print("\nTest Coverage Evaluation:\n")
        chdir(config.root_path)
        if config.args.tc_coverage_type == "meson":
            # TODO: allocate variables like project_path (the inline-if)
            build_folder_name: Path = Path("build")
            keep_build_folder: bool = False
            meson_build_location: Path = config.project_path
            meson_setup_args: list[str] = []
            if config.args.tc_build_folder_name is not None:
                build_folder_name = config.args.tc_build_folder_name
            if config.args.tc_keep_build_folder is not None:
                keep_build_folder = config.args.tc_keep_build_folder
            if config.args.tc_meson_build_location is not None:
                meson_build_location = Path(config.args.tc_meson_build_location)
            if config.args.tc_meson_setup_args is not None:
                if "--backend" in config.args.tc_meson_setup_args:
                    raise Exception("Forbidden meson setup arg. --backend is not allowed. We only support ninja.")
                meson_setup_args = config.args.tc_meson_setup_args.split(" ")
            run_meson(config.testcoveragereport_path, meson_build_location, build_folder_name, keep_build_folder, meson_setup_args)
        # elif

        if config.args.tc_coverage_type == "cmake":
            build_folder_name: Path = Path("build")
            keep_build_folder: bool = False
            cmakelist_location: Path = config.project_path
            cmake_configure_args: list[str] = [".."]
            cmake_build_args: list[str] = ["."]
            ctest_args: list[str] = []
            ctest_substitute: list[str] = []

            if config.args.tc_build_folder_name is not None:
                build_folder_name = config.args.tc_build_folder_name
            if config.args.tc_keep_build_folder is not None:
                keep_build_folder = config.args.tc_keep_build_folder
            if config.args.tc_cmake_configure_args is not None:
                cmake_configure_args = config.args.tc_cmake_configure_args.split(" ")
            if config.args.tc_cmake_build_args is not None:
                cmake_build_args = config.args.tc_cmake_build_args.split(" ")
            if config.args.tc_ctest_args is not None:
                ctest_args = config.args.tc_ctest_args.split(" ")
            if config.args.tc_ctest_substitute is not None:
                ctest_substitute = config.args.tc_ctest_substitute.split(" ")

            run_cmake(config.testcoveragereport_path, )

        # Link coverage report and documentation
        link_tc_report_and_documentation_main(config.out_path_relative / Path(config.args.project_name))
        link_all_tc_report_and_documentation_files(config.out_path_relative / Path(config.args.project_name))
        