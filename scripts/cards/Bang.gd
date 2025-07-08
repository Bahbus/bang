extends Card

class_name BangCard

func _init():
    card_name = "Bang!"

func play(target: Player) -> void:
    if not target:
        return
    target.take_damage(1)
    var gm = get_tree().get_first_node_in_group("game_manager")
    if gm:
        gm.emit_signal("player_damaged", target)
