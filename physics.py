import math


class Vector:
    def __init__(self, angle=0.0, magnitude=0.0):
        self._angle = angle
        self.magnitude = magnitude

    @classmethod
    def from_components(cls, x, y):
        magnitude = math.hypot(x, y)
        if x >= 0 and y <= 0:
            # magnitude = abs(x) ** 2 + abs(y) ** 2
            angle = math.cosh(x / magnitude)
        elif x <=0 and y <= 0:
            # magnitude = abs(x) ** 2 + abs(y) ** 2
            angle = math.cosh(x / magnitude) + 90
        elif x >=0 and y >= 0:
            # magnitude = abs(x) ** 2 + abs(y) ** 2
            angle = math.cosh(x / magnitude) + 180
        else:
            # magnitude = abs(x) ** 2 + abs(y) ** 2
            angle = math.cosh(x / magnitude) + 270
        return cls(angle=angle, magnitude=magnitude)
    
    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        self._angle = value % 360

    def get_components(self):
        angle = self.angle
        if self.angle in range(0, 91):
            x = self.magnitude * math.floor(math.cos(math.radians(angle)))
            y = -1.0 * self.magnitude * math.sin(math.radians(angle))
        elif self.angle in range(91, 181):
            angle -= 90
            x = -1.0 * self.magnitude * math.cos(math.radians(angle))
            y = - 1.0 * self.magnitude * math.sin(math.radians(angle))
        elif self.angle in range(181, 271):
            angle -= 180
            x = -1.0 * self.magnitude * math.cos(math.radians(angle))
            y = self.magnitude * math.sin(math.radians(angle))
        else:
            angle -= 270
            x = self.magnitude * math.cos(math.radians(angle))
            y = self.magnitude * math.sin(math.radians(angle))
        return (x, y)

    def add(self, vector):
        x1, y1 = self.get_components()
        x2, y2 = vector.get_components()
        return Vector.from_components(x1 + x2, y1 + y1)
