import time

from slash.core import Elem
from slash.html import Div, P


def test_loading() -> Elem:
    time.sleep(2)
    return Div(P("The page should have been loading for 2 seconds before showing this text."))
