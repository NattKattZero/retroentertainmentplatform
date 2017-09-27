import math

import cart

class Entity:
    def __init__(self, rect, tiles=[], attrs=[]):
        self.rect = rect
        self.tiles = tiles
        self.attrs = attrs


class Game:
    def __init__(self, cartridge):
        self.entities = set()
        self.cartridge = cartridge
        
    def add_entity(self, entity):
        self.entities.add(entity)
        
    def remove_entity(self, entity):
        if entity in self.entities:
            self.entities.remove(entity)
    
    def advance(self):
        for entity in self.entities:
            new_rect = entity.rect.move(0, 11)
            map_row = math.floor(new_rect.bottom / cart.TileMap.tile_width)
            map_col = math.floor(new_rect.x / cart.TileMap.tile_width)
            tile_number = self.cartridge.map.get_tile(map_row, map_col)
            if tile_number == 0:
                entity.rect = new_rect