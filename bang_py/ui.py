import asyncio
import json
import random
import threading
import queue
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable
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
        self.loop = asyncio.new_event_loop()
        self.server_task: asyncio.Task | None = None

    def run(self) -> None:
        asyncio.set_event_loop(self.loop)
        server = BangServer(
            self.host,
            self.port,
            self.room_code,
            self.expansions,
            self.max_players,
        )
        self.server_task = self.loop.create_task(server.start())
        try:
            self.loop.run_until_complete(self.server_task)
        except asyncio.CancelledError:
            pass
        finally:
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            self.loop.close()

    def stop(self) -> None:
        """Request the server loop shut down."""
        if self.server_task and not self.server_task.done():
            self.loop.call_soon_threadsafe(self.server_task.cancel)
        if self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)


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

    def stop(self) -> None:
        """Close the websocket and stop the event loop."""
        if self.websocket and not self.websocket.closed:
            fut = asyncio.run_coroutine_threadsafe(self.websocket.close(), self.loop)
            try:
                fut.result(timeout=1)
            except Exception:
                pass
        if self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)

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
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
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
        self.auto_miss_var = tk.BooleanVar(value=True)
        self.hand_names: list[str] = []
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
        cb_sound = ttk.Checkbutton(win, text="Sound", variable=self.audio_sound)
        cb_sound.grid(row=0, column=1, sticky="w")

        ttk.Label(win, text="Graphics").grid(row=1, column=0, sticky="w")
        cb_quality = ttk.Checkbutton(win, text="High Quality", variable=self.graphics_quality)
        cb_quality.grid(row=1, column=1, sticky="w")

        ttk.Label(win, text="Expansions").grid(row=2, column=0, sticky="w")
        cb_dodge = ttk.Checkbutton(win, text="Dodge City", variable=self.exp_dodge_city)
        cb_dodge.grid(row=2, column=1, sticky="w")
        cb_noon = ttk.Checkbutton(win, text="High Noon", variable=self.exp_high_noon)
        cb_noon.grid(row=3, column=1, sticky="w")
        cb_fistful = ttk.Checkbutton(win, text="Fistful of Cards", variable=self.exp_fistful)
        cb_fistful.grid(row=4, column=1, sticky="w")
        ttk.Label(win, text="End Turn Key").grid(row=5, column=0, sticky="w")
        self.end_turn_key_var = tk.StringVar(value=self.keybindings.get("end_turn", "e"))
        entry_key = ttk.Entry(win, textvariable=self.end_turn_key_var, width=5)
        entry_key.grid(row=5, column=1, sticky="w")

        def save_and_close() -> None:
            self.keybindings["end_turn"] = self.end_turn_key_var.get().strip() or "e"
            win.destroy()

        btn_save = ttk.Button(win, text="Save", command=save_and_close)
        btn_save.grid(row=6, column=0, columnspan=2, pady=5)

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
        cb_dodge = ttk.Checkbutton(self.root, text="Dodge City", variable=self.exp_dodge_city)
        cb_dodge.grid(row=2, column=1, sticky="w")
        cb_noon = ttk.Checkbutton(self.root, text="High Noon", variable=self.exp_high_noon)
        cb_noon.grid(row=3, column=1, sticky="w")
        cb_fistful = ttk.Checkbutton(self.root, text="Fistful of Cards", variable=self.exp_fistful)
        cb_fistful.grid(row=4, column=1, sticky="w")

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

        self.event_var = tk.StringVar(value="")
        self.event_label = ttk.Label(self.root, textvariable=self.event_var)
        self.event_label.grid(row=1, column=0, columnspan=2)

        self.text = tk.Text(self.root, height=10, width=40, state="disabled")
        self.text.grid(row=2, column=0, columnspan=2)

        self.hand_frame = ttk.Frame(self.root)
        self.hand_frame.grid(row=3, column=0, columnspan=2, pady=5)

        end_btn = ttk.Button(self.root, text="End Turn", command=self._end_turn)
        end_btn.grid(row=4, column=0, columnspan=2, pady=5)

        ttk.Checkbutton(
            self.root,
            text="Auto Miss",
            variable=self.auto_miss_var,
            command=self._send_auto_miss,
        ).grid(row=5, column=0, columnspan=2)

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
                self.event_var.set(data.get("event", ""))
                if "message" in data:
                    self._append_message(data["message"])
                    if any(k in data["message"].lower() for k in ["win", "eliminated"]):
                        messagebox.showinfo("Game Update", data["message"])
            elif isinstance(data, dict) and data.get("prompt") == "vera":
                self._prompt_vera(data.get("options", []))
            elif isinstance(data, dict) and data.get("prompt") == "general_store":
                self._prompt_general_store(data.get("cards", []))
            elif isinstance(data, dict) and data.get("prompt") == "jesse_jones":
                self._prompt_jesse_jones(data.get("targets", []))
            elif isinstance(data, dict) and data.get("prompt") == "kit_carlson":
                self._prompt_kit_carlson(data.get("cards", []))
            elif isinstance(data, dict) and data.get("prompt") == "pedro_ramirez":
                self._prompt_pedro_ramirez()
            elif isinstance(data, dict) and data.get("prompt") == "jose_delgado":
                self._prompt_jose_delgado(data.get("equipment", []))
            elif isinstance(data, dict) and data.get("prompt") == "pat_brennan":
                self._prompt_pat_brennan(data.get("targets", []))
            elif isinstance(data, dict) and data.get("prompt") == "lucky_duke":
                self._prompt_lucky_duke(data.get("cards", []))
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

    def _send_auto_miss(self) -> None:
        if self.client and self.client.websocket:
            payload = json.dumps({
                "action": "set_auto_miss",
                "enabled": self.auto_miss_var.get(),
            })
            asyncio.run_coroutine_threadsafe(
                self.client.websocket.send(payload), self.client.loop
            )

    def _use_ability(
        self,
        ability: str,
        target: int | None = None,
        card_index: int | None = None,
        card: str | None = None,
        indices: list[int] | None = None,
    ) -> None:
        if self.client and self.client.websocket:
            payload = {"action": "use_ability", "ability": ability}
            if target is not None:
                if ability == "jose_delgado":
                    payload["equipment"] = target
                else:
                    payload["target"] = target
            if card_index is not None:
                if ability == "kit_carlson":
                    payload["discard"] = card_index
                elif ability == "pedro_ramirez":
                    payload["use_discard"] = bool(card_index)
                else:
                    payload["card_index"] = card_index
            if card is not None:
                payload["card"] = card
            if indices is not None:
                payload["indices"] = indices
            asyncio.run_coroutine_threadsafe(
                self.client.websocket.send(json.dumps(payload)), self.client.loop
            )

    def _update_hand(self, cards: list[str]) -> None:
        for widget in self.hand_frame.winfo_children():
            widget.destroy()
        self.hand_names = cards
        def _make_play_handler(idx: int) -> Callable[[], None]:
            def _handler() -> None:
                self._play_card(idx)
            return _handler

        for i, card in enumerate(cards):
            btn = ttk.Button(
                self.hand_frame,
                text=card,
                command=_make_play_handler(i),
            )
            btn.grid(row=0, column=i, padx=2)
        if self.current_character == "Sid Ketchum":
            ttk.Button(
                self.hand_frame,
                text="Use Ability",
                command=self._prompt_sid_ketchum,
            ).grid(row=1, column=0, columnspan=len(cards), pady=2)
        elif self.current_character == "Doc Holyday":
            ttk.Button(
                self.hand_frame,
                text="Use Ability",
                command=self._prompt_doc_holyday,
            ).grid(row=1, column=0, columnspan=len(cards), pady=2)
        elif self.current_character in {
            "Chuck Wengam",
            "Jesse Jones",
            "Kit Carlson",
            "Pedro Ramirez",
            "Jose Delgado",
            "Pat Brennan",
            "Lucky Duke",
        }:
            def _use_current_ability() -> None:
                self._use_ability(self.current_character.lower().replace(" ", "_"))

            ttk.Button(
                self.hand_frame,
                text="Use Ability",
                command=_use_current_ability,
            ).grid(row=1, column=0, columnspan=len(cards), pady=2)
        elif self.current_character == "Uncle Will":
            def _make_store_handler(idx: int) -> Callable[[], None]:
                def _handler() -> None:
                    self._use_ability("uncle_will", card_index=idx)
                return _handler

            for i, _ in enumerate(cards):
                ttk.Button(
                    self.hand_frame,
                    text="Store",
                    command=_make_store_handler(i),
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
        """Ask Vera Custer which ability to copy."""
        win = tk.Toplevel(self.root)
        win.title("Vera Custer")
        ttk.Label(win, text="Choose ability to copy:").pack()

        def _make_handler(idx: int) -> Callable[[], None]:
            def _handler() -> None:
                self._use_ability("vera_custer", target=idx)
                win.destroy()

            return _handler

        for opt in options:
            btn = ttk.Button(
                win,
                text=opt.get("name", ""),
                command=_make_handler(opt.get("index")),
            )
            btn.pack(fill="x")

    def _prompt_general_store(self, cards: list[str]) -> None:
        """Prompt players to pick a card from the general store."""
        win = tk.Toplevel(self.root)
        win.title("General Store")
        ttk.Label(win, text="Choose a card:").pack()

        def _make_handler(idx: int) -> Callable[[], None]:
            def _handler() -> None:
                self._pick_general_store(idx)
                win.destroy()

            return _handler

        for i, card in enumerate(cards):
            btn = ttk.Button(
                win,
                text=card,
                command=_make_handler(i),
            )
            btn.pack(fill="x")

    def _prompt_jesse_jones(self, targets: list[dict]) -> None:
        """Prompt Jesse Jones to steal a card from another player."""
        win = tk.Toplevel(self.root)
        win.title("Jesse Jones")
        ttk.Label(win, text="Draw first card from:").pack()
        def _pick(idx: int) -> None:
            """Use Jesse Jones on the selected target."""
            self._use_ability("jesse_jones", target=idx)
            win.destroy()

        def _skip() -> None:
            """Skip using Jesse Jones's ability."""
            self._use_ability("jesse_jones")
            win.destroy()

        def _make_handler(idx: int) -> Callable[[], None]:
            def _handler() -> None:
                _pick(idx)
            return _handler

        for t in targets:
            ttk.Button(
                win,
                text=t.get("name", ""),
                command=_make_handler(t.get("index")),
            ).pack(fill="x")

        ttk.Button(win, text="Skip", command=_skip).pack(fill="x")

    def _prompt_kit_carlson(self, cards: list[str]) -> None:
        """Prompt Kit Carlson to discard one of three drawn cards."""
        win = tk.Toplevel(self.root)
        win.title("Kit Carlson")
        ttk.Label(win, text="Discard one card:").pack()
        def _discard(idx: int) -> None:
            """Discard the chosen card."""
            self._use_ability("kit_carlson", target=None, card_index=idx)
            win.destroy()

        def _make_handler(idx: int) -> Callable[[], None]:
            def _handler() -> None:
                _discard(idx)
            return _handler

        for i, card in enumerate(cards):
            ttk.Button(
                win,
                text=card,
                command=_make_handler(i),
            ).pack(fill="x")

    def _prompt_pedro_ramirez(self) -> None:
        """Ask Pedro Ramirez whether to draw from the discard pile."""
        win = tk.Toplevel(self.root)
        win.title("Pedro Ramirez")
        ttk.Label(win, text="Take top discard instead of draw?").pack()
        def _choose(use_discard: bool) -> None:
            idx = 1 if use_discard else 0
            self._use_ability("pedro_ramirez", card_index=idx)
            win.destroy()

        def _take_discard() -> None:
            _choose(True)

        def _draw_deck() -> None:
            _choose(False)

        ttk.Button(win, text="Yes", command=_take_discard).pack(fill="x")
        ttk.Button(win, text="No", command=_draw_deck).pack(fill="x")

    def _prompt_jose_delgado(self, equipment: list[dict]) -> None:
        """Prompt Jose Delgado to discard equipment for two cards."""
        win = tk.Toplevel(self.root)
        win.title("Jose Delgado")
        ttk.Label(win, text="Discard equipment to draw two?").pack()
        def _discard_equipment(idx: int) -> None:
            """Discard the selected equipment and close the prompt."""
            self._use_ability("jose_delgado", target=idx)
            win.destroy()

        def _skip() -> None:
            """Skip discarding equipment and close the prompt."""
            self._use_ability("jose_delgado")
            win.destroy()

        def _make_eq_handler(idx: int) -> Callable[[], None]:
            def _handler() -> None:
                _discard_equipment(idx)
            return _handler

        for eq in equipment:
            ttk.Button(
                win,
                text=eq.get("name", ""),
                command=_make_eq_handler(eq.get("index")),
            ).pack(fill="x")

        ttk.Button(win, text="Skip", command=_skip).pack(fill="x")

    def _prompt_pat_brennan(self, targets: list[dict]) -> None:
        """Prompt Pat Brennan to take a card in play."""
        win = tk.Toplevel(self.root)
        win.title("Pat Brennan")
        ttk.Label(win, text="Draw a card in play:").pack()

        def _take_card(idx: int, card: str) -> None:
            self._use_ability("pat_brennan", target=idx, card=card)
            win.destroy()

        def _skip() -> None:
            self._use_ability("pat_brennan")
            win.destroy()

        def _make_handler(idx: int, card: str) -> Callable[[], None]:
            def _handler() -> None:
                _take_card(idx, card)
            return _handler

        for t in targets:
            for card in t.get("cards", []):
                ttk.Button(
                    win,
                    text=f"{t.get('index')}: {card}",
                    command=_make_handler(t.get("index"), card),
                ).pack(fill="x")

        ttk.Button(win, text="Skip", command=_skip).pack(fill="x")

    def _prompt_lucky_duke(self, cards: list[str]) -> None:
        """Prompt Lucky Duke to choose a draw! result."""
        if not cards:
            return
        win = tk.Toplevel(self.root)
        win.title("Lucky Duke")
        ttk.Label(win, text="Choose draw! result:").pack()

        def _pick(idx: int) -> None:
            self._use_ability("lucky_duke", card_index=idx)
            win.destroy()

        def _make_handler(idx: int) -> Callable[[], None]:
            def _handler() -> None:
                _pick(idx)
            return _handler

        for i, card in enumerate(cards):
            ttk.Button(
                win,
                text=card,
                command=_make_handler(i),
            ).pack(fill="x")

    def _prompt_sid_ketchum(self) -> None:
        """Allow Sid Ketchum to discard cards for health."""
        if not self.hand_names:
            return
        win = tk.Toplevel(self.root)
        win.title("Sid Ketchum")
        lb = tk.Listbox(win, selectmode="multiple")
        for card in self.hand_names:
            lb.insert(tk.END, card)
        lb.pack()
        def _discard() -> None:
            self._use_ability("sid_ketchum", indices=list(lb.curselection()))
            win.destroy()

        ttk.Button(win, text="Discard", command=_discard).pack(fill="x")

    def _prompt_doc_holyday(self) -> None:
        """Allow Doc Holyday to discard cards for a draw."""
        if not self.hand_names:
            return
        win = tk.Toplevel(self.root)
        win.title("Doc Holyday")
        lb = tk.Listbox(win, selectmode="multiple")
        for card in self.hand_names:
            lb.insert(tk.END, card)
        lb.pack()
        def _discard() -> None:
            self._use_ability("doc_holyday", indices=list(lb.curselection()))
            win.destroy()

        ttk.Button(win, text="Discard", command=_discard).pack(fill="x")

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

        def _handle_end(_e: tk.Event) -> None:
            self._end_turn()

        self.root.bind_all(f"<{key}>", _handle_end)
        self._bound_key = key

    def _on_close(self) -> None:
        """Handle window close by shutting down threads."""
        if self.client:
            self.client.stop()
            self.client.join(timeout=1)
            self.client = None
        if self.server_thread:
            self.server_thread.stop()
            self.server_thread.join(timeout=1)
            self.server_thread = None
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    ui = BangUI()
    ui.run()


if __name__ == "__main__":
    main()

