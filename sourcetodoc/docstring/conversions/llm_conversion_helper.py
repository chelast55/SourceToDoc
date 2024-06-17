import re
from typing import Optional

from ..command_style import CommandStyle
from ..comment_style import CommentStyle, CommentStyler
from ..conversion import ConvEmpty, ConvError, ConvPresent, ConvResult
from ..extractor import Comment
from .llm import LLM


class LLMConversionHelper[T]:
    # Matches "// ..." over multiple lines
    _LINE_COMMENT_REGEX = r"(?://.*\n\s*)*//.*"
    _LINE_COMMENT_PATTERN = re.compile(_LINE_COMMENT_REGEX, re.VERBOSE)

    # Matches "/** ... */"
    _BLOCK_COMMENT_REGEX = r"/\*(?:.|\n)*?\*/"
    _BLOCK_COMMENT_PATTERN = re.compile(_BLOCK_COMMENT_REGEX, re.VERBOSE)

    def __init__(self, llm: LLM) -> None:
        self.llm = llm

    def calc_conversion_with_llm(
            self,
            comment: Comment[T],
            system_prompt: str,
            output_style: CommentStyle
            ) -> ConvResult:
        """
        Helper function to calculate conversion results.

        Parameters
        ----------
        comment : Comment[T]
            The comment that is passed to the LLM as the prompt.
        system_prompt : str
            The system prompt that is passed to the LLM.
        output_style : CommentStyle
            The comment style of the output.
        """
        # Format the comment text and append the symbol text
        match CommentStyler.parse_comment(comment.comment_text):
            case None:
                return ConvError("Comment can not be parsed")
            case CommentStyler(_, style) if style.is_doxygen_style():
                return ConvEmpty("Comment is already a doxygen style comment")
            # Format the comment text and append the symbol text
            case CommentStyler() as input_styler:
                comment_formatted = input_styler.construct_comment()

        prompt = comment_formatted + "\n" + comment.symbol_text

        # Call LLM
        llm_output = self.llm.call_llm(system_prompt, prompt)

        # Extract the comment part from the output
        new_comment = self._extract_comment(llm_output)
        if new_comment is None:
            return ConvError(f"No comment found in output of LLM: {llm_output}")

        # Mark the result as AI generated and format it
        output_styler = CommentStyler.parse_comment(new_comment)
        if output_styler is None:
            raise RuntimeError

        # Replaces @command with \command in the new comment
        with_default_command_style = CommandStyle.sub_to_default_style(output_styler.content)

        # Mark the new comment as AI generated
        content_marked = "AI_GENERATED\n" + with_default_command_style

        # Format the new comment
        formatted_comment = CommentStyler(content_marked, output_style
            ).construct_comment(comment.symbol_indentation)

        return ConvPresent(formatted_comment)


    @classmethod
    def _extract_comment(cls, result: str) -> Optional[str]:
        match = cls._LINE_COMMENT_PATTERN.search(result)
        if match is None:
            match = cls._BLOCK_COMMENT_PATTERN.search(result)

        if match is not None:
            return match[0]
        else:
            return None
