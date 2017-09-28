import math

import pygame

import cart
import game
import tile

class Renderer:
    def __init__(self, cartridge):
        self.cartridge = cartridge
        self.tile_surface_cache = {}

    def render(self):
        clock = pygame.time.Clock()
        pygame.init()
        display_surface = pygame.display.set_mode((1024, 768))
        # display_surface = pygame.display.set_mode((1440, 900), pygame.FULLSCREEN)
        view_surface = pygame.Surface((cart.Map.section_width * tile.TILE_SIZE, cart.Map.section_height * tile.TILE_SIZE))
        pressed_keys = set()
        scroll_buffer = ScrollBuffer(renderer=self)
        scroll_x = 0
        scroll_y = 0
        # testing sprites
        camera = Camera(scroll_buffer=scroll_buffer)
        bob_game = game.Game(self.cartridge)
        bob = game.Entity(
            pygame.Rect(
                cart.Map.section_width / 2 * tile.TILE_SIZE,
                cart.Map.section_height / 2 * tile.TILE_SIZE,
                2 * tile.TILE_SIZE,
                3 * tile.TILE_SIZE
            ),
            tile_width = 2,
            tile_height = 3,
            tiles=[0xD, 0xE, 0xF, 0x10, 0x11, 0x12],
            attrs = [2, 2, 2, 2, 2, 2])
        bob_game.add_entity(bob)
        # -
        is_running = True
        while is_running:
            bob_game.advance()
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
                    pressed_keys.add(event.key)
                elif event.type == pygame.KEYUP:
                    if event.key in pressed_keys:
                        pressed_keys.remove(event.key)
            for key in pressed_keys:
                if key == pygame.K_RIGHT:
                    bob.rect.move_ip(5, 0)
                elif key == pygame.K_LEFT:
                    bob.rect.move_ip(-5, 0)
                elif key == pygame.K_DOWN:
                    bob.rect.move_ip(0, 5)
                elif key == pygame.K_UP:
                    bob.rect.move_ip(0, -35)
            camera.follow(bob.rect.left, bob.rect.top)
            scroll_buffer.render(view_surface)
            self.render_entities(bob_game, view_surface, scroll_buffer)
            # may want option for smoothscale
            pygame.transform.scale(view_surface, (1024, 768), display_surface)
            pygame.display.update()
            clock.tick(60)
        pygame.quit()

    def render_entities(self, bob_game, view_surface, scroll_buffer):
        for entity in bob_game.entities:
            x, y = scroll_buffer.map_to_view_coord((entity.rect.x, entity.rect.y))
            for row in range(0, entity.tile_height):
                for col in range(0, entity.tile_width):
                    tile_number = entity.tiles[row * entity.tile_width + col]
                    attr = entity.attrs[row * entity.tile_width + col]
                    surface = self.surface_for_tile(tile_number, attr=attr)
                    view_surface.blit(surface, (x + col * tile.TILE_SIZE, y + row * tile.TILE_SIZE))

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
    FOLLOW_REVEAL = 2
    
    def __init__(self, x=0, y=0, follow_mode=0, scroll_buffer=None):
        self.x = 0
        self.y = 0
        self.follow_mode = follow_mode
        self.scroll_buffer = scroll_buffer
        
    def follow(self, x, y):
        # follow center implementation for now
        new_x = x - (cart.Map.section_width * tile.TILE_SIZE) / 2
        new_y = y - (cart.Map.section_height * tile.TILE_SIZE) / 2
        delta_x = new_x - self.x
        delta_y = new_y - self.y
        self.x = new_x
        self.y = new_y
        self.scroll_buffer.scroll(delta_x, delta_y)
    
        
class ScrollBuffer:
    quad_width = cart.Map.section_width * tile.TILE_SIZE
    quad_height = cart.Map.section_height * tile.TILE_SIZE
    
    def __init__(self, renderer):
        self.renderer = renderer
        self.quadrants = [
            pygame.Surface((cart.Map.section_width * tile.TILE_SIZE, cart.Map.section_height * tile.TILE_SIZE))
            for _ in range(0, 4)
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
        n_cols_redraw = abs(math.ceil(delta_x / tile.TILE_SIZE))
        n_rows_redraw = abs(math.ceil(delta_y / tile.TILE_SIZE))
        row_range = None
        col_range = None
        if delta_x > 0:
            col_range = range(math.floor(x / tile.TILE_SIZE) + cart.Map.section_width - 1, math.ceil(x / tile.TILE_SIZE) + cart.Map.section_width + n_cols_redraw)
        elif delta_x < 0:
            col_range = range(math.floor(x / tile.TILE_SIZE) - n_cols_redraw - 1, math.ceil(x / tile.TILE_SIZE))
        if delta_y > 0:
            row_range = range(math.floor(y / tile.TILE_SIZE) + cart.Map.section_height - 1, math.ceil(y / tile.TILE_SIZE) + cart.Map.section_height + n_rows_redraw)
        elif delta_y < 0:
            row_range = range(math.floor(y / tile.TILE_SIZE) - n_rows_redraw - 1, math.ceil(y / tile.TILE_SIZE))
        self.redraw(row_range=row_range, col_range=col_range)
        
        
    def redraw(self, row_range=None, col_range=None):
        left, top, right, bottom = self.view_rect
        x, y = self.map_coord
        start_col = math.floor((x - left) / tile.TILE_SIZE)
        start_row = math.floor((y - top) / tile.TILE_SIZE)
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
                for col in range(0, cart.Map.section_width * 2):
                    map_col = quad_col + col
                    quadrant.fill(self.renderer.cartridge.lookup_universal_background_color(), (col * tile.TILE_SIZE, row * tile.TILE_SIZE, tile.TILE_SIZE, tile.TILE_SIZE))
                    tile_surface = self.renderer.surface_for_map_tile(map_row, map_col)
                    if tile_surface:
                        quadrant.blit(tile_surface, (col * tile.TILE_SIZE, row * tile.TILE_SIZE))
            for col in range(0, cart.Map.section_width):
                map_col = quad_col + col
                if col_range and map_col not in col_range:
                    continue
                for row in range(0, cart.Map.section_height * 2):
                    map_row = quad_row + row
                    quadrant.fill(self.renderer.cartridge.lookup_universal_background_color(), (col * tile.TILE_SIZE, row * tile.TILE_SIZE, tile.TILE_SIZE, tile.TILE_SIZE))
                    tile_surface = self.renderer.surface_for_map_tile(map_row, map_col)
                    if tile_surface:
                        quadrant.blit(tile_surface, (col * tile.TILE_SIZE, row * tile.TILE_SIZE))
        
    
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
    