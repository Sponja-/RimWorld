from __future__ import annotations

from typing import Optional

import pygame as pg
from pygame import Vector2, Surface
from pygame.time import Clock

from .core.globals import ALPHA_COLOR
from .core.map import Map
from .core.view import View

class Game:
    def __init__(self: Game, resolution: Vector2, *, max_fps: int = 60) -> None:
        self.resolution = resolution
        self.max_fps = max_fps

    def initialize(self: Game) -> None:
        pg.init()

        self.screen: Surface = pg.display.set_mode(
            (int(self.resolution.x), int(self.resolution.y))
        )
        self.screen.set_colorkey(ALPHA_COLOR)

        self.clock = Clock()

        self.exit = False

        self.maps: dict[str, Map] = {}
        self.active_view: Optional[View] = None
    
    def quit(self: "Game") -> None:
        self.exit = True
    
    def run(self: Game) -> None:
        while not self.exit:
            self.read_events()
            self.draw()
            self.tick()
    
    def read_events(self: Game) -> None:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            else:
                self.active_view.handle_event(event)

    def draw(self: Game) -> None:
        self.screen.fill((0, 0, 0))

        self.active_view.draw(self.screen)
        
        pg.display.flip()

    def tick(self: Game) -> None:
        self.clock.tick(self.max_fps)
        
        delta_time = self.clock.get_time() / 1000.0

        for map in self.maps.values():
            map.tick(delta_time)
