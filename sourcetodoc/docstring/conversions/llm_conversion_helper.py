
from ..command_style import CommandStyle
from ..comment_parsing import find_comments_connected
from ..comment_style import CommentStyle
from ..comment_styler import CommentStyler
from ..conversion import (ConvEmpty, ConvError, ConvPresent, ConvResult,
                          ConvUnsupported)
from ..extractor import Comment
from ..extractors.c_type import CType
from ..extractors.cxx_type import CXXType
from .llm import LLM


class LLMConversionHelper:
    """Helper to calculates new comments with a LLM."""

    def __init__(self, llm: LLM) -> None:
        """
        Creates a new object.

        Parameters
        ----------
        llm : LLM
            The LLM to use.
        """
        self.llm = llm

    def calc_conversion_with_llm(
            self,
            comment: Comment[CType | CXXType],
            system_prompt: str,
            output_style: CommentStyle,
            user_prompt_template: str = "{}"
        ) -> ConvResult:
        """
        Calculates new comment texts results with a LLM.

        Steps:
        1. `comment_text` in `comment` will be parsed and formatted by `CommandStyler`.
        2. Insert the formatted comment in {} of `prompt`.
        3. Pass `system_prompt` with `prompt` to the LLM.
        4. Extract the first found `/*...*/` part in the output of the LLM.
        5. Replace `@command with` `\\command` in the new comment.
        6. Prepend `AI_GENERATED` to the new comment.
        7. Format the new comment.

        Parameters
        ----------
        comment: Comment[T]
            The comment that is passed to the LLM as the prompt.
        system_prompt: str
            The system prompt that is passed to the LLM.
        output_style: CommentStyle
            The comment style of the output.
        prompt: str
            The prompt that is passed to the LLM.

        Returns
        -------
        ConversionResult[T]
            A ConvPresent object if all steps above execute successfully.
            A ConvEmpty object if `comment` is already a Doxygen style comment.
            A ConvUnsupported object if `comment` cannot be parsed in Step 1,
            or if no `/*...*/` is found the output of the LLM.
        """
        # Format the comment text and append the symbol text
        match CommentStyler.parse_comment(comment.comment_text):
            case None:
                return ConvUnsupported("Comment cannot be parsed")
            case CommentStyler(_, style) if style.is_doxygen_style():
                return ConvEmpty("Comment is already a doxygen style comment")
            # Format the comment text and append the symbol text
            case CommentStyler() as input_styler:
                comment_formatted = input_styler.construct_comment()

        prompt_part = comment_formatted + "\n" + comment.symbol_text
        user_prompt = user_prompt_template.format(prompt_part)

        # Call LLM
        llm_output = self.llm.call_llm(system_prompt, user_prompt)

        # Extract the comment part from the output
        new_comment = self._extract_comment(llm_output)
        if new_comment is None:
            return ConvError(f"No comment found in output of LLM: {llm_output}")
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
    def _extract_comment(cls, result: str) -> str | None:
        found_comments = tuple(find_comments_connected(result))
        if not found_comments:
            return None
        range, _ = found_comments[0]
        return result[range.start:range.end]
    