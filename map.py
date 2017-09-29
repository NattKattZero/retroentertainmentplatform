import math


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


class TiledArea:
    def __init__(self, tile_data=[], attr_data=[], width=0, height=0):
        self.width = width
        self.height = height
        self.tiles = [list(zip(tile_data[x:x+width], attr_data[x:x+width])) for x in range(0, len(tile_data), width)]
        print(self.tiles)
