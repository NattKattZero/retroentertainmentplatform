#!/usr/bin/env python3

import sys
import argparse
import math

import pygame

import cart

class Renderer:
    def __init__(self, cartridge):
        self.cartridge = cartridge
        self.tile_surface_cache = {}

    def render(self):
        clock = pygame.time.Clock()
        pygame.init()
        display_surface = pygame.display.set_mode((1024, 768))
        # display_surface = pygame.display.set_mode((1440, 900), pygame.FULLSCREEN)
        view_surface = pygame.Surface((cart.Map.section_width * cart.TileMap.tile_width, cart.Map.section_height * cart.TileMap.tile_width))
        scroll_buffer = ScrollBuffer(renderer=self)
        scroll_x = 0
        # testing sprites
        bob = self.surface_for_tile(0xD, attr=2)
        bob_x = 0
        # -
        is_running = True
        while is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        scroll_x = 1
                    elif event.key == pygame.K_LEFT:
                        scroll_x = -1
                elif event.type == pygame.KEYUP:
                    scroll_x = 0
            if scroll_x != 0:
                if abs(scroll_x) < 10:
                    if scroll_x > 0:
                        scroll_x += 1
                    else:
                        scroll_x -= 1
                scroll_buffer.scroll(scroll_x, 0)
            scroll_buffer.render(view_surface)
            # testing sprites
            bob_x += scroll_x
            sprite_coord = scroll_buffer.map_to_view_coord((cart.Map.section_height / 2 * cart.TileMap.tile_width + bob_x, cart.Map.section_height * cart.TileMap.tile_width - 5 * cart.TileMap.tile_width))
            view_surface.blit(bob, sprite_coord)
            # may want option for smoothscale
            pygame.transform.scale(view_surface, (1024, 768), display_surface)
            pygame.display.update()
            clock.tick(60)
        pygame.quit()

    def surface_for_map_tile(self, map_row, map_col):
        tile_number = self.cartridge.map.get_tile(map_row, map_col)
        if tile_number <= 0:
            return None
        attr = self.cartridge.map.get_attr(map_row, map_col)
        return self.surface_for_tile(tile_number, attr)

    def surface_for_tile(self, tile_number, attr=0):
        tile_lookup = (tile_number, attr)
        if tile_lookup in self.tile_surface_cache:
            return self.tile_surface_cache[tile_lookup]
        transform = (attr >> 4) & 0xF
        palette = attr & 0xF
        tile = self.cartridge.tile_map[tile_number - 1]
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
        self.tile_surface_cache[tile_lookup] = surface
        return surface
      
        
class ScrollBuffer:
    quad_width = cart.Map.section_width * cart.TileMap.tile_width
    quad_height = cart.Map.section_height * cart.TileMap.tile_width
    
    def __init__(self, renderer):
        self.renderer = renderer
        self.quadrants = [
            pygame.Surface((cart.Map.section_width * cart.TileMap.tile_width, cart.Map.section_height * cart.TileMap.tile_width))
            for i in range(0, 4)
        ]
        self.quadrants[0].fill((255, 0, 0))
        self.quadrants[1].fill((0, 255, 0))
        self.quadrants[2].fill((0, 0, 255))
        self.quadrants[3].fill((255, 0, 255))
        # left, top, right, bottom
        self.view_rect = (
            ScrollBuffer.quad_width / 2,
            ScrollBuffer.quad_height / 2,
            ScrollBuffer.quad_width / 2 + ScrollBuffer.quad_width,
            ScrollBuffer.quad_height / 2 + ScrollBuffer.quad_height
        )
        self.map_coord = (0, 0)
        self.redraw()
        
    def scroll(self, delta_x, delta_y):
        x, y = self.map_coord
        self.map_coord = (x + delta_x, y + delta_y)
        left, top, right, bottom = self.view_rect
        left += delta_x
        right += delta_x
        if left >= ScrollBuffer.quad_width:
            left = left - ScrollBuffer.quad_width
            right = right - ScrollBuffer.quad_width
            self.swap_vertical_axis()
        elif left <= 0:
            left = left + ScrollBuffer.quad_width
            right = right + ScrollBuffer.quad_width
            self.swap_vertical_axis()
        top += delta_y
        bottom += delta_y
        if top >= ScrollBuffer.quad_height:
            top = top - ScrollBuffer.quad_height
            bottom = bottom - ScrollBuffer.quad_height
            self.swap_horizontal_axis()
        elif top <= 0:
            top = top + ScrollBuffer.quad_height
            bottom = bottom + ScrollBuffer.quad_height
            self.swap_horizontal_axis()
        self.view_rect = [left, top, right, bottom]
        n_cols_redraw = abs(math.ceil(delta_x / cart.TileMap.tile_width))
        n_rows_redraw = abs(math.ceil(delta_y / cart.TileMap.tile_width))
        row_range = None
        col_range = None
        if delta_x > 0:
            col_range = range(math.floor(x / cart.TileMap.tile_width) + cart.Map.section_width - 1, math.ceil(x / cart.TileMap.tile_width) + cart.Map.section_width + n_cols_redraw)
        elif delta_x < 0:
            col_range = range(math.floor(x / cart.TileMap.tile_width) - n_cols_redraw - 1, math.ceil(x / cart.TileMap.tile_width))
        if delta_y > 0:
            row_range = range(math.floor(y / cart.TileMap.tile_width) + cart.Map.section_height - 1, math.ceil(y / cart.TileMap.tile_width) + cart.Map.section_height + n_rows_redraw)
        elif delta_y < 0:
            row_range = range(math.floor(y / cart.TileMap.tile_width) - n_rows_redraw - 1, math.ceil(y / cart.TileMap.tile_width))
        self.redraw(row_range=row_range, col_range=col_range)
        
        
    def redraw(self, row_range=None, col_range=None):
        left, top, right, bottom = self.view_rect
        x, y = self.map_coord
        start_col = math.floor((x - left) / cart.TileMap.tile_width)
        start_row = math.floor((y - top) / cart.TileMap.tile_width)
        for i, quadrant in enumerate(self.quadrants):
            if i == 0:  # top left
                quad_col = start_col
                quad_row = start_row
            elif i == 1:  # top right
                quad_col = start_col + cart.Map.section_width
                quad_row = start_row
            elif i == 2:  # bottom left
                quad_col = start_col
                quad_row = start_row + cart.Map.section_height
            else:  #  bottom right
                quad_col = start_col + cart.Map.section_width
                quad_row = start_row + cart.Map.section_height
            for row in range(0, cart.Map.section_height):
                map_row = quad_row + row
                if row_range and map_row not in row_range:
                    continue
                for col in range(0, cart.Map.section_width):
                    map_col = quad_col + col
                    if col_range and map_col not in col_range:
                        continue
                    quadrant.fill(self.renderer.cartridge.lookup_universal_background_color(), (col * cart.TileMap.tile_width, row * cart.TileMap.tile_width, cart.TileMap.tile_width, cart.TileMap.tile_width))
                    tile_surface = self.renderer.surface_for_map_tile(map_row, map_col)
                    if tile_surface:
                        quadrant.blit(tile_surface, (col * cart.TileMap.tile_width, row * cart.TileMap.tile_width))
        
    
    def map_to_view_coord(self, map_coord):
        map_x, map_y = map_coord
        x, y = self.map_coord
        return (map_x - x, map_y - y)
        
        
    def swap_vertical_axis(self):
        top_left, top_right, bottom_left, bottom_right = self.quadrants
        self.quadrants = [top_right, top_left, bottom_right, bottom_left]
        
    def swap_horizontal_axis(self):
        top_left, top_right, bottom_left, bottom_right = self.quadrants
        self.quadrants = [bottom_left, bottom_right, top_left, top_right]
        
    def render(self, surface): 
        left, top, right, bottom = self.view_rect
        surface.blit(self.quadrants[0], (0, 0), area=(left, top, ScrollBuffer.quad_width - left, ScrollBuffer.quad_height - top))
        surface.blit(self.quadrants[1], (ScrollBuffer.quad_width - left, 0), area=(0, top, right, ScrollBuffer.quad_height - top))
        surface.blit(self.quadrants[2], (0, ScrollBuffer.quad_height - top), area=(left, 0, ScrollBuffer.quad_width - left, bottom))
        surface.blit(self.quadrants[3], (ScrollBuffer.quad_width - left, ScrollBuffer.quad_height - top), area=(0, 0, right, bottom))
        

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
