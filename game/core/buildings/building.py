from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, make_dataclass
from inspect import isabstract
from typing import Any

from pygame.sprite import Sprite

from ..type_utils import DataclassInheritance, AbstractProperty
from ..events import Event, Eventful
from ..location import Location


class BuildingMeta(DataclassInheritance):
    registry: dict[str, BuildingMeta] = {}

    def __init__(
        cls: BuildingMeta,
        clsname: str,
        bases: tuple[BuildingMeta, ...],
        namespace: dict[str, Any],
    ) -> BuildingMeta:
        if not isabstract(cls):
            BuildingMeta.registry[clsname] = cls


class Building(Eventful, metaclass=BuildingMeta):
    sprite: Sprite = AbstractProperty()

    Place = Event()
    Remove = Event()
    CreateBuilding = Event()

    @dataclass
    class Data:
        location: Location

    def __init__(self: Building, **data: Any) -> None:
        self.data = type(self).Data(**data)

        self.dispatch_event("CreateBuilding")


class BreakableBuilding(Building):
    max_durability: float = AbstractProperty()

    Damage = Event(args=[float])
    Repair = Event(args=[float])

    @dataclass
    class Data:
        durability: float

    def damage(self: Building, damage_amount: float) -> None:
        self.data.durability -= damage_amount
        self.dispatch_event("Damage", damage_amount)

    def repair(self: Building, repair_amount: float) -> None:
        self.data.durability += repair_amount
        self.dispatch_event("Repair", repair_amount)
