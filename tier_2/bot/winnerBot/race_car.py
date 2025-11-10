from collections import deque


class RaceCar:
    x_pos: int
    y_pos: int
    speed_vertical: int
    speed_horizontal: int
    position_history: deque[tuple[int,int]]
    
    def __init__(self):
        self.x_pos = 0
        self.y_pos = 0
        self.speed_vertical = 0
        self.speed_horizontal = 0
        self.position_history = deque()
    
    def read_input (self):
        judge_input = input()
        if judge_input == '~~~END~~~':
            return False
        self.x_pos, self.y_pos, self.speed_horizontal, self.speed_vertical = map(int, judge_input.split(' '))
        self.save_position()
        return True
        
    def save_position(self):
        self.position_history.appendleft((self.x_pos,self.y_pos))   
    
    def get_prev_pos(self):
        return self.position_history[2] if len(self.position_history)>1 else None   
        
    def get_pos(self) -> tuple[int, int]:
        return (self.x_pos, self.y_pos)
        
    def get_speed(self) -> tuple[int, int]:
        return (self.speed_horizontal, self.speed_vertical)