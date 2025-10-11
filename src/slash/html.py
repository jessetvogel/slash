"""This module contains the Slash HTML elements."""

from __future__ import annotations

from typing import Literal, Self

from slash._message import Message
from slash.core import Attr, Children, Elem, Session
from slash.events import ChangeEvent, SupportsOnChange, SupportsOnClick, SupportsOnInput
from slash.js import JSFunction


class Div(Elem, SupportsOnClick):
    """HTML ``<div>`` element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("div", *children)


class P(Elem, SupportsOnClick):
    """HTML ``<p>`` element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("p", *children)


class Code(Elem, SupportsOnClick):
    """HTML ``<code>`` element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("code", *children)


class Br(Elem):
    """HTML ``<br>`` element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("br", *children)


class Span(Elem, SupportsOnClick):
    """HTML ``<span>`` element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("span", *children)


class Pre(Elem, SupportsOnClick):
    """HTML ``<pre>`` element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("pre", *children)


class Ul(Elem, SupportsOnClick):
    """HTML ``<ul>`` element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("ul", *children)


class Ol(Elem, SupportsOnClick):
    """HTML ``<ol>`` element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("ol", *children)


class Li(Elem, SupportsOnClick):
    """HTML ``<li>`` element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("li", *children)


class Details(Elem, SupportsOnClick):
    """HTML ``<details>`` element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("details", *children)


class Summary(Elem, SupportsOnClick):
    """HTML ``<summary>`` element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("summary", *children)


class Label(Elem, SupportsOnClick):
    """HTML ``<label>`` element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("label", *children)


class Table(Elem, SupportsOnClick):
    """HTML ``<table>`` element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("table", *children)


class Tr(Elem, SupportsOnClick):
    """HTML ``<tr>`` element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("tr", *children)


class Th(Elem, SupportsOnClick):
    """HTML ``<th>`` element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("th", *children)


class Td(Elem, SupportsOnClick):
    """HTML ``<td>`` element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("td", *children)


class H1(Elem, SupportsOnClick):
    """HTML ``<h1>`` element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("h1", *children)


class H2(Elem, SupportsOnClick):
    """HTML ``<h2>`` element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("h2", *children)


class H3(Elem, SupportsOnClick):
    """HTML ``<h3>`` element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("h3", *children)


class H4(Elem, SupportsOnClick):
    """HTML ``<h4>`` element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("h4", *children)


class H5(Elem, SupportsOnClick):
    """HTML ``<h5>`` element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("h5", *children)


class H6(Elem, SupportsOnClick):
    """HTML ``<h6>`` element."""

    def __init__(self, *children: Children) -> None:
        super().__init__("h6", *children)


class A(Elem, SupportsOnClick):
    """HTML ``<a>`` element.

    Args:
        children: Child or children of element. Either an element, string or
            list of elements and strings.
        href: URL that the link points to.
        target: Where to display the linked URL.
    """

    href = Attr("href")
    target = Attr("target")

    def __init__(
        self,
        *children: Children,
        href: str = "#",
        target: Literal["_blank", "_self", "_parent", "_top"] | str | None = None,
    ) -> None:
        super().__init__("a", *children)
        self.href = href
        self.target = target

    def set_href(self, href: str) -> Self:
        self.href = href
        return self

    def set_target(self, target: str) -> Self:
        self.target = target
        return self


class Button(Elem, SupportsOnClick):
    """HTML ``<button>`` element."""

    disabled = Attr("disabled")

    def __init__(self, *children: Children, disabled: bool = False) -> None:
        super().__init__("button", *children)
        self.disabled = "" if disabled else None


class Input(Elem, SupportsOnClick, SupportsOnInput, SupportsOnChange):
    """HTML ``<input>`` element.

    Args:
        type: Type of input field, e.g. ``text``, ``number``, ``password``, etc.
        name: Name of the input field.
        value: Default value of the input field.
        placeholder: Placeholder text when input is empty.
    """

    type = Attr("type")
    name = Attr("name")
    value = Attr("value")
    placeholder = Attr("placeholder")

    def __init__(
        self,
        type: str = "text",
        *,
        name: str | None = None,
        value: str = "",
        placeholder: str = "",
    ) -> None:
        super().__init__("input")
        self.type = type
        self.name = name
        self.value = value
        self.placeholder = placeholder
        self.onchange(self._handle_change)

    def _handle_change(self, event: ChangeEvent) -> None:
        self._value = event.value

    def set_name(self, name: str | None) -> Self:
        self.name = name
        return self

    def set_value(self, value: str) -> Self:
        self.value = value
        return self

    def set_placeholder(self, placeholder: str) -> Self:
        self.placeholder = placeholder
        return self


class Textarea(Elem, SupportsOnClick, SupportsOnInput, SupportsOnChange):
    """HTML ``<textarea>`` element.

    Args:
        value: Contents of the textarea.
        placeholder: Placeholder text when textarea is empty.
    """

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
    """HTML ``<img>`` element.

    Args:
        src: URL to the image to show.
        alt: Textual replacement for the image.
    """

    src = Attr("src")
    alt = Attr("alt")

    def __init__(self, *, src: str = "", alt: str = "") -> None:
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
    """HTML ``<select>`` element."""

    def __init__(self, options: list[Option]):
        super().__init__("select", *options)
        if not all(isinstance(option, Option) for option in options):
            msg = "Children of `Select` must be of type `Option`"
            raise ValueError(msg)
        self._value: str = options[0].value
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


class Option(Elem):
    """HTML ``<option>`` element."""

    value = Attr("value")
    disabled = Attr("disabled")
    hidden = Attr("hidden")

    def __init__(
        self,
        text: str = "",
        value: str | None = None,
        disabled: bool = False,
        hidden: bool = False,
    ) -> None:
        super().__init__("option", text)
        self.value = value if value is not None else text
        self.disabled = "" if disabled else None
        self.hidden = "" if hidden else None


_JS_DIALOG_SHOW = JSFunction(["id"], "document.getElementById(id).show()")
_JS_DIALOG_SHOW_MODAL = JSFunction(["id"], "document.getElementById(id).showModal()")
_JS_DIALOG_CLOSE = JSFunction(["id"], "document.getElementById(id).close()")


class Dialog(Elem):
    """HTML ``<dialog>`` element."""

    def __init__(self, *children: Children):
        super().__init__("dialog", *children)

    def show(self) -> None:
        """Show dialog modelessly using the ``HTMLDialogElement.show()`` JavaScript method."""
        Session.require().execute(_JS_DIALOG_SHOW, [self.id])

    def show_modal(self) -> None:
        """Show dialog as a modal using the ``HTMLDialogElement.showModal()`` JavaScript method."""
        Session.require().execute(_JS_DIALOG_SHOW_MODAL, [self.id])

    def close(self) -> None:
        """Close the dialog using the ``HTMLDialogElement.close()`` JavaScript method."""
        Session.require().execute(_JS_DIALOG_CLOSE, [self.id])


class HTML(Elem):
    """HTML ``<div>`` element that contains arbitrary HTML.

    Args:
        html: Arbitrary HTML content.
    """

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
