import base64
import os
import re
import subprocess
from enum import Enum
from itertools import chain
from pathlib import Path
from typing import Iterable, Iterator

from .conf_utils import create_default_conf, create_sequence_diagrams_conf
from .find_functions import FindOption, find_functions_with_libclang
from .function_identifier import FunctionIdentifier


class GeneratorType(Enum):
    PLANTUML = "plantuml"
    MERMAIDJS = "mermaid"
    JSON = "json"


# Diagram name for a dummy clang-uml configuration file to get function identifiers with `clang-uml --print-from`
_SEQUENCE_DUMMY: str = "sequence_dummy"

# Used to identify "empty" diagrams to delete
_FAILED_CONTENT_START = """\
@startuml

'Generated with clang-uml"""


class ClangUML:
    def __init__(
            self,
            compilation_db_dir: Path,
            clanguml_include_path: Path,
            plantuml_jar_path: Path | None = None,
            clanguml_args: list[str] | None = None,
            clanguml_cwd: Path | None = None,
        ) -> None:
        self.compilation_db_dir = compilation_db_dir
        self.clanguml_include_path = clanguml_include_path
        self.plantuml_jar_path = plantuml_jar_path
        if clanguml_args is None:
            clanguml_args = []
        self.clanguml_args = clanguml_args
        self.clanguml_cwd = clanguml_cwd
    
    def create_default_conf_file(self, conf_path: Path, diagrams_dir: Path) -> list[tuple[str,str]]:
        """
        Creates a clang-uml configuration file for class, package and include diagrams in different flavours.
    
        Tries to create parent directories  be created if none exist.

        Parameters
        ----------
        conf_path: Path
            The file to create.
        diagrams_dir: Path
            The output directory of the diagrams.

        Returns
        -------
        list[tuple[str,str]]
            A list of 2-tuples `(diagram_name,diagram_title)`.
        """
        diagrams_dir_from_conf_path: Path = diagrams_dir
        compilation_db_dir_from_conf_path: Path = self.compilation_db_dir
        clanguml_include_path_from_conf_path: Path = self.clanguml_include_path
        # Adjust relative paths with conf_path as start
        if not diagrams_dir.is_absolute():
            diagrams_dir_from_conf_path = Path(os.path.relpath(diagrams_dir, conf_path.parent))
        if not self.compilation_db_dir.is_absolute():
            compilation_db_dir_from_conf_path: Path = Path(os.path.relpath(self.compilation_db_dir, conf_path.parent))
        if not self.clanguml_include_path.is_absolute():
            clanguml_include_path_from_conf_path = Path(os.path.relpath(self.clanguml_include_path, conf_path.parent))

        default_conf, diagram_name_title_paris = create_default_conf(
            compilation_db_dir_from_conf_path,
            diagrams_dir_from_conf_path,
            clanguml_include_path_from_conf_path
        )
        conf_path.parent.mkdir(parents=True, exist_ok=True)
        with open(conf_path, "w") as f:
            f.write(default_conf)
        return diagram_name_title_paris

    def create_sequence_conf_file(
            self,
            conf_path: Path,
            diagrams_dir: Path,
            find_option: FindOption
        ) -> list[tuple[str,str]]:
        """
        Creates a clang-uml configuration file for sequence diagrams.
    
        Tries to create parent directories  be created if none exist.

        Parameters
        ----------
        conf_path: Path
            The file to create.
        diagrams_dir: Path
            The output directory of the diagrams.
        find_option: FindOption
            Function filter.

        Returns
        -------
        list[tuple[str,str]]
            A list of 2-tuples `(diagram_name,function_identifier)`.
        """
        diagrams_dir_from_conf_path: Path = diagrams_dir
        compilation_db_dir_from_conf_path: Path = self.compilation_db_dir
        # Adjust relative paths with conf_path as start
        if not diagrams_dir.is_absolute():
            diagrams_dir_from_conf_path = Path(os.path.relpath(diagrams_dir, conf_path.parent))
        if not self.compilation_db_dir.is_absolute():
            compilation_db_dir_from_conf_path: Path = Path(os.path.relpath(self.compilation_db_dir, conf_path.parent))

        found_functions: Iterable[FunctionIdentifier] = find_functions_with_libclang(self.compilation_db_dir, find_option)
        diagram_name_function_identifier_pairs: list[tuple[str,str]] = [(_diagram_name(e), str(e)) for e in found_functions]
        seq_diagram_conf: Iterable[str] = create_sequence_diagrams_conf(
            compilation_db_dir_from_conf_path,
            diagrams_dir_from_conf_path,
            diagram_name_function_identifier_pairs
        )
        conf_path.parent.mkdir(parents=True, exist_ok=True)
        with open(conf_path, "w") as f:
            f.writelines(seq_diagram_conf)
        return diagram_name_function_identifier_pairs
    
    def generate_intermediate_files(self, conf_path: Path, diagrams_dir: Path, generator_type: GeneratorType) -> None:
        """
        Executes clang-uml to create `.puml`, `.mmd`, or `.json` files.

        Parameters
        ----------
        conf_path: Path
            The clang-uml configuration file to use.
        diagrams_dir: Path
            The output directory of the diagrams.
        generator_type: GeneratorType
            Function filter.
        """
        subprocess.run(
            ["clang-uml", "-c", str(conf_path), "-g", generator_type.value, "-o", str(diagrams_dir)] + self.clanguml_args,
            cwd=self.clanguml_cwd,
            check=True)

        # Remove empty diagrams produced by clang-uml
        match generator_type:
            case GeneratorType.PLANTUML:
                for file in diagrams_dir.glob("*.puml"):
                    if file.read_text().startswith(_FAILED_CONTENT_START):
                        file.unlink()
            case _:
                pass

    def run_plantuml(self, diagrams_dir: Path) -> None:
        """
        Executes PlantUML to generate `.svg` files from `.puml` files in `diagram_dir`.

        Parameters
        ----------
        diagrams_dir: Path
            The directory.
        """
        if self.plantuml_jar_path is None:
            subprocess.run(["plantuml", "-tsvg", "*.puml"], cwd=diagrams_dir, check=True)
        else:
            subprocess.run(["java", "-jar", str(self.plantuml_jar_path), "-tsvg", "*.puml"], cwd=diagrams_dir, check=True)

    def run_mermaid(self, diagrams_dir: Path) -> None:
        """
        Executes Mermaid to generate `.svg` files from `.mmd` files in `diagram_dir`.

        Parameters
        ----------
        diagrams_dir: Path
            The directory.
        """
        for mmd_path in diagrams_dir.glob("*.mmd"):
            if mmd_path.is_dir():
                continue
            subprocess.run(["mmdc", "-i", str(mmd_path), "-o", mmd_path.stem + ".svg"], cwd=diagrams_dir, check=True)

    def _find_functions_with_clanguml(self, compilation_db_dir: Path, find_option: FindOption) -> Iterator[FunctionIdentifier]:
        """
        Executes clang-uml with the `--print-from` option to get a list of candidate functions to create sequence diagrams from.

        A temporary dummy configuration diagram will be passed in stdin of clang-uml.

        Warning: `FindOption.NOT_PRIVATE_OR_PROTECTED` does not work correctly. Public methods can be excluded if that value is passed.
        """
        include_private_and_protected: bool = False if FindOption.EXCLUDE_PRIVATE_AND_PROTECTED else True
        conf: str = _dummy_sequence_diagram_conf(compilation_db_dir, self.clanguml_include_path, include_private_and_protected)
        command: list[str] = ["clang-uml", "-c", "-", "--print-from", "-n", _SEQUENCE_DUMMY] + self.clanguml_args
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            cwd=self.clanguml_cwd,
            text=True,
        )
        if process.stdin is None or process.stdout is None:
            raise RuntimeError("Either stdin or stdout is None")

        process.stdin.write(conf)
        process.stdin.close()

        for line in iter(process.stdout.readline, ""):
            item: FunctionIdentifier = FunctionIdentifier.parse(line.removesuffix("\n"))
            if (find_option is FindOption.ONLY_MAIN_FUNCTION and item.is_main_function() or find_option is not FindOption.ONLY_MAIN_FUNCTION):
                yield item

        process.wait()
        process.stdout.close()

        if process.returncode != 0:
            raise RuntimeError(f"Non-zero return code: {command}")

_NON_VAR_NAME = re.compile(r"[^_a-zA-Z0-9].*")


def _urlsafe_base64_and_add_underscore_prefix(match: re.Match[str]) -> str:
    return "_" + base64.urlsafe_b64encode(match.group().encode()).decode()


def _diagram_name(function_identifier: FunctionIdentifier) -> str:
    function_args_encoded = _NON_VAR_NAME.sub(_urlsafe_base64_and_add_underscore_prefix, function_identifier.function(), count=1)
    result = "_".join(chain(function_identifier.namespaces_and_classes(), (function_args_encoded,)))
    return result


def _dummy_sequence_diagram_conf(compilation_db_dir: Path, src_include: Path, include_private_and_protected: bool) -> str:
    conf: str = f"""\
compilation_database_dir: "{compilation_db_dir}"
diagrams:
  {_SEQUENCE_DUMMY}:
    type: sequence
    include:
      paths:
        - "{src_include}"
    exclude:
      namespaces:
        - std
"""
    if include_private_and_protected:
        return conf
    else:
        return conf + f"""\
      access:
        - private
        - protected
"""
