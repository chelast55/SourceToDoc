from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
import shutil

from ..common.Config import Config

from ..common.helpers import delete_directory_contents

from .clanguml import ClangUML, GeneratorType
from .find_functions import FindOption
from .site import DiagramsInfo, create_diagrams_site


@dataclass(frozen=True)
class SequenceDiagramsConfig:
    find_option: FindOption


@dataclass(frozen=True)
class UmlConfig:
    compilation_db_dir: Path
    clanguml_include_path: Path
    plantuml_jar_path: Path | None = None
    clanguml_args: list[str] | None = None
    sequence_diagrams_config: SequenceDiagramsConfig | None = None


def run_uml_diagrams_generation(parser: ArgumentParser, config: Config) -> None:
    args = config.args

    if args.uml_compilation_db_dir is None:
        parser.error("--uml_compilation_db_dir is required")
    compilation_db_dir: Path = Path(args.uml_compilation_db_dir)

    clanguml_include_path: Path = Path(args.uml_include_path) if args.uml_include_path else config.project_path

    plantuml_jar_path: Path | None = None
    if shutil.which("plantuml") is None:
        if args.uml_plantuml_jar_path is None:
            parser.error("--uml_plant_uml_jar is required because plantuml was not found")
        else:
            plantuml_jar_path = Path(args.uml_plantuml_jar_path)

    clanguml_args: list[str]
    if args.uml_query_driver_dot:
        clanguml_args = ["--query-driver", "."]
    else:
        clanguml_args = []

    seq_diagrams_config: SequenceDiagramsConfig | None = None
    if args.uml_sequence_diagrams:
        match args.uml_find_option:
            case "all":
                find_option = FindOption.ALL
            case "exclude_private_and_protected":
                find_option = FindOption.EXCLUDE_PRIVATE_AND_PROTECTED
            case "only_main_function":
                find_option = FindOption.ONLY_MAIN_FUNCTION
            case _:
                raise ValueError(f"Invalid value: args.uml_find_option = {args.uml_find_option}")
        seq_diagrams_config = SequenceDiagramsConfig(find_option)

    uml_config = UmlConfig(
        compilation_db_dir,
        clanguml_include_path,
        plantuml_jar_path,
        clanguml_args,
        seq_diagrams_config
    )

    dst_dir = config.out_path / "uml"
    generate_uml_diagrams(dst_dir, config, uml_config)


_GENERATOR_TYPE = GeneratorType.PLANTUML


def generate_uml_diagrams(
        dst_dir: Path,
        config: Config,
        uml_config: UmlConfig,
    ) -> None:
    clanguml = ClangUML(
        uml_config.compilation_db_dir,
        uml_config.clanguml_include_path,
        uml_config.plantuml_jar_path,
        uml_config.clanguml_args,
        uml_config.compilation_db_dir, # To prevent "not found translation unit error" by clang-uml 0.5.4
    )
    if dst_dir.is_dir():
        print(f"Clean contents of {dst_dir}")
        delete_directory_contents(dst_dir)

    default_diagrams_conf = config.project_path / "default-clang-uml.yaml"
    default_diagrams_dir = dst_dir / "default_diagrams"

    diagram_name_titles_pairs = clanguml.create_default_conf_file(default_diagrams_conf, default_diagrams_dir)
    clanguml.generate_intermediate_files(default_diagrams_conf, default_diagrams_dir, _GENERATOR_TYPE)
    clanguml.run_plantuml(default_diagrams_dir)

    default_diagrams_info = DiagramsInfo(default_diagrams_dir, diagram_name_titles_pairs)

    sequence_diagrams_info: DiagramsInfo | None = None
    if uml_config.sequence_diagrams_config is not None:
        sequence_diagrams_conf = config.project_path / "clang-uml-sequence-diagrams.yaml"
        sequence_diagrams_dir = dst_dir / "sequence_diagrams"
        diagram_name_function_identifier_pairs = clanguml.create_sequence_conf_file(
            sequence_diagrams_conf,
            sequence_diagrams_dir,
            uml_config.sequence_diagrams_config.find_option
        )
        clanguml.generate_intermediate_files(sequence_diagrams_conf, sequence_diagrams_dir, _GENERATOR_TYPE)
        clanguml.run_plantuml(sequence_diagrams_dir)
        sequence_diagrams_info = DiagramsInfo(sequence_diagrams_dir, diagram_name_function_identifier_pairs)

    create_diagrams_site(dst_dir, default_diagrams_info, sequence_diagrams_info)
