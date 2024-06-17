import re


class CommandStyle:
    _DEFAULT_PATTERN = re.compile(r"\\([\S]+)")
    _JAVADOC_PATTERN = re.compile(r"@([\S]+)")

    @classmethod
    def sub_to_default_style(cls, text: str) -> str:
        """
        Substitutes all `@<non-whitespaces>` with `\\<non-whitespaces>`.
        """
        return cls._JAVADOC_PATTERN.sub(cls._to_default_style, text)

    @classmethod
    def sub_to_javadoc_style(cls, text: str) -> str:
        """
        Substitutes all `\\<non-whitespaces>` with `@<non-whitespaces>`.
        """
        return cls._DEFAULT_PATTERN.sub(cls._to_javadoc_style, text)

    @staticmethod
    def _to_default_style(match: re.Match[str]) -> str:
        return "\\" + match.group(1)

    @staticmethod
    def _to_javadoc_style(match: re.Match[str]) -> str:
        return "@" + match.group(1)
