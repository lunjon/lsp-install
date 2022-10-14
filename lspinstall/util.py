import logging
import os
import stat
import subprocess
from pathlib import Path
from shutil import which


def has_command(*cmds) -> bool:
    """Returns true if all commands exists."""
    return all(which(cmd) is not None for cmd in cmds)


def execute(cmd: list[str]) -> subprocess.CompletedProcess:
    """Runs cmd as a subprocess and returns the result."""
    logging.debug(f"Executing external process: {cmd}")
    result = subprocess.run(cmd, capture_output=True, encoding="utf-8")
    logging.debug(f"Got return code {result.returncode}")
    result.check_returncode()
    return result


def make_executable(dest: Path):
    st = os.stat(dest)
    os.chmod(dest, st.st_mode | stat.S_IEXEC)
    logging.debug(f"Made {dest} into an executable")


home = Path.home()
cache = home / ".cache"
local_bin = home / ".local" / "bin"
