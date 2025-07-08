extends Node

class_name GameManager

signal player_damaged(player)
signal player_healed(player)
signal turn_started(player)

var players: Array[Player] = []
var current_turn: int = 0
var turn_order: Array[int] = []

func _ready() -> void:
    multiplayer.connected_to_server.connect(_on_connected_to_server)
    if multiplayer.is_server():
        _setup_signals()
    add_to_group("game_manager")

func _setup_signals() -> void:
    get_tree().get_root().connect("player_damaged", self, "_on_player_damaged")
    get_tree().get_root().connect("player_healed", self, "_on_player_healed")

func _on_connected_to_server() -> void:
    if multiplayer.is_server():
        start_game()

func start_game() -> void:
    turn_order = []
    for id in multiplayer.get_peers():
        turn_order.append(id)
    current_turn = 0
    _begin_turn()

func _begin_turn() -> void:
    var id = turn_order[current_turn]
    rpc_id(id, "start_turn")
    emit_signal("turn_started", _get_player_by_id(id))

@rpc
func start_turn() -> void:
    # Client side start of turn
    pass

func end_turn() -> void:
    if multiplayer.is_server():
        current_turn = (current_turn + 1) % turn_order.size()
        _begin_turn()

func add_player(player: Player) -> void:
    players.append(player)

func _get_player_by_id(id: int) -> Player:
    for p in players:
        if p.get_multiplayer_authority() == id:
            return p
    return null

func _on_player_damaged(player: Player) -> void:
    if player.health <= 0:
        _check_win_conditions()

func _on_player_healed(player: Player) -> void:
    pass

func _check_win_conditions() -> void:
    var alive = [p for p in players if p.is_alive()]
    var sheriff_alive = alive.any(lambda p: p.role == Player.Role.SHERIFF)
    var outlaws_alive = alive.any(lambda p: p.role == Player.Role.OUTLAW)
    var renegade_alive = alive.any(lambda p: p.role == Player.Role.RENEGADE)
    if not sheriff_alive:
        if alive.size() == 1 and alive[0].role == Player.Role.RENEGADE:
            print("Renegade wins!")
        else:
            print("Outlaws win!")
    elif not outlaws_alive and not renegade_alive:
        print("Sheriff and Deputies win!")
