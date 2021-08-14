from __future__ import annotations

from abc import ABC, ABCMeta
from collections import defaultdict
from random import random
from typing import Any, Callable, Optional

from ordered_set import OrderedSet


class Event:
    def __init__(self: Event, *, args: list[type] = [], name: Optional[str] = None) -> None:
        self.name = name
        self.args = args

    def dispatch(self: Event, obj: Eventful, *args: Any, **kwargs: Any) -> None:
        for handler in obj.__handlers__[self.name]:
            handler(obj, *args, **kwargs)


class RareEvent(Event):
    def __init__(self: RareEvent, *, chance=.01, **kwargs: Any):
        super().__init__(**kwargs)
        self.chance = chance
    
    def dispatch(self: Event, obj: Eventful, *args: Any, **kwargs: Any) -> None:
        if random() < self.chance:
            super().dispatch(obj, *args, **kwargs)


class EventfulMeta(ABCMeta):
    def __new__(
        metacls: type[EventfulMeta],
        clsname: str,
        bases: tuple[EventfulMeta, ...],
        namespace: dict[str, Any],
    ) -> EventfulMeta:
        if any(hasattr(base, "dispatch_event") for base in bases):  # Check that it's not Eventful
            event_handlers: dict[str, OrderedSet] = defaultdict(OrderedSet)

            # Parent handlers
            for base in bases:
                for event_name, handlers in base.__handlers__.items():
                    event_handlers[event_name] |= handlers

            # New events
            for name, value in namespace.items():
                if isinstance(value, Event):
                    if value.name is None:
                        value.name = name
                    event_handlers[name] = OrderedSet([])

            # New handlers
            to_delete: list[str] = []
            for name, value in namespace.items():
                if (target_event := getattr(value, "__target__", None)) is not None:
                    if target_event in event_handlers:
                        event_handlers[target_event].add(value)
                    else:
                        raise NameError(f"Unknown event: {target_event}")
                    to_delete.append(name)

            for name in to_delete:
                del namespace[name]

            namespace["__handlers__"] = dict(event_handlers)

        new_cls = super().__new__(metacls, clsname, bases, namespace)
        return new_cls


def on(target: str) -> Callable[[Callable], Callable]:
    def wrapper(func: Callable) -> Callable:
        func.__target__ = target
        return func

    return wrapper


class Eventful(ABC, metaclass=EventfulMeta):
    __handlers__: dict[str, OrderedSet] = {}

    def dispatch_event(
        self: Eventful, event_name: str, *args: Any, **kwargs: Any
    ) -> None:
        getattr(type(self), event_name).dispatch(self, *args, **kwargs)
