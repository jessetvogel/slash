from slash.core import (
    Attr,
    ChangeEvent,
    Children,
    Elem,
    SupportsOnChange,
    SupportsOnClick,
    SupportsOnInput,
)
from slash.js import JSFunction
from slash.message import Message


class Div(Elem, SupportsOnClick):
    def __init__(self, children: Children = None) -> None:
        super().__init__("div", children=children)
        SupportsOnClick.__init__(self)


class P(Elem, SupportsOnClick):
    def __init__(self, children: Children = None) -> None:
        super().__init__("p", children=children)
        SupportsOnClick.__init__(self)


class Span(Elem, SupportsOnClick):
    def __init__(self, children: Children = None) -> None:
        super().__init__("span", children=children)
        SupportsOnClick.__init__(self)


class H1(Elem, SupportsOnClick):
    def __init__(self, children: Children = None) -> None:
        super().__init__("h1", children=children)
        SupportsOnClick.__init__(self)


class H2(Elem, SupportsOnClick):
    def __init__(self, children: Children = None) -> None:
        super().__init__("h2", children=children)
        SupportsOnClick.__init__(self)


class H3(Elem, SupportsOnClick):
    def __init__(self, children: Children = None) -> None:
        super().__init__("h3", children=children)
        SupportsOnClick.__init__(self)


class H4(Elem, SupportsOnClick):
    def __init__(self, children: Children = None) -> None:
        super().__init__("h4", children=children)
        SupportsOnClick.__init__(self)


class H5(Elem, SupportsOnClick):
    def __init__(self, children: Children = None) -> None:
        super().__init__("h5", children=children)
        SupportsOnClick.__init__(self)


class H6(Elem, SupportsOnClick):
    def __init__(self, children: Children = None) -> None:
        super().__init__("h6", children=children)
        SupportsOnClick.__init__(self)


class A(Elem, SupportsOnClick):
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
    def __init__(self, children: Children = None) -> None:
        super().__init__("button", children=children)
        SupportsOnClick.__init__(self)


class Input(Elem, SupportsOnClick, SupportsOnInput, SupportsOnChange):
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
        SupportsOnClick.__init__(self)
        SupportsOnInput.__init__(self)
        SupportsOnChange.__init__(self)
        self.type = type
        self.value = value
        self.placeholder = placeholder
        self.onchange(self._set_value)

    def _set_value(self, event: ChangeEvent) -> None:
        self._value = event.value


class Textarea(Elem, SupportsOnClick, SupportsOnInput, SupportsOnChange):
    placeholder = Attr("placeholder")

    def __init__(
        self,
        text: str = "",
        *,
        placeholder: str = "",
    ) -> None:
        super().__init__("textarea", [text])
        SupportsOnClick.__init__(self)
        SupportsOnInput.__init__(self)
        SupportsOnChange.__init__(self)
        self.placeholder = placeholder
        self.text = text
        self.onchange(self._set_text)

    def _set_text(self, event: ChangeEvent) -> None:
        self._text = event.value


class Img(Elem):
    src = Attr("src")
    alt = Attr("alt")

    def __init__(self, src: str, *, alt: str = "") -> None:
        super().__init__("img")
        self.src = src
        self.alt = alt


class Select(Elem, SupportsOnChange):
    def __init__(self, options: list[str]):
        super().__init__("select", [Elem("option", option) for option in options])
        SupportsOnChange.__init__(self)
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
    JS_SHOW = JSFunction(["id"], "document.getElementById(id).show()")
    JS_SHOW_MODAL = JSFunction(
        ["id"],
        "document.getElementById(id).showModal()",
    )
    JS_CLOSE = JSFunction(["id"], "document.getElementById(id).close()")

    def __init__(self, children: Children | None = None):
        super().__init__("dialog", children)

    def show(self) -> None:
        self.client.execute(self.JS_SHOW, [self.id])

    def show_modal(self) -> None:
        self.client.execute(self.JS_SHOW_MODAL, [self.id])

    def close(self) -> None:
        self.client.execute(self.JS_CLOSE, [self.id])


class HTML(Elem):
    def __init__(self, html: str) -> None:
        super().__init__("div")
        self.onmount(self._set_html)
        self._html = html

    def _set_html(self) -> None:
        self.client.send(Message.html(self.id, self._html))
