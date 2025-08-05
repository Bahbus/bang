import importlib

from websockets.asyncio.client import connect as async_connect


def test_client_uses_asyncio_connect() -> None:
    module = importlib.import_module("bang_py.network.client")
    assert module.connect is async_connect
