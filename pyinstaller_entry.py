import os
from pathlib import Path

import PySide6
from bang_py.ui import main

if "QT_QPA_PLATFORM_PLUGIN_PATH" not in os.environ:
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(
        Path(PySide6.__file__).resolve().with_name("Qt") / "plugins"
    )

if __name__ == "__main__":
    main()
