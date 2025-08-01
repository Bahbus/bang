import pathlib
import importlib.util

import pytest


@pytest.fixture(scope="session", autouse=True)
def generate_assets():
    if importlib.util.find_spec("PySide6") is None:
        return
    root = pathlib.Path(__file__).resolve().parents[1]
    script_path = root / "scripts" / "generate_assets.py"
    spec = importlib.util.spec_from_file_location("generate_assets", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load generate_assets.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.main()

