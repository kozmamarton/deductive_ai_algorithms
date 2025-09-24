import numpy as np
from track import Track
from race_car import RaceCar
from enemy import EnemyRacer
from vertex import Vertex
import heapq


class RacerAgent:
    
    ktm_exc_300 : RaceCar
    race_track : Track
    enemies : list[EnemyRacer]
    run : bool
    POSSIBLE_DIRECTIONS : list[tuple[int,int]]
    
    def __init__(self):
        self.race_track = Track()
        self.ktm_exc_300 = RaceCar()
        self.enemies = [ EnemyRacer(i) for i in range(0,self.race_track.PLAYERS_COUNT) ]   
        self.race_track.start_position.refresh(self.ktm_exc_300.x_pos, self.ktm_exc_300.y_pos)
        self.POSSIBLE_DIRECTIONS = self.get_possible_directions()
        self.run = True
        
        
    def __heuristic(self, start_x: int, start_y: int, target_x: int, target_y: int) -> float:
        a = np.array([start_x, start_y])
        b = np.array([target_x,target_y])
        return np.linalg.norm(a-b)
    
    
    def __get_closest_goal(self) -> np.ndarray:        
        return min(self.race_track.goal_positions, key = lambda goal_pos : self.__heuristic(self.ktm_exc_300.x_pos, self.ktm_exc_300.y_pos, goal_pos[0], goal_pos[1]))
    
    
    def get_possible_directions(self):
        directions = [(i, j) for i in range(-1,2) for j in range(-1,2)]
        directions.remove((0,0))
        return directions      
    
    def __next_pos_from_velocity(self,start_x, start_y, dx: int, dy: int):
        current_speed = self.ktm_exc_300.get_current_speed()
        return (start_x + current_speed.x + dx ,
                      start_y + current_speed.y + dy)
                      
    
    def illegal_move(self, possible_target_pos : tuple[int, int]):
        for enemy in self.enemies:
            #skipping our position
            if enemy.x == self.ktm_exc_300.x_pos and enemy.y == self.ktm_exc_300.y_pos:
                continue
            if enemy.x == possible_target_pos.x and enemy.y == possible_target_pos.y:
                return True
        return possible_target_pos[0] < 0 or possible_target_pos[0] > self.race_track.TRACK_WIDTH or \
            possible_target_pos[1] < 0 or possible_target_pos[1] > self.race_track.TRACK_HEIGHT or \
            self.race_track.race_track[possible_target_pos[0],possible_target_pos[1]] == -1
    
    def is_a_goal(self, pos_x, pos_y):
        return [pos_x, pos_y] in self.race_track.goal_positions
    
    
    def a_star(self):
        start_pos = (self.ktm_exc_300.x_pos, self.ktm_exc_300.y_pos)
        
        closest_goal = self.__get_closest_goal()
        parents = {}
        traversed_nodes_cost = {start_pos: 0}
        traversed_nodes_f_scores = {start_pos: self.__heuristic(start_pos[0], start_pos[1], closest_goal[0], closest_goal[1])}
        possible_nodes_heap :list[tuple[int, int]] = []
        heapq.heappush(possible_nodes_heap,start_pos)

        while len(possible_nodes_heap) != 0:
            current_node = heapq.heappop(possible_nodes_heap)
 
            current_cost = traversed_nodes_cost[current_node]

            if self.is_a_goal(current_node[0], current_node[1]):
                path = [current_node]
                iterator = parents[current_node]
                while iterator in parents:
                    path.append(iterator)
                    iterator = parents[iterator]
                return path
            
            for dx, dy in self.POSSIBLE_DIRECTIONS:
                child_node = self.__next_pos_from_velocity(current_node[0], current_node[1], dx, dy)
                if self.illegal_move(child_node):
                    continue   
                    
                traversed_nodes_cost[child_node] = current_cost + 1
                child_f_score = traversed_nodes_cost[child_node] + self.__heuristic(child_node[0], child_node[1], closest_goal[0], closest_goal[1])
                if traversed_nodes_f_scores.get(child_node, self.race_track.TRACK_MAXIMUM_DISTANCE) > child_f_score: #and not child_node in possible_nodes_heap:
                    traversed_nodes_f_scores[child_node] = child_f_score
                    parents[child_node] = current_node
                    heapq.heappush(possible_nodes_heap,  child_node)
                    #raise Exception(f"p: {parents}, \n heap: {[(i[1].x, i[1].y) for i in possible_nodes_heap]}")
        #raise Exception(f"p: {parents}, \n heap: {traversed_nodes_f_scores}")
        return None
                    
                    
                
                    
    
    def update_player_positions(self):
        """Reads the observation input from the judge by calling the racer's input reader functions
            If our glorious racer ktm_exc_300 gets an end of race call, 
            then this function implicitly stops the race by setting the race_running object variable
        """
        
        if not self.ktm_exc_300.read_input():
            self.run = False
            return 
        for enemy in self.enemies:
            enemy.read_input()
            
            
    def say_decision_to_judge(self, velocity: tuple):
        self.ktm_exc_300.step_forward(velocity[0],velocity[1])
        print(0,1)
        #print(f'{velocity[1]} {velocity[0]}')
        
        
        
    def race(self):
        
        while self.run:
            self.update_player_positions()
            solution = self.a_star()
            if not solution:
                print(0,0)
                continue
            next_move = solution[-1]
            decision = (next_move[0] - self.ktm_exc_300.x_pos, next_move[1] - self.ktm_exc_300.y_pos)
            self.say_decision_to_judge(decision)
    


def main():
    myPreciousWinner = RacerAgent()
    myPreciousWinner.race()
    

    
if __name__ == '__main__':
    main()
    
