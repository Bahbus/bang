"""Entry script for bundling the Bang app with PyInstaller.

Ensures card handler modules and Qt plugins are included.
"""

import os
from pathlib import Path

from PySide6 import QtWidgets
import PySide6

app = QtWidgets.QApplication.instance()
if app is None:
    app = QtWidgets.QApplication([])

from bang_py.ui import main  # noqa: E402
from importlib import import_module  # noqa: E402
from bang_py.card_handlers import MODULE_REGISTRY  # noqa: E402

# Ensure card handler submodules are bundled by PyInstaller
for path in MODULE_REGISTRY.values():
    import_module(path)

if "QT_QPA_PLATFORM_PLUGIN_PATH" not in os.environ:
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(
        Path(PySide6.__file__).resolve().with_name("Qt") / "plugins"
    )

if __name__ == "__main__":
    main()
