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
    # display_surface = pygame.display.set_mode((1440, 900), pygame.FULLSCREEN)
    surface = pygame.Surface((cart.Map.section_width * cart.TileMap.tile_width, cart.Map.section_height * cart.TileMap.tile_width))
    cartridge = cart.load_cart(cart_file)
    is_running = True
    while is_running:
        surface.fill(cartridge.lookup_universal_background_color())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
        for row in range(0, cart.Map.section_height):
            for col in range(0, cart.Map.section_width):
                tile_number = cartridge.map.get_tile(row, col+scroll_x)
                attr = cartridge.map.get_attr(row, col+scroll_x)
                if tile_number > 0:
                    tile = cartridge.tile_map[tile_number - 1]
                    tile_surface = surface_for_tile(tile, cartridge=cartridge, attr=attr)
                    surface.blit(tile_surface, (col * cart.TileMap.tile_width, row * cart.TileMap.tile_width))
        # may want option for smoothscale
        pygame.transform.scale(surface, (1024, 768), display_surface)
        pygame.display.update()
        scroll_x += 1
        if scroll_x > cart.Map.section_width * 2:
            scroll_x = 0
        clock.tick(60)
    pygame.quit()
    return 0


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
