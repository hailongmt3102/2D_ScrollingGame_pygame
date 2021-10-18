from tools.point import Point


class Transform:
    def __init__(self, position: Point, rotation=0):
        self.position = position
        self.rotation = rotation

    def translate(self, x, y):
        self.position.x += x
        self.position.y += y
    
    
