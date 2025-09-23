from queue import LifoQueue
from vertex import Vertex
import numpy as np


class RaceCar:
    x_pos: int
    y_pos: int
    acceleration_vertical: int
    acceleration_horizontal: int
    distance_traveled : float
    previous_steps : LifoQueue[Vertex]
    
    def __init__(self):
        self.x_pos = 0
        self.y_pos = 0
        self.acceleration_vertical = 0
        self.acceleration_horizontal = 0
        self.distance_traveled = 0
        self.previous_steps = LifoQueue()
    
    def read_input (self):
        judge_input = input()
        if judge_input == '~~~END~~~':
            return False
        self.y_pos, self.x_pos, self.acceleration_vertical, self.acceleration_horizontal = map(int, judge_input.split())
        return True
    
    def step_forward(self, dx: int, dy: int):
        self.previous_steps.put(Vertex(dx,dy))
        self.distance_traveled += np.hypot(abs(dx**2), abs(dy**2))
        
    def step_back(self, steps_count : int):
        steps_taken = []
        for i in range(0, steps_count):
            step = self.previous_steps.get()
            self.distance_traveled -= np.hypot(abs(step.x**2), abs(step.y**2))
            steps_taken.append(step)
        return steps_taken
        