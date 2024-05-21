from typing import Mapping

from openai import OpenAI

from .impl.c_conversion import CConversion
from .impl.c_extractor import CExtractor
from .converter import Converter
from .printconverter import PrintConverter


def get_print_converters(client: OpenAI) -> Mapping[str, Converter]:
    return {
        "c_function_blockcomment_llm": PrintConverter(CExtractor(), CConversion(client))
    }

def get_default_file_extensions() -> Mapping[str, set[str]]:
    return {
        "c_function_blockcomment_llm": {".c", ".h"}
    }