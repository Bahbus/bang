# Bang Card Game

This repository now contains a Python implementation of the Bang card game along with a very small websocket server to experiment with multiplayer connectivity.

## Running the server

```bash
python3 -m bang_py.network.server
```

This starts a websocket server on `ws://localhost:8765`.

## Connecting a client

```bash
python3 -m bang_py.network.client
```

You will be prompted for a name and then receive updates about the game state.

This networking layer is experimental and only demonstrates joining the game and ending turns over websockets.
