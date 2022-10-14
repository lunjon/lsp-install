import logging
import subprocess
import sys
from argparse import ArgumentParser

import requests

from . import cache, green, local_bin, red
from .servers import lang_servers, lang_servers_dict


def handle_list(_):
    for s in lang_servers:
        print(s.status())


def handle_install(args):
    for name in args.server:
        if not name in lang_servers_dict:
            print(f"unknown server name: {name}")
            return

        server = lang_servers_dict[name]
        if server.installed():
            print(f"{server.name} already installed, use 'update'.")
            return

        print(f"Installing {green(server.name)} ...")
        server.install()
        print(f"Installed {green(server.name)}")


def handle_update(args):
    server = lang_servers_dict[args.server]
    if not server.installed():
        print(f"{server.name} is not installed, use 'install'.")
        return

    print(f"Updating {green(server.name)} ...")
    server.update()
    print(f"Updated {green(server.name)}")


def main():
    def global_flags(parser):
        parser.add_argument(
            "-v",
            help="Verbose output with level info",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "-vv",
            help="Verbose logging with level debug",
            action="store_true",
            default=False,
        )

    root = ArgumentParser()
    global_flags(root)
    subparser = root.add_subparsers(required=True)

    def add_subparser(name):
        parser = subparser.add_parser(name)
        global_flags(parser)
        return parser

    install_parser = add_subparser("install")
    install_parser.add_argument(
        "server",
        help="Name of language server to install",
        nargs="+",
    )
    install_parser.set_defaults(cb=handle_install)

    list_parser = add_subparser("list")
    list_parser.set_defaults(cb=handle_list)

    update_parser = add_subparser("update")
    update_parser.add_argument(
        "server",
        help="Name of language server to update",
        choices=lang_servers_dict.keys(),
    )
    update_parser.set_defaults(cb=handle_update)

    args = root.parse_args()
    logging.debug(f"User arguments: {args}")

    try:
        if not cache.exists():
            cache.mkdir()
        if not local_bin.exists():
            local_bin.mkdir()

        level = logging.CRITICAL
        if args.vv:
            level = logging.DEBUG
        elif args.v:
            level = logging.INFO
        logging.basicConfig(level=level, format="[%(levelname)s] %(message)s")

        args.cb(args)
    except subprocess.CalledProcessError as e:
        print(
            f"{red('error')}: '{' '.join(e.args)}' failed with exit status {e.returncode}:\n{e.stderr}"
        )
        sys.exit(1)
    except requests.RequestException as e:
        print(f"{red('request error')}: {e}")
        sys.exit(1)
