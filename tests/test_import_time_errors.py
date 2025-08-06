import sys
from pathlib import Path
import types

import pytest

_SUBMODULES = [
    "QtCore",
    "QtGui",
    "QtWidgets",
    "QtSvg",
    "QtMultimedia",
    "QtQuick",
]


def _make_bad_pyside6(tmp_path: Path, bad_module: str) -> list[str]:
    pkg = tmp_path / "PySide6"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("")
    modules = ["PySide6"]
    for name in _SUBMODULES:
        modules.append(f"PySide6.{name}")
        path = pkg / f"{name}.py"
        if name == bad_module:
            path.write_text("raise RuntimeError('boom')")
        else:
            path.write_text("")
    return modules


def _cleanup(*modules: str) -> None:
    for mod in modules:
        sys.modules.pop(mod, None)


def test_helpers_raises_on_misbehaving_pyside6(monkeypatch, tmp_path):
    mods = _make_bad_pyside6(tmp_path, "QtSvg")
    monkeypatch.syspath_prepend(tmp_path)
    _cleanup(*mods, "bang_py.helpers")
    with pytest.raises(RuntimeError, match="boom"):
        import bang_py.helpers  # noqa: F401
    _cleanup(*mods, "bang_py.helpers")


def test_card_images_raises_on_misbehaving_qtmultimedia(monkeypatch, tmp_path):
    mods = _make_bad_pyside6(tmp_path, "QtMultimedia")
    monkeypatch.syspath_prepend(tmp_path)
    _cleanup(*mods, "bang_py.ui", "bang_py.ui.components", "bang_py.ui.components.card_images")
    ui_pkg = types.ModuleType("bang_py.ui")
    ui_pkg.__path__ = [str(Path(__file__).resolve().parents[1] / "bang_py" / "ui")]
    sys.modules["bang_py.ui"] = ui_pkg
    comp_pkg = types.ModuleType("bang_py.ui.components")
    comp_pkg.__path__ = [str(Path(__file__).resolve().parents[1] / "bang_py" / "ui" / "components")]
    sys.modules["bang_py.ui.components"] = comp_pkg
    with pytest.raises(RuntimeError, match="boom"):
        import bang_py.ui.components.card_images  # noqa: F401
    _cleanup(*mods, "bang_py.ui", "bang_py.ui.components", "bang_py.ui.components.card_images")
