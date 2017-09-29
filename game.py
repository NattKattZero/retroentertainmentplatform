import math

import cart
import tile

class Entity:
    def __init__(self, rect, tiled_area):
        self.rect = rect
        self.tiled_area = tiled_area


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
            start_row = math.floor(new_rect.y / tile.TILE_SIZE)
            start_col = math.floor(new_rect.x / tile.TILE_SIZE)
            end_row = start_row + math.ceil(new_rect.height / tile.TILE_SIZE)
            end_col = start_col + math.ceil(new_rect.width / tile.TILE_SIZE)
            tiles = self.cartridge.map.get_tiles_in_area(
                row_range=range(start_row, end_row), col_range=range(start_col, end_col)
            )
            empty_space = True
            for tile_row in tiles:
                for tile_number in tile_row:
                    if tile_number != 0:
                        empty_space = False
                        break
            if empty_space:
                entity.rect = new_rect
