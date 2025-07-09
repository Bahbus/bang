from __future__ import annotations

from .game_manager import GameManager
from .player import Player, Role
from .cards.bang import BangCard
from .cards.beer import BeerCard


def print_turn_started(player: Player) -> None:
    print(f"Turn started for {player.name}")


def print_damaged(player: Player) -> None:
    print(f"{player.name} took damage, health is now {player.health}")


def print_healed(player: Player) -> None:
    print(f"{player.name} healed, health is now {player.health}")


def main() -> None:
    gm = GameManager()
    gm.turn_started_listeners.append(print_turn_started)
    gm.player_damaged_listeners.append(print_damaged)
    gm.player_healed_listeners.append(print_healed)

    gm.add_player(Player("Alice", role=Role.SHERIFF))
    gm.add_player(Player("Bob", role=Role.OUTLAW))

    gm.start_game()

    bang = BangCard()
    beer = BeerCard()

    target = gm.players[1]
    bang.play(target)
    gm.on_player_damaged(target)

    beer.play(target)
    gm.on_player_healed(target)


if __name__ == "__main__":
    main()

