# Bang Card Game

This repository now contains a Python implementation of the Bang card game along with a very small websocket server to experiment with multiplayer connectivity.

## Running the server

Install the package (which also installs `websockets` and the Qt bindings):

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

The original Tkinter UI has been replaced with a Qt interface written for
PyQt/PySide. It offers smoother graphics using ``QGraphicsView`` and a flexible
layout. The main window starts maximized and you can press ``F11`` to toggle
true full-screen mode. The log now appears in a floating dock that can be
dragged anywhere or docked to the sides of the window.

Install the Qt requirements first:

```bash
pip install PySide6
```

Then run the interface with:

```bash
bang-ui
```

Enter your name and choose **Host Game** or **Join Game**. Hosting launches a
local server and shows a room code to share with friends. The host screen lets
you set the maximum number of players and which expansions to enable. Joining
requires the host address, port and room code.

Available expansions are `dodge_city`, `high_noon`, and `fistful_of_cards`.
`dodge_city` adds extra playing cards and is enabled automatically when no
expansions are specified. The other two names activate their respective event
decks.

Once connected you will see:

1. A list of players with their current health and any equipped items.
2. A log area for game messages.
3. Buttons representing the cards in your hand that can be clicked to play them.
4. A board canvas showing the draw deck and discard pile.

Use the **End Turn** button or press the configured key (default `e`) when you are
finished. Win or elimination messages are shown both in the log and as a popup
dialog.

The card backs and small heart icons are generated at runtime so the GUI does
not require any external image files. Two JPEGs,
``example-bang-menu-ui.jpg`` and ``example_bang_ui.jpg``, remain in the
repository root only as reference screenshots and are **not** loaded by the
program.

## Building a Windows Executable

`pyinstaller` can bundle the UI into a standalone Windows executable. Install the
build dependencies and run the target:

```bash
pip install -r requirements.txt
make build-exe
```

The command produces `dist/bang.exe`. Launch it on Windows by double-clicking or
from the command line:

```cmd
bang.exe
```
A GitHub Actions workflow builds this executable for each tagged release and
automatically attaches `bang.exe` to the release as a downloadable asset. The workflow
needs the `contents: write` permission (or a PAT) to upload the file.


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

Additional characters from the Dodge City and Bullet expansions are also
included:

- Belle Star
- Bill Noface
- Chuck Wengam
- Doc Holyday
- Elena Fuente
- Greg Digger
- Herb Hunter
- Jose Delgado
- Molly Stark
- Pat Brennan
- Pixie Pete
- Sean Mallory
- Tequila Joe
- Vera Custer
- Apache Kid
- Johnny Kisch
- Uncle Will
- Claus the Saint

Create a player with a character using:

```python
from bang_py.characters.rose_doolan import RoseDoolan
player = Player("Rose", character=RoseDoolan())
```

## Using Character Abilities

Character abilities use popups, the **Use Ability** button or happen
automatically. Closing a popup does not forfeit the power&mdash;you can still
press **Use Ability** to activate it later. Sid Ketchum, Doc Holyday,
Chuck Wengam and Uncle Will always display buttons during your turn. All other
powers trigger automatically with a message in the log.

### Character reference

- **Apache Kid** – automatic: ignores Diamond cards.
- **Bart Cassidy** – automatic: draw a card whenever wounded.
- **Belle Star** – automatic: cards in play in front of other players have no
  effect during her turn.
- **Bill Noface** – automatic: draw one extra card per wound during phase 1.
- **Black Jack** – automatic: reveal the second draw; if it is Hearts or Diamonds
  draw one more.
- **Calamity Janet** – automatic: may play Bang! as Missed! and vice versa.
- **Chuck Wengam** – button: lose 1 life point to draw 2 cards.
- **Claus the Saint** – automatic: draw one more card than the number of players,
  keep two and give the rest to the others.
- **Doc Holyday** – button: discard two cards for a Bang! that does not count
  toward your limit.
- **Elena Fuente** – automatic: any card may be played as a Missed!.
 - **El Gringo** – automatic: choose a card blindly from whoever damages him.
- **Greg Digger** – automatic: regain two life points whenever someone is
  eliminated.
- **Herb Hunter** – automatic: draw two cards whenever another player is
  eliminated. The GUI adds these cards to your hand automatically.
 - **Jesse Jones** – popup: may choose an opponent and take a card from their hand
   instead of drawing. Use **Use Ability** if you closed the prompt.
- **Johnny Kisch** – automatic: when you put a card in play, all other copies in
  play are discarded automatically.
 - **Jose Delgado** – popup: optionally discard a blue card to draw two cards.
- **Jourdonnais** – automatic: always has a Barrel.
 - **Kit Carlson** – popup: look at the top three cards of the deck, keep two and
   put the third back on top. Can be triggered again with **Use Ability**.
- **Lucky Duke** – popup: flip two cards for draws and choose one. The button can
  be used to pick again.
 - **Molly Stark** – automatic: draw a card whenever you play or voluntarily
   discard any card out of turn. If targeted by a Duel, draw for all Bangs played
   after the Duel ends.
- **Pat Brennan** – popup: may draw a card in play instead of from the deck.
- **Paul Regret** – automatic: opponents see him at distance +1.
- **Pedro Ramirez** – popup: choose whether to draw the top discard card.
- **Pixie Pete** – automatic: draw three cards each turn.
- **Rose Doolan** – automatic: sees everyone at distance -1.
- **Sean Mallory** – automatic: no hand limit.
- **Sid Ketchum** – button: discard two cards to heal one life point.
- **Slab the Killer** – automatic: requires two Missed! cards to cancel his
  Bang!.
- **Suzy Lafayette** – automatic: draw when your hand becomes empty.
- **Tequila Joe** – automatic: Beer heals two life points.
- **Uncle Will** – button: every card shows a **Store** button to play it as a
  General Store once per turn.
- **Vera Custer** – popup at the start of her turn to copy another ability; use
  the button to reopen the choice.
- **Vulture Sam** – automatic: take all cards from eliminated players.
- **Willy the Kid** – automatic: may play unlimited Bang! cards.

The interface logs every automatic effect. Herb Hunter's extra cards and Johnny
Kisch's forced discards happen seamlessly. Other inputs include the **End Turn**
button (or its hotkey) and an **Auto Miss** checkbox that plays Missed!
automatically when you are attacked.

