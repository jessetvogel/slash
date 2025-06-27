"""Slash HTML elements."""

from slash._message import Message
from slash.core import Attr, Children, Elem, Session
from slash.events import ChangeEvent, SupportsOnChange, SupportsOnClick, SupportsOnInput
from slash.js import JSFunction


class Div(Elem, SupportsOnClick):
    """HTML <div> element."""

    def __init__(self, children: Children = None) -> None:
        super().__init__("div", children=children)
        SupportsOnClick.__init__(self)


class P(Elem, SupportsOnClick):
    """HTML <p> element."""

    def __init__(self, children: Children = None) -> None:
        super().__init__("p", children=children)
        SupportsOnClick.__init__(self)


class Span(Elem, SupportsOnClick):
    """HTML <span> element."""

    def __init__(self, children: Children = None) -> None:
        super().__init__("span", children=children)
        SupportsOnClick.__init__(self)


class H1(Elem, SupportsOnClick):
    """HTML <h1> element."""

    def __init__(self, children: Children = None) -> None:
        super().__init__("h1", children=children)
        SupportsOnClick.__init__(self)


class H2(Elem, SupportsOnClick):
    """HTML <h2> element."""

    def __init__(self, children: Children = None) -> None:
        super().__init__("h2", children=children)
        SupportsOnClick.__init__(self)


class H3(Elem, SupportsOnClick):
    """HTML <h3> element."""

    def __init__(self, children: Children = None) -> None:
        super().__init__("h3", children=children)
        SupportsOnClick.__init__(self)


class H4(Elem, SupportsOnClick):
    """HTML <h4> element."""

    def __init__(self, children: Children = None) -> None:
        super().__init__("h4", children=children)
        SupportsOnClick.__init__(self)


class H5(Elem, SupportsOnClick):
    """HTML <h5> element."""

    def __init__(self, children: Children = None) -> None:
        super().__init__("h5", children=children)
        SupportsOnClick.__init__(self)


class H6(Elem, SupportsOnClick):
    """HTML <h6> element."""

    def __init__(self, children: Children = None) -> None:
        super().__init__("h6", children=children)
        SupportsOnClick.__init__(self)


class A(Elem, SupportsOnClick):
    """HTML <a> element."""

    href = Attr("href")

    def __init__(
        self,
        children: Children = None,
        *,
        href: str = "#",
    ) -> None:
        super().__init__("a", children=children)
        SupportsOnClick.__init__(self)
        self.href = href


class Button(Elem, SupportsOnClick):
    """HTML <button> element."""

    def __init__(self, children: Children = None) -> None:
        super().__init__("button", children=children)
        SupportsOnClick.__init__(self)


class Input(Elem, SupportsOnClick, SupportsOnInput, SupportsOnChange):
    """HTML <input> element."""

    type = Attr("type")
    value = Attr("value")
    placeholder = Attr("placeholder")

    def __init__(
        self,
        type: str = "text",
        *,
        value: str = "",
        placeholder: str = "",
    ) -> None:
        super().__init__("input")
        self.type = type
        self.value = value
        self.placeholder = placeholder
        self.onchange(self._set_value)

    def _set_value(self, event: ChangeEvent) -> None:
        self._value = event.value


class Textarea(Elem, SupportsOnClick, SupportsOnInput, SupportsOnChange):
    """HTML <textarea> element."""

    placeholder = Attr("placeholder")

    def __init__(
        self,
        text: str = "",
        *,
        placeholder: str = "",
    ) -> None:
        super().__init__("textarea", [text])
        self.placeholder = placeholder
        self.text = text
        self.onchange(self._set_text)

    def _set_text(self, event: ChangeEvent) -> None:
        self._text = event.value


class Img(Elem):
    """HTML <img> element."""

    src = Attr("src")
    alt = Attr("alt")

    def __init__(self, src: str, *, alt: str = "") -> None:
        super().__init__("img")
        self.src = src
        self.alt = alt


class Select(Elem, SupportsOnChange):
    """HTML <select> element."""

    def __init__(self, options: list[str]):
        super().__init__("select", [Elem("option", option) for option in options])
        self._value = options[0]
        self.onchange(self._set_value)

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, val: str) -> None:
        self._value = val
        for child in self.children:
            if isinstance(child, Elem) and child.tag == "option":
                if child.text == self._value:
                    child.set_attr("selected")
                else:
                    child.remove_attr("selected")

    def _set_value(self, event: ChangeEvent) -> None:
        self.value = event.value


class Dialog(Elem):
    """HTML <dialog> element."""

    JS_SHOW = JSFunction(["id"], "document.getElementById(id).show()")
    JS_SHOW_MODAL = JSFunction(
        ["id"],
        "document.getElementById(id).showModal()",
    )
    JS_CLOSE = JSFunction(["id"], "document.getElementById(id).close()")

    def __init__(self, children: Children | None = None):
        super().__init__("dialog", children)

    def show(self) -> None:
        Session.require().execute(self.JS_SHOW, [self.id])

    def show_modal(self) -> None:
        Session.require().execute(self.JS_SHOW_MODAL, [self.id])

    def close(self) -> None:
        Session.require().execute(self.JS_CLOSE, [self.id])


class HTML(Elem):
    """Element containing arbitrary HTML."""

    def __init__(self, html: str) -> None:
        super().__init__("div")
        self.onmount(lambda _: self._set_html())
        self._html = html

    def _set_html(self) -> None:
        Session.require().send(Message.html(self.id, self._html))
