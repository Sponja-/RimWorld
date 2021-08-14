from __future__ import annotations

from abc import ABC, abstractmethod

from pygame import Surface
from pygame.event import EventType


class View(ABC):
    @abstractmethod
    def draw(self: View, surface: Surface) -> None:
        pass

    @abstractmethod
    def handle_event(self: View, event: EventType) -> bool:
        pass
