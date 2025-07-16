from slash.core import Elem
from slash.html import H2, Details, Div, P, Summary


def test_details() -> Elem:
    return Div(
        H2("Details"),
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
