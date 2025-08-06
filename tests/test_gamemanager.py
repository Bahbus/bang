from bang_py.game_manager import GameManager
from bang_py.player import Player
from bang_py.deck_factory import create_standard_deck
from bang_py.cards.bang import BangCard


def test_drawing_and_playing() -> None:
    deck = create_standard_deck()
    deck.cards.extend([BangCard(), BangCard()])
    gm = GameManager(deck=deck)
    p1 = Player("A")
    p2 = Player("B")
    gm.add_player(p1)
    gm.add_player(p2)
    gm.draw_card(p1)
    assert len(p1.hand) == 1
    gm.play_card(p1, p1.hand[0], p2)
    assert len(gm.discard_pile) == 1
    assert p2.health == p2.max_health - 1


def test_start_game_initializes_turn_order_and_calls_listener():
    gm = GameManager()
    p1 = Player("Alice")
    p2 = Player("Bob")
    gm.add_player(p1)
    gm.add_player(p2)
    started_players = []

    def _record_start(player: Player) -> None:
        started_players.append(player)

    gm.turn_started_listeners.append(_record_start)

    gm.start_game(deal_roles=False)

    assert gm.turn_order == [0, 1]
    assert gm.current_turn == 0
    assert started_players == [p1]


def test_distance_accounts_for_seating_and_deaths():
    gm = GameManager()
    p1 = Player("A")
    p2 = Player("B")
    p3 = Player("C")
    p4 = Player("D")
    gm.add_player(p1)
    gm.add_player(p2)
    gm.add_player(p3)
    gm.add_player(p4)

    assert p1.distance_to(p3) == 2

    p2.health = 0

    assert p1.distance_to(p3) == 1


def test_distance_with_three_players_is_one():
    gm = GameManager()
    players = [Player(str(i)) for i in range(3)]
    for p in players:
        gm.add_player(p)

    assert all(players[0].distance_to(players[i]) == 1 for i in [1, 2])


def test_max_distance_with_seven_players():
    gm = GameManager()
    players = [Player(str(i)) for i in range(7)]
    for p in players:
        gm.add_player(p)

    assert players[0].distance_to(players[3]) == 3
    assert players[0].distance_to(players[4]) == 3


def test_get_player_by_index_returns_expected_player():
    gm = GameManager()
    p1 = Player("A")
    p2 = Player("B")
    gm.add_player(p1)
    gm.add_player(p2)

    assert gm.get_player_by_index(0) is p1
    assert gm.get_player_by_index(1) is p2
    assert gm.get_player_by_index(2) is None
    assert gm.get_player_by_index(-1) is None
