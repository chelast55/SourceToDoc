from enum import StrEnum
from typing import Any, Iterable, Mapping, Optional

from openai import OpenAI

from .comment_style import CommentStyle
from .conversions.llm import LLM
from .converter import Converter
from .converters import (c_comment_style_converter,
                         c_function_comment_llm_converter,
                         cxx_comment_style_converter,
                         cxx_function_comment_llm_converter)

style_map: Mapping[str, CommentStyle] = {
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


class ConverterNames(StrEnum):
    C_COMMENT_STYLE = "c_comment_style"
    CXX_COMMENT_STYLE = "cxx_comment_style"
    C_FUNCTION_COMMENT_LLM = "c_function_comment_llm"
    CXX_FUNCTION_COMMENT_LLM = "cxx_function_comment_llm"


def get_converter_by_args(**kwargs: str) -> Optional[Converter[Any]]:
    converter: Optional[Converter[Any]] = None
    arg_helper = ArgumentHelper(**kwargs)
    match kwargs["converter"]:
        case ConverterNames.C_COMMENT_STYLE:
            style = arg_helper.get_style()
            if style is not None:
                converter = c_comment_style_converter(style)
        case ConverterNames.CXX_COMMENT_STYLE:
            style = arg_helper.get_style()
            if style is not None:
                converter = cxx_comment_style_converter(style)
        case ConverterNames.C_FUNCTION_COMMENT_LLM:
            llm = arg_helper.get_llm()
            if llm is not None:
                converter = c_function_comment_llm_converter(llm)
        case ConverterNames.CXX_FUNCTION_COMMENT_LLM:
            llm = arg_helper.get_llm()
            if llm is not None:
                converter = cxx_function_comment_llm_converter(llm)
        case _:
            print("Choices for --converter:")
            for e in ConverterNames:
                print(e)
    
    if arg_helper.has_missing_args():
        arg_helper.print_missing_args_message()

    return converter


class ArgumentHelper:
    def __init__(self, **kwargs: Optional[str]) -> None:
        self.args = kwargs
        self.messages: list[str] = []
    
    def get_style(self) -> Optional[CommentStyle]:
        self._check_args_present("style")

        value = self.args["style"]
        if value is None:
            self._add_arg_missing_message(f"style")

        if value not in style_map:
            choices = self.__class__._repr_per_line(style_map)
            self._add_message(f"Choices for --style:\n{choices}")

        if not self.has_missing_args():
            return style_map[value] # type: ignore

    def get_llm(self) -> Optional[LLM]:
        self._check_args_present("openai_base_url", "openai_api_key", "llm_model")

        base_url = self.args["openai_base_url"]
        api_key = self.args["openai_api_key"]
        model = self.args["llm_model"]

        if base_url is None:
            self._add_arg_missing_message("openai_base_url")
        if api_key is None:
            self._add_arg_missing_message("openai_api_key")
        if model is None:
            self._add_arg_missing_message("llm_model")

        if not self.has_missing_args():
            client = OpenAI(base_url=base_url, api_key=api_key)
            return LLM(client, model) # type: ignore
    
    def has_missing_args(self) -> bool:
        return len(self.messages) > 0
    
    def print_missing_args_message(self) -> None:
        if not self.has_missing_args():
            raise ValueError
        print("\n".join(self.messages))

    def _check_args_present(self, *args: str) -> None:
        for arg in args:
            if arg not in self.args:
                raise RuntimeError
    
    def _add_arg_missing_message(self, missing: str) -> None:
        self._add_message(f"--{missing} is not specified")

    def _add_message(self, message: str) -> None:
        self.messages.append(message)

    @classmethod
    def _repr_per_line(cls, iterable: Iterable[Any]) -> str:
        return "\n".join((str(e) for e in iterable))
