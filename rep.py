#!/usr/bin/env python3

import sys

import pygame

import cart

def main():
    scroll_x = 0
    scroll_y = 0
    clock = pygame.time.Clock()
    pygame.init()
    display_surface = pygame.display.set_mode((1024, 768))
    # display_surface = pygame.display.set_mode((1440, 900), pygame.FULLSCREEN)
    surface = pygame.Surface((cart.Map.section_width * cart.TileMap.tile_width, cart.Map.section_height * cart.TileMap.tile_width))
    testcart = cart.load_cart('testcart.cart')
    tile_map = testcart.map[0]
    attr_map = testcart.attr_map[0]
    is_running = True
    while is_running:
        surface.fill(testcart.lookup_universal_background_color())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
        for row in range(0, cart.Map.section_height):
            for col in range(0, cart.Map.section_width):
                tile_number = tile_map[row][col]
                attr = attr_map[row][col]
                if tile_number > 0:
                    tile = testcart.tile_map[tile_number - 1]
                    tile_surface = surface_for_tile(tile, cartridge=testcart, attr=attr)
                    surface.blit(tile_surface, (scroll_x + (col * cart.TileMap.tile_width), row * cart.TileMap.tile_width))
        # may want option for smoothscale
        pygame.transform.scale(surface, (1024, 768), display_surface)
        pygame.display.update()
        # scroll_x -= 1
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
