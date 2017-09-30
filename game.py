import math

import pygame

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
            start_row = math.ceil(new_rect.y / tile.TILE_SIZE)
            start_col = math.ceil(new_rect.x / tile.TILE_SIZE)
            end_row = start_row + math.ceil(new_rect.height / tile.TILE_SIZE)
            end_col = start_col + math.ceil(new_rect.width / tile.TILE_SIZE)
            tiled_area = self.cartridge.map.get_tiles_in_area(
                row_range=range(start_row, end_row), col_range=range(start_col, end_col)
            )
            tiled_area_frame = pygame.Rect(
                start_col * tile.TILE_SIZE,
                start_row * tile.TILE_SIZE,
                tiled_area.bounds.width,
                tiled_area.bounds.height
            )
            tiled_area_hitbox = pygame.Rect(
                tiled_area_frame.x + tiled_area.hitbox.x,
                tiled_area_frame.y + tiled_area.hitbox.y,
                tiled_area.hitbox.width,
                tiled_area.hitbox.height
            )
            if not new_rect.colliderect(tiled_area_hitbox):
                entity.rect = new_rect
            else:
                new_rect.bottom = tiled_area_hitbox.top
                entity.rect = new_rect
