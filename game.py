import math

import cart

class Entity:
    def __init__(self, rect, tiles=[], attrs=[], tile_width=0, tile_height=0):
        self.rect = rect
        self.tiles = tiles
        self.attrs = attrs
        self.tile_width = tile_width
        self.tile_height = tile_height


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
            start_row = math.floor(new_rect.y / cart.TileMap.tile_width)
            start_col = math.floor(new_rect.x / cart.TileMap.tile_width)
            end_row = start_row + math.ceil(new_rect.height / cart.TileMap.tile_width)
            end_col = start_col + math.ceil(new_rect.width / cart.TileMap.tile_width)
            tiles = self.cartridge.map.get_tiles_in_area(
                row_range=range(start_row, end_row), col_range=range(start_col, end_col)
            )
            print(tiles)
            print('---')
            empty_space = True
            for tile_row in tiles:
                for tile in tile_row:
                    if tile != 0:
                        empty_space = False
                        break
            if empty_space:
                entity.rect = new_rect
