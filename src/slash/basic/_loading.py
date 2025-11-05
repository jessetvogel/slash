from typing import Self

from slash.core import Elem, Session
from slash.html import Div, Span


class Loading:
    """Loading screen as asynchronous context manager.

    This class can be used for instance in a handler to show a loading screen
    to give the user feedback about what the handler is doing.

    Example
    -------

    >>> from slash.basic import Loading
    >>>
    >>> async with Loading("Doing first task..") as loading:
    >>>     # Do first task ..
    >>>     await loading.set_description("Doing second task..")
    >>>     # Do second task ..

    Args:
        description: Description to display above loading spinner.
    """

    def __init__(self, description: str | Elem) -> None:
        self._elem = Div(
            _description := Div(),
            Div(),
        ).add_class("slash-loading")
        self._desciption = _description
        self._set_description(description)

    async def __aenter__(self) -> Self:
        self._elem.mount()
        await Session.require().flush()
        return self

    async def __aexit__(self, exc_type, exc_value, exc_tb) -> None:
        self._elem.unmount()

    async def set_description(self, description: str | Elem) -> Self:
        """Set description to display above loading spinner."""
        self._set_description(description)
        await Session.require().flush()
        return self

    def _set_description(self, description: str | Elem) -> None:
        if isinstance(description, str):
            self._desciption.clear()
            self._desciption.append(Span(description).style({"font-size": "1.25rem", "font-weight": "bold"}))
        else:
            if self._desciption.children != [description]:
                self._desciption.clear()
                self._desciption.append(description)
