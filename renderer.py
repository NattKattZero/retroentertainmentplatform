import math
from collections import namedtuple

import pygame

import cart
import game
import tile
import map
import physics

Point = namedtuple('Point', ['x', 'y'])

class Renderer:
    def __init__(self, cartridge):
        self.cartridge = cartridge
        self.tile_surface_cache = {}

    def render(self):
        clock = pygame.time.Clock()
        pygame.init()
        display_surface = pygame.display.set_mode((1024, 768))
        # display_surface = pygame.display.set_mode((1440, 900), pygame.FULLSCREEN)
        view_surface = pygame.Surface((map.Map.section_width * tile.TILE_SIZE, map.Map.section_height * tile.TILE_SIZE))
        pressed_keys = set()
        scroll_buffer = ScrollBuffer(renderer=self)
        scroll_x = 0
        scroll_y = 0
        # testing sprites
        camera = Camera(scroll_buffer=scroll_buffer, follow_mode=Camera.FOLLOW_CENTER)
        bob_game = game.Game(self.cartridge)
        bob = game.Entity(
            pygame.Rect(
                map.Map.section_width / 8 * tile.TILE_SIZE,
                map.Map.section_height / 2 * tile.TILE_SIZE,
                2 * tile.TILE_SIZE,
                3 * tile.TILE_SIZE
            ),
            tiled_area=map.TiledArea(
                tile_data=[0xD, 0xE, 0xF, 0x10, 0x11, 0x12],
                attr_data=[2, 2, 2, 2, 2, 2],
                width=2,
                height=3
            )
        )

        bob_game.add_entity(bob)
        # -
        is_running = True
        while is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        if pygame.K_LEFT in pressed_keys:
                            pressed_keys.remove(pygame.K_LEFT)
                    elif event.key == pygame.K_LEFT:
                        if pygame.K_RIGHT in pressed_keys:
                            pressed_keys.remove(pygame.K_RIGHT)
                    elif event.key == pygame.K_UP:
                        if pygame.K_DOWN in pressed_keys:
                            pressed_keys.remove(pygame.K_DOWN)
                    elif event.key == pygame.K_DOWN:
                        if pygame.K_UP in pressed_keys:
                            pressed_keys.remove(pygame.K_UP)
                    elif event.key == pygame.K_SPACE:
                        bob.vector = bob.vector.add(physics.Vector(x=0, y=-25))
                    pressed_keys.add(event.key)
                elif event.type == pygame.KEYUP:
                    if event.key in pressed_keys:
                        pressed_keys.remove(event.key)
            for key in pressed_keys:
                if key == pygame.K_RIGHT:
                    bob.vector = bob.vector.add(physics.Vector(x=3, y=0))
                elif key == pygame.K_LEFT:
                    bob.vector = bob.vector.add(physics.Vector(x=-3, y=0))
                elif key == pygame.K_DOWN:
                    bob.vector = bob.vector.add(physics.Vector(x=0, y=3))
                elif key == pygame.K_UP:
                    bob.vector = bob.vector.add(physics.Vector(x=0, y=-3))
            bob_game.advance()
            # camera.follow(bob.rect.left, bob.rect.top)
            scroll_buffer.render(view_surface)
            scroll_buffer.scroll(1, 0)
            self.render_entities(bob_game.entities, view_surface, scroll_buffer)
            # may want option for smoothscale
            pygame.transform.scale(view_surface, (1024, 768), display_surface)
            pygame.display.update()
            clock.tick(60)
        pygame.quit()

    def render_entities(self, entities, view_surface, scroll_buffer):
        pass
        # for entity in entities:
        #     x, y = scroll_buffer.map_to_view_coord((entity.rect.x, entity.rect.y))
        #     for row, tile_row in enumerate(entity.tiled_area.tiles):
        #         for col, tile_and_attr in enumerate(tile_row):
        #             tile_number, attr = tile_and_attr
        #             surface = self.surface_for_tile(tile_number, attr=attr)
        #             view_surface.blit(surface, (x + col * tile.TILE_SIZE, y + row * tile.TILE_SIZE))

    def surface_for_map_tile(self, map_col, map_row):
        tile_number = self.cartridge.map.get_tile(map_row, map_col)
        if tile_number <= 0:
            return None
        attr = self.cartridge.map.get_attr(map_row, map_col)
        return self.surface_for_tile(tile_number, attr)

    def surface_for_tile(self, tile_number, attr=0):
        if tile_number <= 0:
            return None
        tile_lookup = (tile_number, attr)
        if tile_lookup in self.tile_surface_cache:
            return self.tile_surface_cache[tile_lookup]
        transform = (attr >> 4) & 0xF
        palette = attr & 0xF
        tile_data = self.cartridge.tile_catalog[tile_number - 1]
        surface = pygame.Surface((tile.TILE_SIZE, tile.TILE_SIZE))
        pix_array = pygame.PixelArray(surface)
        for row in range(0, tile.TILE_SIZE):
            for col in range(0, tile.TILE_SIZE):
                p = tile_data[row][col]
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

        
class Camera:
    FOLLOW_CENTER = 0
    FOLLOW_STATIC = 1
    FOLLOW_LEAD = 2
    
    def __init__(self, x=0, y=0, follow_mode=0, scroll_buffer=None):
        self.x = 0
        self.y = 0
        self.follow_mode = follow_mode
        self.scroll_buffer = scroll_buffer
        
    def follow(self, x, y):
        if self.follow_mode == Camera.FOLLOW_CENTER:
            new_x = x - (map.Map.section_width * tile.TILE_SIZE) / 2
            new_y = y - (map.Map.section_height * tile.TILE_SIZE) / 2
            delta_x = new_x - self.x
            delta_y = new_y - self.y
            self.x = new_x
            self.y = new_y
            self.scroll_buffer.scroll(delta_x, delta_y)
        elif self.follow_mode == Camera.FOLLOW_LEAD:
            view_x, view_y = self.scroll_buffer.map_to_view_coord((x, y))
            if view_x < (map.Map.section_width * tile.TILE_SIZE) * ( 1 / 3 ) or view_x > (map.Map.section_width * tile.TILE_SIZE) * ( 2 / 3 ):
                delta_x = x - self.x
                self.x = x - 30
                self.scroll_buffer.scroll(delta_x - 30, 0)


class ScrollBuffer:
    quad_width = map.Map.section_width * tile.TILE_SIZE
    quad_height = map.Map.section_height * tile.TILE_SIZE

    def __init__(self, renderer):
        self.renderer = renderer
        self.quadrants = [
            pygame.Surface((map.Map.section_width * tile.TILE_SIZE, map.Map.section_height * tile.TILE_SIZE))
            for _ in range(0, 4)
        ]
        self.quadrants[0].fill((255, 0, 0))
        self.quadrants[1].fill((0, 255, 0))
        self.quadrants[2].fill((0, 0, 255))
        self.quadrants[3].fill((255, 0, 255))
        self.map_offset = (-int(map.Map.section_width / 2), -int(map.Map.section_height / 2))
        self.coord = LocalCoord()
        self.coord = self.coord.moved(int(map.Map.section_width / 2) * tile.TILE_SIZE, int(map.Map.section_height / 2) * tile.TILE_SIZE)
        # fill in the whole buffer initially
        upper_left = LocalCoord()
        upper_left.left = 0
        upper_left.top = 0
        lower_right = LocalCoord()
        lower_right.right = map.Map.section_width * 2
        lower_right.bottom = map.Map.section_height * 2
        self.draw_rect(upper_left, lower_right)
    
    def swap_vertical_axis(self):
        top_left, top_right, bottom_left, bottom_right = self.quadrants
        self.quadrants = [top_right, top_left, bottom_right, bottom_left]
        
    def swap_horizontal_axis(self):
        top_left, top_right, bottom_left, bottom_right = self.quadrants
        self.quadrants = [bottom_left, bottom_right, top_left, top_right]
        
    def render(self, surface):
        left = self.coord.tile.x * tile.TILE_SIZE + self.coord.pixel.x
        top = self.coord.tile.y * tile.TILE_SIZE + self.coord.pixel.y
        right = left + ScrollBuffer.quad_width
        bottom = top + ScrollBuffer.quad_height
        if self.coord.quadrant.y == 0:
            if self.coord.quadrant.x == 0:
                top_left = self.quadrants[0]
                top_right = self.quadrants[1]
                bottom_left = self.quadrants[2]
                bottom_right = self.quadrants[3]
            else:
                top_left = self.quadrants[1]
                top_right = self.quadrants[0]
                bottom_left = self.quadrants[3]
                bottom_right = self.quadrants[2]
        else:
            if self.coord.quadrant[0] == 0:
                top_left = self.quadrants[2]
                top_right = self.quadrants[3]
                bottom_left = self.quadrants[0]
                bottom_right = self.quadrants[1]
            else:
                top_left = self.quadrants[3]
                top_right = self.quadrants[2]
                bottom_left = self.quadrants[1]
                bottom_right = self.quadrants[0]
        surface.blit(top_left, (0, 0), area=(left, top, ScrollBuffer.quad_width - left, ScrollBuffer.quad_height - top))
        surface.blit(top_right, (ScrollBuffer.quad_width - left, 0), area=(0, top, right, ScrollBuffer.quad_height - top))
        surface.blit(bottom_left, (0, ScrollBuffer.quad_height - top), area=(left, 0, ScrollBuffer.quad_width - left, bottom))
        surface.blit(bottom_right, (ScrollBuffer.quad_width - left, ScrollBuffer.quad_height - top), area=(0, 0, right, bottom))

    def scroll(self, delta_x, delta_y):
        self.coord = self.coord.moved(delta_x, delta_y)
        top_left = self.coord
        bottom_right = top_left.moved(map.Map.section_width * tile.TILE_SIZE + 1, map.Map.section_height * tile.TILE_SIZE + 1)
        self.draw_rect(top_left, bottom_right)

    def draw_rect(self, top_left, bottom_right):
        # print(f'draw_rect. top_left: {top_left}, bottom_right: {bottom_right}')
        top_left_quad, top_right_quad, bottom_left_quad, bottom_right_quad = self.quadrants
        map_offset_x, map_offset_y = self.map_offset
        # FIXME: should use bottom_right instead of hard-coding width/height
        width = abs(bottom_right.as_tiles().x - top_left.as_tiles().x) + 1
        height = abs(bottom_right.as_tiles().y - top_left.as_tiles().y) + 1
        # for row in range(0, map.Map.section_height):
        for row in range(top_left.tile.y, height):
            # for col in range(map.Map.section_width+1, map.Map.section_width+2):
            for col in range(top_left.tile.x, width):
                coord = top_left.moved(col * tile.TILE_SIZE, row * tile.TILE_SIZE)
                quadrant_x = clamp(coord.quadrant.x, 0, 1)
                quadrant_y = clamp(coord.quadrant.y, 0, 1)
                if quadrant_y == 0:
                    if quadrant_x == 0:
                        quadrant = top_left_quad
                        quad_offset_x = 0
                        quad_offset_y = 0
                    else:
                        quadrant = top_right_quad
                        quad_offset_x = map.Map.section_width
                        quad_offset_y = 0
                else:
                    if quadrant_x == 0:
                        quadrant = bottom_left_quad
                        quad_offset_x = 0
                        quad_offset_y = map.Map.section_height
                    else:
                        quadrant = bottom_right_quad
                        quad_offset_x = map.Map.section_width
                        quad_offset_y = map.Map.section_height
                quadrant.fill(self.renderer.cartridge.lookup_universal_background_color(),
                    (
                        (top_left.tile.x + col - quad_offset_x) * tile.TILE_SIZE,
                        (top_left.tile.y + row - quad_offset_y) * tile.TILE_SIZE,
                        tile.TILE_SIZE,
                        tile.TILE_SIZE
                    )
                )
                tile_surface = self.renderer.surface_for_map_tile(
                    (coord.quadrant.x * map.Map.section_width + coord.tile.x) + map_offset_x,
                    (coord.quadrant.y * map.Map.section_height + coord.tile.y) + map_offset_y
                )
                if tile_surface:
                    quadrant.blit(tile_surface, (
                        (top_left.tile.x + col - quad_offset_x) * tile.TILE_SIZE,
                        (top_left.tile.y + row - quad_offset_y) * tile.TILE_SIZE)
                    )


def clamp(n, min_n, max_n):
    if n > max_n:
        while n > max_n:
            n -= (max_n - min_n + 1)
        return n
    elif n < min_n:
        while n < min_n:
            n += (max_n - min_n + 1)
        return n
    return n

class LocalCoord():
    def __init__(self):
        self.quadrant = Point(0, 0)
        self.tile = Point(0, 0)
        self.pixel = Point(0, 0)

    def moved(self, delta_x, delta_y):
        new_coord = LocalCoord()
        quadrant_x, quadrant_y = self.quadrant
        tile_x, tile_y = self.tile
        pixel_x, pixel_y = self.pixel
        total_pixels_x, total_pixels_y = self.as_pixels()
        # move in the x direction
        move_direc = -1 if delta_x < 0 else 1
        move_remain = abs(delta_x) + total_pixels_x
        quadrant_x = tile_x = pixel_x = 0
        while move_remain >= map.Map.section_width * tile.TILE_SIZE:
            quadrant_x += move_direc
            move_remain -= map.Map.section_width * tile.TILE_SIZE
        # quadrant_x = clamp(quadrant_x, 0, 1)
        while move_remain >= tile.TILE_SIZE:
            tile_x += move_direc
            move_remain -= tile.TILE_SIZE
        if move_direc >= 0:
            pixel_x = move_remain
        else:
            pixel_x = tile.TILE_SIZE - move_remain
        # move in the y direction
        move_direc = -1 if delta_y < 0 else 1
        move_remain = abs(delta_y) + total_pixels_y
        quadrant_y = tile_y = pixel_y = 0
        while move_remain >= map.Map.section_height * tile.TILE_SIZE:
            quadrant_y += move_direc
            move_remain -= map.Map.section_height * tile.TILE_SIZE
        # quadrant_y = clamp(quadrant_y, 0, 1)
        while move_remain >= tile.TILE_SIZE:
            tile_y += move_direc
            move_remain -= tile.TILE_SIZE
        if move_direc >= 0:
            pixel_y = move_remain
        else:
            pixel_y = tile.TILE_SIZE - move_remain
        new_coord.quadrant = Point(quadrant_x, quadrant_y)
        new_coord.tile = Point(tile_x, tile_y)
        new_coord.pixel = Point(pixel_x, pixel_y)
        return new_coord

    def as_pixels(self):
        pixels_x = self.quadrant.x * map.Map.section_width * tile.TILE_SIZE + self.tile.x * tile.TILE_SIZE + self.pixel.x
        pixels_y = self.quadrant.y * map.Map.section_height * tile.TILE_SIZE + self.tile.y * tile.TILE_SIZE + self.pixel.y
        return Point(pixels_x, pixels_y)

    def as_tiles(self):
        tiles_x = self.quadrant.x * map.Map.section_width + self.tile.x
        tiles_y = self.quadrant.y * map.Map.section_height + self.tile.y
        return Point(tiles_x, tiles_y)

    def __str__(self):
        return f'quad: ({self.quadrant.x}, {self.quadrant.y}), tile: ({self.tile.x}, {self.tile.y}), pixel: ({self.pixel.x}, {self.pixel.y})'
