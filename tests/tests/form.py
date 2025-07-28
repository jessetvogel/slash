from slash.basic._checkbox import Checkbox
from slash.basic._radio import Radio
from slash.core import Elem
from slash.html import Code, P
from slash.layout import Column, Row


def test_form() -> Elem:
    return Column(
        P("This page tests the ", Code("Checkbox"), " and ", Code("Radio"), " elements."),
        Row(
            Column(
                Checkbox("Monday"),
                Checkbox("Tuesday"),
                Checkbox("Wednesday"),
            ),
            Column(
                radio := Radio("13:00"),
                Radio("14:00").connect(radio),
                Radio("15:00").connect(radio),
            ),
        ).style({"gap": "32px"}),
    )
