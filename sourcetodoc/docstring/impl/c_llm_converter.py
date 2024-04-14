from typing import override
from sourcetodoc.docstring.common import Comment
from sourcetodoc.docstring.converter import Converter


class CLlmConverter(Converter):
    @override
    def calc_docstring(self, comment: Comment) -> str:
        ...
