# Bang Card Game

This repository now contains a Python implementation of the Bang card game along with a very small websocket server to experiment with multiplayer connectivity.

## Running the server

Install the package (which automatically installs the `websockets` dependency):

```bash
pip install .
bang-server
```

This starts a websocket server on `ws://localhost:8765`.

## Connecting a client

```bash
bang-client
```

You will be prompted for a name and then receive updates about the game state.

This networking layer is experimental and only demonstrates joining the game and ending turns over websockets.

## Graphical Interface

The project also provides a small Tkinter-based GUI for hosting or joining games. Tkinter comes with Python but may require the `python3-tk` package on some Linux systems.
Run the interface with:

```bash
bang-ui
```

Enter your name and choose **Host Game** or **Join Game**. Hosting launches a local
server and shows a room code to share with friends. Joining requires the host
address, port, and the room code.

Once connected you will see:

1. A list of players with their current health and any equipped items.
2. A log area for game messages.
3. Buttons representing the cards in your hand that can be clicked to play them.

Use the **End Turn** button when you are finished. Win or elimination messages are
shown both in the log and as a popup dialog.

## Characters

Players can now be assigned one of the classic Bang characters. Each character has a unique ability that modifies the rules of play. The full roster from the base game is provided:

- Bart Cassidy
- Black Jack
- Calamity Janet
- El Gringo
- Jesse Jones
- Jourdonnais
- Kit Carlson
- Lucky Duke
- Paul Regret
- Pedro Ramirez
- Rose Doolan
- Sid Ketchum
- Slab the Killer
- Suzy Lafayette
- Vulture Sam
- Willy the Kid

Create a player with a character using:

```python
from bang_py.characters import RoseDoolan
player = Player("Rose", character=RoseDoolan())
```

