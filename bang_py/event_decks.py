"""Simple event deck implementations for optional expansions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .game_manager import GameManager


def _peyote(game: GameManager) -> None:
    """Each draw gives one extra card."""
    game.event_flags["peyote_bonus"] = 1


def _ricochet(game: GameManager) -> None:
    """Bang! cards also hit the next player."""
    game.event_flags["ricochet"] = True


def _river(game: GameManager) -> None:
    """Discarded cards pass to the left player."""
    game.event_flags["river"] = True


def _fistful_ghost_town(game: GameManager) -> None:
    """Alias of Ghost Town for the Fistful deck."""
    _ghost_town(game)


def _judge(game: GameManager) -> None:
    """Beer cards cannot be played."""
    game.event_flags["no_beer_play"] = True


def _ghost_town(game: GameManager) -> None:
    """Revive eliminated players with 1 health until the next event card."""
    game.event_flags["ghost_town"] = True
    revived = []
    for p in game.players:
        if not p.is_alive():
            p.health = 1
            p.metadata.ghost_revived = True
            revived.append(p)
    if revived:
        game.turn_order = [i for i, pl in enumerate(game.players) if pl.is_alive()]


def _bounty(game: GameManager) -> None:
    """Reward eliminations with two cards."""
    game.event_flags["bounty"] = True


def _vendetta(game: GameManager) -> None:
    """Outlaws gain +1 attack range."""
    game.event_flags["vendetta"] = True


def _thirst(game: GameManager) -> None:
    game.event_flags["draw_count"] = 1


def _shootout(game: GameManager) -> None:
    """Allow unlimited Bang! cards this turn."""
    game.event_flags["bang_limit"] = 99


def _high_noon(game: GameManager) -> None:
    game.event_flags["start_damage"] = 1


def _fistful(game: GameManager) -> None:
    game.event_flags["damage_by_hand"] = True


def _blessing(game: GameManager) -> None:
    """Heal all players by one."""
    for player in game.players:
        player.heal(1)


def _gold_rush(game: GameManager) -> None:
    """Players draw three cards each draw phase."""
    game.event_flags["draw_count"] = 3


def _law_of_the_west(game: GameManager) -> None:
    """All players have unlimited range."""
    game.event_flags["range_unlimited"] = True


def _siesta(game: GameManager) -> None:
    """Players draw three cards each draw phase."""
    game.event_flags["draw_count"] = 3


def _cattle_drive(game: GameManager) -> None:
    """Each player discards one card if possible."""
    for player in game.players:
        if player.hand:
            player.hand.pop()


def _sermon(game: GameManager) -> None:
    """Bang! cards cannot be played."""
    game.event_flags["no_bang"] = True


def _hangover(game: GameManager) -> None:
    """Beer cards give no health."""
    game.event_flags["no_beer"] = True


def _abandoned_mine(game: GameManager) -> None:
    """All players draw a card."""
    for player in game.players:
        game.draw_card(player)


def _ambush_event(game: GameManager) -> None:
    """Missed! cards have no effect."""
    game.event_flags["no_missed"] = True


def _ranch(game: GameManager) -> None:
    """Heal all players by one."""
    for player in game.players:
        player.heal(1)


def _hard_liquor(game: GameManager) -> None:
    """Beer heals two health."""
    game.event_flags["beer_heal"] = 2


def _prison_break(game: GameManager) -> None:
    """Jail cards are discarded."""
    game.event_flags["no_jail"] = True


def _curse_event(game: GameManager) -> None:
    """Players reveal their hands."""
    game.event_flags["revealed_hands"] = True


def _daltons_event(game: GameManager) -> None:
    """Each player draws a card."""
    for player in game.players:
        game.draw_card(player)


def _doctor_event(game: GameManager) -> None:
    """Players heal 1 life instead of drawing cards."""
    game.event_flags["doctor"] = True


def _reverend_event(game: GameManager) -> None:
    """Limit each player to two cards per turn."""
    game.event_flags["reverend_limit"] = 2


def _train_arrival_event(game: GameManager) -> None:
    """All players draw one card."""
    for player in game.players:
        game.draw_card(player)


def _handcuffs_event(game: GameManager) -> None:
    """Skip the next player's turn."""
    game.event_flags["skip_turn"] = True


def _new_identity_event(game: GameManager) -> None:
    """All players discard their hand and draw the same number of cards."""
    for player in game.players:
        num = len(player.hand)
        while player.hand:
            game.discard_pile.append(player.hand.pop())
        if num:
            game.draw_card(player, num)


def _lasso_event(game: GameManager) -> None:
    """Each player takes the first card from the next player's hand if possible."""
    players = game.players
    taken: list = []
    for i, player in enumerate(players):
        target = players[(i + 1) % len(players)]
        card = target.hand.pop(0) if target.hand else None
        taken.append(card)
    for card, player in zip(taken, players):
        if card:
            player.hand.append(card)


def _sniper_event(game: GameManager) -> None:
    """All players have unlimited range."""
    game.event_flags["range_unlimited"] = True


def _russian_roulette_event(game: GameManager) -> None:
    """All players take 1 damage."""
    for player in list(game.players):
        player.take_damage(1)
        game.on_player_damaged(player)


def _blood_brothers_event(game: GameManager) -> None:
    """Players share damage."""
    game.event_flags["blood_brothers"] = True


def _dead_man_event(game: GameManager) -> None:
    """Players skip their draw phase."""
    game.event_flags["no_draw"] = True


def _high_stakes(game: GameManager) -> None:
    """Players may play any number of Bang! cards."""
    game.event_flags["bang_limit"] = 99


@dataclass
class EventCard:
    """Card used in event deck expansions."""

    name: str
    effect: Callable[[GameManager], None]
    description: str = ""

    def apply(self, game: GameManager) -> None:
        """Execute this event's effect."""
        self.effect(game)


def create_high_noon_deck() -> List[EventCard]:
    """Return a simple High Noon event deck."""
    return [
        EventCard("Blessing", _blessing, "All players heal"),
        EventCard("Curse", _curse_event, "Hands are visible"),
        EventCard("Ghost Town", _ghost_town, "Eliminated players return"),
        EventCard("Gold Rush", _gold_rush, "Draw three cards"),
        EventCard("Hangover", _hangover, "Beer gives no health"),
        EventCard("High Noon", _high_noon, "Lose 1 life at start of turn"),
        EventCard("Shootout", _shootout, "Unlimited Bang!s per turn"),
        EventCard("The Daltons", _daltons_event, "Everyone draws"),
        EventCard("The Doctor", _doctor_event, "Draw to heal"),
        EventCard("The Reverend", _reverend_event, "Limit to two cards"),
        EventCard("The Sermon", _sermon, "Bang! cannot be played"),
        EventCard("Thirst", _thirst, "Players draw only one card"),
        EventCard("Train Arrival", _train_arrival_event, "Everyone draws"),
        EventCard("Handcuffs", _handcuffs_event, "Skip the sheriff's turn"),
        EventCard("New Identity", _new_identity_event, "Players redraw hands"),
    ]


def create_fistful_deck() -> List[EventCard]:
    """Return a simple Fistful of Cards event deck."""
    return [
        EventCard("Abandoned Mine", _abandoned_mine, "Everyone draws"),
        EventCard("Ambush", _ambush_event, "Missed! has no effect"),
        EventCard("Blood Brothers", _blood_brothers_event, "Shared damage"),
        EventCard("Dead Man", _dead_man_event, "Skip draw phase"),
        EventCard("Hard Liquor", _hard_liquor, "Beer heals 2"),
        EventCard("Lasso", _lasso_event, "Steal from next player"),
        EventCard("Law of the West", _law_of_the_west, "Unlimited range"),
        EventCard("Peyote", _peyote, "Lucky draws"),
        EventCard("Ranch", _ranch, "All heal"),
        EventCard("Ricochet", _ricochet, "Bang! hits an extra player"),
        EventCard("Russian Roulette", _russian_roulette_event, "All take damage"),
        EventCard("Sniper", _sniper_event, "Unlimited range"),
        EventCard("The Judge", _judge, "Beer cards cannot be played"),
        EventCard("Vendetta", _vendetta, "Outlaws have +1 range"),
        EventCard("A Fistful of Cards", _fistful, "Damage equal to cards in hand"),
    ]
