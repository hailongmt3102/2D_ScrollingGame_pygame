class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def plus(self, newpoint):
        self.x += newpoint.x
        self.y += newpoint.y

    def equal(self, x, y):
        self.x = x
        self.y = y
