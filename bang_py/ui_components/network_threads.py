from __future__ import annotations

"""Qt threads for running the Bang server and client in the background."""

import asyncio
import json
import logging

from typing import Any

from PySide6 import QtCore

try:  # Optional websockets import for test environments
    import websockets
    from websockets import WebSocketException
    WebSocketClientProtocol = websockets.WebSocketClientProtocol
except ModuleNotFoundError:  # pragma: no cover - handled in _run()
    websockets = None  # type: ignore[assignment]
    WebSocketException = Exception  # type: ignore[assignment]
    WebSocketClientProtocol = Any  # type: ignore[assignment]

from ..network.server import BangServer


class ServerThread(QtCore.QThread):
    """Run a :class:`BangServer` in a background thread."""

    def __init__(self, host: str, port: int, room_code: str,
                 expansions: list[str], max_players: int) -> None:
        super().__init__()
        self.host = host
        self.port = port
        self.room_code = room_code
        self.expansions = expansions
        self.max_players = max_players
        self.loop = asyncio.new_event_loop()
        self.server_task: asyncio.Task | None = None

    def run(self) -> None:  # type: ignore[override]
        asyncio.set_event_loop(self.loop)
        server = BangServer(self.host, self.port, self.room_code,
                            self.expansions, self.max_players)
        self.server_task = self.loop.create_task(server.start())
        try:
            self.loop.run_until_complete(self.server_task)
        except asyncio.CancelledError:
            logging.info("Server thread cancelled")
        finally:
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            self.loop.close()

    def stop(self) -> None:
        if self.server_task and not self.server_task.done():
            self.loop.call_soon_threadsafe(self.server_task.cancel)
        if self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)


class ClientThread(QtCore.QThread):
    """Manage a websocket client connection in a background thread."""

    message_received = QtCore.Signal(str)

    def __init__(self, uri: str, room_code: str, name: str) -> None:
        super().__init__()
        self.uri = uri
        self.room_code = room_code
        self.name = name
        self.loop = asyncio.new_event_loop()
        self.websocket: WebSocketClientProtocol | None = None

    def run(self) -> None:  # type: ignore[override]
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._run())
        self.loop.close()

    def stop(self) -> None:
        if self.websocket and not self.websocket.closed:
            fut = asyncio.run_coroutine_threadsafe(self.websocket.close(),
                                                   self.loop)
            try:
                fut.result(timeout=1)
            except (asyncio.TimeoutError, Exception) as exc:  # noqa: BLE001
                logging.exception("Failed to close websocket: %s", exc)
        if self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)

    async def _run(self) -> None:
        if websockets is None:
            msg = "websockets package is required for networking"
            logging.error(msg)
            self.message_received.emit(msg)
            return
        try:
            self.websocket = await websockets.connect(self.uri)
            await self.websocket.recv()
            await self.websocket.send(self.room_code)
            response = await self.websocket.recv()
            if response != "Enter your name:":
                self.message_received.emit(response)
                return
            await self.websocket.send(self.name)
            join_msg = await self.websocket.recv()
            self.message_received.emit(join_msg)
            async for message in self.websocket:
                self.message_received.emit(message)
        except (OSError, WebSocketException) as exc:
            logging.exception("Connection error: %s", exc)
            self.message_received.emit(f"Connection error: {exc}")
        finally:
            if self.websocket:
                await self.websocket.close()
                self.websocket = None

    def send_end_turn(self) -> None:
        if self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self._send("end_turn"), self.loop)

    def send_json(self, payload: dict) -> None:
        """Serialize ``payload`` and send it to the server."""
        if self.loop.is_running():
            msg = json.dumps(payload)
            asyncio.run_coroutine_threadsafe(self._send(msg), self.loop)

    async def _send(self, msg: str) -> None:
        if not self.websocket or self.websocket.closed:
            self.message_received.emit("Send error: not connected")
            return
        try:
            await self.websocket.send(msg)
        except WebSocketException as exc:
            logging.exception("Send error: %s", exc)
            self.message_received.emit(f"Send error: {exc}")
