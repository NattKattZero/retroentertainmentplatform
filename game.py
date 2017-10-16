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

    def move(self):
        self.rect.x += self.vector.x
        self.rect.y += self.vector.y


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
            # add gravity vector
            entity.vector = entity.vector.add(physics.Vector(x=0, y=1))
            # test new y for collision
            new_rect = entity.rect.move(0, entity.vector.y)  
            background_hitbox = self.get_background_hitbox(new_rect)
            if (background_hitbox.width > 0 and background_hitbox.height > 0) and new_rect.colliderect(background_hitbox):
                delta_y = 0
            else:
                delta_y = entity.vector.y
            # test new x for collission
            new_rect = entity.rect.move(entity.vector.x, 0)  
            background_hitbox = self.get_background_hitbox(new_rect)
            if (background_hitbox.width > 0 and background_hitbox.height > 0) and new_rect.colliderect(background_hitbox):
                delta_x = 0
            else:
                delta_x = entity.vector.x
            entity.rect.move_ip(delta_x, delta_y)
            entity.vector.x = delta_x
            entity.vector.y = delta_y


    def get_background_hitbox(self, rect):
        start_row = math.ceil(rect.y / tile.TILE_SIZE)
        start_col = math.ceil(rect.x / tile.TILE_SIZE)
        end_row = start_row + math.ceil(rect.height / tile.TILE_SIZE)
        end_col = start_col + math.ceil(rect.width / tile.TILE_SIZE)
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
        return tiled_area_hitbox
