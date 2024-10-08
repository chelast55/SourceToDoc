import re
from argparse import ArgumentParser
from enum import StrEnum
from typing import Any, Iterable, Mapping

from openai import OpenAI

from ..common.Config import Config
from .comment_style import CommentStyle
from .conversion import Conversion
from .conversions.command_style_conversion import CommandStyleConversion
from .conversions.comment_style_conversion import CommentStyleConversion
from .conversions.default_comment_conversion import DefaultCommentStyleConversion
from .conversions.find_and_replace_conversion import FindAndReplaceConversion
from .conversions.llm import LLM
from .conversions.llm_conversion import LLMConversion
from .converter import Converter
from .replace import Replace


_style_map: Mapping[str, CommentStyle] = {
    "c_line": CommentStyle.C_LINE,
    "c_block_inline": CommentStyle.C_BLOCK_INLINE,
    "c_block": CommentStyle.C_BLOCK,
    "javadoc_block": CommentStyle.JAVADOC_BLOCK,
    "javadoc_block_inline": CommentStyle.JAVADOC_BLOCK_INLINE,
    "javadoc_block_member_inline": CommentStyle.JAVADOC_BLOCK_MEMBER_INLINE,
    "qt_block": CommentStyle.QT_BLOCK,
    "qt_block_inline": CommentStyle.QT_BLOCK_INLINE,
    "qt_block_member_inline": CommentStyle.QT_BLOCK_MEMBER_INLINE,
    "triple_slash_line": CommentStyle.TRIPLE_SLASH_LINE,
    "triple_slash_line_member": CommentStyle.TRIPLE_SLASH_LINE_MEMBER,
    "qt_line": CommentStyle.QT_LINE,
    "qt_line_member": CommentStyle.QT_LINE_MEMBER,
}


class _ConverterNames(StrEnum):
    DEFAULT = "default"
    COMMENT_STYLE = "comment_style"
    FUNCTION_COMMENT_LLM = "function_comment_llm"
    COMMAND_STYLE = "command_style"
    FIND_AND_REPLACE = "find_and_replace"


def run_comment_converter(parser: ArgumentParser, config: Config) -> None:
    """Runs the converter depending on the given arguments in `kwargs`."""
    kwargs = vars(config.args)

    c_regex: str | None = kwargs["cc_c_regex"]
    try:
        c_pattern = re.compile(c_regex) if c_regex is not None else None
    except re.error:
        parser.error(f"Error: Python RegEx {c_regex} cannot be compiled")

    cxx_regex: str | None = kwargs["cc_cxx_regex"]
    try:
        cxx_pattern = re.compile(cxx_regex) if cxx_regex is not None else None
    except re.error:
        parser.error(f"Error: Python RegEx {cxx_regex} cannot be compiled")

    selected_conversion = _get_conversion(parser, **kwargs)
    if selected_conversion is None:
        raise RuntimeError
    
    match kwargs["cc_replace"]:
        case "replace":
            replace = Replace.REPLACE_OLD_COMMENTS
        case "append":
            replace = Replace.APPEND_TO_OLD_COMMENTS
        case "inline":
            replace = Replace.APPEND_TO_OLD_COMMENTS_INLINE
        case _:
            message = (f"Choices for --converter:\n{"\n".join(e for e in _ConverterNames)}\n\n"
                       f"Got \"{kwargs["converter"]}\" instead")
            parser.error(message)

    converter = Converter(
        selected_conversion,
        replace,
        c_pattern,
        cxx_pattern
    )

    src_path = config.project_path
    if src_path.is_file():
        converter.convert_file(src_path)
    elif src_path.is_dir():
        converter.convert_files(src_path)
    else:
        parser.error(f"{src_path} is not a file or a directory")


def _get_conversion(parser: ArgumentParser, **kwargs: str | None) -> Conversion[Any] | None:
    conversion: Conversion[Any] | None = None
    arg_helper = _ArgumentHelper(**kwargs)
    match kwargs["converter"]:
        case _ConverterNames.DEFAULT:
            conversion = DefaultCommentStyleConversion()
        case _ConverterNames.COMMENT_STYLE:
            result = arg_helper.get_style_and_only_after_member()
            if result is not None:
                style, only_after_member = result
                conversion = CommentStyleConversion(style, only_after_member)
        case _ConverterNames.FUNCTION_COMMENT_LLM:
            llm = arg_helper.get_llm()
            prompts = arg_helper.get_llm_prompts()
            if llm is not None and prompts is not None:
                conversion = LLMConversion(llm, prompts[0], prompts[1], prompts[2], prompts[3])
        case _ConverterNames.COMMAND_STYLE:
            javadoc_style = arg_helper.get_command_style()
            if javadoc_style is not None:
                conversion = CommandStyleConversion(javadoc_style)
        case _ConverterNames.FIND_AND_REPLACE:
            pattern_and_replacement = arg_helper.get_find_and_replace()
            if pattern_and_replacement is not None:
                pattern, replacement = pattern_and_replacement
                conversion = FindAndReplaceConversion(pattern, replacement)
        case _:
            message = (f"Choices for --converter:\n{"\n".join(e for e in _ConverterNames)}\n\n"
                       f"Got \"{kwargs["converter"]}\" instead")
            parser.error(message)

    if arg_helper.has_error_message():
        message = arg_helper.get_error_messages()
        parser.error(message)
    return conversion


class _ArgumentHelper:
    """Parses arguments and produces error messages when doing it."""
    def __init__(self, **kwargs: str | None) -> None:
        self.kwargs = kwargs
        self.error_messages: list[str] = []
    
    def get_style_and_only_after_member(self) -> tuple[CommentStyle, bool] | None:
        self._check_args_present("cc_style", "cc_only_after_member")

        style = self.kwargs["cc_style"]
        if style is None:
            self._add_arg_missing_error_message(f"cc_style")

        if style not in _style_map:
            choices = self.__class__._repr_per_line(_style_map)
            self._add_error_message(f"Choices for --cc_style:\n{choices}")
        
        only_after_member = self.kwargs["cc_only_after_member"]

        if not self.has_error_message():
            return _style_map[style], only_after_member # type: ignore

    def get_llm(self) -> LLM | None:
        self._check_args_present("cc_openai_base_url", "cc_openai_api_key", "cc_llm_model")

        base_url = self.kwargs["cc_openai_base_url"]
        api_key = self.kwargs["cc_openai_api_key"]
        model = self.kwargs["cc_llm_model"]

        if base_url is None:
            self._add_arg_missing_error_message("cc_openai_base_url")
        if api_key is None:
            self._add_arg_missing_error_message("cc_openai_api_key")
        if model is None:
            self._add_arg_missing_error_message("cc_llm_model")

        if not self.has_error_message():
            client = OpenAI(base_url=base_url, api_key=api_key)
            return LLM(client, model) # type: ignore
    
    def get_llm_prompts(self) -> tuple[str,str,str,str] | None:
        c_system_prompt = self.kwargs["cc_c_system_prompt"]
        c_user_prompt_template = self.kwargs["cc_c_user_prompt_template"]
        cxx_system_prompt = self.kwargs["cc_cxx_system_prompt"]
        cxx_user_prompt_template = self.kwargs["cc_cxx_user_prompt_template"]

        if c_system_prompt is None:
            self._add_arg_missing_error_message("cc_c_system_prompt")
        if c_user_prompt_template is None:
            self._add_arg_missing_error_message("cc_c_user_prompt_template")
        if cxx_system_prompt is None:
            self._add_arg_missing_error_message("cc_cxx_system_prompt")
        if cxx_user_prompt_template is None:
            self._add_arg_missing_error_message("cc_cxx_user_prompt_template")

        if c_user_prompt_template is not None:
            try:
                c_user_prompt_template.format("test")
            except Exception:
                self._add_error_message(f"cc_c_user_prompt_template = \"{c_user_prompt_template}\" must have exactly one {{}}")
        if cxx_user_prompt_template is not None:
            try:
                cxx_user_prompt_template.format("test")
            except Exception:
                self._add_error_message(f"cc_cxx_user_prompt_template = \"{cxx_user_prompt_template}\" must have exactly one {{}}")

        if not self.has_error_message():
            return (c_system_prompt, c_user_prompt_template, cxx_system_prompt, cxx_user_prompt_template) # type: ignore

    def get_command_style(self) -> bool | None:
        self._check_args_present("cc_command_style")

        command_style = self.kwargs["cc_command_style"]
        match command_style:
            case "default":
                return False
            case "javadoc":
                return True
            case _:
                self._add_error_message("Value for --cc_command_style must be \"default\" or \"javadoc\"")
                return None
    
    def get_find_and_replace(self) -> tuple[re.Pattern[str], str] | None:
        self._check_args_present("cc_find", "cc_substitution")

        find = self.kwargs["cc_find"]
        pattern = None
        if find is None:
            self._add_arg_missing_error_message("cc_find")
        else:
            try:
                pattern = re.compile(find)
            except Exception:
                self._add_error_message(f"Error: Python RegEx {find} cannot be compiled")
        
        replacement = self.kwargs["cc_substitution"]
        if replacement is None:
            self._add_arg_missing_error_message("cc_substitution")

        if pattern is not None and replacement is not None:
            return (pattern, replacement)

    def has_error_message(self) -> bool:
        return len(self.error_messages) > 0
    
    def get_error_messages(self) -> str:
        if not self.has_error_message():
            raise ValueError
        return "\n".join(self.error_messages)

    def _check_args_present(self, *args: str) -> None:
        for arg in args:
            if arg not in self.kwargs:
                raise RuntimeError
    
    def _add_arg_missing_error_message(self, missing: str) -> None:
        self._add_error_message(f"--{missing} is required")

    def _add_error_message(self, message: str) -> None:
        self.error_messages.append(message)

    @classmethod
    def _repr_per_line(cls, iterable: Iterable[Any]) -> str:
        return "\n".join((str(e) for e in iterable))
