import numpy as np
from logger import get_logger

DEBUG = False


class Track:
    
    TRACK_WIDTH: int
    TRACK_HEIGHT: int
    PLAYERS_COUNT: int
    TRACK_MAXIMUM_DISTANCE: int
    VISIBILITY_RADIUS: int
    map: np.ndarray
    start_position: tuple[int,int]
    OIL_CELL_VALUE: int = 91
    SAND_CELL_VALUE: int = 92
    GOAL_CELL_VALUE: int = 100
    
    def __init__(self):
        self.__read_initial_props()
        self.TRACK_MAXIMUM_DISTANCE = self.TRACK_HEIGHT * self.TRACK_WIDTH
        self.map =np.full((self.TRACK_HEIGHT,self.TRACK_WIDTH),3,dtype=int)
        self.mylogger = get_logger()
    
    def __read_initial_props(self):
        self.TRACK_HEIGHT, self.TRACK_WIDTH, self.PLAYERS_COUNT, self.VISIBILITY_RADIUS = map(int, input().split())  
    
    def read_track(self, playerPos : tuple[int, int]) -> np.ndarray:
        for i in range(2 * self.VISIBILITY_RADIUS + 1):
            line = [int(a) for a in input().split()]
            x = playerPos[0] - self.VISIBILITY_RADIUS + i
            if x < 0 or x >= self.TRACK_HEIGHT:
                continue
            y_start = playerPos[1] - self.VISIBILITY_RADIUS
            y_end = y_start + 2 * self.VISIBILITY_RADIUS + 1
            if y_start < 0:
                line = line[-y_start:]
                y_start = 0
            if y_end > self.TRACK_WIDTH:
                line = line[:-(y_end - self.TRACK_WIDTH)]
                y_end = self.TRACK_WIDTH
            #self.map[x, y_start:y_end] = line
            for column in range(len(line)):
                if self.map[x,y_start+column] == 3 and line[column] != 3:   
                    self.map[x, y_start+column] = line[column]
                    
        if DEBUG:
            for i in range(self.map.shape[0]):
                for j in range(self.map.shape[1]):
                    if (i,j) == playerPos:
                        self.mylogger('X',' ')
                        continue
                    cell_value = self.map[(i,j)]
                    self.mylogger(cell_value,' ' if cell_value < 0 else '  ')
                self.mylogger("")
       
          
    def get_track(self):
        return self.map
    
    def get_visible_track(self):
        mask = (self.map > -1)
        return np.column_stack(np.nonzero(mask))
    
    def get_goals(self):
        return np.argwhere(self.map == self.GOAL_CELL_VALUE)
    
    def get_start(self):
        return np.argwhere(self.map == 1)

    def get_cell_value(self, coords: tuple[int,int]):
        if coords[0] < 0 or coords[0] >= self.map.shape[0]\
            or coords[1] < 0 or coords[1] >= self.map.shape[1]:
                return -1
        return self.map[coords]
    
    def traversable(self,cell_value: int) -> bool:
        return cell_value > -1# and cell_value != 3
    
    def valid_line(self, pos1: np.ndarray, pos2: np.ndarray) -> bool:
        #stolen from lieutenant crown becuase i was lazy to write it myself but i understand how this works
        track = self.map
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
                if (not self.traversable(track[x, y_ceil])
                        and not self.traversable(track[x, y_floor])):
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
                if (not self.traversable(track[x_ceil, y])
                        and not self.traversable(track[x_floor, y])):
                    return False
        return True
    