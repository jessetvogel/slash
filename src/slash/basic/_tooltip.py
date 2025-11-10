from slash.core import Children, Elem, Session
from slash.html import Div
from slash.js import JSFunction

_JS_TOOLTIP_SETUP = JSFunction(
    ["id", "target_id"],
    """
const elem = document.getElementById(id);
const tip = elem.querySelector(".slash-tip");
const target = document.getElementById(target_id);

function show() {
    elem.style.display = null;
    const box = target.getBoundingClientRect();
    let c, dx, dy;
    if (c = elem.offsetParent) {
        const c_box = c.getBoundingClientRect();
        dx = -c_box.left;
        dy = -c_box.top;
    } else {
        dx = window.scrollX;
        dy = window.scrollY;
    }
    const top = box.top + dy - elem.offsetHeight - 8;
    const min_left = 4;
    const max_left = (c ? c.clientWidth : window.innerWidth) - elem.offsetWidth - 4;
    const left = Math.max(min_left, Math.min(max_left, box.left + (target.offsetWidth - elem.offsetWidth) / 2 + dx));
    elem.style.top  = `${top}px`;
    elem.style.left = `${left}px`;
    tip.style.left = `${box.left + target.offsetWidth / 2 - left - 4}px`;
}

function hide() { elem.style.display = "none"; }

target.addEventListener("mouseenter", show);
target.addEventListener("mouseleave", hide);
""",
)


class Tooltip(Elem):
    """Tooltip element."""

    def __init__(self, *children: Children, target: Elem) -> None:
        super().__init__("div", *children, Div().add_class("slash-tip"))
        self.add_class("slash-tooltip")
        self.style({"display": "none"})
        self._target = target
        self.onmount(self._setup)

    def _setup(self) -> None:
        Session.require().execute(_JS_TOOLTIP_SETUP, [self.id, self._target.id])
