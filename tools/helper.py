
from collision import BoxCollider, CircleCollier
from tools.point import Point


def is_contain(c1:BoxCollider, c2:BoxCollider):
    if c1.center.x + c1.width/2 > c2.center.x - c2.width/2 and c1.center.x - c1.width/2 < c2.center.x +  c2.width/2: 
        if c1.center.y + c1.height/2 > c2.center.y - c2.height/2 and c1.center.y - c1.height/2 < c2.center.y + c2.height/2:
            return True
    return False

def is_contain_circle(c1: CircleCollier, c2:BoxCollider):
    if not c1.enable or not c2.enable:
        return False
    if c1.center.x + c1.radius > c2.center.x - c2.width/2 and c1.center.x - c1.radius < c2.center.x +  c2.width/2: 
        if c1.center.y + c1.radius > c2.center.y - c2.height/2 and c1.center.y - c1.radius < c2.center.y + c2.height/2:
            return True
    return False

def is_contain_two_circle(c1: CircleCollier, c2: CircleCollier):
    radius = max(c1.radius, c2.radius)
    if (c1.center.x - c2.center.x) ** 2 + (c1.center.y - c2.center.y) ** 2 < radius **2:
        return True
        
    return False

def smooth_calculate(pos1: Point, pos2:Point, time):
    return Point(pos1.x + (pos2.x - pos1.x) * time, pos1.y + (pos2.y - pos1.y) * time)
