from slash.core import Elem, Session
from slash.html import Button, Div, P, Textarea
from slash.js import JSFunction
from slash.layout import Column


def test_js() -> Elem:
    def execute() -> None:
        jsfunction = JSFunction([], textarea.value)
        Session.require().execute(jsfunction, [])

    return Div(
        P(
            "This page tests JavaScript functionality. Write some JavaScript code in the textarea below,"
            "and press the button to execute it."
        ),
        Column(
            textarea := Textarea("alert('Test successful!');", placeholder="Write some JS here.."),
            Button("Execute").onclick(execute),
        ).style({"gap": "8px"}),
    )
