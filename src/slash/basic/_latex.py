from typing import Self

from slash.core import Session
from slash.html import HTML
from slash.js import JSFunction


class LaTeX(HTML):
    """LaTeX element.

    Args:
        latex: String of LaTeX to be formatted as HTML.
        display: If true, math is rendered display style, otherwise inline math.
    """

    def __init__(self, latex: str, *, display: bool = False) -> None:
        super().__init__("")
        self._display = display
        self.set_latex(latex)
        self.onmount(self._add_script)

        if not display:
            self.style({"display": "inline-block"})

    def set_latex(self, latex) -> Self:
        if self._display:
            self.set_html(f"\[{latex}\]")
        else:
            self.set_html(f"\({latex}\)")
        return self

    def _add_script(self) -> None:
        IS_KATEX_LOADED = "Is KaTeX loaded?"
        session = Session.require()
        if session.get_data(IS_KATEX_LOADED) is not None:
            return

        session.execute(_JS_LOAD_KATEX, [])
        session.set_data(IS_KATEX_LOADED, "true")


# See: https://katex.org/docs/browser#starter-template

_JS_LOAD_KATEX = JSFunction(
    [],
    """
const l = document.createElement("link");
l.rel = "stylesheet",
l.href = "https://cdn.jsdelivr.net/npm/katex@0.16.22/dist/katex.min.css",
l.integrity = "sha384-5TcZemv2l/9On385z///+d7MSYlvIEw9FuZTIdZ14vJLqWphw7e7ZPuOiCHJcFCP",
l.crossOrigin = "anonymous",
document.head.appendChild(l);

new Promise((res, rej) => {
    const s = document.createElement("script");
    s.defer = true;
    s.src = "https://cdn.jsdelivr.net/npm/katex@0.16.22/dist/katex.min.js";
    s.integrity = "sha384-cMkvdD8LoxVzGF/RPUKAcvmm49FQ0oxwDF3BGKtDXcEc+T1b2N+teh/OJfpU0jr6";
    s.crossOrigin = "anonymous"
    s.onload = () => res(s);
    s.onerror = rej;
    document.head.appendChild(s);
}).then(() => {
    new Promise((res, rej) => {
        const s = document.createElement("script");
        s.defer = true;
        s.src = "https://cdn.jsdelivr.net/npm/katex@0.16.22/dist/contrib/auto-render.min.js";
        s.integrity = "sha384-hCXGrW6PitJEwbkoStFjeJxv+fSOOQKOPbJxSfM6G5sWZjAyWhXiTIIAmQqnlLlh";
        s.crossOrigin = "anonymous"
        s.onload = () => res(s);
        s.onerror = rej;
        document.head.appendChild(s);
    }).then(() => {
        renderMathInElement(document.body);
    });
});
""",
)
