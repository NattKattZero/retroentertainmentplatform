import math

TILE_SIZE = 8

class TileCatalog:
    def __init__(self):
        self.tiles = []

    def load(self, raw_data):
        self.tiles = []
        tile_data_size = TILE_SIZE * TILE_SIZE
        tile_count = math.floor(len(raw_data) / tile_data_size)
        for idx_tile in range(0, tile_count):
            tile_data = raw_data[idx_tile * tile_data_size:(idx_tile + 1) * tile_data_size]
            tile = []
            for row in range(0, TILE_SIZE):
                row_data = tile_data[row * TILE_SIZE:(row + 1) * TILE_SIZE]
                tile_row = [p for p in row_data]
                tile.append(tile_row)
            self.tiles.append(tile)

    def __getitem__(self, idx):
        if idx in range(0, len(self.tiles)):
            return self.tiles[idx]
        else:
            raise IndexError
