import numpy as np
from track import Track
from race_car import RaceCar
from enemy import EnemyRacer
from logger import get_logger
import heapq
import math

class Racer:
    track : Track
    ktm_exc : RaceCar
    enemies : list[EnemyRacer]
    logger : callable
    POSSIBLE_DIRECTIONS : list[tuple[int,int]]
    MAXIMUM_SPEED: int = 0
    SIZE_OF_SUBGOALS: int = 5
    
    
    def __init__(self):
        self.track = Track()
        self.ktm_exc = RaceCar()
        self.enemies = []
        for i in range(0, self.track.PLAYERS_COUNT):
            self.enemies.append(EnemyRacer(i))
        self.logger = get_logger()
        self.POSSIBLE_DIRECTIONS = [(i,j) for i in range(-1,2) for j in range(-1,2)]
        self.MAXIMUM_SPEED = min(self.track.VISIBILITY_RADIUS//2,4)
        self.goal_history = set()

        
    def update_enemy_pos(self):
        """Updates all the enemies positions
        """
        for enemy in self.enemies:
            enemy.read_input()
        
        
    def heuristic(self, start , goal) -> float:
        """Heuristic function. Calculates a heuristic based on minimal cost to goal using bang-bang methodology with a priority based on cell value.
        We get the euclidean distance from the goal and assume that on that distance, in the fist half we only accelerate, and on the second half, we only decelerate.
        This heuristic may not be admissible in theory, but in practice it performed better than raw euclidean distance

        Args:
            start (tuple[int,int]): start position
            goal (tuple[int,int]): goal position

        Returns:
            float: The approximated distance from the start position to the goal position.
        """
        
        dx = goal[0] - start[0]
        dy = goal[1] - start[1]
        dist = math.hypot(dx, dy)
        priority = 0 # the lower the priority the more important a node is
        cell_value = self.track.get_cell_value(goal)
        if cell_value == self.track.OIL_CELL_VALUE:
             priority = 2
        if cell_value == self.track.SAND_CELL_VALUE:
            priority = 1
        # estimate minimal time using bang-bang (accel + decel)
        return 2 * math.sqrt(dist) + priority
     
        #return np.linalg.norm(np.array(start) - np.array(goal))    
    
    
    def calculate_pos_from_velocity(self, start: tuple[int,int], current_speed: tuple = None, desired_velocity : tuple = (0,0)) -> tuple[int,int]:
        """Calculates the next position based on start position param and current speed, plus the desired velocity

        Args:
            start (tuple[int,int]): The starting position
            current_speed (tuple, optional): The current speed. Defaults to None. If none is given then we get our glorious ktm exc's position
            desired_velocity (tuple, optional): The desired acceleration. Defaults to (0,0).

        Returns:
            tuple[int,int]: The new position with the given parameters.
        """
        if current_speed is None:
            current_speed = self.ktm_exc.get_speed() 
        return (start[0] + desired_velocity[0] + current_speed[0], start[1] + desired_velocity[1] + current_speed[1])    
    
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
    
    def get_neighbor_nodes(self, node: tuple[int,int]):
        """Returns the given node's neighboring positions

        Args:
            node (tuple[int,int]): The node to be examined

        Returns:
            list[tuple[int,int]]: A list containing the neighboring positions
        """
        return [(i[0]+node[0], i[1] + node[1]) for i in self.POSSIBLE_DIRECTIONS \
            if self.track.TRACK_HEIGHT> i[0]+node[0] >= 0 and self.track.TRACK_WIDTH> i[1]+node[1] >= 0]

    def get_max_subgoals(self, current_pos: tuple[int,int] ):
        """Returns a set of goals of the length of self.SIZE_OF_SUBGOALS (let it be x). The top x goals are the ones with the most unknown neighbors.

        Args:
            current_pos (tuple[int,int]): Current position of the agent

        Returns:
            list[tuple[int,int]]: A list containing a number of goals set by self.SIZE_OF_SUBGOALS
        """
        visible_track = self.track.get_visible_track()
        subgoals = []
        unknown_neighbor_count = {}
        
        for i in visible_track:
            node = tuple(i)
            node_value = self.track.get_cell_value(node)
            if not self.track.traversable(node_value) or node == current_pos \
                or self.track.get_cell_value(node)==3:
                continue
            if self.track.get_cell_value(node) == 100:
                if self.track.valid_line(np.array(current_pos),i):
                    return [node]
                subgoals.append(node)
                continue
            if self.heuristic(current_pos, node) < self.track.VISIBILITY_RADIUS/2:
                continue
            
            unknown_neighbor_count[node] = 0
            neighbors = self.get_neighbor_nodes(node)
            for neighbor in neighbors:
                if neighbor == node:
                    continue
                if self.track.get_cell_value(neighbor) == 3:
                    unknown_neighbor_count[node] +=1
        nodes_with_most_neighbors = sorted(unknown_neighbor_count.items(), key=lambda x: x[1], reverse=True)
        
        for item in nodes_with_most_neighbors:
            if item[0] in self.goal_history \
                or not self.ktm_exc.position_history.count(item[0])==0:
                continue
            #if self.heuristic(item[0], self.track.get_start()[0]) < self.heuristic(self.ktm_exc.position_history[-1], self.track.get_start()[0]):
                #continue
            subgoals.append(item[0])
            
        return subgoals[:self.SIZE_OF_SUBGOALS]
                
    def a_star(self, SPEED_LIMIT: tuple[int,int], goal : tuple[int,int]) -> list[tuple[int,int]]:
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
            
        open_set = {start}
        open_heap = []
        heapq.heappush(open_heap, (0, start))
        closed_set = set()
        parent = {}
        g_score = {start: 0}
     
        self.logger(f"goal is {goal}")
        self.logger(self.track.map[goal])
        while open_heap:
                        
            current = heapq.heappop(open_heap)[1]#min(open_set, key=lambda x: f_score[x])
            if parent.get(current) != None:
                current_speed = (current[0] - parent[current][0], current[1] - parent[current][1])
                
            if self.is_goal(current,goal):
                path = self.__retrieve_path(current, parent)
                #self.logger(f"Goal found!, current: {current}, goal: {goal},\n path: {path}")
                return path

            open_set.remove(current)
            closed_set.add(current)
            for dx, dy in self.POSSIBLE_DIRECTIONS:
                child = self.calculate_pos_from_velocity(current,current_speed, (dx,dy))
                
                if (abs(dx + current_speed[0])>SPEED_LIMIT[0] 
                    or abs(dy + current_speed[1])>SPEED_LIMIT[1] 
                    or child in closed_set  
                    or not self.valid_move(current,child,current_speed)
                    or child in open_set):
                    continue
                
                parent[child] = current
                g_score[child] = g_score[current] + 1
                f_score = g_score[child] + self.heuristic(child, goal)
                heapq.heappush(open_heap,(f_score,child))
                open_set.add(child)    
        return None
    
    def get_a_valid_move(self, position: tuple[int,int]) -> tuple[int,int]:
        """Returns a valid move if there is any with the current velocity modification options.

        Args:
            position (tuple[int,int]): The function starts seeking a valid move from this position.

        Returns:
            tuple[int,int]: A velocity pair that leads to a legal cell. If none found, the function returns (0,0)!
        """
        for dx, dy in self.POSSIBLE_DIRECTIONS:
            child = self.calculate_pos_from_velocity(position, desired_velocity = (dx,dy))
            if self.valid_move(position, child):
                return (dx,dy)
        return (0,0)
    
    
    def calculate_decision(self, next_pos: tuple[int, int]) -> tuple[int, int]:
        current_pos = self.ktm_exc.get_pos()
        current_speed = self.ktm_exc.get_speed()
        result = (next_pos[0] - (current_pos[0] + current_speed[0]), next_pos[1] - (current_pos[1] + current_speed[1]))
        return result
    
    
    def say_decision_to_judge(self, decision : tuple[int, int]):
        print(f'{decision[0]} {decision[1]}', flush=True)
    
    
    def a_star_variable_speeds(self, goal: tuple[int,int]) -> list[tuple[int,int]]:
        for velocity in range(self.MAXIMUM_SPEED,0,-1):
            path_to_goal = self.a_star((velocity,velocity), goal=goal)
            if path_to_goal:
                return path_to_goal
    
    def is_move_safe(self, start: tuple[int,int], dest: tuple[int,int]) -> bool:
        """This function checks if there is any legal move after the step from param start to param dest.

        Args:
            start (tuple[int,int]): The starting position
            dest (tuple[int,int]): The desired destination's position

        Returns:
            bool: True if there is any valid move available after dest is reached with the calculated velocity from the two moves
        """
        dx = dest[0] - start[0]
        dy = dest[1] - start[1]
        pos_after_dest = (dest[0] + dx, dest[1] + dy)
        safe_move = self.get_a_valid_move(pos_after_dest)
        valid_pos_after_dest = self.calculate_pos_from_velocity(dest,current_speed=(dx,dy), desired_velocity=safe_move)
        return self.track.TRACK_HEIGHT > valid_pos_after_dest[0] >= 0 and \
            self.track.TRACK_WIDTH > valid_pos_after_dest[1] >= 0 and \
            self.track.get_cell_value(valid_pos_after_dest) != 3 \
            and self.track.valid_line(np.array(dest),np.array(valid_pos_after_dest))
    
    def race(self):
        """Manages the race according the rules of the judge. This function contains the main loop of the agent.
        """
        goals = []
        goal = (0,0)
        prev_plan = []
        prev_plan_step = 0
        
        while self.ktm_exc.read_input():
            
            self.update_enemy_pos()
            current_pos = self.ktm_exc.get_pos()
            self.track.read_track(current_pos)
            backup_failed = False
            
            #Based on experience when extremely low visibility radius is present, the usual goal selecting method doesn't work well in many cases.
            #So I decided to make a different goal selection method for low visibility conditions.
            '''if self.track.VISIBILITY_RADIUS < 3:
                goals = self.get_raw_subgoals()
                goal = min(goals, key= lambda x: self.heuristic(current_pos,x))
                path_to_goal = self.a_star_variable_speeds(goal)
                if path_to_goal is None:
                    backup_failed = True
                if not backup_failed:
                    self.say_decision_to_judge(self.calculate_decision(path_to_goal[1]))
                    continue
               ''' #If the low visibility pathfinding fails, we make a try with the default navigation method
            
            self.logger("Calculating subgoals")
            goals = self.get_max_subgoals(current_pos) 
            if len(goals) == 0:
                self.goal_history.clear()
                goals = self.get_max_subgoals(current_pos)
            goal = goals[0]
            
            path_to_goal = self.a_star_variable_speeds(goal)
      
            if path_to_goal:
                next_move = path_to_goal[1]
                prev_plan = path_to_goal[2:]
                prev_plan_step = 0
                if next_move == goal:
                    self.logger(f"{next_move}, {goal} is reached.")
                    self.goal_history.update(self.get_neighbor_nodes(goal))

                self.say_decision_to_judge(self.calculate_decision(next_move))
                continue

            else:
                if prev_plan_step >= len(prev_plan):
                    self.logger(f"Getting a valid move only: {self.get_a_valid_move(current_pos)}")
                    self.say_decision_to_judge(self.get_a_valid_move(current_pos))
                    continue
                self.logger(f"Next move from last plan: {self.calculate_decision(prev_plan[prev_plan_step])}, coords:{prev_plan[prev_plan_step]} , Current pos: {current_pos}, speed: {self.ktm_exc.get_speed()}")
                if (self.valid_move(current_pos, prev_plan[prev_plan_step], self.ktm_exc.get_speed())):
                    self.say_decision_to_judge(self.calculate_decision(prev_plan[prev_plan_step]))
                    prev_plan_step +=1
                    continue
                if self.track.VISIBILITY_RADIUS < 8:
                    self.goal_history.update(self.get_neighbor_nodes(goal))
                else:
                    self.goal_history.add(goal)
                self.say_decision_to_judge(self.get_a_valid_move(current_pos))
            
    
def main():
    my_glorious_racer = Racer()
    my_glorious_racer.race()
        
if __name__=='__main__':
    print('READY', flush=True)  
    main()        
        
    
    