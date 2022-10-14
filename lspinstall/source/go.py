from lspinstall.util import execute, has_command

from .base import Source


class GoPackage(Source):
    def __init__(self, name: str, mod: str):
        super().__init__(name)
        self._mod = (
            mod  # The full module path including repo, e.g. golang.org/x/tools/gopls
        )

    def installed(self) -> bool:
        return has_command(self.name)

    def install(self):
        cmd = ["go", "install", f"{self._mod}@latest"]
        execute(cmd)

    def update(self):
        return self.install()
