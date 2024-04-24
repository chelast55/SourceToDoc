from typing import override
from sourcetodoc.docstring.extractor import Comment
from sourcetodoc.docstring.converter import Conversion, Converter


class CLlmConverter(Converter):
    @override
    def calc_docstring(self, comment: Comment) -> Conversion:
        ...
