#!/usr/bin/env python3

import sys
import argparse

import pygame

import cart

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('cart_file', help='Cartridige file')
    args = parser.parse_args()
    cart_file = args.cart_file
    scroll_x = 0
    scroll_y = 0
    clock = pygame.time.Clock()
    pygame.init()
    display_surface = pygame.display.set_mode((1024, 768))
    cartridge = cart.load_cart(cart_file)
    # display_surface = pygame.display.set_mode((1440, 900), pygame.FULLSCREEN)
    surface = pygame.Surface((cart.Map.section_width * cart.TileMap.tile_width * 2, cart.Map.section_height * cart.TileMap.tile_width * 2))
    view_surface = pygame.Surface((cart.Map.section_width * cart.TileMap.tile_width, cart.Map.section_height * cart.TileMap.tile_width))
    # surface = pygame.Surface((cart.Map.section_width * cart.TileMap.tile_width, cart.Map.section_height * cart.TileMap.tile_width))
    # fill in the surface wth the first 4 map sections for testing
    surface.fill(cartridge.lookup_universal_background_color())
    for row in range(0, cart.Map.section_height * 2):
        for col in range(0, cart.Map.section_width * 2):
            tile_number = cartridge.map.get_tile(row, col+scroll_x)
            attr = cartridge.map.get_attr(row, col+scroll_x)
            if tile_number > 0:
                tile = cartridge.tile_map[tile_number - 1]
                tile_surface = surface_for_tile(tile, cartridge=cartridge, attr=attr)
                surface.blit(tile_surface, (col * cart.TileMap.tile_width, row * cart.TileMap.tile_width))
    is_running = True
    while is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
        view_rects = find_view_rects(scroll_x, scroll_y, cart.Map.section_width * cart.TileMap.tile_width, cart.Map.section_height * cart.TileMap.tile_width)
        print(view_rects)
        for dest_x, dest_y, x, y, width, height in view_rects:
            view_surface.blit(surface, (dest_x, dest_y), area=(x, y, width, height))
        # view_surface.blit(surface, (0, 0), area=(scroll_x, 0, cart.Map.section_width * cart.TileMap.tile_width, cart.Map.section_height * cart.TileMap.tile_width))
        # may want option for smoothscale
        pygame.transform.scale(view_surface, (1024, 768), display_surface)
        pygame.display.update()
        scroll_x += 1
        scroll_y += 1
        clock.tick(60)
    pygame.quit()
    return 0

def find_view_rects(x, y, width, height):
    view_rects = []
    a = (x + width) % (width * 2)
    b = (y + height) % (height * 2)
    x = x % (width * 2)
    y = y % (height * 2)
    if a < x and b < y:
        view_rects = [
            (0, 0, x, y, abs(width * 2 - x), abs(height * 2 - y)),
            (abs(width * 2 - x), 0, 0, y, a, abs(height * 2 - y)),
            (0, abs(height * 2 - y), x, 0, abs(width * 2 - x), b),
            (abs(width * 2 - x), abs(height * 2 - y), 0, 0, a, b)
        ]
    elif a < x: #  done, woot!
        view_rects = [
            (0, 0, x, y, abs(width * 2 - x), height),
            (abs(width * 2 - x), 0, 0, y, a, height),
        ]
    elif b < y: #  done, woot!
        view_rects = [
            (0, 0, x, y, width, abs(height * 2 - y)),
            (0, abs(height * 2 - y), x, 0, width, b),
        ]
    else: #  done, woot!
        view_rects = [
            (0, 0, x, y, width, height)
        ]
    return view_rects


def surface_for_tile(tile, cartridge, attr=0):
    transform = (attr >> 4) & 0xF
    palette = attr & 0xF
    surface = pygame.Surface((cart.TileMap.tile_width, cart.TileMap.tile_width))
    pix_array = pygame.PixelArray(surface)
    for row in range(0, cart.TileMap.tile_width):
        for col in range(0, cart.TileMap.tile_width):
            p = tile[row][col]
            if p > 0:
                color = cartridge.lookup_background_color(palette, p)
            else:
                color = cartridge.lookup_universal_background_color()
            if transform == 0:
                pix_array[col, row] = color
            elif transform == 1:  # vertical axis flip
                pix_array[7 - col, row] = color
    return surface


if __name__ == '__main__':
    sys.exit(main())
