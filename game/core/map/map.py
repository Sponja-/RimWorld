from __future__ import annotations

from copy import copy
from math import floor
from numbers import Real
from typing import Optional
from uuid import uuid4

import pygame as pg
from pygame import Vector2, Surface
from pygame.event import EventType

from ..globals import TILE_SIZE
from ..location import Location
from ..view import View
from .layers import *
from .layers.map_layer import LayerMeta, TickableLayer


class Map:
    def __init__(self: Map, size: Vector2) -> None:
        self.size = size
        self.entities: dict[str, Entity] = {}
        self.layers = {name: layer(self) for name, layer in LayerMeta.layers}
        self.id = uuid4()
        self.view = MapView()

    def in_bounds(self: Map, pos: Vector2) -> bool:
        return 0 <= pos.x < self.size.x and 0 <= pos.y < self.size.y

    def print_info(self: Map, pos: Vector2) -> None:
        pass

    def tick(self: Map, delta_time: float) -> None:
        for layer in filter(
            lambda l: isinstance(l, TickableLayer), self.layers.values()
        ):
            layer.tick(delta_time)

        for entity in self.entities.values():
            entity.tick(delta_time)

    def add_entity(self: "Map", entity: Entity) -> None:
        self.entities[entity.id] = entity

    def remove_entity(self: "Map", entity: Entity) -> None:
        del self.entities[entity.id]


class MapTile(Location):
    def __init__(self: MapTile, map: Map, position: tuple[int, int]) -> None:
        self.map = map
        self.position = position


def clamp(n: Real, min_val: Real, max_val: Real) -> Real:
    return max(min_val, min(n, max_val))


def entity_yx(entity: Entity) -> tuple[float, float]:
    pos = entity.data["location"].position
    return (pos.y, pos.x)


class MapView(View):
    def __init__(self: "MapView", map: Map, pos: Optional[Vector2] = None) -> None:
        from ..game import game

        self.map = map
        self.zoom_ratio = 1.0
        self._resolution = copy(game.resolution)
        self.recalculate_sizes()

        self.pos = pos or (self.map.size - self.frustrum_size) / 2

    def recalculate_sizes(self: MapView) -> None:
        self.scaled_tile_size = TILE_SIZE * self.zoom_ratio
        self.frustrum_size = self._resolution / self.scaled_tile_size

    def screen_to_world(self: MapView, screen_pos: Vector2) -> None:
        return self.pos + screen_pos / self.scaled_tile_size

    def world_to_screen(self: MapView, world_pos: Vector2) -> None:
        return (world_pos - self.pos) * self.scaled_tile_size

    def move_pos(self: MapView, movement: Vector2) -> None:
        self.pos += movement
        self.pos.x = clamp(
            self.pos.x, -1, self.map.size.x - self.frustrum_size.size.x + 1
        )
        self.pos.y = clamp(
            self.pos.y, -1, self.map.size.x - self.frustrum_size.size.y + 1
        )

    def handle_move(self: MapView, event: EventType) -> None:
        if event.buttons[1]:  # Middle button
            self.move_pos(Vector2(*event.rel) / -self.scaled_tile_size)

    def handle_wheel(self: MapView, event: EventType) -> None:
        self.zoom_ratio += event.y / 25.0
        self.zoom_ratio = clamp(self.zoom_ratio, 0.5, 2.0)

        old_size = copy(self.frustrum_size)
        self.recalculate_sizes()
        self.move_pos((old_size - self.frustrum_size) / 2)

    def handle_event(self: MapView, event: EventType) -> bool:
        if event.type == pg.MOUSEMOTION:
            self.handle_move(event)
        elif event.type:
            self.handle_wheel(event)
        else:
            return False
        return True

    def draw(self: MapView, screen: Surface) -> None:
        start = self.pos.copy()
        end = self.pos + self.frustrum_size
        start_x = int(clamp(floor(start.x), 0, self.map.size.x))
        end_x = int(clamp(floor(end.x), 0, self.map.size.x))
        start_y = int(clamp(floor(start.x), 0, self.map.size.y))
        end_y = int(clamp(floor(end.x), 0, self.map.size.y))

        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                pos = Vector2(x, y)
                tile = self.map.layers["background_sprites"].get_pos(pos)
                self.draw_tile(screen, pos, tile)

        entity_index = 0
        entity_list = sorted(list(self.map.entities.values()), key=entity_yx)
        foreground_end_y = int(clamp(end.y + 1, 0, self.map.size.y))

        for y in range(start_y, foreground_end_y):
            while (
                entity_index < len(entity_list)
                and entity_list[entity_index].location.position.y < y
            ):
                self.draw_entity(screen, entity_list[entity_index])  # TODO
                entity_index += 1

            for x in range(start_x, end_x):
                pos = Vector2(x, y)
                texture = self.map.foreground_graphics_layer.get_pos(pos)
                if texture is not None:
                    self.draw_foreground(screen, pos, texture)

    def draw_tile(
        self: MapView, screen: Surface, position: Vector2, tile: Surface
    ) -> None:
        scaled_tile = pg.transform.smoothscale(
            tile, (self.scaled_tile_size, self.scaled_tile_size)
        )
        screen_pos = self.world_to_screen(position)
        screen_pos = (int(screen_pos.x), int(screen_pos.y))
        screen.blit(scaled_tile, screen_pos)

    def draw_foreground(
        self: MapView, screen: Surface, position: Vector2, texture: Surface
    ) -> None:
        w, h = texture.get_rect().size
        scaled_height = h * self.zoom_ratio
        scaled_texture = pg.transform.scale(
            texture, (self.scaled_tile_size, self.scaled_tile_size)
        )

        screen_pos = self.world_to_screen(position)
        screen_pos += Vector2(0, self.scaled_tile_size - scaled_height)
        screen_pos = (int(screen_pos.x), int(screen_pos.y))

        screen.blit(scaled_texture, screen_pos)
