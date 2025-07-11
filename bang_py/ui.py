import asyncio
import json
import random
import threading
import queue
import tkinter as tk
from tkinter import ttk, messagebox
import websockets

from .network.server import BangServer


class ServerThread(threading.Thread):
    """Run a :class:`BangServer` in a daemon thread for the UI."""

    def __init__(
        self,
        host: str,
        port: int,
        room_code: str,
        expansions: list[str],
        max_players: int,
    ) -> None:
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.room_code = room_code
        self.expansions = expansions
        self.max_players = max_players

    def run(self) -> None:
        asyncio.run(
            BangServer(
                self.host,
                self.port,
                self.room_code,
                self.expansions,
                self.max_players,
            ).start()
        )


class ClientThread(threading.Thread):
    """Manage a websocket client connection in a background thread."""
    def __init__(self, uri: str, room_code: str, name: str, msg_queue: queue.Queue):
        super().__init__(daemon=True)
        self.uri = uri
        self.room_code = room_code
        self.name = name
        self.msg_queue = msg_queue
        self.loop = asyncio.new_event_loop()
        self.websocket: websockets.WebSocketClientProtocol | None = None

    def run(self) -> None:
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._run())
        self.loop.close()

    async def _run(self) -> None:
        try:
            self.websocket = await websockets.connect(self.uri)
            await self.websocket.recv()  # prompt for code
            await self.websocket.send(self.room_code)
            response = await self.websocket.recv()
            if response != "Enter your name:":
                self.msg_queue.put(response)
                return
            await self.websocket.send(self.name)
            join_msg = await self.websocket.recv()
            self.msg_queue.put(join_msg)
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                except json.JSONDecodeError:
                    data = message
                self.msg_queue.put(str(data))
        except Exception as exc:
            self.msg_queue.put(f"Connection error: {exc}")
        finally:
            if self.websocket:
                await self.websocket.close()
                self.websocket = None

    def send_end_turn(self) -> None:
        if self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self._send("end_turn"), self.loop)

    async def _send(self, msg: str) -> None:
        if not self.websocket or self.websocket.closed:
            self.msg_queue.put("Send error: not connected")
            return
        try:
            await self.websocket.send(msg)
        except Exception as exc:
            self.msg_queue.put(f"Send error: {exc}")


class BangUI:
    """Tkinter interface used to host, join and play a Bang game.

    It starts server and client threads as needed and displays game updates in
    a simple window.
    """
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Bang!")
        self.msg_queue: queue.Queue[str] = queue.Queue()
        self.client: ClientThread | None = None
        self.server_thread: ServerThread | None = None
        # basic settings
        self.audio_sound = tk.BooleanVar(value=True)
        self.graphics_quality = tk.BooleanVar(value=True)
        self.exp_dodge_city = tk.BooleanVar(value=False)
        self.exp_high_noon = tk.BooleanVar(value=False)
        self.exp_fistful = tk.BooleanVar(value=False)
        self.keybindings: dict[str, str] = {"end_turn": "e"}
        self._bound_key = ""
        self.current_character = ""
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
        settings_btn = ttk.Button(self.root, text="Settings", command=self._settings_window)
        settings_btn.grid(row=2, column=0, columnspan=2, pady=5)

    def _settings_window(self) -> None:
        win = tk.Toplevel(self.root)
        win.title("Settings")

        ttk.Label(win, text="Audio").grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(win, text="Sound", variable=self.audio_sound).grid(row=0, column=1, sticky="w")

        ttk.Label(win, text="Graphics").grid(row=1, column=0, sticky="w")
        ttk.Checkbutton(win, text="High Quality", variable=self.graphics_quality).grid(row=1, column=1, sticky="w")

        ttk.Label(win, text="Expansions").grid(row=2, column=0, sticky="w")
        ttk.Checkbutton(win, text="Dodge City", variable=self.exp_dodge_city).grid(row=2, column=1, sticky="w")
        ttk.Checkbutton(win, text="High Noon", variable=self.exp_high_noon).grid(row=3, column=1, sticky="w")
        ttk.Checkbutton(win, text="Fistful of Cards", variable=self.exp_fistful).grid(row=4, column=1, sticky="w")
        ttk.Label(win, text="End Turn Key").grid(row=5, column=0, sticky="w")
        self.end_turn_key_var = tk.StringVar(value=self.keybindings.get("end_turn", "e"))
        ttk.Entry(win, textvariable=self.end_turn_key_var, width=5).grid(row=5, column=1, sticky="w")

        def save_and_close() -> None:
            self.keybindings["end_turn"] = self.end_turn_key_var.get().strip() or "e"
            win.destroy()

        ttk.Button(win, text="Save", command=save_and_close).grid(row=6, column=0, columnspan=2, pady=5)

    def _host_menu(self) -> None:
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter your name")
            return

        for widget in self.root.winfo_children():
            widget.destroy()

        self.port_var = tk.StringVar(value="8765")
        self.max_players_var = tk.StringVar(value="7")
        ttk.Label(self.root, text="Host Port:").grid(row=0, column=0, sticky="e")
        ttk.Entry(self.root, textvariable=self.port_var).grid(row=0, column=1)
        ttk.Label(self.root, text="Max Players:").grid(row=1, column=0, sticky="e")
        ttk.Entry(self.root, textvariable=self.max_players_var).grid(row=1, column=1)

        ttk.Label(self.root, text="Expansions:").grid(row=2, column=0, sticky="w")
        ttk.Checkbutton(self.root, text="Dodge City", variable=self.exp_dodge_city).grid(row=2, column=1, sticky="w")
        ttk.Checkbutton(self.root, text="High Noon", variable=self.exp_high_noon).grid(row=3, column=1, sticky="w")
        ttk.Checkbutton(self.root, text="Fistful of Cards", variable=self.exp_fistful).grid(row=4, column=1, sticky="w")

        start_btn = ttk.Button(self.root, text="Start", command=self._start_host)
        start_btn.grid(row=5, column=0, columnspan=2, pady=5)

    def _start_host(self) -> None:
        port = int(self.port_var.get())
        max_players = int(self.max_players_var.get())
        room_code = str(random.randint(1000, 9999))
        expansions = []
        if self.exp_dodge_city.get():
            expansions.append("dodge_city")
        if self.exp_high_noon.get():
            expansions.append("high_noon")
        if self.exp_fistful.get():
            expansions.append("fistful_of_cards")
        self.server_thread = ServerThread("", port, room_code, expansions, max_players)
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
        self._bind_keys()
        self.root.after(100, self._process_queue)

    def _build_game_view(self) -> None:
        for widget in self.root.winfo_children():
            widget.destroy()

        self.players_text = tk.Text(self.root, height=5, width=40, state="disabled")
        self.players_text.grid(row=0, column=0, columnspan=2)

        self.text = tk.Text(self.root, height=10, width=40, state="disabled")
        self.text.grid(row=1, column=0, columnspan=2)

        self.hand_frame = ttk.Frame(self.root)
        self.hand_frame.grid(row=2, column=0, columnspan=2, pady=5)

        end_btn = ttk.Button(self.root, text="End Turn", command=self._end_turn)
        end_btn.grid(row=3, column=0, columnspan=2, pady=5)

    def _process_queue(self) -> None:
        while not self.msg_queue.empty():
            msg = self.msg_queue.get()
            try:
                data = json.loads(msg)
            except json.JSONDecodeError:
                self._append_message(msg)
                continue

            if isinstance(data, dict) and "players" in data:
                self._update_players(data["players"])
                self.current_character = data.get("character", self.current_character)
                self._update_hand(data.get("hand", []))
                if "message" in data:
                    self._append_message(data["message"])
                    if any(k in data["message"].lower() for k in ["win", "eliminated"]):
                        messagebox.showinfo("Game Update", data["message"])
            elif isinstance(data, dict) and data.get("prompt") == "vera":
                self._prompt_vera(data.get("options", []))
            elif isinstance(data, dict) and data.get("prompt") == "general_store":
                self._prompt_general_store(data.get("cards", []))
            else:
                self._append_message(msg)
        if self.client and self.client.is_alive():
            self.root.after(100, self._process_queue)

    def _end_turn(self) -> None:
        if self.client:
            self.client.send_end_turn()

    def _play_card(self, index: int) -> None:
        if self.client and self.client.websocket:
            payload = json.dumps({"action": "play_card", "card_index": index})
            asyncio.run_coroutine_threadsafe(self.client.websocket.send(payload), self.client.loop)

    def _use_ability(self, ability: str, target: int | None = None, card_index: int | None = None) -> None:
        if self.client and self.client.websocket:
            payload = {"action": "use_ability", "ability": ability}
            if target is not None:
                payload["target"] = target
            if card_index is not None:
                payload["card_index"] = card_index
            asyncio.run_coroutine_threadsafe(
                self.client.websocket.send(json.dumps(payload)), self.client.loop
            )

    def _update_hand(self, cards: list[str]) -> None:
        for widget in self.hand_frame.winfo_children():
            widget.destroy()
        for i, card in enumerate(cards):
            btn = ttk.Button(self.hand_frame, text=card, command=lambda idx=i: self._play_card(idx))
            btn.grid(row=0, column=i, padx=2)
        if self.current_character in {
            "Sid Ketchum",
            "Chuck Wengam",
            "Doc Holyday",
            "Jesse Jones",
            "Kit Carlson",
            "Pedro Ramirez",
            "Jose Delgado",
            "Pat Brennan",
        }:
            ttk.Button(
                self.hand_frame,
                text="Use Ability",
                command=lambda: self._use_ability(
                    self.current_character.lower().replace(" ", "_")
                ),
            ).grid(row=1, column=0, columnspan=len(cards), pady=2)
        elif self.current_character == "Uncle Will":
            for i, _ in enumerate(cards):
                ttk.Button(
                    self.hand_frame,
                    text="Store",
                    command=lambda idx=i: self._use_ability("uncle_will", card_index=idx),
                ).grid(row=1, column=i, padx=2)

    def _update_players(self, players: list[dict]) -> None:
        lines = []
        for idx, p in enumerate(players):
            equip = ", ".join(p.get("equipment", []))
            line = f"{idx}: {p['name']} ({p['role']}) HP {p['health']}"
            if equip:
                line += f" [{equip}]"
            lines.append(line)
        text = "\n".join(lines)
        self.players_text.configure(state="normal")
        self.players_text.delete("1.0", tk.END)
        self.players_text.insert(tk.END, text)
        self.players_text.configure(state="disabled")

    def _append_message(self, msg: str) -> None:
        self.text.configure(state="normal")
        self.text.insert(tk.END, msg + "\n")
        self.text.configure(state="disabled")

    def _prompt_vera(self, options: list[dict]) -> None:
        win = tk.Toplevel(self.root)
        win.title("Vera Custer")
        ttk.Label(win, text="Choose ability to copy:").pack()

        for opt in options:
            btn = ttk.Button(
                win,
                text=opt.get("name", ""),
                command=lambda idx=opt.get("index"): (
                    self._use_ability("vera_custer", target=idx),
                    win.destroy(),
                ),
            )
            btn.pack(fill="x")

    def _prompt_general_store(self, cards: list[str]) -> None:
        win = tk.Toplevel(self.root)
        win.title("General Store")
        ttk.Label(win, text="Choose a card:").pack()

        for i, card in enumerate(cards):
            btn = ttk.Button(
                win,
                text=card,
                command=lambda idx=i: (
                    self._pick_general_store(idx),
                    win.destroy(),
                ),
            )
            btn.pack(fill="x")

    def _pick_general_store(self, index: int) -> None:
        if self.client and self.client.websocket:
            payload = json.dumps({"action": "general_store_pick", "index": index})
            asyncio.run_coroutine_threadsafe(
                self.client.websocket.send(payload), self.client.loop
            )

    def _bind_keys(self) -> None:
        if self._bound_key:
            self.root.unbind_all(f"<{self._bound_key}>")
        key = self.keybindings.get("end_turn", "e")
        self.root.bind_all(f"<{key}>", lambda _e: self._end_turn())
        self._bound_key = key

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    ui = BangUI()
    ui.run()


if __name__ == "__main__":
    main()

