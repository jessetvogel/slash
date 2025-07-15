from slash.basic.checkbox import Checkbox
from slash.basic.radio import Radio
from slash.core import Elem
from slash.html import H2
from slash.layout import Column, Row


def test_form() -> Elem:
    return Column(
        H2("Checkbox"),
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
