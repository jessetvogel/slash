from __future__ import annotations
import asyncio

import numpy as np
from slash.core import Session, Elem
from slash import App
from slash import html, layout
from slash.basic import Progress


async def move_to_value(progress: Progress, value: float) -> None:
    session = Session.require()

    old_value = progress.value
    new_value = value
    diff = new_value - old_value
    if diff == 0.0:
        return

    sign = diff / abs(diff)
    for v in np.arange(old_value, new_value + sign * 0.001, sign * 0.01):
        progress.set_value(float(v))
        await session.flush()
        await asyncio.sleep(0.05)


def home() -> Elem:
    return layout.Column(
        [
            progress := Progress(),
            layout.Row(
                [
                    html.Button("0%").onclick(lambda _: move_to_value(progress, 0.0)),
                    html.Button("50%").onclick(lambda _: move_to_value(progress, 0.5)),
                    html.Button("100%").onclick(lambda _: move_to_value(progress, 1.0)),
                ]
            ),
        ]
    )


def main():
    app = App()
    app.add_endpoint("/", home)
    app.run()


if __name__ == "__main__":
    main()
