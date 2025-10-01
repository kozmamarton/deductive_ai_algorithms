import numpy as np
class Track:
    
    TRACK_WIDTH: int
    TRACK_HEIGHT: int
    PLAYERS_COUNT: int
    TRACK_MAXIMUM_DISTANCE: int
    race_track: np.ndarray
    goal_positions: np.ndarray
    start_position: tuple[int,int]
    
    def __init__(self):
        self.race_track = self.__read_track__()
        self.goal_positions = self.__collect_goal_positions()
        self.TRACK_MAXIMUM_DISTANCE = self.TRACK_HEIGHT + self.TRACK_WIDTH
    
    def __read_track__(self) -> np.ndarray:
        self.TRACK_HEIGHT, self.TRACK_WIDTH, self.PLAYERS_COUNT = map(int, input().split()) 
        raw_race_track = []
        for i in range(self.TRACK_HEIGHT):
            row = list(map(int, input().split()))
            raw_race_track.append(row)
        return np.array(raw_race_track)    
        
    def __collect_goal_positions(self) -> np.ndarray:
        return np.argwhere(self.race_track == 100)
        
    def get_track(self):
        return self.race_track
    
    def get_all_props(self)->dict:
        properties = {
            "width" : self.TRACK_WIDTH,
            "height" : self.TRACK_HEIGHT,
            "players" : self.PLAYERS_COUNT,
            "track" : self.race_track,
            "start" : self.start_position
        }        
        return properties
    