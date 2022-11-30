all: check fmt test

test:
    python -m pytest lspinstall

fmt:
    black lspinstall
    isort lspinstall

pip-compile:
    pip-compile -o requirements.txt pyproject.toml
    pip-compile --extra dev -o dev-requirements.txt pyproject.toml

check:
    flake8 ./lspinstall