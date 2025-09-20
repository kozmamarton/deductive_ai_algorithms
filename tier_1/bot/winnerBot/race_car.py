

class RaceCar:
    x_pos: int
    y_pos: int
    acceleration_vertical: int
    acceleration_horizontal: int
    
    def __init__(self):
        self.x_pos = 0
        self.y_pos = 0
        self.acceleration_vertical = 0
        self.acceleration_horizontal = 0
    
    def read_input (self):
        judge_input = input()
        if judge_input == '~~~END~~~':
            return False
        self.y_pos, self.x_pos, self.acceleration_vertical, self.acceleration_horizontal = map(int, judge_input.split())
        return True
    