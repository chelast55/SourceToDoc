"""
Contains a CLI argument parser class that automatically supports the functionality defined in various YAML files.
"""

from argparse import ArgumentParser, Namespace
from pathlib import Path
from yaml import safe_load as yaml_safe_load
from typing import Any, Optional, Final, Sequence

ARGS_YAML_PATHS: list[Path] = [
    Path("args_base.yaml"),
    Path("args_doxygen.yaml"),
    Path("args_comment.yaml"),
    Path("args_coverage.yaml")
]
"""Paths to YAML files containing parser arguments."""

REQUIRED_ARG_PARAMS: list[str] = [
    "help", "type"
]
"""
Keys considered mandatory for an argument to be "valid".

- "help":   help message for the argument (technically not mandatory, but enforced anyway for usability reasons)
- "type":   expected (or converted to) type of the argument (enforced (when NOT using 'action') for less need of defensive programming measures)
"""

OPTIONAL_ARG_PARAMS: list[str] = [
    "short", "default", "required", "action", "choices", "const", "dest", "metavar", "nargs", "subparser"
]
"""
Keys that have an effect on an argument, but are not mandatory.

Recommended:
    - "short":      short version of argument (later accessed via "-short", should be no more than a single letter)
    - "default":    default value when no argument is present (defaults to None, except bool, where it defaults to False)
    - "required":   indicator of whether argument is required (should be "false" if not absolutely necessary)
    - "choices":    limit acceptable value range (either a list, range or other container in string representation)

More obscure:
    - "action":     one of ["store" (default), "store_const", "store_true", "append", "append_const", "count", "help", "version"]
                    Automatically set to "store_true"/"store false" when type is "bool" and no action is specified.
                    Note, that "type" can not be used when "store_const" or "append_const" is used
    - "const":      store a const value (becomes required of "action" is set to "store_const")
    - "dest":       specify the attribute name used in the result namespace
    - "metavar":    alternate display name for the argument as shown in help
    - "nargs":      number of times the argument can be used
    - "subparser":  subparser to have this arg live in instead of the "regular" parser.
                    Could either be a single string or a list of strings (hierarchy of subparsers)
                    Note, that only one subparser can be "active" at a time.
"""

PREDEFINED_ARGS: list[dict[str, dict[str, Any]]] = [
    {
        "config": {
            "help": f"Path to a (YAML) configuration file, containing a \"configuration\" for an execution of the toolchain. "
                    f"It should only contain one top-level dictionary with (parameter,value)-pairs (except \"config\" and \"help\"). "
                    f"Calling arguments manually still overwrites the configuration from the file.",
            "type": "Path",
            "default": None
        }
    }
]


class ConfiguredParser(ArgumentParser):

    class SubparserReference:
        """
        Data structure to keep track of subparsers (of subparsers) without accessing protected members.

        Attributes
        ----------
        name: str
            name the referenced subparser is called with
        reference: ArgumentParser
            reference to an ArgumentParser object
        subparsers: dict[str, Optional[ConfiguredParser.SubparserReference]]
            dictionary to keep track of a subparser's subparsers in recursive structure
        """
        def __init__(self, name: str, reference: ArgumentParser):
            """
            Data structure to keep track of subparsers (of subparsers) without accessing protected members.

            Attributes
            ----------
            name: str
                name the referenced subparser is called with
            reference: ArgumentParser
                reference to an ArgumentParser object
            """
            self.name: Final[str] = name
            self.reference: Final[ArgumentParser] = reference
            self.subparsers: dict[str, Optional[ConfiguredParser.SubparserReference]] = {}

        def __str__(self):
            return f"{{name: {self.name}, reference: {self.reference}, subparsers: {self.subparsers}}}"

        def __repr__(self):
            return str(self)

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
        self._args += PREDEFINED_ARGS
        self._subparsers_lookup: dict[str, Optional[ConfiguredParser.SubparserReference]] = {}  # workaround for no public way to access subparsers of a parser
        self._add_arguments_from_dict()

    def parse_args(self,
                   args: Optional[Sequence[str]] = None,
                   namespace: Optional[Namespace] = None) -> Namespace:

        parsed_args: Namespace = super().parse_args(args, namespace)
        parsed_args_dict_reference: dict[str, Any] = vars(parsed_args)

        # get CLI arg values from config YAML file (if --config is used)
        if parsed_args.config is not None:
            if not Path(parsed_args.config).is_file():
                raise OSError(f"{parsed_args.config} is not a file")
            else:
                with (open(parsed_args.config, 'r') as yaml_file):
                    yaml_content = yaml_safe_load(yaml_file)
                    if yaml_content is None:  # check for empty config file
                        raise ValueError(f"{parsed_args.config} is an empty file. Is this the correct config file?")
                    elif not isinstance(yaml_content, dict):  # check if config file is one large YAML dict
                        raise ValueError(
                            f"{parsed_args.config} is not formatted correctly. "
                            f"It should only contain (parameter,value)-pairs (or lines of \"parameter: value\" in YAML syntax)"
                        )
                    else:
                        for arg_name in yaml_content.keys():
                            # check if parameters are strings
                            if not isinstance(arg_name, str):
                                raise TypeError(f"\"{arg_name}\" in {parsed_args.config} is not a string, but {type(arg_name)}.")

                            # check if arg attempts to set value for help or config
                            if arg_name in ["help", "config"]:
                                raise KeyError(
                                    f"\"{arg_name}\" is not a parameter that can be set in a config file.")

                            # check if arg exists (was added to the ConfiguredParser instance as an accepted CLI argument)
                            if arg_name not in self.get_valid_args_list():
                                raise KeyError(
                                    f"\"{arg_name}\" is not a recognized CLI argument. Possible arguments:\n{self.get_valid_args_list()}")

                            # case: no store const action ('type' required)
                            if "type" in self.get_valid_arg_details(arg_name):
                                correct_arg_value_type: type = eval(self.get_valid_arg_details(arg_name)["type"])

                                # check if parsed arg matches its default
                                # (CLI should overwrite config, so only use config value if parsed value IS default)
                                if (
                                        "default" not in self.get_valid_arg_details(arg_name)
                                        and parsed_args_dict_reference[arg_name] is None
                                ) or (
                                        self.get_valid_arg_details(arg_name)["default"] is None
                                        and parsed_args_dict_reference[arg_name] is None
                                ) or (
                                        self.get_valid_arg_details(arg_name)["type"] is bool
                                        and bool(parsed_args_dict_reference[arg_name]) is self.get_valid_arg_details(arg_name)["default"]
                                ) or (
                                        self.get_valid_arg_details(arg_name)["type"] is not bool
                                        and correct_arg_value_type(parsed_args_dict_reference[arg_name]) == self.get_valid_arg_details(arg_name)["default"]
                                ):
                                    if self.get_valid_arg_details(arg_name)["type"] is bool:  # special case: bool values get flipped if flag is set
                                        parsed_args_dict_reference[arg_name] = not parsed_args_dict_reference[arg_name]
                                    else:
                                        parsed_args_dict_reference[arg_name] = correct_arg_value_type(yaml_content[arg_name])
                                else:
                                    print(f"Warning! \"{arg_name}\" set to \"{yaml_content[arg_name]}\" in config, but will be overwritten with \"{parsed_args_dict_reference[arg_name]}\"")

                            # case: args performs store const action ('type' not allowed)
                            elif "action" in self.get_valid_arg_details(arg_name):
                                match self.get_valid_arg_details(arg_name)["action"]:
                                    case "store":
                                        raise RuntimeError(
                                            f"action {self.get_valid_arg_details(arg_name)["action"]} is not implemented for config files yet :/")
                                    case "store_const":
                                        if "const" in self.get_valid_arg_details(arg_name):  # stays None otherwise
                                            parsed_args_dict_reference[arg_name] = self.get_valid_arg_details(arg_name)["const"]
                                    case "store_true":
                                        parsed_args_dict_reference[arg_name] = True
                                    case "store_false":
                                        parsed_args_dict_reference[arg_name] = False
                                    case "append":
                                        raise RuntimeError(
                                            f"action {self.get_valid_arg_details(arg_name)["action"]} is not implemented for config files yet :/")
                                    case "append_const":
                                        raise RuntimeError(
                                            f"action {self.get_valid_arg_details(arg_name)["action"]} is not implemented for config files yet :/")
                                    case "count":
                                        raise RuntimeError(
                                            f"action {self.get_valid_arg_details(arg_name)["action"]} is not implemented for config files yet :/")
                                    case "extend":
                                        raise RuntimeError(
                                            f"action {self.get_valid_arg_details(arg_name)["action"]} is not implemented for config files yet :/")
                                    case "help", "version":
                                        raise ValueError(
                                            f"\"{arg_name}\": action {self.get_valid_arg_details(arg_name)["action"]} is not supported for config files")
        return parsed_args

    def get_cli_args(self) -> list[dict[str, dict[str, Any]]]:
        """
        Get all CLI args supported by this ConfiguredParser.

        The key/value pairs contain each arg's configuration (short form, help text, expected type, default value, ...).

        Returns
        -------
        list[dict[str, dict[str, Any]]]
            List of all CLI args (and their configuration) supported by this ConfiguredParser.
        """
        return list(self._args)

    def get_subparser_hierarchy(self) -> dict[str, Optional[SubparserReference]]:
        """
        Get hierarchy of subparsers supported by this ConfiguredParser.

        Returns
        -------
         dict[str, Optional[SubparserReference]]
            Hierarchy of subparsers supported by this ConfiguredParser.
        """
        return dict(self._subparsers_lookup)

    def get_valid_args_list(self) -> list[str]:
        """
        Get a list of all CLI args supported by this ConfiguredParser.

        The list only contains the ars' names.
        For further details, use get_cli_args() instead.

        Returns
        -------
        list[str]
            List of all CLI args supported by this ConfiguredParser.
        """
        valid_args: list = []
        for arg in self._args:
            key: str = list(arg.keys())[0]
            valid_args.append(key)
        return valid_args

    def get_valid_arg_details(self, desired_arg: str) -> dict[str, Any]:
        """
        TODO: document
        """
        valid_arg_details: dict[str, Any] = {}
        for arg in self._args:
            if desired_arg in arg.keys():
                valid_arg_details = arg[desired_arg]
                break
        return valid_arg_details

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

                    # check if arg shadows any predefined args (help, config, ...)
                    predefined_arg_keys: list = []
                    for predefined_arg in PREDEFINED_ARGS:
                        predefined_arg_keys.append(predefined_arg.keys())
                    if arg_name == "help" or arg_name in predefined_arg_keys:
                        raise KeyError(f"\"{arg_name}\" can not be chosen as an argument name, because it already exists as a predefined argument")

                    arg_params: dict[str, Any] = arg[arg_name]
                    for required_param in REQUIRED_ARG_PARAMS:
                        if required_param not in arg_params.keys():  # check for required parameters missing
                            if not (  # special case, 'type' does not work with these const-storing actions
                                    required_param == "type"
                                    and "action" in arg_params.keys()
                                    and arg_params["action"] in ["store_const", "store_true", "store_false", "append_const"]
                            ):
                                raise KeyError(
                                    f"Required parameter \"{required_param}\" missing in \"{arg_name}\" ({args_yaml_path}).\n"
                                    f"Required parameters: {REQUIRED_ARG_PARAMS}"
                                )
                    for key in arg_params.keys():
                        if not isinstance(key, str):  # check for all keys being strings
                            raise TypeError(f"\"{key}\" in \"{arg_name}\" ({args_yaml_path}) is not a string, but {type(key)}.")

                        if key not in (REQUIRED_ARG_PARAMS + OPTIONAL_ARG_PARAMS):  # check for parameters to be supported
                            raise KeyError(
                                f"\"{key}\" in \"{arg_name}\" ({args_yaml_path}) is not a supported parameter for a CLI argument.\n"
                                f"Supported parameters: {REQUIRED_ARG_PARAMS + OPTIONAL_ARG_PARAMS}"
                        )

                        if key == "subparser":
                            if isinstance(arg_params["subparser"], str):  # single subparser as a string
                                arg_params["subparser"] = [
                                    arg_params["subparser"]]  # easiest, if it is always a list internally
                            elif not isinstance(arg_params["subparser"], list):
                                raise TypeError(f"Subparser(s) for {arg_name} is neither of type str or list[str]: {arg_params["subparser"]}")
                            else:  # case: subparser hierarchy given as a list
                                for subparser in arg_params["subparser"]:
                                    if not isinstance(subparser, str):
                                        raise TypeError(
                                            f"Subparser(s) for {arg_name} is list, but contains non-string elements: {arg_params["subparser"]}")
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
            when one or more of the YAML file paths are invalid.
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
        # duplicate allowed if not within the same parser
        seen_arg_names: dict[str, set[Optional[str]]] = {}  # key: arg name, value: subparsers the name appeared in
        seen_arg_shorts: dict[str, set[Optional[str]]] = {}  # key: arg short, value: subparsers the short appeared in
        for arg in args_list:
            arg_name: str = list(arg.keys())[0]
            arg_params: dict[str, Any] = arg[arg_name]

            # full name
            if not arg_name in seen_arg_names.keys():
                seen_arg_names[arg_name] = set()
            if not "subparser" in arg_params.keys(): # case: top level arg
                if arg_name in seen_arg_names.keys() and None in seen_arg_names[arg_name]:
                    raise KeyError(f"Duplicate CLI argument name found: \"{arg_name}\"")
                seen_arg_names[arg_name].add(None)
            else:  # case: arg inside subparser
                if arg_name in seen_arg_names.keys() and str(arg_params["subparser"]) in seen_arg_names[arg_name]:
                    raise KeyError(f"Duplicate CLI argument name in subparser {arg_params["subparser"]} found: \"{arg_name}\".")
                seen_arg_names[arg_name].add(str(arg_params["subparser"]))

            # short name
            if "short" in arg[arg_name].keys():
                if not arg_params["short"] in seen_arg_shorts.keys():
                    seen_arg_shorts[arg_params["short"]] = set()
                if not "subparser" in arg_params.keys(): # case: top level arg
                    if arg_params["short"] in seen_arg_shorts.keys() and None in seen_arg_shorts[arg_params["short"]]:
                        raise KeyError(f"Duplicate CLI argument short form found: \"{arg_params["short"]}\"")
                    seen_arg_shorts[arg_params["short"]].add(None)
                else:  # case: arg inside subparser
                    if arg_params["short"] in seen_arg_shorts.keys() and str(arg_params["subparser"]) in seen_arg_shorts[arg_params["short"]]:
                        raise KeyError(f"Duplicate CLI argument short form in subparser {arg_params["subparser"]} found: \"{arg_params["short"]}\".")
                    seen_arg_shorts[arg_params["short"]].add(str(arg_params["subparser"]))

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

            if "type" in arg_params.keys() and not arg_params["type"] == "bool":
                add_argument_kwargs["type"] = eval(arg_params["type"])  # having any type set causes most(?) actions (store_true/store_false/etc.) to fail

            if "default" in arg_params.keys():
                if arg_params["default"] is None:
                    add_argument_kwargs["default"] = None
                else:  # perform "dynamic cast" to the type specified in arg_params["type"]
                    add_argument_kwargs["default"] = eval(arg_params["type"])(arg_params["default"])
            elif "type" in arg_params.keys() and arg_params["type"] == "bool":
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

            # add argument (while considering and handling subparsers)
            target_parser: ArgumentParser = self
            if "subparser" in arg_params.keys():
                # check if top-level subparser already exists, create otherwise
                if self._subparsers is None:
                    self._top_level_subparser_reference = self.add_subparsers(dest="subparser", parser_class=ArgumentParser)
                target_subparser = self._top_level_subparser_reference

                # add subparser to parser until "lowest level parser" or "leaf parser"
                target_subparser_lookup: dict[str, Optional[ConfiguredParser.SubparserReference]] = self._subparsers_lookup
                for i in range(len(arg_params["subparser"])):
                    subparser_name: str = arg_params["subparser"][i]  # +readability

                    # check if subparser of this name already exists, create otherwise
                    if not subparser_name in target_subparser_lookup.keys():
                        target_parser = target_subparser.add_parser(subparser_name)
                        target_subparser_lookup[subparser_name] \
                            = ConfiguredParser.SubparserReference(subparser_name, target_parser)
                    else:
                        target_parser = target_subparser_lookup[subparser_name].reference

                    # if current level =/= lowest level, check if subparser for the current parser already exists, create otherwise
                    if not i == len(arg_params["subparser"]) - 1 and len(target_subparser_lookup.keys()) == 0:
                        target_subparser = target_parser.add_subparsers(dest=subparser_name, parser_class=ArgumentParser)
                        target_subparser_lookup = target_subparser_lookup[subparser_name].subparsers

            # add argument to (lowest level sub)parser (duplicate arguments already ruled out)
            target_parser.add_argument(*add_argument_args, **add_argument_kwargs)


if __name__ == "__main__":
    # short test:
    parser: ConfiguredParser = ConfiguredParser()
    print(parser.get_cli_args())
    print(parser.get_subparser_hierarchy())
    args = parser.parse_args()
    print(dir(args))
    parser.print_help()
