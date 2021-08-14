from __future__ import annotations

import inspect
from abc import ABC, ABCMeta, abstractmethod, abstractstaticmethod
from typing import Any, Callable, Generic, Optional, TypeVar

from pygame import Vector2

T = TypeVar("T")


class LayerMeta(ABCMeta):
    layers: dict[str, type[MapLayer]] = {}

    def __new__(
        cls: type[MapLayer],
        clsname: str,
        bases: tuple[type[MapLayer], ...],
        namespace: dict[str, Any],
    ) -> LayerMeta:
        new_cls = super().__new__(cls, clsname, bases, namespace)

        if not inspect.isabstract(new_cls):
            LayerMeta.layers[new_cls.__layer_name__] = new_cls

        return new_cls


class MapLayer(ABC, Generic[T], metaclass=LayerMeta):
    default_elem: Optional[T] = None
    default_factory: Optional[Callable[[], T]] = None

    @property
    @classmethod
    @abstractmethod
    def __layer_name__(cls: type[MapLayer[T]]) -> str:
        pass

    def __init__(self: MapLayer[T], map: Map) -> None:
        self.map = map

        self.data: list[T]
        if type(self).default_factory is None:
            self.data = [
                type(self).default_elem
                for _ in range(int(self.map.size.x * self.map.size.y))
            ]
        else:
            self.data = [
                type(self).default_factory()
                for _ in range(int(self.map.size.x * self.map.size.y))
            ]
    
    def get_pos(self: MapLayer[T], pos: Vector2) -> T:
        return self.data[int(pos.x + self.map.size.x * pos.y)]
    
    def set_pos(self: MapLayer[T], pos: Vector2, value: T) -> None:
        self.data[int(pos.x + self.map.size.x * pos.y)] = value

class TickableLayer(MapLayer[T]):
    @abstractmethod
    def tick(self: TickableLayer[T], delta_time: float) -> None:
        pass
