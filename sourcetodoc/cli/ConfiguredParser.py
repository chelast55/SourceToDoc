"""
Contains a CLI argument parser class that automatically supports the functionality defined in various YAML files.
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
    - "default":    default value when no argument is present (defaults to None, except bool, where it defaults to False)
    - "required":   indicator of whether argument is required (should be "false" if not absolutely necessary)
    - "choices":    limit acceptable value range (either a list, range or other container in string representation)

More obscure:
    - "action":     one of ["store", "store_const", "store_true", "append", "append_const", "count", "help", 'version"]
                    defaults to "store_true" when type is "bool" and not specified otherwise
    - "const":      store a const value
    - "dest":       specify the attribute name used in the result namespace
    - "metavar":    alternate display name for the argument as shown in help
    - "nargs":      number of times the argument can be used
"""

class ConfiguredParser(ArgumentParser):
    def __init__(self):
        """
        CLI argument parser class that is preconfigured to support the functionality defined in various YAML files.

        Additional files can be added by (statically) expanding ARGS_YAML_PATHS.
        The content of each file is thoroughly checked (for wrong syntax, wrong structure, duplicate arguments, etc.)
        before registering arguments.
        Bools are automatically handled as flags that enable by default.
        The YAML loading/parsing fucntionality can be accessed statically.

        Intended optional keyword arguments:
            - prog -- The name of the program (default: ``os.path.basename(sys.argv[0])``)
            - usage -- A usage message (default: auto-generated from arguments)
            - description -- A description of what the program does
            - epilog -- Text following the argument descriptions
            - parents -- Parsers whose arguments should be copied into this one
            - formatter_class -- HelpFormatter class for printing help messages
            - conflict_handler -- String indicating how to handle conflicts
            - exit_on_error -- Determines whether or not ArgumentParser exits with error info when an error occurs
        """
        ArgumentParser.__init__(self)
        self._args: list[dict[str, dict[str, Any]]] = self.load_yamls_combined_and_check_structure(ARGS_YAML_PATHS)
        self._add_arguments_from_dict()

    def get_cli_args(self) -> list[dict[str, dict[str, Any]]]:
        """
        Get all CLI args supported by this ConfiguredParser.

        The key/value pairs contain each arg's configuration (short form, help text, expected type, default value, ...).

        Returns
        -------
        list[dict[str, dict[str, Any]]]
            List of all CLI args supported by this ConfiguredParser.
        """
        return self._args

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
        with open(Path(__file__).parent / args_yaml_path, 'r') as yaml_file:  # (indirect)
            yaml_content = yaml_safe_load(yaml_file)
            if not isinstance(yaml_content, list):  # check for list on top level
                raise TypeError(f"Content of {args_yaml_path} does not contain a list at top level.")
            else:
                for arg in yaml_content:
                    if not isinstance(arg, dict):  # check for all entries being dicts
                        raise TypeError(f"{arg} in {args_yaml_path} is not a dictionary.")
                    if not len(arg.keys()) == 1 and isinstance(list(arg.keys())[0], str):  # check for 1 string beeing the only key
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
            ConfiguredParser.check_for_duplicate_argument_names(yaml_content)
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

        ConfiguredParser.check_for_duplicate_argument_names(combined_yaml_content)
        return combined_yaml_content

    @staticmethod
    def check_for_duplicate_argument_names(args_list: list[dict[str, Any]]):
        seen_arg_names: set[str] = set()
        seen_arg_shorts: set[str] = set()
        for arg in args_list:
            arg_name: str = list(arg.keys())[0]
            if arg_name in seen_arg_names:
                raise KeyError(f"Duplicate CLI argument name found: \"{arg_name}\"")
            seen_arg_names.add(arg_name)
            if "short" in arg[arg_name].keys():
                if arg[arg_name]["short"] in seen_arg_shorts:
                    raise KeyError(f"Duplicate CLI argument short form found: \"{arg[arg_name]["short"]}\"")
                seen_arg_shorts.add(arg[arg_name]["short"])

    def _add_arguments_from_dict(self):
        """
        Iterates over self.__args and registers (self.add_argument) all CLI args (stored as dicts) as actions.

        Optional parameters are only cosidered when they are present.
        When the type of the parameter is bool, additional steps are performed, to make it behave correctly as a flag.
        This does not check if the dict's content is valid, as this is expected to be done while generating the dict.
        """
        for arg in self._args:
            arg_name: str = list(arg.keys())[0]
            arg_params: dict[str, Any] = arg[arg_name]

            add_argument_args: list[str] = [f'--{arg_name}']

            if "short" in arg_params.keys():
                add_argument_args.insert(0, f'-{arg_params["short"]}')

            add_argument_kwargs: dict[str, Any] = {"help": arg_params["help"]}

            if not arg_params["type"] == "bool":  # having any type set causes store_true/store_false to fail
                add_argument_kwargs["type"] = eval(arg_params["type"])

            if "default" in arg_params.keys():
                if arg_params["default"].upper() in ["NONE", "NULL"]:
                    add_argument_kwargs["default"] = None
                elif arg_params["default"].upper() == "TRUE":
                    add_argument_kwargs["default"] = True
                elif arg_params["default"].upper() == "FALSE":
                    add_argument_kwargs["default"] = False
                else:
                    # perform "dynamic cast" to the type specified in arg_params["type"]
                    add_argument_kwargs["default"] = eval(arg_params["type"])(arg_params["default"])
            elif arg_params["type"] == "bool":
                add_argument_kwargs["default"] = False

            if "required" in arg_params.keys():
                add_argument_kwargs["required"] = arg_params["required"]

            if "choices" in arg_params.keys():
                add_argument_kwargs["choices"] = arg_params["choices"]

            if "action" in arg_params.keys():
                add_argument_kwargs["action"] = arg_params["action"]
            elif arg_params["type"] == "bool":
                if add_argument_kwargs["default"] is True:
                    add_argument_kwargs["action"] = "store_false"
                else:
                    add_argument_kwargs["action"] = "store_true"

            if "const" in arg_params.keys():
                add_argument_kwargs["const"] = arg_params["const"]

            if "dest" in arg_params.keys():
                add_argument_kwargs["dest"] = arg_params["dest"]

            if "metavar" in arg_params.keys():
                add_argument_kwargs["metavar"] = arg_params["metavar"]

            if "nargs" in arg_params.keys():
                add_argument_kwargs["nargs"] = arg_params["nargs"]

            self.add_argument(*add_argument_args, **add_argument_kwargs)

if __name__ == "__main__":
    # short test:
    parser: ConfiguredParser = ConfiguredParser()
    print(parser.get_cli_args())
    args = parser.parse_args()
    print(dir(args))
    parser.print_help()
