import builtins
import importlib
import sys


def test_client_import_without_websockets(monkeypatch):
    """Client module should import even if websockets is missing."""
    original_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "websockets":
            raise ModuleNotFoundError
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    sys.modules.pop("bang_py.network.client", None)

    module = importlib.import_module("bang_py.network.client")
    assert module.websockets is None
