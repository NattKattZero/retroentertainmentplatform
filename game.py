import math

import pygame

import cart
import tile
import physics

class Entity:
    def __init__(self, rect, tiled_area):
        self.rect = rect
        self.tiled_area = tiled_area
        self.vector = physics.Vector()


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
            for _ in range(0, 11):
                new_vector = entity.vector.add(physics.Vector(angle=270.0, magnitude=1.0))
                x, y = new_vector.get_components()
                print(f'moving x:{x}, y:{y}')
                new_rect = entity.rect.move(x, y)
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
                    entity.vector = new_vector
                else:
                    entity.vector = entity.vector.add(physics.Vector(angle=90.0, magnitude=y))
