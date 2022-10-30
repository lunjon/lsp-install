from pathlib import Path

home = Path.home()
cache = home / ".cache"
local_bin = home / ".local" / "bin"


def color(*codes):
    cs = ";".join([str(c) for c in codes])
    return lambda s: f"\x1b[{cs}m{s}\x1b[0m"


red = color(31, 1)
green = color(32, 1)
