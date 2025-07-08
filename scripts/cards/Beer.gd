extends Card

class_name BeerCard

func _init():
    card_name = "Beer"

func play(target: Player) -> void:
    if not target:
        return
    target.heal(1)
    var gm = get_tree().get_first_node_in_group("game_manager")
    if gm:
        gm.emit_signal("player_healed", target)
