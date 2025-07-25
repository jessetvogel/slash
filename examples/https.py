from __future__ import annotations

import ssl
from pathlib import Path

from slash import App
from slash.core import Elem
from slash.html import H1


def home() -> Elem:
    return H1("Hello secure world!").style({"text-align": "center"})


PATH_CERT = Path(__file__).resolve().parent.parent / "cert" / "cert.pem"
PATH_KEY = Path(__file__).resolve().parent.parent / "cert" / "key.pem"


def main():
    print(PATH_CERT)

    # Create SSL context
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(PATH_CERT, PATH_KEY)

    # Create and run application
    app = App()
    app.set_ssl_context(ssl_context)
    app.add_route("/", home)
    app.run()


if __name__ == "__main__":
    main()
