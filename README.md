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
server and shows a room code to share with friends. The host screen now lets you
set the maximum number of players and which expansions to enable. Joining requires
the host address, port, and the room code.

Available expansions are `dodge_city`, `high_noon`, and `fistful_of_cards`.
`dodge_city` adds extra playing cards and is enabled automatically when no
expansions are specified. The other two names activate their respective event
decks.

Once connected you will see:

1. A list of players with their current health and any equipped items.
2. A log area for game messages.
3. Buttons representing the cards in your hand that can be clicked to play them.

Use the **End Turn** button or press the configured key (default `e`) when you are
finished. Win or elimination messages are shown both in the log and as a popup
dialog.

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
from bang_py.characters import RoseDoolan
player = Player("Rose", character=RoseDoolan())
```

## Using Character Abilities

Abilities are handled in three ways: popup prompts, a **Use Ability** button or
automatic triggers.

### Popup prompts
The GUI opens a dialog whenever a choice is required:

- Vera Custer – choose a living character to copy.
- Jesse Jones – steal the first card from an opponent or skip.
- Kit Carlson – discard one of three drawn cards.
- Pedro Ramirez – decide whether to take the top discard card.
- Jose Delgado – optionally discard equipment for two cards.
- Pat Brennan – draw a card in play instead of from the deck.
- Lucky Duke – pick one of two cards when drawing!.

You can also use the **Use Ability** button for these characters if you close
the prompt and want to activate the power later in the turn.

### Use Ability button
The button below your hand activates:

- Sid Ketchum – discard two cards to heal one life point.
- Doc Holyday – discard two cards for a free Bang!.
- Chuck Wengam – lose one life point to draw two cards.
- Jesse Jones, Kit Carlson, Pedro Ramirez, Jose Delgado, Pat Brennan and
  Lucky Duke after the initial prompt.
- Uncle Will – each card shows a **Store** button to play it as a General Store
  once per turn.

### Automatic abilities
All other powers trigger automatically with a message in the log:

- Bart Cassidy draws when wounded.
- Black Jack reveals the second draw and may gain an extra card.
- Calamity Janet swaps Bang! and Missed! freely.
- El Gringo steals a card from whoever damages him.
- Jourdonnais always has a Barrel.
- Paul Regret is seen at distance +1.
- Rose Doolan sees everyone one space closer.
- Slab the Killer requires two Missed! for his Bang!.
- Suzy Lafayette draws when her hand is empty.
- Vulture Sam takes all cards from eliminated players.
- Willy the Kid may play unlimited Bang!s.
- Pixie Pete draws three cards each turn.
- Sean Mallory has no hand limit.
- Tequila Joe's Beer heals two life points.
- Vera Custer copies another ability at the start of her turn.
- Apache Kid ignores diamond cards.
- Greg Digger regains two life when someone dies.
- Belle Star ignores cards in play during her turn.
- Bill Noface draws one extra card per wound.
- Elena Fuente may play any card as a Missed!.
- Herb Hunter draws two cards when a player is eliminated.
- Molly Stark draws whenever she plays certain cards out of turn.
- Johnny Kisch discards duplicates when putting a card in play.
- Claus the Saint draws extra cards and gives one to each other player.

The game screen also includes an **Auto Miss** checkbox controlling whether
available Missed! cards are played automatically when you are attacked.

