import asyncio
import random
import threading
import queue
import tkinter as tk
from tkinter import ttk, messagebox
import websockets

from .network.server import BangServer


class ServerThread(threading.Thread):
    def __init__(self, host: str, port: int, room_code: str):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.room_code = room_code

    def run(self) -> None:
        asyncio.run(BangServer(self.host, self.port, self.room_code).start())


class ClientThread(threading.Thread):
    def __init__(self, uri: str, room_code: str, name: str, msg_queue: queue.Queue):
        super().__init__(daemon=True)
        self.uri = uri
        self.room_code = room_code
        self.name = name
        self.msg_queue = msg_queue
        self.loop = asyncio.new_event_loop()

    def run(self) -> None:
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._run())

    async def _run(self) -> None:
        try:
            async with websockets.connect(self.uri) as websocket:
                await websocket.recv()  # prompt for code
                await websocket.send(self.room_code)
                response = await websocket.recv()
                if response != "Enter your name:":
                    self.msg_queue.put(response)
                    return
                await websocket.send(self.name)
                join_msg = await websocket.recv()
                self.msg_queue.put(join_msg)
                async for message in websocket:
                    self.msg_queue.put(message)
        except Exception as exc:
            self.msg_queue.put(f"Connection error: {exc}")

    def send_end_turn(self) -> None:
        if self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self._send("end_turn"), self.loop)

    async def _send(self, msg: str) -> None:
        try:
            async with websockets.connect(self.uri) as websocket:
                await websocket.send(msg)
        except Exception as exc:
            self.msg_queue.put(f"Send error: {exc}")


class BangUI:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Bang!")
        self.msg_queue: queue.Queue[str] = queue.Queue()
        self.client: ClientThread | None = None
        self.server_thread: ServerThread | None = None
        self._build_start_menu()

    def _build_start_menu(self) -> None:
        for widget in self.root.winfo_children():
            widget.destroy()

        ttk.Label(self.root, text="Name:").grid(row=0, column=0, sticky="e")
        self.name_var = tk.StringVar()
        ttk.Entry(self.root, textvariable=self.name_var).grid(row=0, column=1)

        host_btn = ttk.Button(self.root, text="Host Game", command=self._host_menu)
        host_btn.grid(row=1, column=0, pady=5)
        join_btn = ttk.Button(self.root, text="Join Game", command=self._join_menu)
        join_btn.grid(row=1, column=1, pady=5)

    def _host_menu(self) -> None:
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter your name")
            return

        for widget in self.root.winfo_children():
            widget.destroy()

        self.port_var = tk.StringVar(value="8765")
        ttk.Label(self.root, text="Host Port:").grid(row=0, column=0, sticky="e")
        ttk.Entry(self.root, textvariable=self.port_var).grid(row=0, column=1)

        start_btn = ttk.Button(self.root, text="Start", command=self._start_host)
        start_btn.grid(row=1, column=0, columnspan=2, pady=5)

    def _start_host(self) -> None:
        port = int(self.port_var.get())
        room_code = str(random.randint(1000, 9999))
        self.server_thread = ServerThread("", port, room_code)
        self.server_thread.start()
        uri = f"ws://localhost:{port}"
        self._start_client(uri, room_code)
        messagebox.showinfo("Room Code", f"Give this code to friends: {room_code}")

    def _join_menu(self) -> None:
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter your name")
            return

        for widget in self.root.winfo_children():
            widget.destroy()

        self.addr_var = tk.StringVar(value="localhost")
        self.port_var = tk.StringVar(value="8765")
        self.code_var = tk.StringVar()

        ttk.Label(self.root, text="Host Address:").grid(row=0, column=0, sticky="e")
        ttk.Entry(self.root, textvariable=self.addr_var).grid(row=0, column=1)
        ttk.Label(self.root, text="Port:").grid(row=1, column=0, sticky="e")
        ttk.Entry(self.root, textvariable=self.port_var).grid(row=1, column=1)
        ttk.Label(self.root, text="Room Code:").grid(row=2, column=0, sticky="e")
        ttk.Entry(self.root, textvariable=self.code_var).grid(row=2, column=1)

        join_btn = ttk.Button(self.root, text="Join", command=self._start_join)
        join_btn.grid(row=3, column=0, columnspan=2, pady=5)

    def _start_join(self) -> None:
        addr = self.addr_var.get().strip()
        port = int(self.port_var.get())
        code = self.code_var.get().strip()
        uri = f"ws://{addr}:{port}"
        self._start_client(uri, code)

    def _start_client(self, uri: str, code: str) -> None:
        name = self.name_var.get().strip()
        self.client = ClientThread(uri, code, name, self.msg_queue)
        self.client.start()
        self._build_game_view()
        self.root.after(100, self._process_queue)

    def _build_game_view(self) -> None:
        for widget in self.root.winfo_children():
            widget.destroy()

        self.text = tk.Text(self.root, height=15, width=40, state="disabled")
        self.text.grid(row=0, column=0, columnspan=2)
        end_btn = ttk.Button(self.root, text="End Turn", command=self._end_turn)
        end_btn.grid(row=1, column=0, columnspan=2, pady=5)

    def _process_queue(self) -> None:
        while not self.msg_queue.empty():
            msg = self.msg_queue.get()
            self.text.configure(state="normal")
            self.text.insert(tk.END, msg + "\n")
            self.text.configure(state="disabled")
        if self.client and self.client.is_alive():
            self.root.after(100, self._process_queue)

    def _end_turn(self) -> None:
        if self.client:
            self.client.send_end_turn()

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    ui = BangUI()
    ui.run()


if __name__ == "__main__":
    main()

