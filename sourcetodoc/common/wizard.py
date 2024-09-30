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
MSG_ASK_LLM: str = ("Do you want to use an LLM for the conversion? (yes/no)\n"
                    "(this may generate many API call, so some publicly available models may not willingly handle "
                    "processing the whole source code)\n")
MSG_ASK_CC_OPENAI_BASE_URL: str = "Please provide the \"OpenAI base URL\" of the LLM host:\n(could also be localhost)\n"
MSG_ASK_CC_OPENAI_API_KEY: str = "Please provide the \"OpenAI API key\" for the LLM host:\n"
MSG_ASK_CC_LLM_MODEL: str = "Please provide the name of the LLM model you want to use:\n"
MSG_ASK_PROJECT_NUMBER: str = "Please provide the software version number of \"$\": (leave empty if unknown)\n"
MSG_ASK_PROJECT_BRIEF: str = "Please provide a short/one-line description of \"$\":\n"
MSG_ASK_DG_TIMESTAMP: str = "Do you want to add a timestamp of when documentation was generated? (yes/no)\n"
MSG_ASK_DG_DISABLE_EXTRACT_PRIVATE: str = "Do you want to include private members in the documentation? (yes/no)\n"
MSG_ASK_DG_DISABLE_EXTRACT_ANON_NAMESPACES: str = ("Do you want to include members of anonymous namespaces in the "
                                                   "documentation? (yes/no)\n")
MSG_ASK_DG_DISABLE_DOT_GRAPHS: str = ("Do you want to generate various interactive graphs (class collaboration, header "
                                      "include, function call, ...) from source code? (yes/no)\n"
                                      "(recommended for better architectural visualization, but will take more time)\n")
MSG_ASK_DG_HTML_THEME: str = ("Doxygen-generated documentation can look somewhat dated by todays standards. "
                              "Do you want to use \"doxygen-awesome\" "
                              "(a custom theme for a more modern look)? (yes/no)\n")
MSG_ASK_TC_TYPE: str = "Please provide the build system to create the testcoverage report with. Allowed answeres are: 'meson', 'cmake', 'generic'.\n"
MSG_ASK_BUILD_FOLDER_NAME: str = ("Please provide a name for the build folder (used to create the testcoverage report). This can be nested (e.g. 'sub/build'). " 
                                  "Existing folders with the given name will be deleted beforehand. (Press enter to create 'build')\n")
MSG_ASK_KEEP_BUILD_FOLDER: str = "Do you want to keep the build folder after the testcoverage was generated? (yes/no)\n"
MSG_ASK_MESON_BUILD_LOCATION: str = "Is your meson.build not located in the root of your project? Then please provide a path to it here (otherwise just press enter).\n"
MSG_ASK_MESON_SETUP_ARGS: str = "Please provide additional arguments to pass to the meson setup call, if any (otherwise just press enter).\n"
MSG_ASK_CMAKE_CONFIG_ARGS: str = "Please provide additional arguments to pass to the cmake configure call 'cmake', default is '..', if any (otherwise just press enter).\n"
MSG_ASK_CMAKE_BUILD_ARGS: str = "Please provide additional arguments to pass to the cmake build call 'cmake --build', default is '.', if any (otherwise just press enter).\n"
MSG_ASK_USE_CTEST_OR_SUB: str = "Does your project support/use ctest? (yes/no)\n"
MSG_ASK_CTEST_ARGS: str = "Please provide additional arguments to pass to the ctest call 'ctest', default is '-VV', if any (otherwise just press enter).\n"
MSG_ASK_CTEST_SUBSTITUTE: str = "Please provide the arguments to call instead of ctest.\n"
MSG_ASK_GENERIC_REPORT_LOCATION: str = "Please provide a path to the testcoverage containing folder.\n"

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

    if temp_answer_converter:  # LLM? + related parameters
        temp_answer_llm: bool | str = ""
        while type(temp_answer_llm) is str:
            temp_answer_llm = input_expect_bool(MSG_ASK_LLM)
            if type(temp_answer_llm) is str:
                print_with_replace(MSG_UNACCEPTED_ANSWER, temp_answer_llm)

        if temp_answer_llm:
            args.converter = "function_comment_llm"

            args.cc_openai_base_url = input(MSG_ASK_CC_OPENAI_BASE_URL)
            args.cc_openai_api_key = input(MSG_ASK_CC_OPENAI_API_KEY)
            args.cc_llm_model = input(MSG_ASK_CC_LLM_MODEL)


    # documentation generation?
    temp_answer_docgen: bool | str = ""
    while type(temp_answer_docgen) is str:
        temp_answer_docgen = input_expect_bool(MSG_ASK_DOCGEN)
        if type(temp_answer_docgen) is str:
            print_with_replace(MSG_UNACCEPTED_ANSWER, temp_answer_docgen)
    args.disable_doc_gen = temp_answer_docgen

    if temp_answer_docgen:
        temp_answer_project_number: str = input_with_replace(MSG_ASK_PROJECT_NUMBER, args.project_name)
        if not temp_answer_project_number == "":
            args.project_number = temp_answer_project_number
        temp_answer_project_brief: str = input_with_replace(MSG_ASK_PROJECT_BRIEF, args.project_name)
        if not temp_answer_project_brief == "":
            args.project_brief = temp_answer_project_brief

        temp_answer_timestamp: bool | str = ""
        while type(temp_answer_timestamp) is str:
            temp_answer_timestamp = input_expect_bool(MSG_ASK_DG_TIMESTAMP)
            if type(temp_answer_timestamp) is str:
                print_with_replace(MSG_UNACCEPTED_ANSWER, temp_answer_timestamp)
        args.dg_timestamp = "DATETIME" if temp_answer_timestamp else "NO"

        temp_answer_extract_private: bool | str = ""
        while type(temp_answer_extract_private) is str:
            temp_answer_extract_private = input_expect_bool(MSG_ASK_DG_DISABLE_EXTRACT_PRIVATE)
            if type(temp_answer_extract_private) is str:
                print_with_replace(MSG_UNACCEPTED_ANSWER, temp_answer_extract_private)
        args.dg_disable_extract_private = temp_answer_extract_private

        temp_answer_extract_anon_namespaces: bool | str = ""
        while type(temp_answer_extract_anon_namespaces) is str:
            temp_answer_extract_anon_namespaces = input_expect_bool(MSG_ASK_DG_DISABLE_EXTRACT_ANON_NAMESPACES)
            if type(temp_answer_extract_anon_namespaces) is str:
                print_with_replace(MSG_UNACCEPTED_ANSWER, temp_answer_extract_anon_namespaces)
        args.dg_disable_extract_anon_namespaces = temp_answer_extract_anon_namespaces

        temp_answer_dot_graphs: bool | str = ""
        while type(temp_answer_dot_graphs) is str:
            temp_answer_dot_graphs = input_expect_bool(MSG_ASK_DG_DISABLE_DOT_GRAPHS)
            if type(temp_answer_dot_graphs) is str:
                print_with_replace(MSG_UNACCEPTED_ANSWER, temp_answer_dot_graphs)
        args.dg_disable_dot_graphs = temp_answer_dot_graphs

        temp_answer_html_theme: bool | str = ""
        while type(temp_answer_html_theme) is str:
            temp_answer_html_theme = input_expect_bool(MSG_ASK_DG_HTML_THEME)
            if type(temp_answer_html_theme) is str:
                print_with_replace(MSG_UNACCEPTED_ANSWER, temp_answer_html_theme)
        args.dg_html_theme = "doxygen-awesome" if temp_answer_html_theme else "standard"

    # test coverage evaluation?
    temp_answer_testcov: bool | str = ""
    while type(temp_answer_testcov) is str:
        temp_answer_testcov = input_expect_bool(MSG_ASK_TESTCOV, temp_project_name_to_path)
        if type(temp_answer_testcov) is str:
            print_with_replace(MSG_UNACCEPTED_ANSWER, temp_answer_testcov)
    args.disable_test_cov = temp_answer_testcov

    if temp_answer_testcov:
        temp_answer_testcov_type: str = ""
        while temp_answer_testcov_type not in ["meson", "cmake", "generic"]:
            temp_answer_testcov_type = input(MSG_ASK_TC_TYPE)
            if temp_answer_testcov_type not in ["meson", "cmake", "generic"]:
                print_with_replace(MSG_UNACCEPTED_ANSWER, temp_answer_testcov_type)
        args.tc_coverage_type = temp_answer_testcov_type

        args.tc_build_folder_name = input(MSG_ASK_BUILD_FOLDER_NAME)
        if args.tc_build_folder_name == "": args.tc_build_folder_name = "build"
        
        temp_answer_keep_build_folder: bool | str = ""
        while type(temp_answer_keep_build_folder) is str:
            temp_answer_keep_build_folder = input_expect_bool(MSG_ASK_KEEP_BUILD_FOLDER)
            if type(temp_answer_keep_build_folder) is str:
                print_with_replace(MSG_UNACCEPTED_ANSWER, temp_answer_keep_build_folder)
        args.tc_keep_build_folder = temp_answer_keep_build_folder

        if args.tc_coverage_type == "meson":
            args.tc_meson_build_location = input(MSG_ASK_MESON_BUILD_LOCATION)
            if args.tc_meson_build_location == "": args.tc_meson_build_location = None

            args.tc_meson_setup_args = input(MSG_ASK_MESON_SETUP_ARGS)

        elif args.tc_coverage_type == "cmake":
            args.tc_cmake_configure_args = input(MSG_ASK_CMAKE_CONFIG_ARGS)
            if args.tc_cmake_configure_args == "": args.tc_cmake_configure_args = ".."

            args.tc_cmake_build_args = input(MSG_ASK_CMAKE_BUILD_ARGS)
            if args.tc_cmake_build_args == "": args.tc_cmake_build_args = "."

            temp_answer_use_ctest: bool | str = ""
            while type(temp_answer_use_ctest) is str:
                temp_answer_use_ctest = input_expect_bool(MSG_ASK_USE_CTEST_OR_SUB)
                if type(temp_answer_use_ctest) is str:
                    print_with_replace(MSG_UNACCEPTED_ANSWER, temp_answer_use_ctest)
            if temp_answer_use_ctest:
                args.tc_ctest_args = input(MSG_ASK_CTEST_ARGS)
            else:
                args.tc_ctest_substitute = input(MSG_ASK_CTEST_SUBSTITUTE)

        elif args.tc_coverage_type == "generic":
            temp_answer_generic_report_location: Path = Path(":?!%&")  # this should be invalid for most file systems
            while not temp_answer_generic_report_location.exists() or not temp_answer_generic_report_location.is_dir():
                temp_answer_generic_report_location = Path(input(MSG_ASK_GENERIC_REPORT_LOCATION))
                if not temp_answer_generic_report_location.exists() or not temp_answer_generic_report_location.is_dir():
                    print_with_replace(MSG_UNACCEPTED_ANSWER, temp_answer_generic_report_location)
            args.tc_generic_report_location = str(temp_answer_generic_report_location)

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
