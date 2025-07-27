"""This module contains the Slash JavaScript functionality."""

from slash._utils import random_id


class JSFunction:
    """Class representing a JavaScript function.

    Example:

        >>> f = JSFunction(["msg"], "alert(msg)")
        >>> Session.require().execute(f, ["Hello world!"])
    """

    def __init__(self, params: list[str], body: str) -> None:
        """Initialize JavaScript function`.

        Args:
            params: List of parameter names for the JavaScript function.
            body: Body for the JavaScript function.
        """
        self._id = random_id()
        self._params = params
        self._body = body

    @property
    def id(self) -> str:
        """Function id."""
        return self._id

    @property
    def params(self) -> list[str]:
        """List of function parameters."""
        return self._params

    @property
    def body(self) -> str:
        """Function body."""
        return self._body
