from slash.basic import Axes, Graph, Markdown
from slash.core import Elem
from slash.html import H3, Button, P
from slash.layout import Column, Panel, Row


def test_tinker() -> Elem:
    return Column(
        P(
            "This page contains lots of elements, showing all kinds of available elements. "
            "It gives an impression of what a slash page may look like."
        ),
        Row(
            Panel(
                H3("Panel 1").style({"margin-top": "0px"}),
                P(
                    "Cum tenetur neque magnam reprehenderit non quia maiores. "
                    "Debitis vero non saepe cumque non illo rerum. "
                    "Quas eum quaerat aut sunt quaerat animi provident aut. "
                    "Delectus fugit totam non doloremque. Nihil inventore qui nesciunt. "
                    "Sunt sint eius deserunt."
                ),
                Row(Button("Cut"), Button("Copy"), Button("Paste")).style({"gap": "16px"}),
            ).style({"padding": "16px"}),
            Panel(
                H3("Panel 2").style({"margin-top": "0px"}),
                P(
                    "Repellat excepturi eligendi voluptas et reprehenderit delectus in. "
                    "Et doloribus sint est quas dolore. Exercitationem ex corporis asperiores quod. "
                    "Ex facere amet ab."
                ),
                Row(Button("Work it"), Button("Do it"), Button("Make it")).style({"gap": "16px"}),
            ).style({"padding": "16px"}),
        ).style({"gap": "16px"}),
        Panel(
            Markdown(
                """
### Markdown panel

Markdown allows for text to be *italic* or **bold** or ***both***.
There can be [hyperlinks](https://jessetvogel.nl) and `code`.
Now follows a horizontal line.

---

> Once upon a time, there were blockquotes, like this one.
"""
            )
        ),
        Panel(
            axes := Axes(width=512, height=384)
            .add_plot(Graph([0, 1, 2, 3], [0.5, 0.7, 0.2, 0.4], label="Series A"))
            .add_plot(Graph([0, 1, 2, 3], [0.2, 0.4, 0.7, 0.5], label="Series B"))
            .set_grid(True)
            .set_legend(True)
            .set_xlabel("x-axis")
            .set_ylabel("y-axis")
            .set_title("Some random graph")
            .onmount(lambda: axes.render())
            .style({"margin": "0px auto"}),
        ),
    ).style({"gap": "16px"})
