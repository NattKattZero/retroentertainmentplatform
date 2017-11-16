import math

import pygame

import cart
import game
import tile
import map
import physics

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
        coord_x = int(map.Map.section_width / 2)
        coord_y = int(map.Map.section_height / 2)
        self.coord = (coord_x, coord_y)  # col, row
        self.map_coord = (-coord_x, -coord_y)  # col, row
        self.offset = (0, 0)  # pixel offset
        # self.draw_rect(0, 0, map.Map.section_width * 2, map.Map.section_height * 2)
    
    def swap_vertical_axis(self):
        top_left, top_right, bottom_left, bottom_right = self.quadrants
        self.quadrants = [top_right, top_left, bottom_right, bottom_left]
        
    def swap_horizontal_axis(self):
        top_left, top_right, bottom_left, bottom_right = self.quadrants
        self.quadrants = [bottom_left, bottom_right, top_left, top_right]
        
    def render(self, surface):
        col, row = self.coord
        offset_x, offset_y = self.offset
        left = col * tile.TILE_SIZE + offset_x
        top = row * tile.TILE_SIZE + offset_y
        right = left + ScrollBuffer.quad_width
        bottom = top + ScrollBuffer.quad_height
        surface.blit(self.quadrants[0], (0, 0), area=(left, top, ScrollBuffer.quad_width - left, ScrollBuffer.quad_height - top))
        surface.blit(self.quadrants[1], (ScrollBuffer.quad_width - left, 0), area=(0, top, right, ScrollBuffer.quad_height - top))
        surface.blit(self.quadrants[2], (0, ScrollBuffer.quad_height - top), area=(left, 0, ScrollBuffer.quad_width - left, bottom))
        surface.blit(self.quadrants[3], (ScrollBuffer.quad_width - left, ScrollBuffer.quad_height - top), area=(0, 0, right, bottom))

    def scroll(self, delta_x, delta_y):
        coord_x, coord_y = self.coord
        map_coord_x, map_coord_y = self.map_coord
        offset_x, offset_y = self.offset
        scroll_direc = 1 if delta_x >= 0 else -1
        # offset isn't accumulating correctly, this needs thought
        offset_x += delta_x
        while abs(offset_x) >= tile.TILE_SIZE:
            coord_x += scroll_direc
            # map_coord_x += scroll_direc
            offset_x -= (scroll_direc * tile.TILE_SIZE)
            if coord_x < 0 or coord_x > map.Map.section_width:
                coord_x = clamp(coord_x, 0, map.Map.section_width)
                self.swap_vertical_axis()
                map_coord_x += map.Map.section_width
                self.map_coord = (map_coord_x, map_coord_y)
            if scroll_direc > 0:
                self.draw_rect(int(coord_x + map.Map.section_width + 1), 0, 1, int(map.Map.section_height * 2))
            elif scroll_direc < 0:
                self.draw_rect(int(coord_x - 1), 0, 1, int(map.Map.section_height * 2))
        # print(f'coord_x: {coord_x}, offset_x: {offset_x}')
        """
        scroll_amt = offset_x + abs(delta_x)
        while scroll_amt > 0:
            if scroll_amt >= tile.TILE_SIZE:
                coord_x += scroll_direc
                map_coord_x += scroll_direc
                scroll_amt -= tile.TILE_SIZE
                if coord_x < 0 or coord_x > map.Map.section_width:
                    coord_x = clamp(coord_x, 0, map.Map.section_width)
                    self.swap_vertical_axis()
                if scroll_amt == 0:
                    offset_x = 0
                if scroll_direc > 0:
                    self.map_coord = (map_coord_x, map_coord_y)
                    self.draw_rect(int(coord_x + map.Map.section_width + 1), 0, 1, int(map.Map.section_height * 2))
                elif scroll_direc < 0:
                    self.map_coord = (map_coord_x, map_coord_y)
                    self.draw_rect(int(coord_x - 1), 0, 1, int(map.Map.section_height * 2))
            else:
                if scroll_direc >= 0:
                    offset_x = scroll_amt
                else:
                    offset_x = tile.TILE_SIZE - scroll_amt
                scroll_amt = 0
        """
        """
        scroll_direc = 1 if delta_y >=0 else -1
        scroll_amt = abs(delta_y)
        while scroll_amt > 0:
            if scroll_amt >= tile.TILE_SIZE:
                coord_y += scroll_direc
                map_coord_y += scroll_direc
                scroll_amt -= tile.TILE_SIZE
                if coord_y < 0 or coord_y > map.Map.section_height * 2:
                    coord_y = clamp(coord_y, 0, map.Map.section_height * 2)
                    self.swap_horizontal_axis()
            else:
                if scroll_direc >= 0:
                    offset_y = scroll_amt
                else:
                    offset_y = tile.TILE_SIZE - scroll_amt
                scroll_amt = 0
        """
        self.coord = (coord_x, coord_y)
        self.map_coord = (map_coord_x, map_coord_y)
        self.offset = (offset_x, offset_y)

    def draw_rect(self, x, y, width, height): 
        top_left, top_right, bottom_left, bottom_right = self.quadrants
        map_coord_x, map_coord_y = self.map_coord
        print(f'draw_rect: x:{x}, map_coord_x:{map_coord_x}')
        for row in range(y, y + height):
            for col in range(x, x + width):
                if row < map.Map.section_height:
                    if col < map.Map.section_width:
                        quadrant = top_left
                        quad_offset_x = 0
                        quad_offset_y = 0
                    else:
                        quadrant = top_right
                        quad_offset_x = map.Map.section_width + 1
                        quad_offset_y = 0
                else:
                    if col < map.Map.section_width:
                        quadrant = bottom_left
                        quad_offset_x = 0
                        quad_offset_y = map.Map.section_height
                    else:
                        quadrant = bottom_right
                        quad_offset_x = map.Map.section_width + 1
                        quad_offset_y = map.Map.section_height
                quadrant.fill(self.renderer.cartridge.lookup_universal_background_color(),
                    (
                        (col - quad_offset_x) * tile.TILE_SIZE,
                        (row - quad_offset_y) * tile.TILE_SIZE,
                        tile.TILE_SIZE,
                        tile.TILE_SIZE
                    )
                )
                tile_surface = self.renderer.surface_for_map_tile(int(map_coord_x + col), int(map_coord_y + row))
                if tile_surface:
                    quadrant.blit(tile_surface, (
                        (col - quad_offset_x) * tile.TILE_SIZE,
                        (row - quad_offset_y) * tile.TILE_SIZE)
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
