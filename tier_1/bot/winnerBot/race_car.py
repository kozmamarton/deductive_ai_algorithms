from queue import LifoQueue
import numpy as np


class RaceCar:
    x_pos: int
    y_pos: int
    speed_vertical: int
    speed_horizontal: int
    
    def __init__(self):
        self.x_pos = 0
        self.y_pos = 0
        self.speed_vertical = 0
        self.speed_horizontal = 0
    
    def read_input (self):
        judge_input = input()
        if judge_input == '~~~END~~~':
            return False
        self.x_pos, self.y_pos, self.speed_horizontal, self.speed_vertical = map(int, judge_input.split())
        return True
    
    def step_forward(self, dx: int, dy: int):
        self.speed_vertical += dx
        self.speed_horizontal += dy
        
    def get_pos(self) -> tuple[int, int]:
        return (self.x_pos, self.y_pos)
        
    def get_speed(self) -> tuple[int, int]:
        return (self.speed_horizontal, self.speed_vertical)