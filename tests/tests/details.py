from slash.core import Elem
from slash.html import Code, Details, Div, P, Summary


def test_details() -> Elem:
    return Div(
        P("This page tests the ", Code("Details"), " and ", Code("Summary"), " elements."),
        Details(
            Summary("Click to expand!"),
            P(
                "Non quos doloremque nihil magni molestiae distinctio. "
                "Corporis accusantium mollitia esse ut quis temporibus ducimus. "
                "Earum beatae repudiandae itaque quas quia. "
                "Est deserunt inventore at ut ipsam."
            ),
        ),
    )
