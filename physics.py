class Vector:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def add(self, vector2):
        return Vector(x=self.x + vector2.x, y=self.y + vector2.y)

