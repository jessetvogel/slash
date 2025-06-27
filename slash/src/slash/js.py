"""Slash JS functionality."""

from slash._utils import random_id


class JSFunction:
    """Class representing a JavaScript function."""

    def __init__(self, args: list[str], body: str) -> None:
        self._id = random_id()
        self._args = args
        self._body = body

    @property
    def id(self) -> str:
        """Id of the function."""
        return self._id

    @property
    def args(self) -> list[str]:
        """List of arguments the function."""
        return self._args

    @property
    def body(self) -> str:
        """Body of the function."""
        return self._body
