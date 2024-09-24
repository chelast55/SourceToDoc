from dataclasses import dataclass
from itertools import chain
from typing import Iterable, Self


@dataclass(frozen=True)
class FunctionIdentifier:
    """
    Represents a qualified name that identifies a function or method.

    Example: `NamespaceA::ClassA::method()`
    """
    namespaces_classes_function: tuple[str,...]

    @classmethod
    def parse(cls, function_identifier: str) -> Self:
        """
        Parses a string in the form of `NamespaceA::ClassA::method()`.

        Parameters
        ----------
        function_identifier : str
            The string to parse.

        Returns
        -------
        Self
            A new `FunctionIdentifier` object.
        """
        parenthese_index: int = function_identifier.find("(") # Arguments may include "::"
        tmp: list[str] = function_identifier[:parenthese_index].split("::")
        namespaces_classes: list[str] = tmp[:-1]
        function: str = tmp[-1] + function_identifier[parenthese_index:]
        namespaces_classes_function: Iterable[str] = chain(namespaces_classes, (function,))
        return cls(tuple(namespaces_classes_function))

    def namespaces_and_classes(self) -> tuple[str,...]:
        """Returns the namespaces and a class (if existing) of the function or method."""
        return self.namespaces_classes_function[:-1]

    def function(self) -> str:
        """Returns the function name."""
        return self.namespaces_classes_function[-1]

    def is_main_function(self) -> bool:
        """
        Returns `True` if the function is in the global scope und the function name starts with `main(`,
        else `False`.
        """
        return len(self.namespaces_classes_function) == 1 and self.namespaces_classes_function[0].startswith("main(")

    def __str__(self) -> str:
        """Returns a string in the form of `NamespaceA::ClassA::method()`."""
        return "::".join(self.namespaces_classes_function)
