from __future__ import annotations

from slash import App
from slash.basic import Markdown, Tabs
from slash.core import Elem, Session
from slash.html import (
    H1,
    H2,
    Button,
    Dialog,
    Div,
    Input,
    Select,
    Span,
    Textarea,
)
from slash.js import JSFunction
from slash.layout import Column, Panel, Row


def home() -> Elem:
    return Div(
        H1("Slash test page").style({"text-align": "center"}),
        test_markdown(),
        test_counter(),
        test_select(),
        test_dialog(),
        test_log(),
        test_input(),
        test_js(),
        test_tabs(),
    ).style({"max-width": "640px", "margin": "0px auto"})


def test_markdown() -> Elem:
    output = Markdown("")

    return Div(
        H2("Markdown test"),
        Panel(
            Textarea(placeholder="Write some markdown..").oninput(
                lambda event: output.set_markdown(event.value)
            ),
            output,
        ),
    )


def test_counter() -> Elem:
    state = {"count": 0}
    label = Span().style({"padding": "8px"})

    def set_counter(value: int) -> None:
        state["count"] = value
        label.text = f"Counter: {value}"

    set_counter(0)

    return Div(
        H2("Counter test"),
        Panel(
            label,
            Row(
                Button("+1").onclick(lambda: set_counter(state["count"] + 1)),
                Button("-1").onclick(lambda: set_counter(state["count"] - 1)),
                Button("Reset").onclick(lambda: set_counter(0)),
            ),
        ),
    )


def test_select() -> Elem:
    return Div(
        H2("Select test"),
        select := Select(
            [
                "Woodpecker",
                "Pigeon",
                "Peacock",
                "Rooster",
                "Vulture",
                "Swallow",
                "Seagull",
                "Quail",
                "Duck",
                "Pelican",
                "Magpie",
                "Parrot",
                "Turkey",
                "Crane",
                "Kingfisher",
                "Hummingbird",
                "Sparrow",
                "Cormorant",
                "Ostrich",
                "Crow",
                "Raven",
                "Dove",
                "Hen",
                "Nightingale",
                "Eagle",
                "Swan",
                "Penguin",
                "Flamingo",
                "Goose",
                "Cuckoo",
                "Owl",
                "Hawk",
                "Partridge",
                "Goldfinch",
                "Robin",
                "Finch",
                "Frigatebird",
                "Sandpiper",
                "Stork",
                "Ibis",
                "Hornbill",
                "Bulbul",
                "Skylark",
                "Canary",
                "Wagtail",
                "Starling",
                "Macaw",
                "Cockatoo",
                "Heron",
                "Toucan",
                "Jay",
                "Mynah",
                "Cardinal",
                "Chickadee",
                "Junco",
                "Bluebird",
                "Swift",
                "Gull",
                "Lovebird",
                "Spoonbill",
                "Kiwi",
                "Avocet",
                "Wren",
                "Mockingbird",
                "Pheasant",
                "Hoopoe",
                "Kite",
                "Peahen",
                "Falcon",
                "Mallard",
                "Bald eagle",
                "Tern",
                "Night hawk",
                "Crossbill",
                "Lapwing",
                "Puffin",
                "Koyal",
                "Bullfinch",
                "Emu",
                "Condor",
            ]
        ).onchange(
            lambda: span.set_text(f"You selected '{select.value}'"),
        ),
        span := Span().style({"padding": "8px"}),
    )


def test_log() -> Elem:
    return Div(
        H2("Logging test"),
        Button("Trigger info").onclick(
            lambda: Session.require().log("info", "Example info message")
        ),
        Button("Trigger debug").onclick(
            lambda: Session.require().log("debug", "Example debug message")
        ),
        Button("Trigger warning").onclick(
            lambda: Session.require().log("warning", "Example warning message")
        ),
        Button("Trigger error").onclick(
            lambda: Session.require().log("error", "Example error message")
        ),
    )


def test_input() -> Elem:
    return Div(
        H2("Input test"),
        Input(placeholder="Write here!").oninput(
            lambda event: out.set_value("".join(reversed(event.value)))
        ),
        out := Input(),
    )


def test_js() -> Elem:
    def execute() -> None:
        jsfunction = JSFunction([], textarea.value)
        Session.require().execute(jsfunction, [])

    return Div(
        H2("JavaScript test"),
        Column(
            textarea := Textarea(placeholder="Write some JS here.."),
            Button("Execute").onclick(execute),
        ),
    )


def test_tabs() -> Elem:
    def set_tab(value: str) -> None:
        if value == "Tab 1":
            content.set_text("This is the first tab!")
        elif value == "Tab 2":
            content.set_text("Welcome to the second tab!")
        elif value == "Tab 3":
            content.set_text("You made it to the third tab!")

    return Div(
        H2("Tabs test"),
        tabs := Tabs(
            ["Tab 1", "Tab 2", "Tab 3"],
        ).onchange(lambda event: set_tab(event.value)),
        content := Div().style({"padding": "8px"}).onmount(lambda: set_tab(tabs.value)),
    )


def test_dialog() -> Elem:
    return Div(
        H2("Dialog test"),
        Div(
            Button("Dialog.show()").onclick(lambda: dialog.show()),
            Button("Dialog.show_modal()").onclick(lambda: dialog.show_modal()),
            dialog := Dialog(
                Column(
                    Span("This is a dialog element!"),
                    Button("Close").onclick(lambda: dialog.close()),
                ).style({"gap": "16px"})
            ),
        ),
    )


def main():
    app = App()
    app.add_endpoint("/", home)
    app.run()


if __name__ == "__main__":
    main()
