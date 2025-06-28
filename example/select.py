from __future__ import annotations

from slash import App
from slash.core import Elem
from slash.html import H1, Select, Span
from slash.layout import Column


def update_span(span: Span, text: str) -> None:
    span.text = f"You selected: {text}"


def home() -> Elem:
    return Column(
        [
            H1("Select demo"),
            select := Select(
                [
                    "Woodpecker",
                    "Pigeon",
                    "Peacock",
                    "Rooster",
                    "Vulture",
                    "Swallow",
                    "Seagull",
                    "Quail",
                    "Duck",
                    "Pelican",
                    "Magpie",
                    "Parrot",
                    "Turkey",
                    "Crane",
                    "Kingfisher",
                    "Hummingbird",
                    "Sparrow",
                    "Cormorant",
                    "Ostrich",
                    "Crow",
                    "Raven",
                    "Dove",
                    "Hen",
                    "Nightingale",
                    "Eagle",
                    "Swan",
                    "Penguin",
                    "Flamingo",
                    "Goose",
                    "Cuckoo",
                    "Owl",
                    "Hawk",
                    "Partridge",
                    "Goldfinch",
                    "Robin",
                    "Finch",
                    "Frigatebird",
                    "Sandpiper",
                    "Stork",
                    "Ibis",
                    "Hornbill",
                    "Bulbul",
                    "Skylark",
                    "Canary",
                    "Wagtail",
                    "Starling",
                    "Macaw",
                    "Cockatoo",
                    "Heron",
                    "Toucan",
                    "Jay",
                    "Mynah",
                    "Cardinal",
                    "Chickadee",
                    "Junco",
                    "Bluebird",
                    "Swift",
                    "Gull",
                    "Lovebird",
                    "Spoonbill",
                    "Kiwi",
                    "Avocet",
                    "Wren",
                    "Mockingbird",
                    "Pheasant",
                    "Hoopoe",
                    "Kite",
                    "Peahen",
                    "Falcon",
                    "Mallard",
                    "Bald eagle",
                    "Tern",
                    "Night hawk",
                    "Crossbill",
                    "Lapwing",
                    "Puffin",
                    "Koyal",
                    "Bullfinch",
                    "Emu",
                    "Condor",
                ]
            ).onchange(
                lambda _: update_span(span, select.value),
            ),
            span := Span().style({"padding": "8px"}),
        ]
    ).style({"width": "512px", "align-items": "center", "margin": "0px auto"})


def main():
    app = App()
    app.add_endpoint("/", home)
    app.run()


if __name__ == "__main__":
    main()
