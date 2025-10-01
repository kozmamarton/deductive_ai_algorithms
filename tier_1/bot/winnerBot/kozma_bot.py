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
        
        
    def heuristic(self, start : np.ndarray, goal: np.ndarray):
        return np.linalg.norm(start - goal)    
    
    
    def calculate_pos_from_velocity(self, position: tuple[int,int], dx: int, dy: int) -> tuple[int,int]:
        return (position[0] + dx, position[1] + dy)
    
    def valid_move(self, start_pos : tuple[int, int],pos : tuple[int, int]):
        for enemy in self.enemies:
            if enemy.x == start_pos[0] and enemy.y == start_pos[1]:
                continue
            if enemy.x == pos[0] and enemy.y == pos[1]:
                return False
    
        track = self.track.get_track()
        return 0 <= pos[0] < track.shape[0] and \
            0 <= pos[1] < track.shape[1] and \
            track[pos[0], pos[1]] >= 0
        
        
    def is_goal(self, position : tuple[int, int]) -> bool:
        return (np.array(position) == self.track.goal_positions).all(1).any()
                
    def a_star(self):
        start_pos = self.ktm_exc.get_pos()
        start_node = (0, start_pos)
        goals = self.track.goal_positions
        parents = {} # each nodes parent
        closed_set = {} # storing positions with f scores
        g_scores = {start_pos: 0} #storing positions with their actual costs(g scores)
        
        open_queue: list[tuple[np.floating, tuple[int, int]]] = []
        heapq.heappush(open_queue,start_node)
        
        while len(open_queue) != 0:            
            current_node = heapq.heappop(open_queue)
            current_f_score = current_node[0]
            current_pos = current_node[1]
            
            if self.is_goal(current_pos):
                path = [current_pos]
                iterator = parents[current_pos]
                while iterator in parents:
                    path.append(iterator)
                    iterator = parents[iterator]
                self.logger(f"\n\n PATH:  {path} \n \n")
                return path
            
            closed_set[current_pos] = current_f_score
            
            for dx, dy in self.POSSIBLE_DIRECTIONS:
                child_pos = self.calculate_pos_from_velocity(current_pos, dx, dy)
                if not self.valid_move(current_pos,child_pos) or closed_set.get(child_pos) != None:
                    continue
                
                closest_goal = min(goals, key=lambda x : self.heuristic(np.array(start_pos),x))
                child_g_score = g_scores[current_pos] + 1
                child_f_score = child_g_score + self.heuristic(np.array(child_pos), closest_goal)
                child_node = (child_f_score, child_pos)
                if child_node not in open_queue and child_pos not in self.way_behind:
                    g_scores[child_pos] = child_g_score
                    heapq.heappush(open_queue,child_node)
                    parents[child_pos] = current_pos         
                    
            #self.logger(f"Heap: {open_queue}\n current: {current_pos}, parent: {parents.get(current_pos)}\n")
        return None
    
    
    def say_decision_to_judge(self, decision : tuple[int, int]):
        #self.ktm_exc.step_forward(decision[0], decision[1])
        print(f'{decision[0]} {decision[1]}', flush=True)
    
    def calculate_decision(self, next_pos: tuple[int, int]) -> tuple[int, int]:
        current_pos = self.ktm_exc.get_pos()
        return (next_pos[0] - current_pos[0], next_pos[1] - current_pos[1])
    
    def race(self):
        last_plan = []
        while self.ktm_exc.read_input():
            self.update_enemy_pos()
            path_to_goal = self.a_star()
            if not path_to_goal:
                self.say_decision_to_judge(self.calculate_decision(last_plan[-1]))
                continue 
            last_plan = path_to_goal
            next_move = path_to_goal[-1]
            self.way_behind.append(next_move)
            self.say_decision_to_judge(self.calculate_decision(next_move))
            
    
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
        
    
    