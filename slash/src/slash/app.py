from slash.elem.elem import Elem
from slash.server import Server


class App:

    def __init__(self):
        self.pages = {}

    def add_page(self, endpoint: str, page: Elem):
        self.pages[endpoint] = page

    def run(self):
        print("test")
        server = Server("127.0.0.1", 8080)
        server.serve()
