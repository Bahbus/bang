import os
from pathlib import Path

from PySide6 import QtWidgets
import PySide6

app = QtWidgets.QApplication.instance()
if app is None:
    app = QtWidgets.QApplication([])

from bang_py.ui import main

if "QT_QPA_PLATFORM_PLUGIN_PATH" not in os.environ:
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(
        Path(PySide6.__file__).resolve().with_name("Qt") / "plugins"
    )

if __name__ == "__main__":
    main()
