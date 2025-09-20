from random import Random
import numpy as np
from track import Track
from race_car import RaceCar
from enemy import EnemyRacer


class RacerAgent:
    
    ktm_exc_300 : RaceCar
    race_track : Track
    enemies : list[EnemyRacer]
    race_running : bool
    
    def __init__(self):
        self.race_track = Track()
        self.ktm_exc_300 = RaceCar()
        self.enemies = [ EnemyRacer(i) for i in range(0,self.race_track.PLAYERS_COUNT) ]   
        self.race_running = True
        
        
    def race(self):
        
        while self.race_running:
            self.update_player_positions()
            self.say_decision_to_judge()
    
    
    def update_player_positions(self):
        """Reads the observation input from the judge by calling the racer's input reader functions
            If our glorious racer ktm_exc_300 gets an end of race call, 
            then this function implicitly stops the race by setting the race_running object variable
        """
        
        if not self.ktm_exc_300.read_input():
            self.race_running = False
            return 
        for enemy in self.enemies:
            enemy.read_input()
            
            
    def say_decision_to_judge(self):
        rand = Random()
        vel_x = rand.randint(-1,1)
        vel_y = rand.randint(-1,1)
        print(f'{vel_x} {vel_y}')


def main():
    myPreciousWinner = RacerAgent()
    myPreciousWinner.race()
    

    
if __name__ == '__main__':
    main()
    
