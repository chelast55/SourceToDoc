from typing import override

from ..converter import Conversion, Converter
from ..extractor import Comment


class CLlmConverter(Converter):
    @override
    def calc_docstring(self, comment: Comment) -> Conversion:
        ...
