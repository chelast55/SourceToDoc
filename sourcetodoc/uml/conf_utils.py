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
        2-tuples `(diagram_name,diagram_title)`.
    """
    diagram_name_title_pairs: list[tuple[str,str]] = []
    conf: list[str] = []
    # Start of config file
    conf.append(_start_part(compilation_database_dir, diagrams_dir))

    # Add class diagram
    diagram_name_class = "class_diagram"
    diagram_name_title_pairs.append((diagram_name_class, "Class Diagram"))
    conf.append(_part_with_include_path_and_exclude_std_namepace(diagram_name_class, "class", "namespace", clanguml_include_path))

    # Add variations of class and package diagrams
    types: list[tuple[str,list[str]]] = [
        ("class", ["generate_packages: true"]),
        ("package", [])
    ]
    package_types: tuple[str,...] = ("namespace", "directory", "module")
    for (type, options), package_type in itertools.product(types, package_types):
        diagram_title: str = f"{type.capitalize()} Diagram - {package_type.capitalize()}"
        diagram_name: str = f"{type}_diagram_{package_type}"
        diagram_name_title_pairs.append((diagram_name, diagram_title))
        conf.append(_part_with_include_path_and_exclude_std_namepace(diagram_name, type, package_type, clanguml_include_path))
        for suffix in options:
            conf.append("    " + suffix + "\n")

    # Add include diagram
    diagram_name_include = "include_diagram"
    diagram_name_title_pairs.append((diagram_name_include, "Include Diagram"))
    conf.append(_part_with_include_path(diagram_name_include, "include", clanguml_include_path))

    return "".join(conf), diagram_name_title_pairs


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

def _part_with_include_path_and_exclude_std_namepace(
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

def _part_with_include_path(
        diagram_name: str,
        type: str,
        clanguml_include_path: Path
    ) -> str:
    return f"""\
  {diagram_name}:
    type: {type}
    include:
      paths:
        - "{clanguml_include_path}"
"""
