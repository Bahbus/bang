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

Enter your name and choose **Host Game** or **Join Game**. Hosting launches a local server and shows a room code to share with friends. Joining requires the host address, port, and the room code.

