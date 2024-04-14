from typing import override

from sourcetodoc.docstring.common import Comment
from sourcetodoc.docstring.filter import Filter


class CFilter(Filter):
    @override
    def is_valid(self, comment: Comment) -> bool:
        return not comment.text.startswith("/**") # TODO: Doxygen supports other formats
