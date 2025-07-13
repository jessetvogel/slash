"""Slash basic components."""

from slash.basic.checkbox import Checkbox
from slash.basic.data import Data
from slash.basic.figure import Figure
from slash.basic.markdown import Markdown
from slash.basic.pie import Pie
from slash.basic.progress import Progress
from slash.basic.radio import Radio
from slash.basic.svg import SVG
from slash.basic.table import Table
from slash.basic.tabs import Tabs

__all__: list[str] = [
    "Figure",
    "Markdown",
    "Progress",
    "Table",
    "Tabs",
    "SVG",
    "Pie",
    "Checkbox",
    "Radio",
    "Data",
]
