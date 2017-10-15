#!/usr/bin/env python3

import sys

import pygame

class ScreenCoord():
    PRECISION = 1

    def __init__(self, value):
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value
        self.remainder = 0

    def add(self, value2):
        do_add = value2 >= 0
        to_add = abs(value2) + self.remainder
        while to_add > 0:
            if to_add >= ScreenCoord.PRECISION:
                if do_add:
                    self.value += 1
                else:
                    self.value -= 1
                to_add -= ScreenCoord.PRECISION
                if to_add == 0:
                    self.remainder = 0
            else:
                if do_add:
                    self.remainder = to_add
                else:
                    self.remainder = ScreenCoord.PRECISION - to_add
                to_add = 0


class Guy():
    def __init__(self, x, y, speed):
        self._x = ScreenCoord(x)
        self._y = ScreenCoord(y)
        self.speed = speed

    @property
    def x(self):
        return self._x.value

    @x.setter
    def x(self, value):
        self._x.value = value

    @property
    def y(self):
        return self._y.value

    @y.setter
    def y(self, value):
        self._y.value = value

    def move(self, delta_x, delta_y):
        self._x.add(delta_x)
        self._y.add(delta_y)


class Guy2():
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed

    def move(self, delta_x, delta_y):
        self.x += delta_x
        self.y += delta_y


def main():
    clock = pygame.time.Clock()
    pygame.init()
    display_surface = pygame.display.set_mode((1024, 768))
    guy_surface = pygame.Surface((10, 10))
    guy_surface.fill((255, 0, 0))
    guys = [Guy(x=500, y=10 + i * 20, speed=-(i+1)) for i in range(0, 10)]
    # guys = [Guy2(x=0, y=10 + i * 20, speed=i*0.1) for i in range(0, 10)]
    is_running = True
    while is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
        display_surface.fill((0, 0, 0))
        for guy in guys:
            display_surface.blit(guy_surface, (guy.x, guy.y))
            guy.move(guy.speed, 0)
        pygame.display.update()
        clock.tick(60)
    pygame.quit()
    return 0

if __name__ == '__main__':
    sys.exit(main())
