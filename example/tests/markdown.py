from slash.basic.markdown import Markdown
from slash.core import Elem
from slash.html import H2, Div, Textarea
from slash.layout import Panel


def test_markdown() -> Elem:
    output = Markdown("")

    return Div(
        H2("Markdown"),
        Panel(
            Textarea(placeholder="Write some markdown..").oninput(
                lambda event: output.set_markdown(event.value)
            ),
            output,
        ),
    )
