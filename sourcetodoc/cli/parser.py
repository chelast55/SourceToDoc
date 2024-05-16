"""
Contains a CLI argument parser class that automatically supports the functionality defined in args_base.yaml
"""

from argparse import ArgumentParser
from pathlib import Path
from yaml import safe_load as yaml_safe_load
from typing import Any

ARGS_YAML_PATHS: list[Path] = [
    Path("args_base.yaml")
]
"""Paths to YAML files containing parser arguments."""

REQUIRED_ARG_PARAMS: list[str] = [
    "help", "type"
]
"""
Keys considered mandatory for an argument to be "valid".

- "help":   help message for the argument (technically not mandatory, but enforced anyway for usability reasons)
- "type":   expected (or converted to) type of the argument (enforced for less need of defensive programming measures)
"""

OPTIONAL_ARG_PARAMS: list[str] = [
    "short", "default", "required", "action", "choices", "const", "dest", "metavar", "nargs"
]
"""
Keys that have an effect on an argument, but are not mandatory.

Recommended:
    - "short":      short version of argument (later accessed via "-short", should be no more than a single letter)
    - "default":    default value when no argument is present (defaults to None)
    - "required":   indicator of whether argument is required (should be "false" if not absolutely necessary)
    - "choices":    limit acceptable value range (either a list, range or other container in string representation)

More obscure:
    - "action":     one of ["store", "store_const", "store_true", "append", "append_const", "count", "help", 'version"]
                    "store_true" is automatically added when type is "bool"
    - "const":      store a const value
    - "dest":       specify the attribute name used in the result namespace
    - "metavar":    alternate display name for the argument as shown in help
    - "nargs":      number of times the argument can be used

"""

class ConfiguredParser(ArgumentParser):
    def __init__(self):
        """
        TODO: document!
        Additional files can be added by (statically) expanding ARGS_YAML_PATHS.
        """
        ArgumentParser.__init__(self)
        self.__args: list[dict[str, dict[str, Any]]] = self.load_yamls_combined_and_check_structure(ARGS_YAML_PATHS)
        # TODO: add args (special consideration for name and short)

    def get_cli_args(self) -> list[dict[str, dict[str, Any]]]:
        """
        Get all CLI args supported by this ConfiguredParser.

        The key/value pairs contain each arg's configuration (short form, help text, expected type, default value, ...).

        Returns
        -------
        list[dict[str, dict[str, Any]]]
            List of all CLI args supported by this ConfiguredParser.
        """
        return self.__args

    @staticmethod
    def load_yaml_and_check_structure(args_yaml_path: Path) -> list[dict[str, dict[str, Any]]]:
        """
        Load CLI arguments defined in a YAML file into a list of dictionaries.

        Includes validity check of the YAML files' structure and content.
        The key/value pairs contain each arg's configuration (short form, help text, expected type, default value, ...).
        This will raise various unhandled (detailed) exceptions when something is wrong with the given YAML file.

        Parameters
        ----------
        args_yaml_path: Path
            Path to YAML file containing configuration for CLI arguments.

        Returns
        -------
        list[dict[str, Any]]
            List of (validity-checked) CLI args extracted from the YAMl source file.

        Raises
        ------
        FileNotFoundError
            when the YAMl file path is invalid.
        TypeError
            when the YAML file contains values of the wrong type at expected locations.
        KeyError
            when the YAML file contains unexpected values or is missing required values.
        """
        with open(args_yaml_path, 'r') as yaml_file:  # (indirect)
            yaml_content = yaml_safe_load(yaml_file)
            if not isinstance(yaml_content, list):  # check for list on top level
                raise TypeError(f"Content of {args_yaml_path} does not contain a list at top level.")
            else:
                for arg in yaml_content:
                    if not isinstance(arg, dict):  # check for all entries being dicts
                        raise TypeError(f"{arg} in {args_yaml_path} is not a dictionary.")
                    if not len(arg.keys()) == 1 and isinstance(list(arg.keys())[0], str):
                        raise KeyError(
                            f"Entry with Key {list(arg.keys())} does not contain exactly 1 key of type str.\n"
                            f"The single key acts a the arg's name."
                        )
                    arg_name: str = list(arg.keys())[0]
                    arg_params: dict[str, Any] = arg[arg_name]
                    for required_param in REQUIRED_ARG_PARAMS:
                        if not required_param in arg_params.keys():  # check for required parameters missing
                            raise KeyError(
                                f"Required parameter \"{required_param}\" missing in \"{arg_name}\" ({args_yaml_path}).\n"
                                f"Required parameters: {REQUIRED_ARG_PARAMS}"
                            )
                    for key in arg_params.keys():
                        if not isinstance(key, str):  # check for all keys being strings
                            raise TypeError(f"\"{key}\" in \"{arg_name}\" ({args_yaml_path}) is not a string.")
                        if not key in (REQUIRED_ARG_PARAMS + OPTIONAL_ARG_PARAMS):  # check for parameters to be supported
                            raise KeyError(
                                f"\"{key}\" in \"{arg_name}\" ({args_yaml_path}) is not a supported parameter for a CLI argument.\n"
                                f"Supported parameters: {REQUIRED_ARG_PARAMS + OPTIONAL_ARG_PARAMS}"
                        )
            return yaml_content

    @staticmethod
    def load_yamls_combined_and_check_structure(args_yaml_paths: list[Path]) -> list[dict[str, dict[str, Any]]]:
        """
        Load CLI arguments defined in potentially multiple YAML files into a single list of dictionaries.

        Includes validity check of the YAML files' structure and content.
        The key/value pairs contain each arg's configuration (short form, help text, expected type, default value, ...).

        Parameters
        ----------
        args_yaml_paths: list[Path]
            List of paths to YAML files containing configuration for CLI arguments.

        Returns
        -------
        list[dict[str, Any]]
            List of (validity-checked) CLI args from all YAMl sources combined.

        Raises
        ------
        FileNotFoundError
            when one or more of the YAMl file paths are invalid.
        TypeError
            when one or more of the YAML files contain values of the wrong type at expected locations.
        KeyError
            when one or more of the YAML files contain unexpected values or is missing required values.
        """
        combined_yaml_content: list[dict[str, dict[str, Any]]] = []
        for args_yaml_path in args_yaml_paths:
            combined_yaml_content += ConfiguredParser.load_yaml_and_check_structure(args_yaml_path)
        return combined_yaml_content

if __name__ == "__main__":
    # short test:
    parser: ConfiguredParser = ConfiguredParser()
    print(parser.get_cli_args())
