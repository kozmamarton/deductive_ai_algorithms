import numpy as np
from track import Track
from race_car import RaceCar
from enemy import EnemyRacer
from logger import get_logger
import heapq
import math
from collections import deque

class Racer:
    track : Track
    ktm_exc : RaceCar
    enemies : list[EnemyRacer]
    logger : callable
    way_behind: set
    POSSIBLE_DIRECTIONS : list[tuple[int,int]]
    MAXIMUM_SPEED: int = 2
    SIZE_OF_SUBGOALS: int = 5
    
    
    def __init__(self):
        self.track = Track()
        self.ktm_exc = RaceCar()
        self.enemies = []
        for i in range(0, self.track.PLAYERS_COUNT):
            self.enemies.append(EnemyRacer(i))
        self.logger = get_logger()
        self.way_behind = set()
        self.POSSIBLE_DIRECTIONS = [(i,j) for i in range(-1,2) for j in range(-1,2)]

        
    def update_enemy_pos(self):
        """Updates all the enemies positions
        """
        for enemy in self.enemies:
            enemy.read_input()
        
        
    def heuristic(self, start , goal) -> float:
        """Heuristic function. Calculates a heuristic based on minimal cost to goal using bang-bang methodology.
        We get the euclidean distance from the goal and assume that on that distance, in the fist half we only accelerate, and on the second half, we only decelerate.

        Args:
            start (tuple[int,int]): start position
            goal (tuple[int,int]): goal position

        Returns:
            float: The approximated distance from the start position to the goal position.
        """
        dx = goal[0] - start[0]
        dy = goal[1] - start[1]
        dist = math.hypot(dx, dy)
        # estimate minimal time using bang-bang (accel + decel)
        return 2 * math.sqrt(dist)

        #return np.linalg.norm(np.array(start) - np.array(goal))    
    
    
    def calculate_pos_from_velocity(self, position: tuple[int,int], current_speed: tuple = None, desired_velocity : tuple = (0,0)) -> tuple[int,int]:
        """Calculates the next position based on position and current speed, plus the desired velocity

        Args:
            position (tuple[int,int]): The starting position
            current_speed (tuple, optional): The current speed. Defaults to None. If none is given then we get our glorious ktm exc's position
            desired_velocity (tuple, optional): The desired acceleration. Defaults to (0,0).

        Returns:
            tuple[int,int]: The new position with the given parameters.
        """
        if not current_speed:
            current_speed = self.ktm_exc.get_speed() 
        return (position[0] + desired_velocity[0] + current_speed[0], position[1] + desired_velocity[1] + current_speed[1])    
    
    def valid_move(self, start:tuple[int,int], pos : tuple[int, int], speed: tuple[int, int] = None) -> bool:
        """Returns if a move is valid or not. It checks:
        - collision with walls or other players 
        - if the given speed is valid
        - if the desired position isnt outside the map

        Args:
            start (tuple[int,int]): The starting position
            pos (tuple[int, int]): The desired position of the move
            speed (tuple[int,int]): The desired speed to move with.

        Returns:
            bool: True if the move is legal, false otherwise
        """
        try:
            for enemy in self.enemies:
                if enemy.x == pos[0] and enemy.y == pos[1]:
                    return False
            if not speed:
                speed = self.ktm_exc.get_speed()
            track = self.track.get_track()
            return 0 <= pos[0] < self.track.TRACK_HEIGHT and \
                0 <= pos[1] < self.track.TRACK_WIDTH and \
                track[pos[0], pos[1]] >= 0 and self.track.valid_line(np.array(start),np.array(pos)) and \
                -1 <= abs(speed[0]) - abs(pos[0] - start[0]) <= 1 and \
                -1 <= abs(speed[1]) - abs(pos[1] - start[1]) <= 1
        except Exception:
            self.logger(f"track h: {self.track.TRACK_HEIGHT}, track w: {self.track.TRACK_WIDTH}")
            self.logger(f"pos0: {pos[0]}, pos1: {pos[1]}")
            return False
                
        
    def is_goal(self, position : tuple[int, int], goal: tuple[int,int] = None) -> bool:
        """Determines if a given position is a goal

        Args:
            position (tuple[int, int]): The position to be examined. First item is the x, second item is the y position.

        Returns:
            bool: Wether the position is a goal position or not.
        """
        if type(goal) == type(None) or len(self.track.get_goals())>0:
            return (np.array(position) == self.track.get_goals()).all(1).any()
        return position == goal
                
    def __retrieve_path(self, root: tuple[int, int], tree: dict) -> list[tuple[int, int]]:
        """Recursively iterates the dict 'tree' which supposed to describe different graphs where each key 
        is a position and each value is the position's 'parent' - the position where we go to the child node

        Args:
            root (tuple[int, int]): The root of the graph, the position on the grid which we need to have a path for.
            tree (dict): The graph which has the connection between positions on the grid. 

        Returns:
            list[tuple[int, int]]: A list containing the path from the start node to the root node.
        """
        path = [root]
        iterator = root
        while iterator in tree:
            iterator = tree[iterator]
            path.append(iterator)
        return path[::-1]
    
    def get_neighboring_positions(self, node: tuple[int,int]):
        return [(i[0]+node[0], i[1] + node[1]) for i in self.POSSIBLE_DIRECTIONS \
            if self.track.TRACK_HEIGHT> i[0]+node[0] >= 0 and self.track.TRACK_WIDTH> i[1]+node[1] >= 0]
        
    
    def get_subgoals(self):
        visible_track = self.track.get_visible_track()
        #self.logger(visible_track)
        subgoals = []
        neighbours = {}
        for i in visible_track:
            node = tuple(i)
            if node in self.ktm_exc.position_history:
                #self.logger("skip happened!")
                continue
            if self.track.map[node] == 3:
                continue
            neighbours[node] = 0
            surrounding_nodes = self.get_neighboring_positions(i)
            for j in surrounding_nodes:
                if self.track.map[j] != 3:
                    continue
                neighbours[node] +=1
        top_nodes = sorted(neighbours.items(), key= lambda x: x[1], reverse=True)[:self.SIZE_OF_SUBGOALS]
        for i in top_nodes:
            subgoals.append(i[0])
        return subgoals
        

    def min_steps_a_star(self):
        """Min steps a star. A modified a star that searches every possible path with every possible speed. 
         This function has terrible complexity, approximately O(n^8) where n is the total number of available positions.
         Recommended use is to run in parallel with the speed limited astar and set a timeout for this little baby because it can take 1-3 entire seconds in each turn to calculate a valid path.

        Returns:
            list[tuple[int,int]]: A list containing the path to the goal.
        """
        start = self.ktm_exc.get_pos()
        start_state = (*start, *self.ktm_exc.get_speed())
        goals = self.track.get_goals()
        closest_goal = min(goals, key=lambda x: self.heuristic(start, x))           

        pq = [(0, start_state)]  # (f, state)
        g_score = {start_state: 0}
        visited = set()
        parent = {}
        while pq:
            f, (x, y, speed_x, speed_y) = heapq.heappop(pq)
            current_pos = (x,y)
            current_speed = (speed_x,speed_y)
            current_state =  (*current_pos, *current_speed)
            
            if self.is_goal(current_pos) and speed_x == 0 and speed_y == 0:
                return self.__retrieve_path(current_state,parent)
            
            if current_state in visited:
                continue
            visited.add(current_state)

            for dx,dy in self.POSSIBLE_DIRECTIONS:
                child_speed = (speed_x + dx, speed_y + dy)

                child_pos = self.calculate_pos_from_velocity(current_pos,child_speed)
                child = (*child_pos,*child_speed)
                child_cost = g_score[(x, y, speed_x, speed_y)] + 1

                if child in visited or not self.valid_move(current_pos, child_pos,child_speed):
                    continue
                old_cost = g_score.get(child, math.inf)
                if child_cost < old_cost:
                    g_score[child] = child_cost
                    closest_goal = min(goals, key=lambda x: self.heuristic(child_pos, x))
                    f_score = child_cost + self.heuristic(child_speed,closest_goal)
                    parent[child] = current_state
                    heapq.heappush(pq, (f_score, child))

        return None

                
    def a_star(self, SPEED_LIMIT: tuple[int,int]) -> list[tuple[int,int]]:
        """Modified astar algorithm that calculates a path with the maximum speed set in param 1.
            The main modification on vanilla astar is that when we calculate the path, we calculate the speed dynamically 
            Usually this doesn't work above (2,2) as max speed, because the closed set saves only the positions and not the speeds. 
            So it tries out a few different speeds and usually gets a dead end when all the nodes towards the goal are in the closed set but no goal is met because of illegal moves.

        Args:
            SPEED_LIMIT (tuple[int,int]): The maximum reachable velocity on x and y axis respectively.

        Returns:
            list[tuple[int,int]]:  A list containing the path to the goal.
        """
    
            
        start = self.ktm_exc.get_pos()
        current_speed = self.ktm_exc.get_speed()
        goals = self.track.get_goals() if len(self.track.get_goals())>1 else self.get_subgoals() 
        open_set = {start}
        closed_set = set()
        parent = {}
        g_score = {start: 0}
        closest_goal = min(goals, key=lambda x: self.heuristic (start, x))
        f_score = {start: self.heuristic(start, closest_goal)}
        while open_set:            
            current = min(open_set, key=lambda x: f_score[x])
            if parent.get(current) != None:
                current_speed = (current[0] - parent[current][0], current[1] - parent[current][1])
            if self.is_goal(current,closest_goal):
               return self.__retrieve_path(current, parent)

            open_set.remove(current)
            closed_set.add(current)
            for dx, dy in self.POSSIBLE_DIRECTIONS:
                child = self.calculate_pos_from_velocity(current,current_speed, (dx,dy))
                if not self.valid_move(current,child,current_speed) \
                    or child in closed_set or child in open_set \
                    or abs(dx + current_speed[0])>SPEED_LIMIT[0] \
                    or abs(dy + current_speed[1])>SPEED_LIMIT[1] \
                    or child in self.way_behind:
                    continue
                
                parent[child] = current
                g_score[child] = g_score[current] + 1
                closest_goal = min(goals, key=lambda x: self.heuristic(child, x))
                f_score[child] = g_score[child] + self.heuristic(child, closest_goal)
                open_set.add(child)    
        return None
    
    


    def bfs(self):
        """Breadth first search. This works the best so far, because in this grid race, every direction costs the same, and therefore, heuristics can be misleading.
            We check every direction with dynamic speed just like in the modified astar but we don't use heuiristics because every grid has the same cost to get to.
            Although this is fast, on large maps the complexity is big, so to run in parallel with a speed limited astar is strongly advised.
        Returns:
           list[tuple[int,int]]:  A list containing the path to the goal.
        """
        start = self.ktm_exc.get_pos()
        queue = deque()
        queue.append((start, self.ktm_exc.get_speed(), [start])) #pos, velocity, path
        visited = set()
        visited.add((start, self.ktm_exc.get_speed()))

        while queue:
            pos, vel, path = queue.popleft()

            if self.is_goal(pos):
                return path

            for dx, dy in self.POSSIBLE_DIRECTIONS:
                new_vel = (vel[0] + dx, vel[1] + dy)
                new_pos = self.calculate_pos_from_velocity(pos, new_vel)#(pos[0] + new_vel[0], pos[1] + new_vel[1])

                state = (new_pos, new_vel)
                if state in visited:
                    continue
                if not self.valid_move(pos, new_pos, new_vel)\
                    or abs(new_vel[0])>self.MAXIMUM_SPEED \
                    or abs(new_vel[1])>self.MAXIMUM_SPEED \
                    or new_pos in self.way_behind:
                    continue

                visited.add(state)
                queue.append((new_pos, new_vel, path + [new_pos]))

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
        while self.ktm_exc.read_input():
            self.update_enemy_pos()
            self.track.read_track(self.ktm_exc.get_pos())
            path_to_goal = self.a_star_variable_speeds()
            if path_to_goal:
                last_plan = path_to_goal
                next_move = path_to_goal[1]
                self.way_behind.add(next_move)
                self.say_decision_to_judge(self.calculate_decision(next_move))
                failed = 0
                continue 
            #if any attempt to calculate a path with a* is failed we stick to the latest calculated path
            if(1 + failed < len(last_plan) > 0 ):
                next_move_from_last_plan = last_plan[1 + failed]
                current_pos = self.ktm_exc.get_pos()
                i = 0              
                while not self.valid_move(current_pos,next_move_from_last_plan):
                    next_move_from_last_plan = last_plan[1 + i]
                    i += 1
                    if i >= len(last_plan) -1:
                        next_move_from_last_plan = None
                        break
                if next_move_from_last_plan:
                    self.way_behind.add(next_move_from_last_plan)
                    self.say_decision_to_judge(self.calculate_decision(next_move_from_last_plan))
                    failed+=1
                    continue
            #if there isn't any calculated path ever, then we do some BogoNav and hope we will find a solution later
            import random
            r = random.Random()
            self.say_decision_to_judge((0,0))

    
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
        
    
    