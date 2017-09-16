#!/usr/bin/env python3

import sys
import argparse
import math

import pygame

import cart

class Renderer:
    def __init__(self, cartridge):
        self.cartridge = cartridge
        self.backing = None
        self.scroll_x = 0
        self.scroll_y = 0
        self.scroll_col = 0
        self.scroll_row = 0
        self.scroll_col_acc = 0
        self.scroll_row_acc = 0

    def render(self):
        clock = pygame.time.Clock()
        pygame.init()
        display_surface = pygame.display.set_mode((1024, 768))
        # display_surface = pygame.display.set_mode((1440, 900), pygame.FULLSCREEN)
        self.backing = pygame.Surface((cart.Map.section_width * cart.TileMap.tile_width * 2, cart.Map.section_height * cart.TileMap.tile_width * 2))
        view_surface = pygame.Surface((cart.Map.section_width * cart.TileMap.tile_width, cart.Map.section_height * cart.TileMap.tile_width))
        # surface = pygame.Surface((cart.Map.section_width * cart.TileMap.tile_width, cart.Map.section_height * cart.TileMap.tile_width))
        # fill in the surface wth the first 4 map sections for testing
        self.backing.fill(self.cartridge.lookup_universal_background_color())
        for row in range(0, cart.Map.section_height * 2):
            for col in range(0, cart.Map.section_width * 2):
                self.render_tile_col(col, col)
                """
                tile_number = self.cartridge.map.get_tile(row, col)
                attr = self.cartridge.map.get_attr(row, col)
                if tile_number > 0:
                    tile = self.cartridge.tile_map[tile_number - 1]
                    tile_surface = self.surface_for_tile(tile, attr=attr)
                    self.backing.blit(tile_surface, (col * cart.TileMap.tile_width, row * cart.TileMap.tile_width))
                """
        is_running = True
        while is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_running = False
            view_rects = self.scroll(2, 0, cart.Map.section_width * cart.TileMap.tile_width, cart.Map.section_height * cart.TileMap.tile_width)
            for dest_x, dest_y, x, y, width, height in view_rects:
                view_surface.blit(self.backing, (dest_x, dest_y), area=(x, y, width, height))
            # view_surface.blit(surface, (0, 0), area=(scroll_x, 0, cart.Map.section_width * cart.TileMap.tile_width, cart.Map.section_height * cart.TileMap.tile_width))
            # may want option for smoothscale
            pygame.transform.scale(view_surface, (1024, 768), display_surface)
            pygame.display.update()
            clock.tick(60)
        pygame.quit()

    def scroll(self, delta_x, delta_y, width, height):
        x = self.scroll_x + delta_x
        y = self.scroll_y + delta_y
        self.scroll_col_acc += delta_x
        self.scroll_row_acc += delta_y
        scroll_col_delta = 0
        while self.scroll_col_acc > cart.TileMap.tile_width:
            scroll_col_delta += 1
            self.scroll_col_acc -= cart.TileMap.tile_width
        a = (x + width) % (width * 2)
        b = (y + height) % (height * 2)
        x = x % (width * 2)
        y = y % (height * 2)
        left_col = 0
        right_col = 0
        top_row = 0
        bottom_row = 0
        view_rects = []
        if a < x and b < y:  # view rect is split 4 ways
            view_rects = [
                (0, 0, x, y, abs(width * 2 - x), abs(height * 2 - y)),
                (abs(width * 2 - x), 0, 0, y, a, abs(height * 2 - y)),
                (0, abs(height * 2 - y), x, 0, abs(width * 2 - x), b),
                (abs(width * 2 - x), abs(height * 2 - y), 0, 0, a, b)
            ]
        elif a < x:  # view is split in two horizontally
            view_rects = [
                (0, 0, x, y, abs(width * 2 - x), height),
                (abs(width * 2 - x), 0, 0, y, a, height),
            ]
            left_col = math.floor(x / cart.TileMap.tile_width)
            right_col = math.ceil(a / cart.TileMap.tile_width)
            top_row = math.floor(y / cart.TileMap.tile_width)
            bottom_row = math.ceil((y + height) / cart.TileMap.tile_width)
        elif b < y:  # view is split in two vertically
            view_rects = [
                (0, 0, x, y, width, abs(height * 2 - y)),
                (0, abs(height * 2 - y), x, 0, width, b),
            ]
        else: #  view is completely contained in backing
            view_rects = [
                (0, 0, x, y, width, height)
            ]
            left_col = math.floor(x / cart.TileMap.tile_width)
            right_col = math.ceil((x + width) / cart.TileMap.tile_width)
            top_row = math.floor(y / cart.TileMap.tile_width)
            bottom_row = math.ceil((y + height) / cart.TileMap.tile_width)
        if scroll_col_delta > 0:
            for col in range(self.scroll_col, self.scroll_col + scroll_col_delta):
                self.render_tile_col(col, right_col)
            self.scroll_col += scroll_col_delta
        self.scroll_x = x
        self.scroll_y = y
        return view_rects

    def render_tile_col(self, col, backing_col):
        # clear the column with the background color
        self.backing.fill(self.cartridge.lookup_universal_background_color(), rect=(
            backing_col * cart.TileMap.tile_width,
            0,
            backing_col * cart.TileMap.tile_width + cart.TileMap.tile_width,
            cart.Map.section_height * cart.TileMap.tile_width * 2
            ))
        for row in range(0, cart.Map.section_height * 2):
            tile_number = self.cartridge.map.get_tile(row, col)
            attr = self.cartridge.map.get_attr(row, col)
            if tile_number > 0:
                tile = self.cartridge.tile_map[tile_number - 1]
                tile_surface = self.surface_for_tile(tile, attr=attr)
                self.backing.blit(tile_surface, (backing_col * cart.TileMap.tile_width, row * cart.TileMap.tile_width))

    def surface_for_tile(self, tile, attr=0):
        transform = (attr >> 4) & 0xF
        palette = attr & 0xF
        surface = pygame.Surface((cart.TileMap.tile_width, cart.TileMap.tile_width))
        pix_array = pygame.PixelArray(surface)
        for row in range(0, cart.TileMap.tile_width):
            for col in range(0, cart.TileMap.tile_width):
                p = tile[row][col]
                if p > 0:
                    color = self.cartridge.lookup_background_color(palette, p)
                else:
                    color = self.cartridge.lookup_universal_background_color()
                if transform == 0:
                    pix_array[col, row] = color
                elif transform == 1:  # vertical axis flip
                    pix_array[7 - col, row] = color
        return surface

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('cart_file', help='Cartridige file')
    args = parser.parse_args()
    cart_file = args.cart_file
    cartridge = cart.load_cart(cart_file)
    renderer = Renderer(cartridge)
    renderer.render()
    return 0


if __name__ == '__main__':
    sys.exit(main())
