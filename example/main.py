from slash.app import App
from slash.elem.elem import Elem


def main():
    app = App()
    app.add_page("/", Elem("Hello worlD!"))
    app.run()


if __name__ == "__main__":
    main()
