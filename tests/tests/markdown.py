from slash.basic._markdown import Markdown
from slash.core import Elem
from slash.html import Code, Div, P, Textarea
from slash.layout import Panel


def test_markdown() -> Elem:
    output = Markdown("The rendered markdown should appear here")

    return Div(
        P(
            "This page tests the ",
            Code("Markdown"),
            " element. Type some markdown in the textarea below. "
            "The rendered markdown should appear in the panel below.",
        ),
        Textarea(placeholder="Write some markdown..")
        .oninput(lambda event: output.set_markdown(event.value))
        .style({"width": "100%", "box-sizing": "border-box", "margin": "16px 0px"}),
        Panel(output),
    )
