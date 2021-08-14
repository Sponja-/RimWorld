from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, is_dataclass
from inspect import isabstract
from typing import Any

from pygame.sprite import Sprite

from ..type_utils import DataclassInheritance, AbstractProperty
from ..events import Event, Eventful
from ..location import Location


class ItemMeta(DataclassInheritance):
    registry: dict[str, ItemMeta] = {}

    def __init__(
        cls: ItemMeta,
        clsname: str,
        bases: tuple[ItemMeta, ...],
        namespace: dict[str, Any],
    ) -> ItemMeta:
        if not isabstract(cls):
            ItemMeta.registry[clsname] = cls


class Item(Eventful, metaclass=ItemMeta):
    sprite: Sprite = AbstractProperty()
    weight: float = AbstractProperty()  # Unit weight

    PickUp = Event()
    Drop = Event()
    CreateItem = Event()

    @dataclass(frozen=False, order=False, eq=True)
    class Data:
        location: Location

    def __init__(self: Item, **data: Any) -> None:
        self.data = type(self).Data(**data)

        self.dispatch_event("CreateItem")

    def total_weight(self: Item) -> float:
        return self.weight


class StackableItem(Item):
    max_stack_amount: int = AbstractProperty()
    unit_weight: float = AbstractProperty()

    AddAmount = Event()
    RemoveAmount = Event()

    @dataclass
    class Data:
        stack_amount: int

    @property
    def weight(self: StackableItem) -> float:
        return self.data.stack_amount * self.unit_weight
