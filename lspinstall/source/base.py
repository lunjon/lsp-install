from abc import ABC, abstractmethod

from lspinstall import green, red


class Source(ABC):
    """ABC for types representing a language server, e.g. gopls."""

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def status(self):
        st = green("installed") if self.installed() else red("not installed")
        return f"{self.name} is {st}"

    @abstractmethod
    def installed(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def install(self):
        raise NotImplementedError

    @abstractmethod
    def update(self):
        raise NotImplementedError
