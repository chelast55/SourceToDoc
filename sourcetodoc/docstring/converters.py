from typing import Any, Mapping

from .impl.c_conversion import CLLMFunctionBlockCommentConversion
from .impl.c_extractor import CExtractor
from .impl.format_conversion import CCommentToDocstringConversion
from .impl.llm import LLM
from .printconverter import PrintConverter


def get_print_converters(llm: LLM) -> Mapping[str, PrintConverter[Any]]:
    return {
        "c_function_block_comment_llm": PrintConverter(CExtractor(), CLLMFunctionBlockCommentConversion(llm), r".*\.[ch]"),
        "c_comment_to_docstring": PrintConverter(CExtractor(), CCommentToDocstringConversion(), r".*\.[ch]")
    }
