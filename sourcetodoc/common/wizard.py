from argparse import Namespace
from pathlib import Path
from typing import Any, Optional

ACCEPTED_INPUT_BOOL_LOOKUP: dict[str, bool] = {
    "YES": True,
    "Y": True,
    "NO": False,
    "N": False
}

MSG_PLACEHOLDER: str = '$'

MSG_WELCOME: str = "Welcome to SourceToDoc - the documentation and design reverse engineering toolchain!"
MSG_ASK_FOR_PROJECT_NAME: str = "Please enter the name of the project you want to use this on:\n"
MSG_PROJECT_DIR_FOUND_CONFIRM: str = "Found directory at \"$\". Is this the correct project directory? (yes/no)\n"
MSG_PROJECT_DIR_CONFIRM_TRY_AGAIN: str = "\"$\" is not an accepted answer."


def run_wizard(args: Namespace):
    print(MSG_WELCOME)

    # project_name
    temp_project_name: str = input(MSG_ASK_FOR_PROJECT_NAME).strip()
    temp_project_name_to_path: Path = Path(__file__).parent.parent.parent / temp_project_name
    explicit_project_path: bool = True
    if temp_project_name_to_path.exists() and temp_project_name_to_path.is_dir():  # case: directory with project name exists
        temp_answer_project_dir_confirm: bool | str = ""
        while type(temp_answer_project_dir_confirm) is str:
            temp_answer_project_dir_confirm = input_expect_bool(
                MSG_PROJECT_DIR_FOUND_CONFIRM, temp_project_name_to_path
            )
            if temp_answer_project_dir_confirm is str:
                print(MSG_PROJECT_DIR_CONFIRM_TRY_AGAIN)
        if temp_answer_project_dir_confirm:
            args.project_name = temp_project_name

    # TODO: implement the rest!
    # TODO: control flow diagram?


def input_with_replace(prompt: str, replacement: Any) -> str:

    """
    input(), but everything in the prompt that matches `MSG_PLACEHOLDER` will be replaced with `replacement`

    Parameters
    ----------
    prompt: str
        The prompt to display to the user
    replacement: Any
        The string (or string representation of Any) to replace the placeholder with

    Returns
    -------
    str
        The processed user input

    Documentation for input():
    Read a string from standard input. The trailing newline is stripped.
    The prompt string, if given, is printed to standard output without a trailing newline before reading input.
    If the user hits EOF (*nix: Ctrl-D, Windows: Ctrl-Z+Return), raise EOFError. On *nix systems, readline is used if
    available.
    `input(__prompt="")` on docs.python.org
    """
    return input(prompt.replace(MSG_PLACEHOLDER, str(replacement)))


def input_expect_bool(prompt: str, replacement: Any = "") -> bool | str:
    """
    input(), but user is expected to answer a yes/no-question and the answer is translated to a boolean value.

    The user input will be parsed according to what is defined in `ACCEPTED_INPUT_BOOL_LOOKUP`.
    If the user input is invalid and can not be translated to a boolean value, the raw input is returned.
    Everything in the prompt that matches `MSG_PLACEHOLDER` will be replaced with `replacement`.

    Parameters
    ----------
    prompt: str
        The prompt to display to the user
    replacement: Any (optional, defaults to empty string)
        The string (or string representation of Any) to replace the placeholder with

    Returns
    -------
    bool | str
        The processed user input. Boolean value if user input was valid, raw input string otherwise.
    """
    answer: bool | str = input_with_replace(prompt, replacement).upper()
    answer = ACCEPTED_INPUT_BOOL_LOOKUP[answer] if answer in ACCEPTED_INPUT_BOOL_LOOKUP.keys() else answer
    return answer
