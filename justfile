all: fmt test

test:
    python -m pytest lspinstall

fmt:
    python -m black lspinstall
    python -m isort lspinstall

pip-compile:
    pip-compile -o requirements.txt pyproject.toml
    pip-compile --extra dev -o dev-requirements.txt pyproject.toml

install:
    python -m pip install --upgrade .
