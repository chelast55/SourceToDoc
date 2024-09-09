from os import chdir

from sourcetodoc.cli.ConfiguredParser import ConfiguredParser
from sourcetodoc.common.Config import Config
from sourcetodoc.docstring.cli import run_comment_converter
from sourcetodoc.docgen.doc_gen import run_documentation_generation
from sourcetodoc.testcoverage.cover_meson import *
from sourcetodoc.testcoverage.linker import *


if __name__ == "__main__":
    parser: ConfiguredParser = ConfiguredParser()
    config = Config()
    config.initialize(parser.parse_args())

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
        # elif

        # Link coverage report and documentation TODO
        link_tc_report_and_documentation_main(out_path, args.project_name)
        link_all_tc_report_and_documentation_files(Path("out"), args.project_name)
        