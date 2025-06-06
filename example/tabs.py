from __future__ import annotations

from slash.app import App
from slash.core import Elem
from slash.tabs import Tabs


def home() -> Elem:
    return Tabs(
        ["Tab 1", "Tab 2", "Tab 3"],
    )


def main():
    app = App()
    app.add_endpoint("/", home)
    app.run()


if __name__ == "__main__":
    main()
