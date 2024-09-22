import itertools
from pathlib import Path
from typing import Iterable, Iterator


def create_default_conf(
        compilation_database_dir: Path,
        diagrams_dir: Path,
        clanguml_include_path: Path
    ) -> tuple[str,list[tuple[str,str]]]:
    """
    Creates a clang-uml configuration for class, package and include diagrams in different flavours.

    Parameters
    ----------
    compilation_database_dir: Path
        The directory that contains the compilation database.
    src_include: Path
        The source code path filter.
    diagrams_dir: Path
        The output directory of the diagrams.

    Returns
    -------
    tuple[str,list[tuple[str,str]]]
        _description_
    """    
    types: list[tuple[str,list[str],str]] = [
        ("class", [], ""),
        ("class", ["generate_packages: true"], "with generated packages"),
        ("package", [], "")
    ]
    package_types: tuple[str,...] = ("namespace", "directory", "module")

    diagram_name_title_pairs: list[tuple[str,str]] = []
    middle_parts: list[str] = []

    for i, ((type, options, description), package_type) in enumerate(itertools.product(types, package_types), 1):
        diagram_title: str = f"{type.capitalize()} Diagram - {package_type.capitalize()} {description}"
        diagram_name: str = f"{type}_diagram_{package_type}_{i}"
        diagram_name_title_pairs.append((diagram_name, diagram_title))

        middle_part: str = _part(diagram_name, type, package_type, clanguml_include_path)
        middle_parts.append(middle_part)
        for suffix in options:
            middle_parts.append("    " + suffix + "\n")

    conf: str = f"""\
{_start_part(compilation_database_dir, diagrams_dir)}
{"".join(middle_parts)}\
  include_diagram:
    type: include
    include:
      paths:
        - "{clanguml_include_path}"
"""
    diagram_name_title_pairs.append(("include_diagram", "Include Diagram"))
    return conf, diagram_name_title_pairs


def create_sequence_diagrams_conf(
        compilation_database_dir: Path,
        diagrams_dir: Path,
        diagram_name_function_identifier_pairs: Iterable[tuple[str, str]]
    ) -> Iterator[str]:
    """
    Creates a clang-uml configuration for sequence diagrams.

    Example:

    `diagram_name_function_identifier_pairs = [("diagram_a","a(void)")]`

    results in this part in the clang-uml configuration file:
    ```yaml
    ...
    diagram_a:
      type: sequence
      from:
        - function: "a(void)"
      exclude:
        namespaces:
          - std
      combine_free_functions_into_file_participants: true
      generate_return_types: true
      generate_condition_statements: true
    ```

    Parameters
    ----------
    compilation_database_dir: Path
        The directory that contains the compilation database.
    output_dir: Path
        The output directory of the diagrams.
    diagram_name_function_identifier_pairs: Iterable[tuple[str, str]]
        2-tuples `(diagram_name,function_identifier)`.

    Yields
    ------
    str
        Parts of the configuration that can be concatenated.
    """    
    yield _start_part(compilation_database_dir, diagrams_dir)
    for e in diagram_name_function_identifier_pairs:
        diagram_name, function_identifier = e
        yield _function_part(diagram_name, function_identifier)


def _start_part(compilation_database_dir: Path, diagrams_dir: Path):
    return f"""\
compilation_database_dir: "{compilation_database_dir}"
output_directory: "{diagrams_dir}"
add_compile_flags:
  - -fparse-all-comments
diagrams:
"""


def _function_part(diagram_name: str, function_identifier: str) -> str:
    return f"""\
  {diagram_name}:
    type: sequence
    from:
      - function: "{function_identifier}"
    exclude:
      namespaces:
        - std
    combine_free_functions_into_file_participants: true
    generate_return_types: true
    generate_condition_statements: true
"""


def _part(
        diagram_name: str,
        type: str,
        package_type: str,
        clanguml_include_path: Path,
    ) -> str:
    return f"""\
  {diagram_name}:
    type: {type}
    package_type: {package_type}
    include:
      paths:
        - "{clanguml_include_path}"
    exclude:
      namespaces:
        - std
"""