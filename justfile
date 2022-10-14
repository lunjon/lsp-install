fmt:
    python -m black lspinstall
    python -m isort lspinstall

setup:
    python -m venv .venv && \
        . .venv/bin/activate && \
        python -m pip install -r requirements-dev.txt

install:
    python -m pip install --upgrade .
