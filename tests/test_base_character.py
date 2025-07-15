from bang_py.characters.base import BaseCharacter
from bang_py.game_manager import GameManager
from bang_py.player import Player
import pytest


class Dummy(BaseCharacter):
    """Minimal concrete character for testing."""

    def ability(self, gm: GameManager, player: Player, **_: object) -> bool:
        return True


def test_base_character_is_abstract() -> None:
    with pytest.raises(TypeError):
        BaseCharacter()


class NullChar(BaseCharacter):
    def ability(self, gm: GameManager, player: Player, **_: object) -> bool:
        return False


def test_simple_character_ability_returns_false() -> None:
    gm = GameManager()
    player = Player("Hero", character=NullChar())
    gm.add_player(player)
    assert player.character.ability(gm, player) is False
