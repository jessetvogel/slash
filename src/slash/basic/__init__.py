"""This module contains the Slash basic components."""

from slash.basic._axes import Axes, Bar, Graph, Plot, Scatter
from slash.basic._checkbox import Checkbox
from slash.basic._data_table import DataTable
from slash.basic._download import Download
from slash.basic._markdown import Markdown
from slash.basic._pie import Pie
from slash.basic._progress import Progress
from slash.basic._radio import Radio
from slash.basic._svg import SVG, SVGElem
from slash.basic._tabs import Tabs
from slash.basic._upload import Upload

__all__: list[str] = [
    "Axes",
    "Bar",
    "Checkbox",
    "DataTable",
    "Download",
    "Graph",
    "Markdown",
    "Pie",
    "Plot",
    "Progress",
    "Radio",
    "Scatter",
    "SVG",
    "SVGElem",
    "Tabs",
    "Upload",
]
