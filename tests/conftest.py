import pathlib
import importlib.util

import pytest

try:
    from bang_py.network.server import DEFAULT_TOKEN_KEY
except Exception:
    DEFAULT_TOKEN_KEY = None


@pytest.fixture(scope="session", autouse=True)
def generate_assets() -> None:
    """Generate placeholder assets only when required files are missing."""
    root = pathlib.Path(__file__).resolve().parents[1]
    assets = root / "bang_py" / "assets"
    char_dir = assets / "characters"
    audio_dir = assets / "audio"
    char_files = list(char_dir.glob("*.webp"))
    audio_files = list(audio_dir.glob("*.mp3")) + list(audio_dir.glob("*.ogg"))
    if char_files and audio_files:
        return
    try:
        from PySide6 import QtCore, QtGui, QtWidgets  # noqa: F401
    except Exception:
        return
    script_path = root / "scripts" / "generate_assets.py"
    spec = importlib.util.spec_from_file_location("generate_assets", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load generate_assets.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.main()


@pytest.fixture(autouse=True)
def _set_token_key(monkeypatch: pytest.MonkeyPatch) -> None:
    if DEFAULT_TOKEN_KEY is not None:
        monkeypatch.setenv("BANG_TOKEN_KEY", DEFAULT_TOKEN_KEY.decode())

