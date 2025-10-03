import numpy as np
class Track:
    
    TRACK_WIDTH: int
    TRACK_HEIGHT: int
    PLAYERS_COUNT: int
    TRACK_MAXIMUM_DISTANCE: int
    map: np.ndarray
    goal_positions: np.ndarray
    start_position: tuple[int,int]
    
    def __init__(self):
        self.map = self.__read_track()
        self.goal_positions = self.__collect_goal_positions()
        self.TRACK_MAXIMUM_DISTANCE = self.TRACK_HEIGHT * self.TRACK_WIDTH
    
    def __read_track(self) -> np.ndarray:
        self.TRACK_HEIGHT, self.TRACK_WIDTH, self.PLAYERS_COUNT = map(int, input().split()) 
        raw_race_track = []
        for _ in range(self.TRACK_HEIGHT):
            row = list(map(int, input().split()))
            raw_race_track.append(row)
        return np.array(raw_race_track)    
        
    def __collect_goal_positions(self) -> np.ndarray:
        return np.argwhere(self.map == 100)
        
    def get_track(self):
        return self.map
    
    def get_goals(self):
        return self.goal_positions
    
    def __traversable(self,cell_value: int) -> bool:
        return cell_value > -1
    
    def valid_line(self, pos1: np.ndarray, pos2: np.ndarray) -> bool:
        #stolen from lieutenant crown becuase i was lazy to write it myself but i understand how this works
        track = self.map
        if (np.any(pos1 < 0) or np.any(pos2 < 0) or np.any(pos1 >= track.shape)
                or np.any(pos2 >= track.shape)):
            return False
        diff = pos2 - pos1
        # Go through the straight line connecting ``pos1`` and ``pos2``
        # cell-by-cell. Wall is blocking if either it is straight in the way or
        # there are two wall cells above/below each other and the line would go
        # "through" them.
        if diff[0] != 0:
            slope = diff[1] / diff[0]
            d = np.sign(diff[0])  # direction: left or right
            for i in range(abs(diff[0]) + 1):
                x = pos1[0] + i*d
                y = pos1[1] + i*slope*d
                y_ceil = np.ceil(y).astype(int)
                y_floor = np.floor(y).astype(int)
                if (not self.__traversable(track[x, y_ceil])
                        and not self.__traversable(track[x, y_floor])):
                    return False
        # Do the same, but examine two-cell-wall configurations when they are
        # side-by-side (east-west).
        if diff[1] != 0:
            slope = diff[0] / diff[1]
            d = np.sign(diff[1])  # direction: up or down
            for i in range(abs(diff[1]) + 1):
                x = pos1[0] + i*slope*d
                y = pos1[1] + i*d
                x_ceil = np.ceil(x).astype(int)
                x_floor = np.floor(x).astype(int)
                if (not self.__traversable(track[x_ceil, y])
                        and not self.__traversable(track[x_floor, y])):
                    return False
        return True
    