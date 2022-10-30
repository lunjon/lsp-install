from .servers import sumneko
from pathlib import Path
import pytest


@pytest.fixture(autouse=True)
def conf_path(monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory):
    def mock_home():
        return tmp_path / "home"

    monkeypatch.setattr(Path, "home", mock_home)
