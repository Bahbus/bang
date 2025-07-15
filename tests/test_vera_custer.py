from bang_py.game_manager import GameManager
from bang_py.player import Player
from bang_py.characters.vera_custer import VeraCuster
from bang_py.characters.willy_the_kid import WillyTheKid
from bang_py.cards.bang import BangCard
from bang_py.helpers import has_ability


def test_vera_custer_copies_other_ability() -> None:
    gm = GameManager()
    vera = Player("Vera", character=VeraCuster())
    willy = Player("Willy", character=WillyTheKid())
    target = Player("Target")
    gm.add_player(vera)
    gm.add_player(willy)
    gm.add_player(target)

    vera.character.copy_ability(gm, vera, willy)
    assert has_ability(vera, WillyTheKid)

    vera.hand.extend([BangCard(), BangCard()])
    gm.play_card(vera, vera.hand[0], target)
    gm.play_card(vera, vera.hand[0], target)
    assert len(vera.hand) == 0

    gm.reset_turn_flags(vera)
    assert not has_ability(vera, WillyTheKid)
