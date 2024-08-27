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
MSG_UNACCEPTED_ANSWER: str = "\"$\" is not an accepted answer."
MSG_ASK_FOR_PROJECT_DIRECTORY: str = "Please enter the path to the root directory of the project \"$\":\n"
MSG_ASK_CONVERTER: str = ("Do you want to use the Comment Converter tool? (yes/no)\n"
                          "(recommended: \"yes\", as it may lead to better generated documentation, but keep in mind "
                          "that this will modify the source code in \"$\")\n")
MSG_ASK_DOCGEN: str = "Do you want to use the Documentation Generation tool? (yes/no)\n"
MSG_ASK_TESTCOV: str = ("Do you want to use the Testcoverage Evaluation tool? (yes/no)\n"
                        "(to use properly, make sure the project in \"$\" is set up to build correctly)\n")


def run_wizard(args: Namespace):
    print(MSG_WELCOME)

    # project_name
    temp_project_name: str = input(MSG_ASK_FOR_PROJECT_NAME).strip()
    temp_project_name_to_path: Path = Path(__file__).parent.parent.parent / temp_project_name
    args.project_name = temp_project_name
    explicit_project_path: bool = True
    if temp_project_name_to_path.exists() and temp_project_name_to_path.is_dir():
        temp_answer_project_dir_confirm: bool | str = ""
        while type(temp_answer_project_dir_confirm) is str:
            temp_answer_project_dir_confirm = input_expect_bool(
                MSG_PROJECT_DIR_FOUND_CONFIRM, temp_project_name_to_path
            )
            if type(temp_answer_project_dir_confirm) is str:
                print_with_replace(MSG_UNACCEPTED_ANSWER, temp_answer_project_dir_confirm)
        if temp_answer_project_dir_confirm:
            explicit_project_path = False

    # project path
    if explicit_project_path:
        temp_answer_project_path: Path = Path(":?!%&")  # this should be invalid for most file systems
        while not temp_answer_project_path.exists() or not temp_answer_project_path.is_dir():
            temp_answer_project_path = Path(input_with_replace(MSG_ASK_FOR_PROJECT_DIRECTORY, args.project_name))
            if not temp_answer_project_path.exists() or not temp_answer_project_path.is_dir():
                print_with_replace(MSG_UNACCEPTED_ANSWER, temp_answer_project_path)
        args.project_path = temp_answer_project_path

    # comment converter?
    temp_answer_converter: bool | str = ""
    while type(temp_answer_converter) is str:
        temp_answer_converter = input_expect_bool(MSG_ASK_CONVERTER, temp_project_name_to_path)
        if type(temp_answer_converter) is str:
            print_with_replace(MSG_UNACCEPTED_ANSWER, temp_answer_converter)
    args.converter = "default" if temp_answer_converter else None

    # documentation generation?
    temp_answer_docgen: bool | str = ""
    while type(temp_answer_docgen) is str:
        temp_answer_docgen = input_expect_bool(MSG_ASK_DOCGEN)
        if type(temp_answer_docgen) is str:
            print_with_replace(MSG_UNACCEPTED_ANSWER, temp_answer_docgen)
    args.disable_doc_gen = temp_answer_docgen

    # test coverage evaluation?
    temp_answer_testcov: bool | str = ""
    while type(temp_answer_testcov) is str:
        temp_answer_testcov = input_expect_bool(MSG_ASK_TESTCOV, temp_project_name_to_path)
        if type(temp_answer_testcov) is str:
            print_with_replace(MSG_UNACCEPTED_ANSWER, temp_answer_testcov)
    args.disable_test_cov = temp_answer_testcov

    # TODO: implement the rest!
    # TODO: control flow diagram?


def print_with_replace(prompt: str, replacement: Any):
    """
    print(), but everything in the prompt that matches `MSG_PLACEHOLDER` will be replaced with `replacement`

    Parameters
    ----------
    prompt: str
        The prompt to display to the user
    replacement: Any
        The string (or string representation of Any) to replace the placeholder with

    Documentation for print():
    Prints the values to a stream, or to sys.stdout by default.
    sep string inserted between values, default a space.
    end string appended after the last value, default a newline.
    file a file-like object (stream); defaults to the current sys.stdout.
    flush whether to forcibly flush the stream.
    `print(*values, sep=" ", end="\n", file=None, flush=False)` on docs.python.org
    """
    print(prompt.replace(MSG_PLACEHOLDER, str(replacement)))


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
    answer: bool | str = input_with_replace(prompt, replacement)
    answer = ACCEPTED_INPUT_BOOL_LOOKUP[answer.upper()] if answer.upper() in ACCEPTED_INPUT_BOOL_LOOKUP.keys() else answer
    return answer
