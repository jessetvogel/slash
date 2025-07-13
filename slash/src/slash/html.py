"""Slash HTML elements."""

from typing import Self

from slash._message import Message
from slash.core import Attr, Children, Elem, Session
from slash.events import ChangeEvent, SupportsOnChange, SupportsOnClick, SupportsOnInput
from slash.js import JSFunction


class Div(Elem, SupportsOnClick):
    """HTML <div> element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("div", *children)
        SupportsOnClick.__init__(self)


class P(Elem, SupportsOnClick):
    """HTML <p> element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("p", *children)
        SupportsOnClick.__init__(self)


class Span(Elem, SupportsOnClick):
    """HTML <span> element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("span", *children)
        SupportsOnClick.__init__(self)


class Label(Elem, SupportsOnClick):
    """HTML <label> element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("label", *children)
        SupportsOnClick.__init__(self)


class Tr(Elem, SupportsOnClick):
    """HTML <tr> element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("tr", *children)
        SupportsOnClick.__init__(self)


class Th(Elem, SupportsOnClick):
    """HTML <th> element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("th", *children)
        SupportsOnClick.__init__(self)


class Td(Elem, SupportsOnClick):
    """HTML <td> element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("td", *children)
        SupportsOnClick.__init__(self)


class H1(Elem, SupportsOnClick):
    """HTML <h1> element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("h1", *children)
        SupportsOnClick.__init__(self)


class H2(Elem, SupportsOnClick):
    """HTML <h2> element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("h2", *children)
        SupportsOnClick.__init__(self)


class H3(Elem, SupportsOnClick):
    """HTML <h3> element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("h3", *children)
        SupportsOnClick.__init__(self)


class H4(Elem, SupportsOnClick):
    """HTML <h4> element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("h4", *children)
        SupportsOnClick.__init__(self)


class H5(Elem, SupportsOnClick):
    """HTML <h5> element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("h5", *children)
        SupportsOnClick.__init__(self)


class H6(Elem, SupportsOnClick):
    """HTML <h6> element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("h6", *children)
        SupportsOnClick.__init__(self)


class A(Elem, SupportsOnClick):
    """HTML <a> element."""

    href = Attr("href")

    def __init__(
        self,
        *children: Children,
        href: str = "#",
    ) -> None:
        super().__init__("a", *children)
        SupportsOnClick.__init__(self)
        self.href = href

    def set_href(self, href: str) -> Self:
        self.href = href
        return self


class Button(Elem, SupportsOnClick):
    """HTML <button> element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("button", *children)
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
        self.onchange(self._handle_change)

    def _handle_change(self, event: ChangeEvent) -> None:
        self._value = event.value

    def set_value(self, value: str) -> Self:
        self.value = value
        return self

    def set_placeholder(self, placeholder: str) -> Self:
        self.placeholder = placeholder
        return self


class Textarea(Elem, SupportsOnClick, SupportsOnInput, SupportsOnChange):
    """HTML <textarea> element."""

    placeholder = Attr("placeholder")

    def __init__(
        self,
        value: str = "",
        *,
        placeholder: str = "",
    ) -> None:
        super().__init__("textarea", value)
        self.placeholder = placeholder
        self._value = value
        self.onchange(self._handle_change)

    def _handle_change(self, event: ChangeEvent) -> None:
        self._value = event.value

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        self.set_value(value)

    def set_value(self, value: str) -> Self:
        self._value = value
        self.set_text(value)
        return self

    def set_placeholder(self, placeholder: str) -> Self:
        self.placeholder = placeholder
        return self


class Img(Elem):
    """HTML <img> element."""

    src = Attr("src")
    alt = Attr("alt")

    def __init__(self, src: str, *, alt: str = "") -> None:
        super().__init__("img")
        self.src = src
        self.alt = alt

    def set_src(self, src: str) -> Self:
        self.src = src
        return self

    def set_alt(self, alt: str) -> Self:
        self.alt = alt
        return self


class Select(Elem, SupportsOnChange):
    """HTML <select> element."""

    def __init__(self, options: list[str]):
        super().__init__("select", *[Elem("option", option) for option in options])
        self._value = options[0]
        self.onchange(self._handle_change)

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

    def _handle_change(self, event: ChangeEvent) -> None:
        self.value = event.value


class Dialog(Elem):
    """HTML <dialog> element."""

    JS_SHOW = JSFunction(["id"], "document.getElementById(id).show()")
    JS_SHOW_MODAL = JSFunction(
        ["id"],
        "document.getElementById(id).showModal()",
    )
    JS_CLOSE = JSFunction(["id"], "document.getElementById(id).close()")

    def __init__(self, *children: Children):
        super().__init__("dialog", *children)

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
        self.set_html(html)
        self.onmount(lambda _: self._update_html())

    def _update_html(self) -> None:
        Session.require().send(Message.html(self.id, self._html))

    @property
    def html(self) -> str:
        return self._html

    @html.setter
    def html(self, html: str) -> None:
        self.set_html(html)

    def set_html(self, html: str) -> Self:
        self._html = html
        if self.is_mounted():
            self._update_html()
        return self
