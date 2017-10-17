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
            entity.vector = entity.vector.add(physics.Vector(x=0, y=3))
            v_x = 1 if entity.vector.x >= 0 else -1
            v_y = 1 if entity.vector.y >= 0 else -1
            for i in range(0, max(abs(entity.vector.x), abs(entity.vector.y))):
                delta_y = 0
                if i < abs(entity.vector.y):
                    # test new y for collision
                    new_rect = entity.rect.move(0, v_y)  
                    if not self.collides_with_background(new_rect):
                        delta_y = v_y
                delta_x = 0
                if i < abs(entity.vector.x):
                    # test new x for collission
                    new_rect = entity.rect.move(v_x, 0)  
                    if not self.collides_with_background(new_rect):
                        delta_x = v_x
                entity.rect.move_ip(delta_x, delta_y)
                if delta_x == 0:
                    entity.vector.x = 0
                    v_x = 0
                if delta_y == 0:
                    entity.vector.y = 0
                    v_y = 0


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
            end_col * tile.TILE_SIZE,
            end_row * tile.TILE_SIZE
        )
        tiled_area_hitbox = pygame.Rect(
            tiled_area_frame.x + tiled_area.hitbox.x,
            tiled_area_frame.y + tiled_area.hitbox.y,
            tiled_area.hitbox.width,
            tiled_area.hitbox.height
        )
        if tiled_area_hitbox.width == 0 or tiled_area_hitbox.height == 0:
            return None
        return tiled_area_hitbox

    def collides_with_background(self, rect):
        start_row = math.floor(rect.y / tile.TILE_SIZE)
        start_col = math.floor(rect.x / tile.TILE_SIZE)
        end_row = start_row + math.floor(rect.height / tile.TILE_SIZE) + 1
        end_col = start_col + math.floor(rect.width / tile.TILE_SIZE) + 1
        tiled_area = self.cartridge.map.get_tiles_in_area(
            row_range=range(start_row, end_row), col_range=range(start_col, end_col)
        )
        return not tiled_area.is_empty()
