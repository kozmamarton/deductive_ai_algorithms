import numpy as np



class Track:
    
    TRACK_WIDTH: int
    TRACK_HEIGHT: int
    PLAYERS_COUNT: int
    race_track: np.ndarray
    
    
    def __init__(self):
        self.__read_track__()
    
    def __read_track__(self):
        self.TRACK_HEIGHT, self.TRACK_WIDTH, self.PLAYERS_COUNT = map(int, input().split()) 
        raw_race_track = []
        for i in range(self.TRACK_HEIGHT):
            row = list(map(int, input().split()))
            raw_race_track.append(row)
        self.race_track = np.array(raw_race_track)
        
    def get_track(self):
        return self.race_track
    
    def get_all_props(self)->dict:
        properties = {
            "width" : self.TRACK_WIDTH,
            "height" : self.TRACK_HEIGHT,
            "players" : self.PLAYERS_COUNT,
            "track" : self.race_track
        }        
        return properties