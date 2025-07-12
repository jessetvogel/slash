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
                Row(Checkbox(), "Monday"),
                Row(Checkbox(), "Tuesday"),
                Row(Checkbox(), "Wednesday"),
            ),
            Column(
                Row(radio := Radio(), "13:00"),
                Row(Radio().connect(radio), "14:00"),
                Row(Radio().connect(radio), "15:00"),
            ),
        ).style({"gap": "32px"}),
    )
