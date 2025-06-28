from __future__ import annotations

from slash import App
from slash.core import Elem
from slash.html import H2, Button, Input, Span
from slash.layout import Column, Row

input_text = ""

BOX_STYLE = {
    "background-color": "var(--white)",
    "border": "1px solid #bbb",
    "border-radius": "8px",
    "padding": "8px",
}


def swap_column(new_task: Elem, tasks: Elem, finished: Elem) -> None:
    if tasks.contains(new_task):
        finished.append(new_task)
    else:
        tasks.append(new_task)


def add_task(tasks: Elem, finished: Elem) -> None:
    tasks.append(
        new_task := Row(
            [
                Span(input_text).style({"margin-right": "auto", "font-weight": "bold"}),
                Button("move").onclick(
                    lambda _: swap_column(new_task, tasks, finished)
                ),
                Button("delete").onclick(lambda _: new_task.unmount()),
            ]
        ).style(
            {"align-items": "center"},
        )
    )


def set_text(value: str) -> None:
    global input_text
    input_text = value


def home() -> Elem:
    return Column(
        [
            Row(
                [
                    Input("text").onchange(lambda event: set_text(event.value)),
                    Button("add task").onclick(lambda _: add_task(tasks, finished)),
                ]
            ),
            Row(
                [
                    tasks := Column(
                        [
                            H2("Tasks 📝").style(
                                {"text-align": "center", "color": "blue"},
                            )
                        ]
                    ).style(
                        {"width": "256px"},
                    ),
                    finished := Column(
                        [
                            H2("Finished 🎉").style(
                                {"text-align": "center", "color": "green"},
                            )
                        ]
                    ).style(
                        {"width": "256px"},
                    ),
                ]
            ).style(
                {"gap": "32px"},
            ),
        ]
    ).style(
        {"width": "512px", "align-items": "center", "margin": "0px auto"},
    )


def main():
    app = App()
    app.add_endpoint("/", home)
    app.run()


if __name__ == "__main__":
    main()
