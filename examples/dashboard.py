import math
import random

from slash import App
from slash.basic import Axes, DataTable, Graph, Scatter
from slash.basic._markdown import Markdown
from slash.basic._pie import Pie
from slash.core import Elem
from slash.html import H3, Button, P
from slash.layout import Column, Panel, Row


def home() -> Elem:
    return Column(
        H3("Slash dashboard"),
        Row(Panel(graph()), table()).style({"gap": "16px"}).style({"justify-content": "stretch"}),
        Row(panel_1(), panel_2(), Panel(pie())).style({"gap": "16px"}).style({"justify-content": "stretch"}),
    ).style({"gap": "16px", "margin": "auto", "width": "1024px", "align-items": "center"})


def graph() -> Axes:
    xs = [x for x in range(100)]
    ys_1 = [20 + 10 * math.sin(x / 10) for x in xs]
    ys_1_noise = [y + 3 * (random.random() - 0.5) for y in ys_1]
    ys_2 = [20 + 5 * math.sin(x / 10 - math.pi / 2) for x in xs]
    ys_2_noise = [y + 3 * (random.random() - 0.5) for y in ys_2]
    return (
        Axes(width=512, height=320)
        .add_plot(Scatter(xs, ys_1_noise, label="scatter"))
        .add_plot(Graph(xs, ys_1, label="graph"))
        .add_plot(Scatter(xs, ys_2_noise, label="scatter"))
        .add_plot(Graph(xs, ys_2, label="graph"))
        .set_grid(True)
        .set_xlabel("x-axis")
        .set_ylabel("y-axis")
        .set_title("Graph title")
        .set_legend(True)
        .onmount(lambda event: event.target.render())
    )


def panel_1() -> Panel:
    return Panel(
        H3("Latin"),
        P(
            "Cum tenetur neque magnam reprehenderit non quia maiores. "
            "Debitis vero non saepe cumque non illo rerum. "
            "Quas eum quaerat aut sunt quaerat animi provident aut. "
            "Delectus fugit totam non doloremque. Nihil inventore qui nesciunt. "
            "Sunt sint eius deserunt."
        ),
        Row(Button("Cut"), Button("Copy"), Button("Paste")).style({"gap": "16px"}),
    )


def panel_2() -> Panel:
    return Panel(
        H3("Reviews"),
        Markdown("> Best product ever!"),
        Markdown("> Perfect five out of seven ⭐"),
        Markdown("> Cannot live without this"),
        Markdown("[Click here for more!](#)"),
    ).style({"min-width": "192px"})


def pie() -> Pie:
    return (
        Pie()
        .set_title("Colored Pie")
        .render(
            ("Blue", "Yellow", "Green", "Red"),
            (0.1, 0.2, 0.3, 0.4),
        )
    )


def table() -> DataTable:
    return (
        DataTable(("ID", "Name", "Country"), max_rows=8)
        .set_data(
            [
                {
                    "ID": n,
                    "Name": random.choice(
                        [
                            "Peter",
                            "Andrew",
                            "James",
                            "John",
                            "Philip",
                            "Bart",
                            "Thomas",
                            "Matt",
                            "Thad",
                            "Simon",
                            "Judas",
                        ]
                    )
                    + " "
                    + random.choice(
                        ["Smith", "Brown", "Jones", "Miller", "Davis", "Moore", "Lee", "White", "Green", "Black"]
                    ),
                    "Age": random.randint(18, 90),
                    "Country": random.choice(
                        [
                            "Netherlands",
                            "Belgium",
                            "France",
                            "Germany",
                            "Denmark",
                            "Luxembourgh",
                            "Spain",
                            "Portugal",
                            "Norway",
                            "Sweden",
                            None,
                        ]
                    ),
                }
                for n in range(95)
            ]
        )
        .style({"width": "462px"})
    )


if __name__ == "__main__":
    app = App()
    app.add_route("/", home)
    app.run()
