from __future__ import annotations

from collections.abc import Callable

from slash import App
from slash.core import Elem, Session
from slash.html import H2, A, Button, Div, Li, P, Ul
from slash.layout import Column, Row
from tests.axes import test_axes
from tests.colors import test_colors
from tests.data_table import test_data
from tests.details import test_details
from tests.dialog import test_dialog
from tests.dom import test_dom
from tests.download import test_download
from tests.form import test_form
from tests.history import test_history
from tests.html import test_html
from tests.image import test_image
from tests.input import test_input
from tests.js import test_js
from tests.latex import test_latex
from tests.loading import test_loading
from tests.log import test_log
from tests.markdown import test_markdown
from tests.progress import test_progress
from tests.select import test_select
from tests.session import test_session
from tests.storage import test_storage
from tests.svg import test_svg
from tests.tabs import test_tabs
from tests.tinker import test_tinker
from tests.upload import test_upload

TESTS: dict[str, Callable[[], Elem]] = dict(
    sorted(
        {
            "colors": test_colors,
            "session": test_session,
            "data": test_data,
            "form": test_form,
            "upload": test_upload,
            "download": test_download,
            "storage": test_storage,
            "axes": test_axes,
            "image": test_image,
            "svg": test_svg,
            "markdown": test_markdown,
            "details": test_details,
            "dom": test_dom,
            "select": test_select,
            "dialog": test_dialog,
            "log": test_log,
            "input": test_input,
            "js": test_js,
            "progress": test_progress,
            "tabs": test_tabs,
            "html": test_html,
            "history": test_history,
            "latex": test_latex,
            "loading": test_loading,
            "tinker": test_tinker,
        }.items()
    )
)


def home() -> Elem:
    return Div(
        H2("Slash tests").style({"text-align": "center"}),
        P("Click on one of the links below to navigate to the corresponding test page."),
        Ul([Li(A(f"Test {test}", href=f"/test/{test}")) for test in TESTS]),
    ).style({"max-width": "640px", "margin": "0px auto", "padding": "8px"})


def wrap_test(test: str, method: Callable[[], Elem]) -> Callable[[], Elem]:
    # Button to previous and next tests
    tests = list(TESTS.keys())
    test_index = tests.index(test)
    prev_test = tests[test_index - 1] if test_index > 0 else None
    next_test = tests[test_index + 1] if test_index < len(tests) - 1 else None

    def page() -> Elem:
        return Column(
            H2(f"Slash test - {test}").style({"text-align": "center"}),
            Row(
                Button("Previous test", disabled=prev_test is None).onclick(
                    lambda: Session.require().set_location(f"/test/{prev_test}")
                ),
                Button("Next test", disabled=next_test is None).onclick(
                    lambda: Session.require().set_location(f"/test/{next_test}")
                ),
            ).style({"gap": "16px", "justify-content": "center"}),
            method(),
        ).style({"max-width": "640px", "margin": "0px auto", "padding": "8px"})

    return page


def main():
    app = App()
    app.add_route("/", home)
    for test, method in TESTS.items():
        app.add_route(f"/test/{test}", wrap_test(test, method))
    app.run()


if __name__ == "__main__":
    main()
