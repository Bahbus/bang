# Bang Card Game

This project implements a very small subset of the **Bang!** card game in Python.  It includes a few basic cards, a simple `GameManager` and minimal networking so multiple players can connect over websockets.  A Tkinter based UI is provided to host or join a local game.

## Current Features
* `Player` and `GameManager` classes
* Basic cards: **Bang!**, **Beer** and **Missed!**
* Experimental websocket server and client
* Small Tkinter UI for hosting or joining a game
* Example script demonstrating the core classes

## Running the server
```bash
python3 -m bang_py.network.server
```
This starts a websocket server on `ws://localhost:8765`.

## Connecting a client
```bash
python3 -m bang_py.network.client
```
You will be prompted for a room code and a name, then receive updates about the game state.

## Graphical UI
To try the graphical interface run:
```bash
python3 -m bang_py.ui
```
From the start menu you can host a game (which also launches the server) or join an existing one.  The UI is very small and currently only allows players to join and end turns.

