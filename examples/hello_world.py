from slash import App
from slash.core import Elem
from slash.html import H1


def home() -> Elem:
    return H1("Hello world!").style({"text-align": "center"})


if __name__ == "__main__":
    # Create and run application
    app = App()
    app.add_route("/", home)
    app.run()
