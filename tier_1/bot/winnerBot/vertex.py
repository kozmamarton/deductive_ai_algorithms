


class Vertex:
    x : int
    y : int
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        
    def refresh(self, new_x: int, new_y: int):
        self.x = new_x
        self.y = new_y