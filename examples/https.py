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


if __name__ == "__main__":
    # Check if certificate files exist
    if not PATH_CERT.exists() or not PATH_KEY.exists():
        print(f"Make sure that certificate files {PATH_CERT} and {PATH_KEY} exist.")
        exit(0)

    # Create SSL context
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(PATH_CERT, PATH_KEY)

    # Create and run application
    app = App(ssl_context=ssl_context)
    app.add_route("/", home)
    app.run()
