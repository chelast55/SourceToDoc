from openai import OpenAI

from ..simpleparser import SimpleParser
from .c_converter import CConverter
from .c_extractor import CExtractor, CType


class CParser(SimpleParser[CType]):
    def __init__(self, client: OpenAI) -> None:
        super().__init__(CExtractor(), CConverter(client))
