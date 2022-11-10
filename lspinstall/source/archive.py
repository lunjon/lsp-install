import gzip
import logging
import os
import tarfile
import zipfile
from pathlib import Path
from shutil import copyfileobj, rmtree
from typing import Callable, Literal, Optional

import requests

from .base import Source
from lspinstall.util import make_executable
from lspinstall import cache, local_bin

FinalizeFunc = Callable[[Path], None]
ArchiveType = Literal["zip", "tar.gz", "gz"]


class _Archive(Source):
    """Target that install/updates from an archive file, e.g. zip file."""

    def __init__(
        self,
        name: str,
        destination: Path,
        url: str,
        archive_type: ArchiveType,
        finalize: Optional[FinalizeFunc] = None,
    ):
        super().__init__(name)
        self._dest = destination
        self._url = url
        self._type = archive_type
        self._finalize = finalize

    def installed(self) -> bool:
        return self._dest.exists()

    def install(self):
        dest = self._dest
        if dest.exists():
            logging.info(f"Destination {dest} already exists, removing")
            if dest.is_dir():
                rmtree(dest)
                dest.mkdir()
            else:
                os.remove(dest)

        res = requests.get(self._url)
        logging.info(f"GET {self._url} responded with status {res.status_code}")
        res.raise_for_status()

        outfile = Path(f"tmp.{self._type}")
        total_written = 0
        with open(outfile, "wb") as f:
            for ch in res.iter_content(1024):
                total_written += f.write(ch)
        logging.debug(f"Wrote {total_written} bytes to {outfile}")

        match self._type:
            case "zip":
                with zipfile.ZipFile(outfile) as z:
                    z.extractall(dest)
            case "gz":
                with gzip.open(outfile, "rb") as z:
                    with open(dest, "wb") as f:
                        copyfileobj(z, f)
            case "tar.gz":
                tarball = tarfile.open(outfile)
                tarball.extractall(dest)
                tarball.close()
            case _:
                raise Exception(f"unknown archive type: {self._type}")

        if outfile.exists():
            os.unlink(outfile)
            logging.debug(f"Removed temporary file {outfile}")

        if self._finalize:
            logging.debug(f"Calling finalize function for {self.name}")
            self._finalize(dest)

    def update(self):
        self.install()


def _create_bash_script(name: str, content: str):
    bin = local_bin() / name
    with open(bin, "w") as f:
        f.write("#!/usr/bin/env bash\n")
        f.write(content)
    make_executable(bin)


def _finalize_elixirls(dest: Path):
    shell_bin = dest / "language_server.sh"
    make_executable(shell_bin)
    make_executable(dest / "launch.sh")
    bin = local_bin() / "elixir-ls"
    with open(bin, "w") as f:
        f.write("#!/usr/bin/env bash\n")
        f.write('exec "')
        f.write(str(shell_bin))
        f.write('" "$@"')

    make_executable(shell_bin)
    make_executable(bin)
    make_executable(dest / "launch.sh")


def _finalize_sumneko(dest: Path):
    path = dest / "bin" / "lua-language-server"
    args = '"$@"'
    content = f"""exec {path.absolute()} {args}"""
    _create_bash_script("lua-language-server", content)


def _finalize_bicep(dest: Path):
    dll = dest / "Bicep.LangServer.dll"
    content = f"exec dotnet {dll.absolute()}"
    _create_bash_script("bicep-langserver", content)


def _finalize_omnisharp(dest: Path):
    script = dest / "run"
    make_executable(script)
    args = '"$@"'
    content = f"exec {script.absolute()} {args}"
    _create_bash_script("OmniSharp", content)


def _make_exec(ext: str):
    def f(dest: Path):
        make_executable(dest / ext)

    return f


_urls = {
    "sumneko": "https://github.com/sumneko/lua-language-server/releases/download/3.5.5/lua-language-server-3.5.5-linux-x64.tar.gz",
    "bicep": "https://github.com/Azure/bicep/releases/download/v0.8.9/bicep-langserver.zip",
    # TODO: use rustup and add as component (added as of rust 1.64)
    "rust-analyzer": "https://github.com/rust-analyzer/rust-analyzer/releases/latest/download/rust-analyzer-x86_64-unknown-linux-gnu.gz",
    "omnisharp": "https://github.com/OmniSharp/omnisharp-roslyn/releases/download/v1.38.2/omnisharp-linux-x64.zip",
    "elixirls": "https://github.com/elixir-lsp/elixir-ls/releases/latest/download/elixir-ls.zip",
}


sumneko = _Archive(
    "sumneko", cache() / "sumneko-lua", _urls["sumneko"], "tar.gz", _finalize_sumneko
)

bicep = _Archive(
    "bicep",
    cache() / "bicep-langserver",
    _urls["bicep"],
    "zip",
    finalize=_finalize_bicep,
)

rust_analuzer = _Archive(
    "rust-analyzer",
    local_bin() / "rust-analyzer",
    _urls["rust-analyzer"],
    "gz",
    finalize=make_executable,
)

omnisharp = _Archive(
    "omnisharp",
    cache() / "omnisharp",
    _urls["omnisharp"],
    "zip",
    finalize=_finalize_omnisharp,
)

elixirls = _Archive(
    "elixirls",
    cache() / "elixirls",
    _urls["elixirls"],
    "zip",
    finalize=_finalize_elixirls,
)
