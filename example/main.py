from __future__ import annotations

from slash import App
from slash.core import Elem
from slash.html import (
    H1,
    Div,
)

from tests.pre import test_pre
from tests.table import test_table
from tests.svg import test_svg
from tests.image import test_image
from tests.colors import test_colors
from tests.figure import test_figure
from tests.dom import test_dom
from tests.progress import test_progress
from tests.select import test_select
from tests.tabs import test_tabs
from tests.dialog import test_dialog
from tests.js import test_js
from tests.input import test_input
from tests.log import test_log
from tests.markdown import test_markdown
from tests.form import test_form
from tests.data import test_data


def home() -> Elem:
    return Div(
        H1("Slash tests").style({"text-align": "center"}),
        test_colors(),
        test_data(),
        test_form(),
        test_figure(),
        test_image(),
        test_svg(),
        test_markdown(),
        test_dom(),
        test_select(),
        test_dialog(),
        test_log(),
        test_input(),
        test_js(),
        test_progress(),
        test_tabs(),
        test_table(),
        test_pre(),
    ).style({"max-width": "640px", "margin": "0px auto"})


def main():
    app = App()
    app.add_endpoint("/", home)
    app.run()


if __name__ == "__main__":
    main()
