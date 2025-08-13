from slash.basic import LaTeX
from slash.core import Elem
from slash.html import Code, P
from slash.layout import Column


def test_latex() -> Elem:
    return Column(
        P(
            "This page tests the ",
            Code("LaTeX"),
            " element.",
        ),
        P("The Pythagorean theorem ", LaTeX("a^2 + b^2 = c^2"), " should be rendered inline."),
        P(
            "The following equation should be rendered block-style.",
            LaTeX("f(x) = \\int_{0}^{2 \\pi} \\sin(x + y) \\cos(y) dy", display=True),
        ),
    )
