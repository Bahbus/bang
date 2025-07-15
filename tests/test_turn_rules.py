from bang_py.game_manager import GameManager
from bang_py.deck import Deck
from bang_py.player import Player
from bang_py.cards.roles import SheriffRoleCard, OutlawRoleCard
from bang_py.cards.bang import BangCard
from bang_py.characters.willy_the_kid import WillyTheKid


def test_bang_limit_default():
    gm = GameManager()
    p1 = Player("A")
    p2 = Player("B")
    gm.add_player(p1)
    gm.add_player(p2)
    p1.hand.extend([BangCard(), BangCard()])
    gm.play_card(p1, p1.hand[0], p2)
    gm.play_card(p1, p1.hand[0], p2)
    assert p2.health == p2.max_health - 1
    assert len(p1.hand) == 1


def test_willy_the_kid_unlimited_bang():
    gm = GameManager()
    p1 = Player("Willy", character=WillyTheKid())
    p2 = Player("B")
    gm.add_player(p1)
    gm.add_player(p2)
    p1.hand.extend([BangCard(), BangCard()])
    gm.play_card(p1, p1.hand[0], p2)
    gm.play_card(p1, p1.hand[0], p2)
    assert p2.health == p2.max_health - 2
    assert len(p1.hand) == 0


def test_discard_phase():
    gm = GameManager(deck=Deck([]))
    p1 = Player("A")
    p2 = Player("B")
    gm.add_player(p1)
    gm.add_player(p2)
    gm.turn_order = [0, 1]
    gm.current_turn = 0
    p1.hand.extend([BangCard() for _ in range(5)])
    p1.health = 3
    gm.end_turn()
    assert len(p1.hand) == 3


def test_outlaws_win_when_sheriff_dies():
    gm = GameManager()
    sheriff = Player("S", role=SheriffRoleCard())
    outlaw = Player("O", role=OutlawRoleCard())
    gm.add_player(sheriff)
    gm.add_player(outlaw)
    results: list[str] = []

    def _record_result(r: str) -> None:
        results.append(r)

    gm.game_over_listeners.append(_record_result)
    sheriff.health = 1
    outlaw.hand.append(BangCard())
    gm.play_card(outlaw, outlaw.hand[0], sheriff)
    assert results == ["Outlaws win!"]
