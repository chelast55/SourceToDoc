import re
from argparse import ArgumentParser
from enum import StrEnum
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional

from openai import OpenAI

from .comment_style import CommentStyle
from .conversions.llm import LLM
from .converter import Converter
from .converters import (c_command_style_converter, c_comment_style_converter,
                         c_find_and_replace_converter,
                         c_function_comment_llm_converter,
                         cxx_command_style_converter,
                         cxx_comment_style_converter,
                         cxx_find_and_replace_converter,
                         cxx_function_comment_llm_converter)
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
    C_COMMENT_STYLE = "c_comment_style"
    CXX_COMMENT_STYLE = "cxx_comment_style"
    C_FUNCTION_COMMENT_LLM = "c_function_comment_llm"
    CXX_FUNCTION_COMMENT_LLM = "cxx_function_comment_llm"
    C_COMMAND_STYLE = "c_command_style"
    CXX_COMMAND_STYLE = "cxx_command_style"
    C_FIND_AND_REPLACE = "c_find_and_replace"
    CXX_FIND_AND_REPLACE = "cxx_find_and_replace"


def comment(parser: ArgumentParser, **kwargs: str) -> None:
    """Runs a converter depending on the given arguments in `kwargs`."""
    if kwargs["converter"] == "default":
        c_converter = c_comment_style_converter(CommentStyle.JAVADOC_BLOCK, False)
        cxx_converter = cxx_comment_style_converter(CommentStyle.JAVADOC_BLOCK, False)
        _run_converter(parser, c_converter, **kwargs)
        _run_converter(parser, cxx_converter, **kwargs)
    else:
        converter = _get_converter(parser, **kwargs)
        if converter is None:
            raise RuntimeError
        _run_converter(parser, converter, **kwargs)


def _run_converter(parser: ArgumentParser, converter: Converter[Any], **kwargs: str):
    match kwargs["replace"]:
        case "replace":
            replace = Replace.REPLACE_OLD_COMMENTS
        case "append":
            replace = Replace.APPEND_TO_OLD_COMMENTS
        case "inline":
            replace = Replace.APPEND_TO_OLD_COMMENTS_INLINE
        case _:
            raise RuntimeError

    path = Path(kwargs["project_path"])
    if path.is_file():
        converter.convert_file(path, replace)
    elif path.is_dir():
        converter.convert_files(path, replace, kwargs["src_filter"])
    else:
        parser.error(f"{path} is not a file or a directory")


def _get_converter(parser: ArgumentParser, **kwargs: str) -> Converter[Any] | None:
    converter: Optional[Converter[Any]] = None
    arg_helper = _ArgumentHelper(**kwargs)
    match kwargs["converter"]:
        case "default":
            style = CommentStyle.JAVADOC_BLOCK
            converter = cxx_comment_style_converter(style, False)
        case _ConverterNames.C_COMMENT_STYLE:
            result = arg_helper.get_style_and_only_after_member()
            if result is not None:
                style, only_after_member = result
                converter = c_comment_style_converter(style, only_after_member)
        case _ConverterNames.CXX_COMMENT_STYLE:
            result = arg_helper.get_style_and_only_after_member()
            if result is not None:
                style, only_after_member = result
                converter = cxx_comment_style_converter(style, only_after_member)
        case _ConverterNames.C_FUNCTION_COMMENT_LLM:
            llm = arg_helper.get_llm()
            if llm is not None:
                converter = c_function_comment_llm_converter(llm)
        case _ConverterNames.CXX_FUNCTION_COMMENT_LLM:
            llm = arg_helper.get_llm()
            if llm is not None:
                converter = cxx_function_comment_llm_converter(llm)
        case _ConverterNames.C_COMMAND_STYLE:
            javadoc_style = arg_helper.get_command_style()
            if javadoc_style is not None:
                converter = c_command_style_converter(javadoc_style)
        case _ConverterNames.CXX_COMMAND_STYLE:
            javadoc_style = arg_helper.get_command_style()
            if javadoc_style is not None:
                converter = cxx_command_style_converter(javadoc_style)
        case _ConverterNames.C_FIND_AND_REPLACE:
            pattern_and_replacement = arg_helper.get_find_and_replace()
            if pattern_and_replacement is not None:
                pattern, replacement = pattern_and_replacement
                converter = c_find_and_replace_converter(pattern, replacement)
        case _ConverterNames.CXX_FIND_AND_REPLACE:
            pattern_and_replacement = arg_helper.get_find_and_replace()
            if pattern_and_replacement is not None:
                pattern, replacement = pattern_and_replacement
                converter = cxx_find_and_replace_converter(pattern, replacement)
        case _:
            message = "Choices for --converter:\n" + "\n".join(e for e in _ConverterNames)
            parser.error(message)
    
    if arg_helper.has_missing_args():
        message = arg_helper.get_missing_args_message()
        parser.error(message)
    return converter


class _ArgumentHelper:
    def __init__(self, **kwargs: str | None) -> None:
        self.kwargs = kwargs
        self.messages: list[str] = []
    
    def get_style_and_only_after_member(self) -> Optional[tuple[CommentStyle, bool]]:
        self._check_args_present("style", "only_after_member")

        style = self.kwargs["style"]
        if style is None:
            self._add_arg_missing_message(f"style")

        if style not in _style_map:
            choices = self.__class__._repr_per_line(_style_map)
            self._add_message(f"Choices for --style:\n{choices}")
        
        only_after_member = self.kwargs["only_after_member"]

        if not self.has_missing_args():
            return _style_map[style], only_after_member # type: ignore

    def get_llm(self) -> Optional[LLM]:
        self._check_args_present("openai_base_url", "openai_api_key", "llm_model")

        base_url = self.kwargs["openai_base_url"]
        api_key = self.kwargs["openai_api_key"]
        model = self.kwargs["llm_model"]

        if base_url is None:
            self._add_arg_missing_message("openai_base_url")
        if api_key is None:
            self._add_arg_missing_message("openai_api_key")
        if model is None:
            self._add_arg_missing_message("llm_model")

        if not self.has_missing_args():
            client = OpenAI(base_url=base_url, api_key=api_key)
            return LLM(client, model) # type: ignore
    
    def get_command_style(self) -> Optional[bool]:
        self._check_args_present("command_style")

        command_style = self.kwargs["command_style"]
        match command_style:
            case "default":
                return False
            case "javadoc":
                return True
            case _:
                self._add_message("Value for --command_style must be \"default\" or \"javadoc\"")
                return None
    
    def get_find_and_replace(self) -> Optional[tuple[re.Pattern[str], str]]:
        self._check_args_present("find", "replacement")

        find = self.kwargs["find"]
        pattern = None
        if find is None:
            self._add_arg_missing_message("find")
        else:
            try:
                pattern = re.compile(find)
            except Exception:
                self._add_message(f"Error occured when compiling {find}")
        
        replacement = self.kwargs["replacement"]
        if replacement is None:
            self._add_arg_missing_message("replacement")

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
        self._add_message(f"--{missing} is not specified")

    def _add_message(self, message: str) -> None:
        self.messages.append(message)

    @classmethod
    def _repr_per_line(cls, iterable: Iterable[Any]) -> str:
        return "\n".join((str(e) for e in iterable))
