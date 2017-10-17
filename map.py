import math

import pygame

import tile

class Map:
    section_width = 32
    section_height = 30

    def __init__(self):
        self.sections = []
        self.attr_sections = []
        self.map_map = []
        self.map_width = 0
        self.map_height = 0

    def load(self, raw_data):
        self.sections = []
        section_size = Map.section_height * Map.section_width
        section_count = math.floor(len(raw_data) / section_size)
        for idx_section in range(0, section_count):
            section_data = raw_data[idx_section * section_size:(idx_section + 1) * section_size]
            section = []
            for row in range(0, Map.section_height):
                row_data = section_data[row * Map.section_width:(row + 1) * Map.section_width]
                map_row = [t for t in row_data]
                section.append(map_row)
            self.sections.append(section)

    def load_attr_map(self, raw_data):
        self.attr_sections = []
        section_size = Map.section_height * Map.section_width
        section_count = math.floor(len(raw_data) / section_size)
        for idx_section in range(0, section_count):
            section_data = raw_data[idx_section * section_size:(idx_section + 1) * section_size]
            section = []
            for row in range(0, Map.section_height):
                row_data = section_data[row * Map.section_width:(row + 1) * Map.section_width]
                map_row = [t for t in row_data]
                section.append(map_row)
            self.attr_sections.append(section)

    def load_mapmap(self, raw_data):
        self.map_map = []
        self.map_width = int.from_bytes(raw_data[0:2], byteorder='big')
        self.map_height = int.from_bytes(raw_data[2:4], byteorder='big')
        map_data = raw_data[4:len(raw_data)]
        self.map_map = [m for m in map_data]

    def get_section_address(self, row, col):
        section_row = math.floor(row / Map.section_height)
        section_col = math.floor(col / Map.section_width)
        if section_row < 0 or section_row >= self.map_height or section_col < 0 or section_col >= self.map_width:
            return -1
        return section_row * self.map_width + section_col

    def get_tile(self, row, col):
        idx_section = self.get_section_address(row, col)
        if idx_section < 0:
            return 0
        tile_row = row % Map.section_height
        tile_col = col % Map.section_width
        section = self.sections[idx_section]
        return section[tile_row][tile_col]

    def get_attr(self, row, col):
        idx_section = self.get_section_address(row, col)
        if idx_section < 0:
            return 0
        attr_row = row % Map.section_height
        attr_col = col % Map.section_width
        section = self.attr_sections[idx_section]
        return section[attr_row][attr_col]

    def get_tiles_in_area(self, row_range, col_range):
        tile_data = []
        attr_data = []
        for row in row_range:
            for col in col_range:
                tile_number = self.get_tile(row, col)
                tile_data.append(tile_number)
                attr = self.get_attr(row, col)
                attr_data.append(attr)
        tiled_area = TiledArea(tile_data=tile_data, attr_data=attr_data, width=len(col_range), height=len(row_range))
        return tiled_area

    def __getitem__(self, idx):
        if idx in range(0, len(self.sections)):
            return self.sections[idx]
        else:
            raise IndexError


class TiledArea:
    def __init__(self, tile_data=[], attr_data=[], width=0, height=0):
        self.width = width
        self.height = height
        self.tiles = [list(zip(tile_data[x:x+width], attr_data[x:x+width])) for x in range(0, len(tile_data), width)]
        self.bounds = pygame.Rect(0, 0, self.width * tile.TILE_SIZE, self.height * tile.TILE_SIZE)
        self.hitbox = self.calculate_hitbox()

    def is_empty(self):
        for row_data in self.tiles:
            for tile_number, attr in row_data:
                if tile_number > 0:
                    return False
        return True

    def calculate_hitbox(self):
        end_row = end_col = 0
        start_row = self.height
        start_col = self.width
        for row, row_data in enumerate(self.tiles):
            for col, tile_and_attr in enumerate(row_data):
                tile_number, attr = tile_and_attr
                if tile_number != 0:
                    if row < start_row:
                        start_row = row
                    if row > end_row:
                        end_row = row
                    if col < start_col:
                        start_col = col
                    if col > end_col:
                        end_col = col
        if start_col > end_col or start_row > end_row:
            start_col = end_col = start_row = end_row = 0
        return pygame.Rect(
            start_col * tile.TILE_SIZE,
            start_row * tile.TILE_SIZE,
            (end_col - start_col) * tile.TILE_SIZE,
            (end_row - start_row) * tile.TILE_SIZE
        )