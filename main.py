from os import chdir
from time import time
from shutil import copytree

from sourcetodoc.cli.ConfiguredParser import ConfiguredParser
from sourcetodoc.common.Config import Config
from sourcetodoc.docstring.cli import run_comment_converter
from sourcetodoc.docgen.doc_gen import run_documentation_generation
from sourcetodoc.testcoverage.cover_meson import *
from sourcetodoc.testcoverage.cover_cmake import *
from sourcetodoc.testcoverage.linker import *
from sourcetodoc.uml.cli import run_uml_diagrams_generation


if __name__ == "__main__":
    error_in_cc: str = ""
    error_in_dg: str = ""
    error_in_tc: str = ""
    error_in_lnk: str = ""
    error_in_uml: str = ""

    t_start: float = time()
    parser: ConfiguredParser = ConfiguredParser()
    config = Config(parser.parse_args())

    # general stuff
    if not config.project_path.exists():
        raise OSError(f"No project at {config.project_path}. Path does not exist :/")

    t_setup: float = time()

    # docstring preprocessing
    if config.args.converter is not None:
        print("\nComment Conversion:\n")
        try:
            run_comment_converter(parser, config)
        except Exception as e:
            error_in_cc = f"Exception occured while running the Comment Converter:\n{e}"
            print(error_in_cc)
            print("Continuing without further comment conversion...")

    t_converter: float = time()

    # documentation generation
    if config.args.disable_doc_gen:
        print("\nDocumentation Generation:\n")
        try:
            run_documentation_generation(config)
        except Exception as e:
            error_in_dg = f"Exception occured while running the Documentation Generation:\n{e}"
            print(error_in_dg)
            print("Continuing without generating further documentation...")

    t_docgen: float = time()
    
    # coverage
    if config.args.disable_test_cov:
        print("\nTest Coverage Evaluation:\n")
        try:
            chdir(config.root_path)
            if config.args.tc_coverage_type == "meson":
                # TODO: allocate variables like project_path (the inline-if)
                build_folder_name: Path = Path("build")
                keep_build_folder: bool = False
                meson_build_location: Path = config.project_path
                meson_setup_args: list[str] = []
                if config.args.tc_build_folder_name is not None:
                    build_folder_name = Path(config.args.tc_build_folder_name)
                if config.args.tc_delete_build_folder is not None:
                    keep_build_folder = not config.args.tc_delete_build_folder
                if config.args.tc_meson_build_location is not None:
                    meson_build_location = Path(config.args.tc_meson_build_location)
                if config.args.tc_meson_setup_args is not None:
                    if "--backend" in config.args.tc_meson_setup_args:
                        raise Exception("Forbidden meson setup arg. --backend is not allowed. We only support ninja.")
                    meson_setup_args = config.args.tc_meson_setup_args.split(" ")
                run_meson(config.testcoveragereport_path, meson_build_location, build_folder_name, keep_build_folder, meson_setup_args)

            elif config.args.tc_coverage_type == "cmake":
                build_folder_name: Path = Path("build")
                keep_build_folder: bool = False
                project_root: Path = config.project_path
                cmake_configure_args: list[str] = [".."]
                cmake_build_args: list[str] = ["."]
                ctest_args: list[str] = []
                ctest_substitute: list[str] = []

                if config.args.tc_build_folder_name is not None:
                    build_folder_name = Path(config.args.tc_build_folder_name)
                if config.args.tc_delete_build_folder is not None:
                    keep_build_folder = not config.args.tc_delete_build_folder
                if config.args.tc_cmake_configure_args is not None:
                    cmake_configure_args = config.args.tc_cmake_configure_args.split(" ")
                if config.args.tc_cmake_build_args is not None:
                    cmake_build_args = config.args.tc_cmake_build_args.split(" ")
                if config.args.tc_ctest_args is not None:
                    ctest_args = config.args.tc_ctest_args.split(" ")
                if config.args.tc_ctest_substitute is not None:
                    ctest_substitute = config.args.tc_ctest_substitute.split(" ")

                run_cmake(config.testcoveragereport_path, project_root, cmake_configure_args, cmake_build_args, ctest_args, ctest_substitute, build_folder_name, keep_build_folder)

            elif config.args.tc_coverage_type == "generic":
                if config.args.tc_generic_report_location is not None:
                    report_folder: Path = Path(config.args.tc_generic_report_location)
                    if report_folder.exists() and report_folder.is_dir():  # if build failed or is impossible, there is nothing to copy
                        copytree(report_folder, config.testcoveragereport_path, dirs_exist_ok=True)
                    else:
                        raise Exception(f"{config.args.tc_generic_report_location} is not a folder. Please pass the testcoverage containing folder.")
                else:
                    raise Exception("Generic test coverage type was selected but no config.args.tc_generic_report_location was passed.")
        except Exception as e:
            error_in_tc = f"Exception occured while running the Test Coverage Evaluation:\n{e}"
            print(error_in_tc)
            print("Continuing without generating test coverage report...")

        # Link coverage report and documentation
        if config.args.disable_doc_gen:  # can not link TC report to generated documentation, if no documentation was generated
            try:
                link_tc_report_and_documentation_main(config.out_path_relative / Path(config.args.project_name))
                link_all_tc_report_and_documentation_files(config.out_path_relative / Path(config.args.project_name))
            except Exception as e:
                error_in_lnk = f"Exception occured while linking API Documentation and Test Coverage Report:\n{e}"
                print(error_in_lnk)
                print("Continuing without linking...")

    t_coverage: float = time()

    # uml diagrams
    if config.args.generate_uml_diagrams:
        try:
            run_uml_diagrams_generation(parser, config)
        except Exception as e:
            error_in_lnk = f"Exception occured while generating UML diagrams:\n{e}"
            print(error_in_uml)
            print("Continuing without generating further UML...")
    
    t_uml_diagrams: float = time()

    # print if errors occured in any of the tools
    print("\n")
    print(error_in_cc)
    print(error_in_dg)
    print(error_in_tc)
    print(error_in_lnk)
    print(error_in_uml)

    # copy output
    print(f"Output was generated at \"{config.out_path}\"")
    if config.args.output_path is not None:
        output_copy_path: Path = Path(config.args.output_path)
        try:
            chdir(config.root_path)
            output_copy_path.mkdir(parents=True, exist_ok=True)
            copytree(config.out_path / config.args.project_name, output_copy_path, dirs_exist_ok=True)
            print(f"Copied output to \"{output_copy_path.resolve()}\"")
        except Exception as e:
            print(f"Exception while trying to copy toolchain output to \"{config.args.output_path}\":\n{e}")
            print("Copied output may be incomplete or non-existing.")

    if config.args.measure_runtime:
        print("\n")
        print(f"Runtime measurements:\n"
              f"\n"
              f"Toolchain Setup: {t_setup - t_start} seconds\n"
              f"Comment Converter: {t_converter - t_setup} seconds\n"
              f"Documentation Generation: {t_docgen - t_converter} seconds\n"
              f"Test Coverage Evaluation: {t_coverage - t_docgen} seconds\n"
              f"UML Diagrams Generation: {t_uml_diagrams - t_coverage} seconds \n"
              f"\n"
              f"Total toolchain runtime: {t_uml_diagrams - t_start}")
