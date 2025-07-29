"""This module contains the Slash JavaScript functionality.

JavaScript functions can be defined using the :py:class:`JSFunction` class
and executed using the :py:meth:`Session.execute() <slash.core.Session.execute>` method,
as in the following example.

    >>> f = JSFunction(["msg"], "alert(msg)")
    >>> Session.require().execute(f, ["Hello world!"])

By setting the :py:const:`name <slash.core.Session.execute>` argument in
:py:meth:`Session.execute() <slash.core.Session.execute>`, the return value of the function
is stored under the given name, and can be accessed later in JavaScript via ``Slash.value(name)``.
This is shown in the following example.

    >>> add = JSFunction(["a", "b"], "return a + b")
    >>> Session.require().execute(add, [3, 4], "3_plus_4")
    >>>
    >>> alert = JSFunction(["name"], "alert(Slash.value(name))")
    >>> Session.require().execute(alert, ["3_plus_4"])
"""

from slash._utils import random_id


class JSFunction:
    """JavaScript function.

    Args:
        params: List of parameter names.
        body: String contents of the function as JavaScript code.
    """

    def __init__(self, params: list[str], body: str) -> None:
        self._id = random_id()
        self._params = params
        self._body = body

    @property
    def id(self) -> str:
        return self._id

    @property
    def params(self) -> list[str]:
        return self._params

    @property
    def body(self) -> str:
        return self._body
