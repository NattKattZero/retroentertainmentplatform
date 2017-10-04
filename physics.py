import math


class Vector:
    def __init__(self, angle=0, magnitude=0):
        self._angle = angle
        self.magnitude = magnitude
    
    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        self._angle = value % 360

    def get_components(self):
        angle = self.angle
        if self.angle in range(0, 90):
            x = self.magnitude * math.cos(math.radians(angle))
            y = -1.0 * self.magnitude * math.sin(math.radians(angle))
        elif self.angle in range(90, 180):
            angle -= 90
            x = -1.0 * self.magnitude * math.cos(math.radians(angle))
            y = self.magnitude * math.sin(math.radians(angle))
        elif self.angle in range(180, 270):
            angle -= 180
            x = -1.0 * self.magnitude * math.cos(math.radians(angle))
            y = -1.0 * self.magnitude * math.sin(math.radians(angle))
        else:
            angle -= 270
            x = self.magnitude * math.cos(math.radians(angle))
            y = -1.0 * self.magnitude * math.sin(math.radians(angle))
        return (x, y)
