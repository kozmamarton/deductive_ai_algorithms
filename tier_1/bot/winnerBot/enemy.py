

class EnemyRacer:
    x: int
    y: int
    ID: int
    
    def __init__(self, id: int):
        self.x = 0
        self.y = 0
        self.ID = id
        
    def read_input(self):
        self.y, self.x = map(int, input().split(' '))