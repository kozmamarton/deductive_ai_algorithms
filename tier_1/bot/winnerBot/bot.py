import numpy as np
from track import Track
from race_car import RaceCar
from enemy import EnemyRacer
from logger import get_logger

class Racer:
    track : Track
    ktm_exc : RaceCar
    enemies : list[EnemyRacer]
    logger : callable
    POSSIBLE_DIRECTIONS : list[tuple[int,int]]
    MAXIMUM_SPEED: int = 6
    
    def __init__(self):
        self.track = Track()
        self.ktm_exc = RaceCar()
        self.enemies = []
        for i in range(0, self.track.PLAYERS_COUNT):
            self.enemies.append(EnemyRacer(i))
        self.logger = get_logger()
        self.POSSIBLE_DIRECTIONS = [(i,j) for i in range(-1,2) for j in range(-1,2)]
        
    def heuristic(self, start , goal):
        return np.linalg.norm(np.array(start) - np.array(goal))    
    
    
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
            track[pos[0], pos[1]] >= 0 and \
            -1 <= abs(speed[0]) - abs(pos[0] - start[0]) <= 1 and \
            -1 <= abs(speed[1]) - abs(pos[1] - start[1]) <= 1 and \
                self.track.valid_line(np.array(start),np.array(pos))
        
    def is_goal(self, position : tuple[int, int]) -> bool:
        return (np.array(position) == self.track.get_goals()).all(1).any()
                
    def __retrieve_path(self, start_node: tuple[int, int], tree: dict) -> list[tuple[int, int]]:
        path = [start_node]
        iterator = start_node
        while iterator in tree:
            iterator = tree[iterator]
            path.append(iterator)
        return path
                
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
    
    def race(self):
        last_plan = []
        failed = 0
        
        while self.ktm_exc.read_input():
            self.update_enemy_pos()
            
            for velocity in range(self.MAXIMUM_SPEED,0,-1):
                path_to_goal = self.a_star((velocity,velocity))
                if path_to_goal:
                    break
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
        
    
    