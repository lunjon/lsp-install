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

FinalizeFunc = Callable[[Path], None]


class Archive(Source):
    """Target that install/updates from an archive file, e.g. zip file."""

    def __init__(
        self,
        name: str,
        destination: Path,
        url: str,
        archive_type: Literal["zip", "tar.gz", "gz"],
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

        if self._type == "zip":
            with zipfile.ZipFile(outfile) as z:
                z.extractall(dest)
        elif self._type == "gz":
            with gzip.open(outfile, "rb") as z:
                with open(dest, "wb") as f:
                    copyfileobj(z, f)
        else:
            tarball = tarfile.open(outfile)
            tarball.extractall(dest)
            tarball.close()

        if outfile.exists():
            os.unlink(outfile)
            logging.debug(f"Removed temporary file {outfile}")

        if self._finalize:
            logging.debug(f"Calling finalize function for {self.name}")
            self._finalize(dest)

    def update(self):
        self.install()
