extends Card

class_name MissedCard

func _init():
    card_name = "Missed!"

func play(target: Player) -> void:
    if not target:
        return
    # mark target as having dodged the last Bang
    target.metadata["dodged"] = true
