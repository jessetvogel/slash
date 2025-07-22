from slash.core import Elem, Session
from slash.html import H2, Button, Div, Textarea
from slash.js import JSFunction
from slash.layout import Column


def test_js() -> Elem:
    def execute() -> None:
        jsfunction = JSFunction([], textarea.value)
        Session.require().execute(jsfunction, [])

    return Div(
        H2("JavaScript"),
        Column(
            textarea := Textarea("alert('Test successful!');", placeholder="Write some JS here.."),
            Button("Execute").onclick(execute),
        ),
    )
