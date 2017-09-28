import math

import pygame

import tile

class Cart:
    def __init__(self, filepath):
        self.map = None
        self.tile_map = None
        self.palette = [
            ( 84,  84,  84),  (  0,  30, 116),  (  8,  16, 144),
            ( 48,   0, 136),  ( 68,   0, 100),  ( 92,   0,  48),
            ( 84,   4,   0),  ( 60,  24,   0),  ( 32,  42,   0),
            (  8,  58,   0),  (  0,  64,   0),  (  0,  60,   0),
            (  0,  50,  60),  (  0,   0,   0),  (  0,   0,   0),
            (  0,   0,   0),  (152, 150, 152),  (  8,  76, 196),
            ( 48,  50, 236),  ( 92,  30, 228),  (136,  20, 176),
            (160,  20, 100),  (152,  34,  32),  (120,  60,   0),
            ( 84,  90,   0),  ( 40, 114,   0),  (  8, 124,   0),
            (  0, 118,  40),  (  0, 102, 120),  (  0,   0,   0),
            (  0,   0,   0),  (  0,   0,   0),  (236, 238, 236),
            ( 76, 154, 236),  (120, 124, 236),  (176,  98, 236),
            (228,  84, 236),  (236,  88, 180),  (236, 106, 100),
            (212, 136,  32),  (160, 170,   0),  (116, 196,   0),
            ( 76, 208,  32),  ( 56, 204, 108),  ( 56, 180, 204),
            ( 60,  60,  60),  (  0,   0,   0),  (  0,   0,   0),
            (236, 238, 236),  (168, 204, 236),  (188, 188, 236),
            (212, 178, 236),  (236, 174, 236),  (236, 174, 212),
            (236, 180, 176),  (228, 196, 144),  (204, 210, 120),
            (180, 222, 120),  (168, 226, 144),  (152, 226, 180),
            (160, 214, 228),  (160, 162, 160),  (  0,   0,   0),
            (  0,   0,   0)
        ]
        self.background_color = 0x0F  # black
        self.background_palettes = [
            ( 0,  1,  2),
            ( 3,  4,  5),
            ( 6,  7,  8),
            ( 9, 10, 11)
        ]
        # load the cart file
        with open(filepath, 'rb') as cart_file:
            cart_data = cart_file.read()
            header = cart_data[0:20]
            palette_offset = int.from_bytes(header[0:4], byteorder='big')
            tile_offset = int.from_bytes(header[4:8], byteorder='big')
            map_offset = int.from_bytes(header[8:12], byteorder='big')
            attr_offset = int.from_bytes(header[12:16], byteorder='big')
            mapmap_offset = int.from_bytes(header[16:20], byteorder='big')
            palette_data = cart_data[palette_offset:tile_offset]
            self.background_color = palette_data[0]
            self.background_palettes[0] = (palette_data[1], palette_data[2], palette_data[3])
            self.background_palettes[1] = (palette_data[4], palette_data[5], palette_data[6])
            self.background_palettes[2] = (palette_data[7], palette_data[8], palette_data[9])
            self.background_palettes[3] = (palette_data[10], palette_data[11], palette_data[12])
            tile_data = cart_data[tile_offset:map_offset]
            self.tile_map = tile.TileMap()
            self.tile_map.load(tile_data)
            map_data = cart_data[map_offset:attr_offset]
            self.map = Map()
            self.map.load(map_data)
            attr_data = cart_data[attr_offset:mapmap_offset]
            self.map.load_attr_map(attr_data)
            mapmap_data = cart_data[mapmap_offset:len(cart_data)]
            self.map.load_mapmap(mapmap_data)

    def lookup_universal_background_color(self):
        return self.palette[self.background_color]

    def lookup_background_color(self, palette, color):
        if palette in range (0, len(self.background_palettes)) and color > 0:
            background_palette = self.background_palettes[palette]
            return self.palette[background_palette[color-1]]
        return self.palette[self.background_color]

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
        tiles = []
        for row in row_range:
            tile_col = []
            for col in col_range:
                tile = self.get_tile(row, col)
                tile_col.append(tile)
            tiles.append(tile_col)
        return tiles

    def __getitem__(self, idx):
        if idx in range(0, len(self.sections)):
            return self.sections[idx]
        else:
            raise IndexError


