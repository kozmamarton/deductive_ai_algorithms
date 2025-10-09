import numpy as np
from track import Track
from race_car import RaceCar
from enemy import EnemyRacer
from logger import get_logger
import heapq
import math
from multiprocessing import Pool


class Racer:
    track : Track
    ktm_exc : RaceCar
    enemies : list[EnemyRacer]
    logger : callable
    POSSIBLE_DIRECTIONS : list[tuple[int,int]]
    MAXIMUM_SPEED: int = 3
    
    def __init__(self):
        self.track = Track()
        self.ktm_exc = RaceCar()
        self.enemies = []
        for i in range(0, self.track.PLAYERS_COUNT):
            self.enemies.append(EnemyRacer(i))
        self.logger = get_logger()
        self.POSSIBLE_DIRECTIONS = [(i,j) for i in range(-1,2) for j in range(-1,2)]
        
    def heuristic(self, start , goal):
        dx = goal[0] - start[0]
        dy = goal[1] - start[1]
        dist = math.hypot(dx, dy)
        # estimate minimal time using bang-bang (accel + decel)
        return 2 * math.sqrt(dist)
        #return np.linalg.norm(np.array(start) - np.array(goal))    
    
    
    def calculate_pos_from_velocity(self, position: tuple[int,int], current_speed: tuple = None, desired_velocity : tuple = (0,0)) -> tuple[int,int]:
        if not current_speed:
            current_speed = self.ktm_exc.get_speed() 
        return (position[0] + desired_velocity[0] + current_speed[0], position[1] + desired_velocity[1] + current_speed[1])    
    
    def valid_move(self, start, pos : tuple[int, int], speed):
        for enemy in self.enemies:
            if enemy.x == pos[0] and enemy.y == pos[1]:
                return False
            
        track = self.track.get_track()
        return 0 <= pos[0] < self.track.TRACK_HEIGHT and \
            0 <= pos[1] < self.track.TRACK_WIDTH and \
            track[pos[0], pos[1]] >= 0 and self.track.valid_line(np.array(start),np.array(pos)) and \
            -1 <= abs(speed[0]) - abs(pos[0] - start[0]) <= 1 and \
            -1 <= abs(speed[1]) - abs(pos[1] - start[1]) <= 1
                
        
    def is_goal(self, position : tuple[int, int]) -> bool:
        return (np.array(position) == self.track.get_goals()).all(1).any()
                
    def __retrieve_path(self, start_node: tuple[int, int], tree: dict) -> list[tuple[int, int]]:
        path = [start_node]
        iterator = start_node
        while iterator in tree:
            iterator = tree[iterator]
            path.append(iterator)
        return path

    def min_steps_a_star(self):
        # state = (x, y, vx, vy)
        start = self.ktm_exc.get_pos()
        start_state = (*start, *self.ktm_exc.get_speed())
        goals = self.track.get_goals()
        closest_goal = min(goals, key=lambda x: self.heuristic(start, x))           

        pq = [(0, start_state)]  # (f, state)
        g_score = {start_state: 0}
        visited = set()
        parent = {}
        while pq:
            f, (x, y, vx, vy) = heapq.heappop(pq)
            current_pos = (x,y)
            current_speed = (vx,vy)
            current_state =  (*current_pos, *current_speed)
            
            if self.is_goal(current_pos) and vx == 0 and vy == 0:
                return self.__retrieve_path(current_state,parent)
            
            if current_state in visited:
                continue
            visited.add(current_state)

            for ax,ay in self.POSSIBLE_DIRECTIONS:
                nvx = vx + ax
                nvy = vy + ay
                nx = x + nvx
                ny = y + nvy

                new_pos = (nx,ny)
                new_state = (*new_pos, nvx, nvy)
                new_cost = g_score[(x, y, vx, vy)] + 1

                if new_state in visited or not self.valid_move(current_pos, new_pos,(nvx,nvy)):
                    continue
                old_cost = g_score.get(new_state, math.inf)
                if new_cost < old_cost:
                    g_score[new_state] = new_cost
                    closest_goal = min(goals, key=lambda x: self.heuristic(new_pos, x))
                    f_score = new_cost + self.heuristic((nx, ny),closest_goal)
                    parent[new_state] = current_state
                    heapq.heappush(pq, (f_score, new_state))

        return None  # unreachable

                
    def a_star(self, SPEED_LIMIT: tuple[int,int]):
        start = self.ktm_exc.get_pos()
        current_speed = self.ktm_exc.get_speed()
        goals = self.track.get_goals()
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
            if self.is_goal(current):
               return self.__retrieve_path(current, parent)

            openSet.remove(current)
            closedSet.add(current)
            for dx, dy in self.POSSIBLE_DIRECTIONS:
                child = self.calculate_pos_from_velocity(current,current_speed, (dx,dy))
                if not self.valid_move(current,child,current_speed) \
                    or child in closedSet or child in openSet \
                    or abs(dx + current_speed[0])>SPEED_LIMIT[0] \
                    or abs(dy + current_speed[1])>SPEED_LIMIT[1]:
                    continue
                
                parent[child] = current
                g_score[child] = g_score[current] + 1
                closestGoal = min(goals, key=lambda x: self.heuristic(child, x))
                f_score[child] = g_score[child] + self.heuristic(child, closestGoal)
                openSet.add(child)    
        return None
    
    def calculate_decision(self, next_pos: tuple[int, int]) -> tuple[int, int]:
        current_pos = self.ktm_exc.get_pos()
        current_speed = self.ktm_exc.get_speed()
        result = (next_pos[0] - (current_pos[0] + current_speed[0]), next_pos[1] - (current_pos[1] + current_speed[1]))
        return result
    
    def say_decision_to_judge(self, decision : tuple[int, int]):
        print(f'{decision[0]} {decision[1]}', flush=True)
    
    
    def a_star_variable_speeds(self):
        for velocity in range(self.MAXIMUM_SPEED,0,-1):
            path_to_goal = self.a_star((velocity,velocity))
            if path_to_goal:
                return path_to_goal
                
    
    def race(self):
        last_plan = []
        failed = 0
        timeout_seconds = 0.95
        with Pool(processes=2) as pool:
            while self.ktm_exc.read_input():
                self.update_enemy_pos()
                # Start both concurrently
                res1 = pool.apply_async(self.a_star_variable_speeds, [])
                res2 = pool.apply_async(self.min_steps_a_star, [])

                try:
                    result2 = res2.get(timeout=timeout_seconds)
                except Exception:
                    result2 = None

                result1 = res1.get()
                
                path_to_goal = result2 if result2 != None else result1
                
                if path_to_goal:
                    last_plan = path_to_goal
                    next_move = path_to_goal[-2]
                    self.say_decision_to_judge(self.calculate_decision(next_move))
                    failed = 0
                    continue 
                #if any attempt to calculate a path with a* is failed we stick to the latest calculated path
                if(len(last_plan)>0):
                    self.say_decision_to_judge(self.calculate_decision(last_plan[-3 - failed]))
                    failed+=1
                    continue
                #if there isn't any calculated path ever, then we do some BogoNav and hope we will find a solution later
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
        
    
    