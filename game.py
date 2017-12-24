import math

import pygame

import cart
import tile
import physics

class Entity:
    def __init__(self, coord, tiled_area):
        self.coord = coord
        self.tiled_area = tiled_area
        self.vector = physics.Vector()

    def move(self):
        self.coord = self.coord.moved(self.vector.x, self.vector.y)


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
            entity.move()

