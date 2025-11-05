import time

from slash._utils import random_id
from slash.basic import Checkbox, Loading
from slash.core import Elem
from slash.html import H3, Button, Code, Div, P
from slash.layout import Column


def test_loading() -> Elem:
    time.sleep(1)
    return Column(
        P("The page should have been loading for 1 seconds before showing this text."),
        P("Click one of the buttons below to show a new loading screen."),
        Button("🚀 Launch easy task!").onclick(easy).style({"margin-bottom": "8px"}),
        Button("🚀 Launch complicated task!").onclick(complicated),
    )


async def easy() -> None:
    async with Loading("Starting tasks..") as loading:
        time.sleep(1)
        for i in range(n := 3):
            await loading.set_description(f"Completed {i}/{n} tasks..")
            time.sleep(1)


async def complicated() -> None:
    description = Column(
        H3("Doing complicated tasks.."),
        Div(checkbox_1 := Checkbox(Code(random_id()))),
        Div(checkbox_2 := Checkbox(Code(random_id()))),
        Div(checkbox_3 := Checkbox(Code(random_id()))),
    ).style({"gap": "8px"})

    async with Loading(description) as loading:
        time.sleep(1)
        checkbox_1.checked = True
        await loading.set_description(description)
        time.sleep(1)
        checkbox_2.checked = True
        await loading.set_description(description)
        time.sleep(1)
        checkbox_3.checked = True
        await loading.set_description(description)
        time.sleep(1)
