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
            camera.follow(bob.rect.left, bob.rect.top)
            scroll_buffer.render(view_surface)
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

    def surface_for_map_tile(self, map_row, map_col):
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

class Background:
    width = map.Map.section_width * 2
    height = map.Map.section_height * 2

    def __init__(self, game_map):
        self.map = game_map
        # fill background store with blank tiles and attrs
        self.rows = [[(0, 0) for _ in range(0, Background.width)] for _ in range(0, Background.height)]
        self.offset = (0, 0)
        self.map_offset = (0, 0)

    def translate_col_row(self, col, row):
        if row not in range(0, map.Map.section_height) or col not in range(0, map.Map.section_width):
            raise IndexError
        offset_col, offset_row = self.offset
        return (
            clamp(offset_col + col, min_n=0, max_n=Background.width),
            clamp(offset_row + row, min_n=0, max_n=Background.height)
        )

    def get_tile_and_attr(self, col, row):
        try:
            translated_col, translated_row = self.translate_col_row(col, row)
            row_data = self.rows[translated_row]
            return row_data[translated_col]
        except IndexError:
            return (0, 0)
        return (0, 0)

    def set_buffered_tile_and_attr(self, col, row, tile_and_attr):
        if row not in range(0, Background.height) or col not in range(0, Background.width):
            return
        row_data = self.rows[row]
        row_data[col] = tile_and_attr

    def scroll(self, delta_col, delta_row):
        self.scroll_row(delta_row)
        self.scroll_col(delta_col)
        col, row = self.offset
        self.offset = (
            clamp(col + delta_col, min_n=0, max_n=Background.width),
            clamp(row + delta_row, min_n=0, max_n=Background.height)
        )
        map_col, map_row = self.map_offset
        self.map_offset = (map_col + delta_col, map_row + delta_row)

    def scroll_col(self, delta_col):
        col, row = self.offset
        map_col, map_row = self.map_offset
        # row_range spans the whole height of the background buffer
        row_range = range(0, Background.height)
        map_row_range = range(map_row - row, (map_row - row) + Background.height)
        if delta_col > 0:
            col_range = range(
                clamp(col + map.Map.section_width + 1, min_n=0, max_n = Background.height),
                clamp(col + map.Map.section_width + 1 + delta_col, min_n=0, max_n = Background.height)
            )
            map_col_range = range(map_col + map.Map.section_width + 1, map.Map.section_width + 1 + delta_col)
        else:
            col_range = range(
                clamp(col + delta_col, min_n=0, max_n = Background.height),
                clamp(col - 1, min_n=0, max_n = Background.height)
            )
            map_col_range = range(map_col + delta_col, map_col - 1)
        self.load_tiles(col_range, row_range, map_col_range, map_row_range)

    def scroll_row(self, delta_row):
        col, row = self.offset
        map_col, map_row = self.map_offset
        # col_range spans the whole width of the background buffer
        col_range = range(0, Background.width)
        map_col_range = range(map_col - col, (map_col - col) + Background.width)
        if delta_row > 0:
            row_range = range(
                clamp(row + map.Map.section_height + 1, min_n=0, max_n = Background.width),
                clamp(row + map.Map.section_height + 1 + delta_row, min_n=0, max_n = Background.width)
            )
            map_row_range = range(map_row + map.Map.section_height + 1, map.Map.section_height + 1 + delta_row)
        else:
            row_range = range(
                clamp(row + delta_row, min_n=0, max_n = Background.width),
                clamp(row - 1, min_n=0, max_n = Background.width)
            )
            map_row_range = range(map_row + delta_row, map_row - 1)
        self.load_tiles(col_range, row_range, map_col_range, map_row_range)
        
    def load_tiles(self, col_range, row_range, map_col_range, map_row_range):
        if len(map_col_range) <= 0 or len(map_row_range) <= 0:
            return
        tiled_area = self.map.get_tiles_in_area(col_range=map_col_range, row_range=map_row_range)
        for tile_row in range(0, tiled_area.height):
            tile_row_data = tiled_area.tiles[tile_row]
            for tile_col in range(0, tiled_area.width):
                tile_and_attr = tile_row_data[tile_col]
                self.set_buffered_tile_and_attr(col_range.start + tile_col, row_range.start + tile_row, tile_and_attr)
        

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
        self.coord = (map.Map.section_width / 2, map.Map.section_height / 2)  # col, row
        self.offset = (0, 0)  # pixel offset
    
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
        offset_x, offset_y = self.offset
        scroll_direc = 1 if delta_x >=0 else -1
        scroll_amt = abs(delta_x)
        while scroll_amt > 0:
            if scroll_amt > tile.TILE_SIZE:
                coord_x += scroll_direc
                scroll_amt -= tile.TILE_SIZE
                if coord_x < 0 or coord_x > map.Map.section_width:
                    coord_x = clamp(coord_x, 0, map.Map.section_width)
                    self.swap_vertical_axis()
            else:
                if scroll_direc >= 0:
                    offset_x = scroll_amt
                else:
                    offset_x = tile.TILE_SIZE - scroll_amt
                scroll_amt = 0
        scroll_direc = 1 if delta_y >=0 else -1
        scroll_amt = abs(delta_y)
        while scroll_amt > 0:
            if scroll_amt > tile.TILE_SIZE:
                coord_y += scroll_direc
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
        self.coord = (coord_x, coord_y)
        self.offset = (offset_x, offset_y)
        


class ScrollBufferOld:
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
        # left, top, right, bottom
        self.view_rect = (
            ScrollBuffer.quad_width / 2,
            ScrollBuffer.quad_height / 2,
            ScrollBuffer.quad_width / 2 + ScrollBuffer.quad_width,
            ScrollBuffer.quad_height / 2 + ScrollBuffer.quad_height
        )
        self.offset = (0, 0)
        self.map_coord = (0, 0)
        self.background = Background(renderer.cartridge.map)
        # self.redraw()
        
    def scroll(self, delta_x, delta_y):
        offset_x, offset_y = self.offset
        left, top, right, bottom = self.view_rect
        scroll_x = abs(delta_x)
        if delta_x >= 0:
            scroll_direc = 1
        else:
            scroll_direc = -1
        while scroll_x > 0:
            if scroll_x > tile.TILE_SIZE:
                left += scroll_direc * tile.TILE_SIZE
                right += scroll_direc * tile.TILE_SIZE
                self.background.scroll(scroll_direc * 1, 0)
                scroll_x -= tile.TILE_SIZE
            else:
                left += scroll_direc * scroll_x
                right += scroll_direc * scroll_x
                if scroll_direc > 0:
                    offset_x = scroll_x
                else:
                    offset_x = tile.TILE_SIZE - scroll_x
                scroll_x = 0
            if left >= ScrollBuffer.quad_width:
                left = left - ScrollBuffer.quad_width
                right = right - ScrollBuffer.quad_width
                self.swap_vertical_axis()
            elif left <= 0:
                left = left + ScrollBuffer.quad_width
                right = right + ScrollBuffer.quad_width
                self.swap_vertical_axis()
            if scroll_x > tile.TILE_SIZE:
                self.redraw_col(5)
        scroll_y = abs(delta_y)
        if delta_y >= 0:
            scroll_direc = 1
        else:
            scroll_direc = -1
        while scroll_y > 0:
            if scroll_y > tile.TILE_SIZE:
                left += scroll_direc * tile.TILE_SIZE
                right += scroll_direc * tile.TILE_SIZE
                self.background.scroll(0, scroll_direc * 1)
                scroll_y -= tile.TILE_SIZE
            else:
                top += scroll_direc * scroll_y
                bottom += scroll_direc * scroll_y
                if scroll_direc > 0:
                    offset_y = scroll_y
                else:
                    offset_y = tile.TILE_SIZE - scroll_y
                scroll_y = 0
            if top >= ScrollBuffer.quad_height:
                top = top - ScrollBuffer.quad_height
                bottom = bottom - ScrollBuffer.quad_height
                self.swap_horizontal_axis()
            elif top <= 0:
                top = top + ScrollBuffer.quad_height
                bottom = bottom + ScrollBuffer.quad_height
                self.swap_horizontal_axis()
        self.offset = (offset_x, offset_y)
        self.view_rect = [left, top, right, bottom]
        """
        n_cols_redraw = abs(math.ceil(delta_x / tile.TILE_SIZE))
        n_rows_redraw = abs(math.ceil(delta_y / tile.TILE_SIZE))
        row_range = None
        col_range = None
        if delta_x > 0:
            col_range = range(math.floor(x / tile.TILE_SIZE) + map.Map.section_width - 1, math.ceil(x / tile.TILE_SIZE) + map.Map.section_width + n_cols_redraw)
        elif delta_x < 0:
            col_range = range(math.floor(x / tile.TILE_SIZE) - n_cols_redraw - 1, math.ceil(x / tile.TILE_SIZE))
        if delta_y > 0:
            row_range = range(math.floor(y / tile.TILE_SIZE) + map.Map.section_height - 1, math.ceil(y / tile.TILE_SIZE) + map.Map.section_height + n_rows_redraw)
        elif delta_y < 0:
            row_range = range(math.floor(y / tile.TILE_SIZE) - n_rows_redraw - 1, math.ceil(y / tile.TILE_SIZE))
        self.background.scroll(n_cols_redraw, n_rows_redraw)
        self.redraw(row_range=row_range, col_range=col_range)
        """
        
    def redraw_col(self, col):
        pass
        
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
                quad_col = start_col + map.Map.section_width
                quad_row = start_row
            elif i == 2:  # bottom left
                quad_col = start_col
                quad_row = start_row + map.Map.section_height
            else:  #  bottom right
                quad_col = start_col + map.Map.section_width
                quad_row = start_row + map.Map.section_height
            for row in range(0, map.Map.section_height):
                map_row = quad_row + row
                if row_range and map_row not in row_range:
                    continue
                for col in range(0, map.Map.section_width * 2):
                    map_col = quad_col + col
                    quadrant.fill(self.renderer.cartridge.lookup_universal_background_color(), (col * tile.TILE_SIZE, row * tile.TILE_SIZE, tile.TILE_SIZE, tile.TILE_SIZE))
                    # there's no way this will work
                    tile_number, attr = self.background.get_tile_and_attr(col, row)
                    tile_surface = self.renderer.surface_for_tile(tile_number, attr=attr)
                    if tile_surface:
                        quadrant.blit(tile_surface, (col * tile.TILE_SIZE, row * tile.TILE_SIZE))
                    # tile_surface = self.renderer.surface_for_map_tile(map_row, map_col)
                    # if tile_surface:
                    #     quadrant.blit(tile_surface, (col * tile.TILE_SIZE, row * tile.TILE_SIZE))
            for col in range(0, map.Map.section_width):
                map_col = quad_col + col
                if col_range and map_col not in col_range:
                    continue
                for row in range(0, map.Map.section_height * 2):
                    map_row = quad_row + row
                    quadrant.fill(self.renderer.cartridge.lookup_universal_background_color(), (col * tile.TILE_SIZE, row * tile.TILE_SIZE, tile.TILE_SIZE, tile.TILE_SIZE))
                    # there's no way this will work
                    tile_number, attr = self.background.get_tile_and_attr(col, row)
                    tile_surface = self.renderer.surface_for_tile(tile_number, attr=attr)
                    if tile_surface:
                        quadrant.blit(tile_surface, (col * tile.TILE_SIZE, row * tile.TILE_SIZE))
                    # tile_surface = self.renderer.surface_for_map_tile(map_row, map_col)
                    # if tile_surface:
                    #     quadrant.blit(tile_surface, (col * tile.TILE_SIZE, row * tile.TILE_SIZE))
        
    
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
    

def clamp(n, min_n, max_n):
    if n > max_n:
        while n > max_n:
            n -= (max_n - min_n)
        return n
    elif n < min_n:
        while n < min_n:
            n += (max_n - min_n)
        return n
    return n
