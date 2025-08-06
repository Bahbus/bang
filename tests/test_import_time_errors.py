import sys
from pathlib import Path
import pytest

def _make_bad_pyside6(tmp_path: Path, bad_module: str) -> None:
    pkg = tmp_path / "PySide6"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("")
    submodules = ["QtCore", "QtGui", "QtWidgets", "QtSvg", "QtMultimedia", "QtQuick"]
    for name in submodules:
        path = pkg / f"{name}.py"
        if name == bad_module:
            path.write_text("raise RuntimeError('boom')")
        else:
            path.write_text("")


def test_helpers_raises_on_misbehaving_pyside6(monkeypatch, tmp_path):
    _make_bad_pyside6(tmp_path, "QtSvg")
    monkeypatch.syspath_prepend(tmp_path)
    monkeypatch.delitem(sys.modules, "PySide6", raising=False)
    monkeypatch.delitem(sys.modules, "bang_py.helpers", raising=False)
    with pytest.raises(RuntimeError, match="boom"):
        import bang_py.helpers  # noqa: F401


def test_card_images_raises_on_misbehaving_qtmultimedia(monkeypatch, tmp_path):
    _make_bad_pyside6(tmp_path, "QtMultimedia")
    monkeypatch.syspath_prepend(tmp_path)
    monkeypatch.delitem(sys.modules, "PySide6", raising=False)
    monkeypatch.delitem(sys.modules, "bang_py.ui.components.card_images", raising=False)
    with pytest.raises(RuntimeError, match="boom"):
        import bang_py.ui.components.card_images  # noqa: F401
