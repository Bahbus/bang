extends Node

class_name Player

enum Role {SHERIFF, DEPUTY, OUTLAW, RENEGADE}

var name: String
var role: int = Role.OUTLAW
var health: int = 4
var max_health: int = 4
var metadata: Dictionary = {}

func _init(_name: String="", _role: int=Role.OUTLAW, _max_health: int=4):
    name = _name
    role = _role
    max_health = _max_health
    health = max_health

func take_damage(amount: int) -> void:
    health = max(0, health - amount)

func heal(amount: int) -> void:
    health = min(max_health, health + amount)

func is_alive() -> bool:
    return health > 0
