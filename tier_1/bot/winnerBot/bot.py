import numpy as np
import heapq

from track import Track
from race_car import RaceCar
from enemy import EnemyRacer
from logger import get_logger

class Racer:
    track : Track
    ktm_exc : RaceCar
    enemies : list[EnemyRacer]
    
    def __init__(self):
        self.track = Track()
        self.ktm_exc = RaceCar()
        self.enemies = []
        for i in range(0, self.track.PLAYERS_COUNT):
            self.enemies.append(EnemyRacer(i))
        self.logger = get_logger()
        self.POSSIBLE_DIRECTIONS = [(i,j) for i in range(-1,2) for j in range(-1,2)]
        self.way_behind = []
        self.g_scores = {}
        
        
    def heuristic(self, start , goal):
        return np.linalg.norm(np.array(start) - np.array(goal))    
    
    
    def calculate_pos_from_velocity(self, position: tuple[int,int], dx: int, dy: int) -> tuple[int,int]:
        curr_vel = self.ktm_exc.get_speed()
        return (position[0] + dx + curr_vel[0], position[1] + dy + curr_vel[1])
    
    def traversable(self,cell_value: int) -> bool:
        return cell_value >= 0

    def valid_line(self, pos1: np.ndarray, pos2: np.ndarray) -> bool:
        track = self.track.get_track()
        if (np.any(pos1 < 0) or np.any(pos2 < 0) or np.any(pos1 >= track.shape)
                or np.any(pos2 >= track.shape)):
            return False
        diff = pos2 - pos1
        # Go through the straight line connecting ``pos1`` and ``pos2``
        # cell-by-cell. Wall is blocking if either it is straight in the way or
        # there are two wall cells above/below each other and the line would go
        # "through" them.
        if diff[0] != 0:
            slope = diff[1] / diff[0]
            d = np.sign(diff[0])  # direction: left or right
            for i in range(abs(diff[0]) + 1):
                x = pos1[0] + i*d
                y = pos1[1] + i*slope*d
                y_ceil = np.ceil(y).astype(int)
                y_floor = np.floor(y).astype(int)
                if (not self.traversable(track[x, y_ceil])
                        and not self.traversable(track[x, y_floor])):
                    return False
        # Do the same, but examine two-cell-wall configurations when they are
        # side-by-side (east-west).
        if diff[1] != 0:
            slope = diff[0] / diff[1]
            d = np.sign(diff[1])  # direction: up or down
            for i in range(abs(diff[1]) + 1):
                x = pos1[0] + i*slope*d
                y = pos1[1] + i*d
                x_ceil = np.ceil(x).astype(int)
                x_floor = np.floor(x).astype(int)
                if (not self.traversable(track[x_ceil, y])
                        and not self.traversable(track[x_floor, y])):
                    return False
        return True
    
    
    
    def valid_move(self, start, pos : tuple[int, int], speed):
        for enemy in self.enemies:
            if enemy.x == pos[0] and enemy.y == pos[1]:
                return False
    
        track = self.track.get_track()
        return 0 <= pos[0] < track.shape[0] and \
            0 <= pos[1] < track.shape[1] and \
            track[pos[0], pos[1]] >= 0 and \
            -1 <= abs(speed[0]) - abs(pos[0] - start[0]) <= 1 and \
            -1 <= abs(speed[1]) - abs(pos[1] - start[1]) <= 1 and \
                self.valid_line(np.array(start),np.array(pos))
        
    def is_goal(self, position : tuple[int, int]) -> bool:
        return (np.array(position) == self.track.goal_positions).all(1).any()
                
    def a_star(self):
        start = self.ktm_exc.get_pos()
        current_speed = self.ktm_exc.get_speed()
        goals = self.track.goal_positions
        openSet = {start}
        closedSet = set()
        parent = {}
        g_score = {start: 0}
        closestGoal = min(goals, key=lambda x: self.heuristic (start, x))
        f_score = {start: self.heuristic(start, closestGoal)}

        while openSet:            
            current = min(openSet, key=lambda x: f_score[x])
            if parent.get(current) != None:
                current_speed = (current[0] - parent[current][0], current[1] - parent[current][1])
            if (np.array(current) == goals).all(1).any():
                path = [current]
                while current in parent:
                    current = parent[current]
                    path.append(current)
                return path

            openSet.remove(current)
            closedSet.add(current)
            illegal = 0
            for dx, dy in [(i,j) for i in range(-1,2) for j in range(-1, 2)]:
                
                child = (current[0] + dx + current_speed[0] , current[1] + dy + current_speed[1])
                if not self.valid_move(current,child,current_speed) or child in closedSet or abs(dx + current_speed[0])>2 or abs(dy + current_speed[1]) >2:
                    illegal+=1
                    continue
                if child not in openSet:
                    openSet.add(child)
                    parent[child] = current
                    g_score[child] = g_score[current] + 1
                    closestGoal = min(goals, key=lambda x: self.heuristic(child, x))
                    f_score[child] = g_score[child] + self.heuristic(child, closestGoal)
                
                
        return None
    
    
    def say_decision_to_judge(self, decision : tuple[int, int]):
        #self.ktm_exc.step_forward(decision[0], decision[1])
        print(f'{decision[0]} {decision[1]}', flush=True)
    
    def calculate_decision(self, next_pos: tuple[int, int]) -> tuple[int, int]:
        current_pos = self.ktm_exc.get_pos()
        current_speed = self.ktm_exc.get_speed()
        result = (next_pos[0] - (current_pos[0] + current_speed[0]), next_pos[1] - (current_pos[1] + current_speed[1]))
        return result
    
    def race(self):
        last_plan = []
        
        while self.ktm_exc.read_input():
            self.update_enemy_pos()
            path_to_goal = self.a_star()
            if path_to_goal:
                last_plan = path_to_goal
                next_move = path_to_goal[-2]
                self.way_behind.append(next_move)
                self.say_decision_to_judge(self.calculate_decision(next_move))
                continue 
            if(len(last_plan)>0):
                self.say_decision_to_judge(self.calculate_decision(last_plan[-2]))
                continue
            import random
            r = random.Random()
            self.say_decision_to_judge((r.randint(-1,1),r.randint(-1,1)))
            
            
    
    def update_enemy_pos(self):
        """Updates all the enemies positions
        """
        for enemy in self.enemies:
            enemy.read_input()
    
def main():
    my_glorious_racer = Racer()
    my_glorious_racer.race()
        
        
        

if __name__=='__main__':
    print('READY', flush=True)
    main()        
        
    
    