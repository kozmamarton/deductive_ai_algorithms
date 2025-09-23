from random import Random
import numpy as np
from track import Track
from race_car import RaceCar
from enemy import EnemyRacer
from vertex import Vertex

class RacerAgent:
    
    ktm_exc_300 : RaceCar
    race_track : Track
    enemies : list[EnemyRacer]
    run : bool
    
    def __init__(self):
        self.race_track = Track()
        self.ktm_exc_300 = RaceCar()
        self.enemies = [ EnemyRacer(i) for i in range(0,self.race_track.PLAYERS_COUNT) ]   
        self.race_track.start_position.refresh(self.ktm_exc_300.x_pos, self.ktm_exc_300.y_pos)
        self.run = True
        
        
    def __heuristic__(self, start_x, start_y, target_x, target_y) -> float:
        dx = abs(start_x - target_x)
        dy = abs(start_y - target_y)
        return (dx + dy) + (pow(2,0.5) - 2) * min(dx,dy) 
    
    
    def __get_closest_goal__(self) -> Vertex:
        min_dist_to_goal = self.race_track.TRACK_HEIGHT + self.race_track.TRACK_WIDTH
        closest_goal_coordinates = Vertex(0,0)
        
        for x,y in np.ndindex(self.race_track.goal_positions.shape):
            goal = self.__heuristic__(self.ktm_exc_300.x_pos, self.ktm_exc_300.y_pos,
                                      x, y)
            if goal < min_dist_to_goal:
                min_dist_to_goal = goal
                closest_goal_coordinates.refresh(x,y)
        return closest_goal_coordinates
    
    
    def get_possible_accelerations(self):
        return [(i, j) for i in range(-1,2) for j in range(-1,2)]
    
    
    def calculate_cost(self, target_velocity : Vertex, heuristic : float ):
        return self.ktm_exc_300.distance_traveled + np.hypot(abs(target_velocity.x **2),abs(target_velocity.y**2)) + heuristic
    
    def check_illegal_move(self, possible_target_pos : Vertex):
        for enemy in self.enemies:
            #skipping our position
            if enemy.x == self.ktm_exc_300.x_pos and enemy.y == self.ktm_exc_300.y_pos:
                continue
            if enemy.x == possible_target_pos.x and enemy.y == possible_target_pos.y:
                return True
        return self.race_track.race_track[possible_target_pos.x,possible_target_pos.y] != -1
    
    
    def a_star(self):
        curr_pos_x = self.ktm_exc_300.x_pos
        curr_pos_y = self.ktm_exc_300.y_pos
        curr_vel_x = self.ktm_exc_300.acceleration_horizontal
        curr_vel_y = self.ktm_exc_300.acceleration_vertical

        #the currently closest goal field's coordinates
        closest_goal = self.__get_closest_goal__()
        lowest_cost = self.race_track.TRACK_WIDTH + self.race_track.TRACK_HEIGHT
        dir_to_lowest_f = Vertex(0,0)
        
        for dx, dy in self.get_possible_accelerations():
            possible_target_pos = Vertex(curr_pos_x + curr_vel_x + dx, curr_pos_y + curr_vel_y + dy)
            heuristic = self.__heuristic__(possible_target_pos.x,possible_target_pos.y, closest_goal.x, closest_goal.y)
            cost = self.calculate_cost(Vertex(dx,dy), heuristic)
            if cost < lowest_cost and not self.check_illegal_move(possible_target_pos):
                lowest_cost = cost
                dir_to_lowest_f.refresh(dx,dy)
        return dir_to_lowest_f
        
        
    
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
            
            
    def say_decision_to_judge(self, velocity: Vertex):
        print(f'{velocity.y} {velocity.x}')
        
        
        
    def race(self):
        
        while self.run:
            self.update_player_positions()
            decision = self.a_star()
            self.say_decision_to_judge(decision)
    


def main():
    myPreciousWinner = RacerAgent()
    myPreciousWinner.race()
    

    
if __name__ == '__main__':
    main()
    
