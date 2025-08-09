"""Character ability helpers for :class:`GameManager`."""

from __future__ import annotations

from .cards.bang import BangCard
from .cards.missed import MissedCard
from .cards.general_store import GeneralStoreCard
from .characters.vera_custer import VeraCuster
from .cards.card import BaseCard
from .game_manager_protocol import GameManagerProtocol
from .helpers import handle_out_of_turn_discard
from .player import Player


class AbilityDispatchMixin:
    """Implement miscellaneous character abilities."""

    event_flags: dict
    discard_pile: list[BaseCard]

    def chuck_wengam_ability(self: GameManagerProtocol, player: "Player") -> None:
        """Lose 1 life to draw 2 cards, usable multiple times per turn."""
        if player.health <= 1:
            return
        player.take_damage(1)
        self.on_player_damaged(player)
        self.draw_card(player, 2)

    def doc_holyday_ability(
        self: GameManagerProtocol, player: "Player", indices: list[int] | None = None
    ) -> None:
        """Discard two cards to gain a Bang! that doesn't count toward the limit."""
        if player.metadata.doc_used:
            return
        if len(player.hand) < 2:
            return
        discard_indices = indices or list(range(2))
        discard_indices = sorted(discard_indices, reverse=True)[:2]
        for idx in discard_indices:
            if 0 <= idx < len(player.hand):
                card = player.hand.pop(idx)
                self._pass_left_or_discard(player, card)
        player.metadata.doc_used = True
        player.metadata.doc_free_bang += 1
        player.hand.append(BangCard())

    def pat_brennan_draw(
        self: GameManagerProtocol,
        player: "Player",
        target: "Player" | None = None,
        card_name: str | None = None,
    ) -> bool:
        """During draw phase, draw a card in play instead of from deck."""
        targets = [t for t in self._players if t is not player]
        if (
            isinstance(target, Player)
            and isinstance(card_name, str)
            and target in targets
            and card_name in target.equipment
        ):
            card = target.unequip(card_name)
            if card:
                player.hand.append(card)
                return True
        for p in targets:
            for card in list(p.equipment.values()):
                p.unequip(card.card_name)
                player.hand.append(card)
                return True
        return False

    def uncle_will_ability(self: GameManagerProtocol, player: "Player", card: BaseCard) -> bool:
        """Play any card as General Store once per turn."""
        if player.metadata.uncle_used:
            return False
        player.metadata.uncle_used = True
        GeneralStoreCard().play(player, player, game=self)
        player.hand.remove(card)
        self._pass_left_or_discard(player, card)
        return True

    def vera_custer_copy(self: GameManagerProtocol, player: "Player", target: "Player") -> None:
        """Copy another living character's ability for the turn."""
        if not isinstance(player.character, VeraCuster):
            return
        if not isinstance(target, Player):
            return
        if not target.is_alive() or target is player:
            return
        if target.character is None:
            raise ValueError("Target has no character to copy")
        player.metadata.vera_copy = target.character.__class__
        player.metadata.abilities.add(target.character.__class__)
        target.character.ability(self, player)

    def ricochet_shoot(
        self: GameManagerProtocol, player: "Player", target: "Player", card_name: str
    ) -> bool:
        """Discard a Bang! to shoot at ``card_name`` in front of ``target``."""
        if (
            not self.event_flags.get("ricochet")
            or not isinstance(target, Player)
            or not isinstance(card_name, str)
        ):
            return False
        bang = next((c for c in player.hand if isinstance(c, BangCard)), None)
        card = target.equipment.get(card_name)
        if not bang or not card:
            return False
        player.hand.remove(bang)
        self._pass_left_or_discard(player, bang)
        miss = next((c for c in target.hand if isinstance(c, MissedCard)), None)
        if miss:
            target.hand.remove(miss)
            self._pass_left_or_discard(target, miss)
            handle_out_of_turn_discard(self, target, miss)
            return False
        target.unequip(card_name)
        self.discard_pile.append(card)
        return True

    def reset_turn_flags(self: GameManagerProtocol, player: "Player") -> None:
        """Clear per-turn ability flags on ``player``."""
        player.metadata.doc_used = False
        player.metadata.doc_free_bang = 0
        player.metadata.uncle_used = False
        if isinstance(player.character, VeraCuster):
            player.metadata.vera_copy = None
            player.metadata.unlimited_bang = False
            player.metadata.ignore_others_equipment = False
            player.metadata.no_hand_limit = False
            player.metadata.double_miss = False
            player.metadata.draw_when_empty = False
            player.metadata.immune_diamond = False
            player.metadata.play_missed_as_bang = False
            player.metadata.bang_as_missed = False
            player.metadata.any_card_as_missed = False
            player.metadata.lucky_duke = False
            player.metadata.virtual_barrel = False
            player.metadata.beer_heal_bonus = 0
            player.metadata.hand_limit = None
            player.metadata.abilities = {VeraCuster}
