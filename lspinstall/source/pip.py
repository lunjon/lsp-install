from lspinstall.util import execute, has_command

from .base import Source


class PythonPip(Source):
    def __init__(self, name: str, command_name: str, pkg: str):
        super().__init__(name)
        self._command_name = command_name
        self._pkg = pkg

    def installed(self) -> bool:
        return has_command(self._command_name)

    def _cmd(self, upgrade: bool = False):
        cmds = ["python", "-m", "pip", "install"]
        if upgrade:
            cmds.append("--upgrade")
        cmds.append(self._pkg)
        execute(cmds)

    def install(self):
        self._cmd()

    def update(self):
        self._cmd(True)
