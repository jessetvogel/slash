from __future__ import annotations

from tests.axes import test_axes
from tests.colors import test_colors
from tests.data_table import test_data
from tests.dialog import test_dialog
from tests.dom import test_dom
from tests.download import test_download
from tests.form import test_form
from tests.image import test_image
from tests.input import test_input
from tests.js import test_js
from tests.log import test_log
from tests.markdown import test_markdown
from tests.pre import test_pre
from tests.progress import test_progress
from tests.select import test_select
from tests.storage import test_storage
from tests.svg import test_svg
from tests.tabs import test_tabs
from tests.upload import test_upload

from slash import App
from slash.core import Elem
from slash.html import H1, Div


def home() -> Elem:
    return Div(
        H1("Slash tests").style({"text-align": "center"}),
        test_colors(),
        test_data(),
        test_form(),
        test_upload(),
        test_download(),
        test_storage(),
        test_axes(),
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
        test_pre(),
    ).style({"max-width": "640px", "margin": "0px auto"})


def main():
    app = App()
    app.add_endpoint("/", home)
    app.run()


if __name__ == "__main__":
    main()
