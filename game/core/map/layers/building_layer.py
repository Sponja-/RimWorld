from __future__ import annotations

from typing import Any, Optional

from pygame import Vector2

from ...buildings import Building, SimpleBuilding
from .map_layer import TickableLayer

class BuildingLayer(TickableLayer[Optional[Building]]):
    __layer_name__ = "buildings"
    default_elem = None

    def tick(self: BuildingLayer, delta_time: float) -> None:
        for building in self.data:
            building.tick(delta_time)
    
    def add_building(self: BuildingLayer, pos: Vector2, building: Building) -> None:
        if isinstance(building.type, SimpleBuilding):
            self.set_pos(pos, building)

            self.map.layers["speed_modifiers"].add_modifiers(
                pos, "building", building.type.speed_modifier
            )

            if isinstance(building.sprite, TileSprite):
                self.map.layers["background_sprites"].redraw_pos(pos)
            else:
                self.map.layers["foreground_sprites"].set_pos(pos, building.sprite)
    
    def remove_building(self: BuildingLayer, pos: Vector2) -> None:
        building = self.get_pos(pos)
        assert building is not None
        if isinstance(building.type, SimpleBuilding):
            self.set_pos(pos, None)

            self.map.layers["speed_modifiers"].remove_modifier(pos, "building")

            if isinstance(building.sprite, TileSprite):
                self.map.layers["background_sprites"].redraw_pos(pos)
            else:
                self.map.layers["foreground_sprites"].set_pos(pos, None)
