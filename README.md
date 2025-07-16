<img src="img/banner.png" style="height: 128px;"/>

Slash is a Python framework for creating web apps.

## 📦 Installation

Slash can be installed directly using `pip`.

```sh
pip install "slash @ git+https://github.com/jessetvogel/slash.git@main"
```

Alternatively, slash can be installed by adding the following dependency to your
`pyproject.toml` file.

```toml
[project]
dependencies = [
  "slash @ git+https://github.com/jessetvogel/slash.git@main"
]
```

## 📘 Example

The following script will create a page with the text 'Hello world'. Run the
script and go to [http://localhost:8080](http://localhost:8080) to see the
result.

```python
from slash import App
from slash.html import Span

def home():
    return Span("Hello world").style({"color": "red"})

def main():
    app = App()
    app.add_endpoint("/", home)
    app.run()

if __name__ == "__main__":
    main()
```

For more elaborate examples, take a look at the `examples` folder.
