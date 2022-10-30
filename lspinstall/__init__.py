from pathlib import Path


def _home():
    return Path.home()


def cache() -> Path:
    return _home() / ".cache"


def local_bin() -> Path:
    return _home() / ".local" / "bin"


def color(*codes):
    cs = ";".join([str(c) for c in codes])
    return lambda s: f"\x1b[{cs}m{s}\x1b[0m"


red = color(31, 1)
green = color(32, 1)
