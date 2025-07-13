(
    echo "\x1b[34mRunning \`ruff format .\` .. \x1b[0m" && \
    ruff format . && \
    echo "\n\x1b[34mRunning \`ruff check . --fix\` .. \x1b[0m" && \
    ruff check . --fix && \
    echo "\n\x1b[34mRunning \`mypy src\` .. \x1b[0m" && \
    mypy src
)