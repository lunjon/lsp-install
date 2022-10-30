from pathlib import Path

from . import cache, local_bin
from .source import NPM, Archive, GoPackage, PythonPip
from .util import make_executable

urls = {
    "sumneko": "https://github.com/sumneko/lua-language-server/releases/download/3.5.5/lua-language-server-3.5.5-linux-x64.tar.gz",
    "bicep": "https://github.com/Azure/bicep/releases/download/v0.8.9/bicep-langserver.zip",
    # TODO: use rustup and add as component (added as of rust 1.64)
    "rust-analyzer": "https://github.com/rust-analyzer/rust-analyzer/releases/latest/download/rust-analyzer-x86_64-unknown-linux-gnu.gz",
    "omnisharp": "https://github.com/OmniSharp/omnisharp-roslyn/releases/download/v1.38.2/omnisharp-linux-x64.zip",
    "elixirls": "https://github.com/elixir-lsp/elixir-ls/releases/latest/download/elixir-ls.zip",
}


def _finalize_elixirls(dest: Path):
    shell_bin = dest / "language_server.sh"
    make_executable(shell_bin)
    make_executable(dest / "launch.sh")
    bin = local_bin / "elixir-ls"
    with open(bin, "w") as f:
        f.write("#!/usr/bin/env bash\n")
        f.write('exec "')
        f.write(str(shell_bin))
        f.write('" "$@"')

    make_executable(shell_bin)
    make_executable(bin)
    make_executable(dest / "launch.sh")


def _finalize_sumneko(dest: Path):
    bin = local_bin / "lua-language-server"
    with open(bin, "w") as f:
        f.write("#!/bin/bash\n")
        f.write('exec "')
        f.write(str(dest / "bin" / "lua-language-server"))
        f.write('" "$@"')
    make_executable(bin)


def _finalize_bicep(dest: Path):
    bin = local_bin / "bicep-langserver"
    dll = dest / "Bicep.LangServer.dll"
    with open(bin, "w") as f:
        f.write("#!/bin/bash\n")
        f.write("exec dotnet ")
        f.write(str(dll))
    make_executable(bin)


def _make_exec(ext: str):
    def f(dest: Path):
        make_executable(dest / ext)

    return f


lang_servers = [
    PythonPip("pylsp", "pylsp", "python-lsp-server[all]"),
    GoPackage("gopls", "golang.org/x/tools/gopls"),
    Archive(
        "sumneko", cache / "sumneko-lua", urls["sumneko"], "tar.gz", _finalize_sumneko
    ),
    Archive(
        "bicep",
        cache / "bicep-langserver",
        urls["bicep"],
        "zip",
        finalize=_finalize_bicep,
    ),
    Archive(
        "rust-analyzer",
        local_bin / "rust-analyzer",
        urls["rust-analyzer"],
        "gz",
        finalize=make_executable,
    ),
    Archive(
        "omnisharp", cache / "omnisharp", urls["omnisharp"], "zip", _make_exec("run")
    ),
    Archive(
        "elixirls",
        cache / "elixirls",
        urls["elixirls"],
        "zip",
        finalize=_finalize_elixirls,
    ),
    NPM("pyright"),
    NPM("tsserver", "typescript-language-server", requires=["typescript"]),
    NPM(
        "vscode-langservers-extracted",
    ),
    NPM("bashls", "bash-language-server"),
    NPM("yamlls", "yaml-language-server"),
    NPM("graphql-lsp", "graphql-language-service-cli"),
    NPM("awk_ls", "awk-language-server"),
]

lang_servers_dict = {s.name: s for s in lang_servers}
