


class Vertex:
    x : int
    y : int
    def __init__(self, x: int = 0, y: int = 0):
        self.x = x
        self.y = y
    
    def __lt__(self, other): return (self.x, self.y) < (other.x, other.y)    
    
    def __eq__(self, other):
        return isinstance(other, Vertex) and self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def refresh(self, new_x: int, new_y: int):
        self.x = new_x
        self.y = new_y