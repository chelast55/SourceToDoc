import re
from argparse import ArgumentParser
from enum import StrEnum
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional

from openai import OpenAI

from .comment_style import CommentStyle
from .conversion import Conversion
from .conversions.command_style_conversion import CommandStyleConversion
from .conversions.comment_style_conversion import CommentStyleConversion
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


def run_comment_converter(parser: ArgumentParser, src_path: Path, **kwargs: str) -> None:
    """Runs the converter depending on the given arguments in `kwargs`."""

    c_regex = kwargs["cc_c_regex"] if "cc_c_regex" in kwargs else r".*\.[ch]"
    cxx_regex = kwargs["cc_cxx_regex"] if "cc_cxx_regex" in kwargs else r".*\.(c(pp|xx|c)|h(pp|xx|h)?)"
    try:
        c_pattern = re.compile(c_regex)
    except Exception:
        parser.error(f"Error: Python RegEx {c_regex} cannot be compiled")
    try:
        cxx_pattern = re.compile(cxx_regex)
    except Exception:
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
            raise RuntimeError

    converter = Converter(
        c_pattern,
        cxx_pattern,
        selected_conversion,
        replace
    )
    if src_path.is_file():
        converter.convert_file(src_path)
    elif src_path.is_dir():
        converter.convert_files(src_path)
    else:
        parser.error(f"{src_path} is not a file or a directory")


def _get_conversion(parser: ArgumentParser, **kwargs: str) -> Conversion[Any] | None:
    conversion: Optional[Conversion[Any]] = None
    arg_helper = _ArgumentHelper(**kwargs)
    match kwargs["converter"]:
        case _ConverterNames.DEFAULT:
            style = CommentStyle.JAVADOC_BLOCK
            conversion = CommentStyleConversion(style)
        case _ConverterNames.COMMENT_STYLE:
            result = arg_helper.get_style_and_only_after_member()
            if result is not None:
                style, only_after_member = result
                conversion = CommentStyleConversion(style, only_after_member)
        case _ConverterNames.FUNCTION_COMMENT_LLM:
            llm = arg_helper.get_llm()
            if llm is not None:
                conversion = LLMConversion(llm)
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
            message = "Choices for --converter:\n" + "\n".join(e for e in _ConverterNames)
            parser.error(message)

    if arg_helper.has_missing_args():
        message = arg_helper.get_missing_args_message()
        parser.error(message)
    return conversion


class _ArgumentHelper:
    def __init__(self, **kwargs: str | None) -> None:
        self.kwargs = kwargs
        self.messages: list[str] = []
    
    def get_style_and_only_after_member(self) -> Optional[tuple[CommentStyle, bool]]:
        self._check_args_present("cc_style", "cc_only_after_member")

        style = self.kwargs["cc_style"]
        if style is None:
            self._add_arg_missing_message(f"cc_style")

        if style not in _style_map:
            choices = self.__class__._repr_per_line(_style_map)
            self._add_message(f"Choices for --cc_style:\n{choices}")
        
        only_after_member = self.kwargs["cc_only_after_member"]

        if not self.has_missing_args():
            return _style_map[style], only_after_member # type: ignore

    def get_llm(self) -> Optional[LLM]:
        self._check_args_present("cc_openai_base_url", "cc_openai_api_key", "cc_llm_model")

        base_url = self.kwargs["cc_openai_base_url"]
        api_key = self.kwargs["cc_openai_api_key"]
        model = self.kwargs["cc_llm_model"]

        if base_url is None:
            self._add_arg_missing_message("cc_openai_base_url")
        if api_key is None:
            self._add_arg_missing_message("cc_openai_api_key")
        if model is None:
            self._add_arg_missing_message("cc_llm_model")

        if not self.has_missing_args():
            client = OpenAI(base_url=base_url, api_key=api_key)
            return LLM(client, model) # type: ignore
    
    def get_command_style(self) -> Optional[bool]:
        self._check_args_present("cc_command_style")

        command_style = self.kwargs["cc_command_style"]
        match command_style:
            case "default":
                return False
            case "javadoc":
                return True
            case _:
                self._add_message("Value for --cc_command_style must be \"default\" or \"javadoc\"")
                return None
    
    def get_find_and_replace(self) -> Optional[tuple[re.Pattern[str], str]]:
        self._check_args_present("cc_find", "cc_substitution")

        find = self.kwargs["cc_find"]
        pattern = None
        if find is None:
            self._add_arg_missing_message("cc_find")
        else:
            try:
                pattern = re.compile(find)
            except Exception:
                self._add_message(f"Error: Python RegEx {find} cannot be compiled")
        
        replacement = self.kwargs["cc_substitution"]
        if replacement is None:
            self._add_arg_missing_message("cc_substitution")

        if pattern is not None and replacement is not None:
            return (pattern, replacement)

    def has_missing_args(self) -> bool:
        return len(self.messages) > 0
    
    def get_missing_args_message(self) -> str:
        if not self.has_missing_args():
            raise ValueError
        return "\n".join(self.messages)

    def _check_args_present(self, *args: str) -> None:
        for arg in args:
            if arg not in self.kwargs:
                raise RuntimeError
    
    def _add_arg_missing_message(self, missing: str) -> None:
        self._add_message(f"--{missing} is mandatory")

    def _add_message(self, message: str) -> None:
        self.messages.append(message)

    @classmethod
    def _repr_per_line(cls, iterable: Iterable[Any]) -> str:
        return "\n".join((str(e) for e in iterable))
