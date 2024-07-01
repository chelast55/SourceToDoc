import re


class CommandStyle:
    """
    Provides methods to change the Doxygen command style in comments.
    """
    _DEFAULT_PATTERN = re.compile(r"\\([\S]+)")
    _JAVADOC_PATTERN = re.compile(r"@([\S]+)")

    @classmethod
    def sub_to_default_style(cls, text: str) -> str:
        """
        Substitutes all `@<non-whitespaces>` with `\\<non-whitespaces>`.
        """
        return cls._JAVADOC_PATTERN.sub(r"\\\1", text)

    @classmethod
    def sub_to_javadoc_style(cls, text: str) -> str:
        """
        Substitutes all `\\<non-whitespaces>` with `@<non-whitespaces>`.
        """
        return cls._DEFAULT_PATTERN.sub(r"@\1", text)
