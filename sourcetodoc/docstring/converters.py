from typing import Any, Mapping

from openai import OpenAI

from .impl.format_conversion import CCommentToDocstringConversion

from .impl.c_conversion import CLlmFunctionBlockCommentConversion
from .impl.c_extractor import CExtractor
from .printconverter import PrintConverter


def get_print_converters(client: OpenAI) -> Mapping[str, PrintConverter[Any]]:
    return {
        "c_function_block_comment_llm": PrintConverter(CExtractor(), CLlmFunctionBlockCommentConversion(client), r".*\.[ch]"),
        "c_comment_to_docstring": PrintConverter(CExtractor(), CCommentToDocstringConversion(), r".*\.[ch]")
    }
