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
        self.game = None
        self.scroll_buffer = None

    def render(self):
        clock = pygame.time.Clock()
        pygame.init()
        display_surface = pygame.display.set_mode((1024, 768))
        # display_surface = pygame.display.set_mode((1440, 900), pygame.FULLSCREEN)
        view_surface = pygame.Surface((map.Map.section_width * tile.TILE_SIZE, map.Map.section_height * tile.TILE_SIZE))
        pressed_keys = set()
        self.scroll_buffer = ScrollBuffer(renderer=self)
        scroll_x = 0
        scroll_y = 0
        # testing sprites
        camera = Camera(scroll_buffer=self.scroll_buffer, follow_mode=Camera.FOLLOW_CENTER)
        self.game = game.Game(self.cartridge)
        bob = game.Entity(
            LocalCoord().moved(map.Map.section_width / 2 * tile.TILE_SIZE, (map.Map.section_height / 2) * tile.TILE_SIZE),
            # LocalCoord(),
            tiled_area=map.TiledArea(
                tile_data=[0xD, 0xE, 0xF, 0x10, 0x11, 0x12],
                attr_data=[2, 2, 2, 2, 2, 2],
                width=2,
                height=3
            )
        )
        
        self.game.add_entity(bob)
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
                    if event.key == pygame.K_ESCAPE:
                        is_running = False
                    if event.key in pressed_keys:
                        pressed_keys.remove(event.key)
            for key in pressed_keys:
                if key == pygame.K_RIGHT:
                    bob.vector = bob.vector.add(physics.Vector(x=1, y=0))
                elif key == pygame.K_LEFT:
                    bob.vector = bob.vector.add(physics.Vector(x=-1, y=0))
                elif key == pygame.K_DOWN:
                    bob.vector = bob.vector.add(physics.Vector(x=0, y=1))
                elif key == pygame.K_UP:
                    bob.vector = bob.vector.add(physics.Vector(x=0, y=-1))
            self.game.advance()
            camera.follow(bob.coord.as_pixels().x, bob.coord.as_pixels().y)
            self.scroll_buffer.render(view_surface)
            self.render_entities(view_surface)
            # may want option for smoothscale
            pygame.transform.scale(view_surface, (1024, 768), display_surface)
            pygame.display.update()
            clock.tick(60)
        pygame.quit()

    def render_entities(self, view_surface):
        for entity in self.game.entities:
            for row in range(0, entity.tiled_area.height):
                for col in range(0, entity.tiled_area.width):
                    coord = entity.coord.moved(col * tile.TILE_SIZE, row * tile.TILE_SIZE)
                    tile_number, attr = entity.tiled_area.tiles[row][col]
                    tile_surface = self.surface_for_tile(tile_number, attr)
                    if tile_surface:
                        view_surface.blit(tile_surface, (
                            coord.tile.x * tile.TILE_SIZE + coord.pixel.x,
                            coord.tile.y * tile.TILE_SIZE + coord.pixel.y)
                        )

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
        surface.set_colorkey((1, 1, 1))
        pix_array = pygame.PixelArray(surface)
        for row in range(0, tile.TILE_SIZE):
            for col in range(0, tile.TILE_SIZE):
                p = tile_data[row][col]
                if p > 0:
                    color = self.cartridge.lookup_background_color(palette, p)
                else:
                    color = (1, 1, 1)
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
        self.x = x
        self.y = y
        self.follow_mode = follow_mode
        self.scroll_buffer = scroll_buffer
        
    def follow(self, x, y):
        if self.follow_mode == Camera.FOLLOW_CENTER:
            delta_x = x - self.x
            delta_y = y - self.y
            self.x = x
            self.y = y
            self.scroll_buffer.scroll(delta_x, 0)
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
        quad_surface = lambda: pygame.Surface((map.Map.section_width * tile.TILE_SIZE, map.Map.section_height * tile.TILE_SIZE))
        self.quadrants = [
            [quad_surface(), quad_surface()],
            [quad_surface(), quad_surface()]
        ]
        self.quadrants[0][0].fill((255, 0, 0))
        self.quadrants[0][1].fill((0, 255, 0))
        self.quadrants[1][0].fill((0, 0, 255))
        self.quadrants[1][1].fill((255, 0, 255))
        self.map_offset = (-int(map.Map.section_width / 2), -int(map.Map.section_height / 2))
        self.coord = LocalCoord()
        self.coord = self.coord.moved(int(map.Map.section_width / 2) * tile.TILE_SIZE, int(map.Map.section_height / 2) * tile.TILE_SIZE)
        # fill in the whole buffer initially
        upper_left = self.coord
        lower_right = upper_left.moved((map.Map.section_width + 1) * tile.TILE_SIZE, (map.Map.section_height + 1) * tile.TILE_SIZE)
        self.draw_rect(upper_left, lower_right)
        
    def render(self, surface):
        left = self.coord.tile.x * tile.TILE_SIZE + self.coord.pixel.x
        top = self.coord.tile.y * tile.TILE_SIZE + self.coord.pixel.y
        right = left + ScrollBuffer.quad_width
        bottom = top + ScrollBuffer.quad_height
        quadrant_x = clamp(self.coord.quadrant.x, 0, 1)
        quadrant_y = clamp(self.coord.quadrant.y, 0, 1)
        if quadrant_y == 0:
            if quadrant_x == 0:
                top_left = self.quadrants[0][0] #0
                top_right = self.quadrants[0][1] #1
                bottom_left = self.quadrants[1][0] #2
                bottom_right = self.quadrants[1][1] #3
            else:
                top_left = self.quadrants[0][1]
                top_right = self.quadrants[0][0]
                bottom_left = self.quadrants[1][1]
                bottom_right = self.quadrants[1][0]
        else:
            if quadrant_x == 0:
                top_left = self.quadrants[1][0]
                top_right = self.quadrants[1][1]
                bottom_left = self.quadrants[0][0]
                bottom_right = self.quadrants[0][1]
            else:
                top_left = self.quadrants[1][1]
                top_right = self.quadrants[1][0]
                bottom_left = self.quadrants[0][1]
                bottom_right = self.quadrants[0][0]
        surface.blit(top_left, (0, 0), area=(left, top, ScrollBuffer.quad_width - left, ScrollBuffer.quad_height - top))
        surface.blit(top_right, (ScrollBuffer.quad_width - left, 0), area=(0, top, right, ScrollBuffer.quad_height - top))
        surface.blit(bottom_left, (0, ScrollBuffer.quad_height - top), area=(left, 0, ScrollBuffer.quad_width - left, bottom))
        surface.blit(bottom_right, (ScrollBuffer.quad_width - left, ScrollBuffer.quad_height - top), area=(0, 0, right, bottom))

    def scroll(self, delta_x, delta_y):
        old_coord = self.coord
        self.coord = self.coord.moved(delta_x, delta_y)
        delta_x_tiles = self.coord.as_tiles().x - old_coord.as_tiles().x
        delta_y_tiles = self.coord.as_tiles().y - old_coord.as_tiles().y
        for x in range(0, abs(delta_x_tiles)):
            if delta_x_tiles >= 0:
                top_left = old_coord.moved((map.Map.section_width + x + 1) * tile.TILE_SIZE, 0)
                bottom_right = top_left.moved(tile.TILE_SIZE, (map.Map.section_height + 1) * tile.TILE_SIZE)
                self.draw_rect(top_left, bottom_right)
            else:
                top_left = old_coord.moved(-x - 1, old_coord.tile.y)
                bottom_right = top_left.moved(tile.TILE_SIZE, (map.Map.section_height * 2) * tile.TILE_SIZE)
                self.draw_rect(top_left, bottom_right)
        for y in range(0, abs(delta_y_tiles)):
            if delta_y_tiles >= 0:
                top_left = old_coord.moved(old_coord.tile.x, (map.Map.section_height + y + 1) * tile.TILE_SIZE)
                bottom_right = top_left.moved((map.Map.section_width * 2) * tile.TILE_SIZE, tile.TILE_SIZE)
                self.draw_rect(top_left, bottom_right)
            else:
                top_left = old_coord.moved(old_coord.tile.x, -y)
                bottom_right = top_left.moved((map.Map.section_width *2) * tile.TILE_SIZE, tile.TILE_SIZE)
                self.draw_rect(top_left, bottom_right)

    def draw_rect(self, top_left, bottom_right):
        map_offset_x, map_offset_y = self.map_offset
        width = abs(bottom_right.as_tiles().x - top_left.as_tiles().x)
        height = abs(bottom_right.as_tiles().y - top_left.as_tiles().y)
        for row in range(0, height):
            for col in range(0, width):
                coord = top_left.moved(col * tile.TILE_SIZE, row * tile.TILE_SIZE)
                quadrant_x = clamp(coord.quadrant.x, 0, 1)
                quadrant_y = clamp(coord.quadrant.y, 0, 1)
                quadrant = self.quadrants[quadrant_y][quadrant_x]
                quadrant.fill(self.renderer.cartridge.lookup_universal_background_color(),
                    (
                        coord.tile.x * tile.TILE_SIZE + coord.pixel.x,
                        coord.tile.y * tile.TILE_SIZE + coord.pixel.y,
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
                        coord.tile.x * tile.TILE_SIZE,
                        coord.tile.y * tile.TILE_SIZE)
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
        if delta_x >= 0:
            move_remain = abs(delta_x) + total_pixels_x
        else:
            move_remain = total_pixels_x - abs(delta_x)
            if move_remain < 0:
                move_remain = total_pixels_x
        quadrant_x = tile_x = pixel_x = 0
        while move_remain >= map.Map.section_width * tile.TILE_SIZE:
            quadrant_x += 1
            move_remain -= map.Map.section_width * tile.TILE_SIZE
        while move_remain >= tile.TILE_SIZE:
            tile_x += 1
            move_remain -= tile.TILE_SIZE
        pixel_x = move_remain
        # move in the y direction
        if delta_y >= 0:
            move_remain = abs(delta_y) + total_pixels_y
        else:
            move_remain = total_pixels_y - abs(delta_y)
        quadrant_y = tile_y = pixel_y = 0
        while move_remain >= map.Map.section_height * tile.TILE_SIZE:
            quadrant_y += 1
            move_remain -= map.Map.section_height * tile.TILE_SIZE
        while move_remain >= tile.TILE_SIZE:
            tile_y += 1
            move_remain -= tile.TILE_SIZE
        pixel_y = move_remain
        new_coord.quadrant = Point(quadrant_x, quadrant_y)
        new_coord.tile = Point(tile_x, tile_y)
        new_coord.pixel = Point(pixel_x, pixel_y)
        return new_coord

    def truncated_pixels(self):
        new_coord = LocalCoord()
        new_coord.quadrant = self.quadrant
        new_coord.tile = self.tile
        new_coord.pixel = Point(0, 0)
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
