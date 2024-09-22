from os import chdir
from time import time

from sourcetodoc.cli.ConfiguredParser import ConfiguredParser
from sourcetodoc.common.Config import Config
from sourcetodoc.docstring.cli import run_comment_converter
from sourcetodoc.docgen.doc_gen import run_documentation_generation
from sourcetodoc.testcoverage.cover_meson import *
from sourcetodoc.testcoverage.linker import *
from sourcetodoc.uml.cli import run_uml_diagrams_generation


if __name__ == "__main__":
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
        run_comment_converter(parser, config.project_path, **vars(config.args))

    t_converter: float = time()

    # documentation generation
    if config.args.disable_doc_gen:
        print("\nDocumentation Generation:\n")
        run_documentation_generation(config)

    t_docgen: float = time()
    
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
            run_meson(config.testcoveragereport_path, meson_build_location, build_folder_name, keep_build_folder, meson_setup_args)
        # elif

        # Link coverage report and documentation
        if config.args.disable_doc_gen:  # can not link TC report to generated documentation, if no documentation was generated
            link_tc_report_and_documentation_main(config.out_path_relative / Path(config.args.project_name))
            link_all_tc_report_and_documentation_files(config.out_path_relative / Path(config.args.project_name))

    t_coverage: float = time()

    # uml diagrams
    if config.args.generate_uml_diagrams:
        run_uml_diagrams_generation(parser, config)
    
    t_uml_diagrams: float = time()

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
