import math

import pygame

class Cart:
    def __init__(self):
        self.map = None
        self.tile_map = None
        self.attr_map = None
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

    def load(self, filepath):
        with open(filepath, 'rb') as cart_file:
            cart_data = cart_file.read()
            header = cart_data[0:16]
            palette_offset = int.from_bytes(header[0:4], byteorder='big')
            tile_offset = int.from_bytes(header[4:8], byteorder='big')
            map_offset = int.from_bytes(header[8:12], byteorder='big')
            attr_offset = int.from_bytes(header[12:16], byteorder='big')
            print(f'palette: {palette_offset}, tile: {tile_offset}, map: {map_offset}, attr: {attr_offset}')
            palette_data = cart_data[palette_offset:tile_offset]
            self.background_color = palette_data[0]
            self.background_palettes[0] = (palette_data[1], palette_data[2], palette_data[3])
            self.background_palettes[1] = (palette_data[4], palette_data[5], palette_data[6])
            self.background_palettes[2] = (palette_data[6], palette_data[7], palette_data[8])
            self.background_palettes[3] = (palette_data[9], palette_data[10], palette_data[11])
            tile_data = cart_data[tile_offset:map_offset]
            self.tile_map = TileMap()
            self.tile_map.load(tile_data)
            map_data = cart_data[map_offset:attr_offset]
            self.map = Map()
            self.map.load(map_data)
            attr_data = cart_data[attr_offset:len(cart_data)]
            self.attr_map = AttributeMap()
            self.attr_map.load(attr_data)


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

    def __getitem__(self, idx):
        if idx in range(0, len(self.sections)):
            return self.sections[idx]
        else:
            raise IndexError

class AttributeMap:
    section_width = Map.section_width
    section_height = Map.section_height

    def __init__(self):
        self.sections = []

    def load(self, raw_data):
        self.sections = []
        section_size = AttributeMap.section_height * AttributeMap.section_width
        section_count = math.floor(len(raw_data) / section_size)
        for idx_section in range(0, section_count):
            section_data = raw_data[idx_section * section_size:(idx_section + 1) * section_size]
            section = []
            for row in range(0, AttributeMap.section_height):
                row_data = section_data[row * AttributeMap.section_width:(row + 1) * AttributeMap.section_width]
                map_row = [t for t in row_data]
                section.append(map_row)
            self.sections.append(section)

    def __getitem__(self, idx):
        if idx in range(0, len(self.sections)):
            return self.sections[idx]
        else:
            raise IndexError


class TileMap:
    tile_width = 8

    def __init__(self):
        self.tiles = []

    def load(self, raw_data):
        self.tiles = []
        tile_size = TileMap.tile_width * TileMap.tile_width
        tile_count = math.floor(len(raw_data) / tile_size)
        for idx_tile in range(0, tile_count):
            tile_data = raw_data[idx_tile * tile_size:(idx_tile + 1) * tile_size]
            tile = []
            for row in range(0, TileMap.tile_width):
                row_data = tile_data[row * TileMap.tile_width:(row + 1) * TileMap.tile_width]
                tile_row = [p for p in row_data]
                tile.append(tile_row)
            self.tiles.append(tile)

    def __getitem__(self, idx):
        if idx in range(0, len(self.tiles)):
            return self.tiles[idx]
        else:
            raise IndexError


def load_cart(filepath):
    cart = Cart()
    cart.load(filepath)
    return cart
