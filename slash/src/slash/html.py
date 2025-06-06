from slash.core import (
    Attr,
    ChangeEvent,
    ChangeEventHandler,
    Children,
    ClickEventHandler,
    Elem,
    InputEventHandler,
    SupportsOnChange,
    SupportsOnClick,
    SupportsOnInput,
)


class Div(Elem, SupportsOnClick):
    def __init__(
        self,
        children: Children = None,
        *,
        style: dict[str, str] | None = None,
        onclick: ClickEventHandler | None = None,
    ) -> None:
        super().__init__("div", children=children, style=style)
        SupportsOnClick.__init__(self, onclick)


class P(Elem, SupportsOnClick):
    def __init__(
        self,
        children: Children = None,
        *,
        style: dict[str, str] | None = None,
        onclick: ClickEventHandler | None = None,
    ) -> None:
        super().__init__("p", children=children, style=style)
        SupportsOnClick.__init__(self, onclick)


class Span(Elem, SupportsOnClick):
    def __init__(
        self,
        children: Children = None,
        *,
        style: dict[str, str] | None = None,
        onclick: ClickEventHandler | None = None,
    ) -> None:
        super().__init__("span", children=children, style=style)
        SupportsOnClick.__init__(self, onclick)


class H1(Elem, SupportsOnClick):
    def __init__(
        self,
        children: Children = None,
        *,
        style: dict[str, str] | None = None,
        onclick: ClickEventHandler | None = None,
    ) -> None:
        super().__init__("h1", children=children, style=style)
        SupportsOnClick.__init__(self, onclick)


class H2(Elem, SupportsOnClick):
    def __init__(
        self,
        children: Children = None,
        *,
        style: dict[str, str] | None = None,
        onclick: ClickEventHandler | None = None,
    ) -> None:
        super().__init__("h2", children=children, style=style)
        SupportsOnClick.__init__(self, onclick)


class H3(Elem, SupportsOnClick):
    def __init__(
        self,
        children: Children = None,
        *,
        style: dict[str, str] | None = None,
        onclick: ClickEventHandler | None = None,
    ) -> None:
        super().__init__("h3", children=children, style=style)
        SupportsOnClick.__init__(self, onclick)


class H4(Elem, SupportsOnClick):
    def __init__(
        self,
        children: Children = None,
        *,
        style: dict[str, str] | None = None,
        onclick: ClickEventHandler | None = None,
    ) -> None:
        super().__init__("h4", children=children, style=style)
        SupportsOnClick.__init__(self, onclick)


class H5(Elem, SupportsOnClick):
    def __init__(
        self,
        children: Children = None,
        *,
        style: dict[str, str] | None = None,
        onclick: ClickEventHandler | None = None,
    ) -> None:
        super().__init__("h5", children=children, style=style)
        SupportsOnClick.__init__(self, onclick)


class H6(Elem, SupportsOnClick):
    def __init__(
        self,
        children: Children = None,
        *,
        style: dict[str, str] | None = None,
        onclick: ClickEventHandler | None = None,
    ) -> None:
        super().__init__("h6", children=children, style=style)
        SupportsOnClick.__init__(self, onclick)


class A(Elem, SupportsOnClick):
    href = Attr("href")

    def __init__(
        self,
        children: Children = None,
        *,
        href: str = "#",
        style: dict[str, str] | None = None,
        onclick: ClickEventHandler | None = None,
    ) -> None:
        super().__init__("a", children=children, style=style)
        SupportsOnClick.__init__(self, onclick)
        self.href = href


class Button(Elem, SupportsOnClick):
    def __init__(
        self,
        children: Children = None,
        *,
        style: dict[str, str] | None = None,
        onclick: ClickEventHandler | None = None,
    ) -> None:
        super().__init__("button", children=children, style=style)
        SupportsOnClick.__init__(self, onclick)


class Input(Elem, SupportsOnClick, SupportsOnInput, SupportsOnChange):
    type = Attr("type")
    value = Attr("value")
    placeholder = Attr("placeholder")

    def __init__(
        self,
        type: str = "text",
        *,
        style: dict[str, str] | None = None,
        value: str = "",
        placeholder: str = "",
        onclick: ClickEventHandler | None = None,
        oninput: InputEventHandler | None = None,
        onchange: ChangeEventHandler | None = None,
    ) -> None:
        super().__init__("input", style=style)
        SupportsOnClick.__init__(self, onclick)
        SupportsOnInput.__init__(self, oninput)
        SupportsOnChange.__init__(self, onchange or (lambda _: None))
        self.type = type
        self.value = value
        self.placeholder = placeholder

    def change(self, event: ChangeEvent) -> None:
        Input.value.set_silently(self, event.value)
        if self.onchange:
            self.onchange(event)


class Textarea(Elem, SupportsOnClick, SupportsOnInput, SupportsOnChange):
    placeholder = Attr("placeholder")

    def __init__(
        self,
        text: str = "",
        *,
        style: dict[str, str] | None = None,
        placeholder: str = "",
        onclick: ClickEventHandler | None = None,
        oninput: InputEventHandler | None = None,
        onchange: ChangeEventHandler | None = None,
    ) -> None:
        super().__init__("textarea", [text], style=style)
        SupportsOnClick.__init__(self, onclick)
        SupportsOnInput.__init__(self, oninput)
        SupportsOnChange.__init__(self, onchange or (lambda _: None))
        self.placeholder = placeholder
        self.text = text

    def change(self, event: ChangeEvent) -> None:
        self._text = event.value
        if self.onchange:
            self.onchange(event)
