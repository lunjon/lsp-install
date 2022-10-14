import json
from typing import Optional

from lspinstall.util import execute

from .base import Source


class NPMRegistry:
    """Used to lookup packages installed with npm."""

    def __init__(self):
        self._registry = None

    def lookup(self, pkg: str) -> Optional[str]:
        if self._registry is None:
            res = execute(["npm", "list", "-g", "--json"])
            output = json.loads(res.stdout)
            self._registry = output["dependencies"]
        return self._registry.get(pkg)


class NPM(Source):
    _registry = NPMRegistry()

    def __init__(self, name: str, pkg: str = "", requires: list[str] = None):  # type: ignore
        super().__init__(name)
        self._pkg = name if pkg == "" else pkg
        self._requires = requires if requires else []

    def installed(self) -> bool:
        return self._registry.lookup(self._pkg) is not None

    def _cmd(self, cmd: str):
        cmds = ["npm", cmd, "-g", self._pkg]
        cmds.extend(self._requires)
        execute(cmds)

    def install(self):
        self._cmd("install")

    def update(self):
        self._cmd("update")
