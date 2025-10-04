import sys
import numpy as np
from heapq import heappop, heappush
from typing import Optional, NamedTuple, List, Tuple, Dict, Set


class Player(NamedTuple):
    x: int
    y: int
    vel_x: int
    vel_y: int

    @property
    def pos(self) -> np.ndarray:
        return np.array([self.x, self.y])

    @property
    def vel(self) -> np.ndarray:
        return np.array([self.vel_x, self.vel_y])


class Circuit(NamedTuple):
    track: np.ndarray  # the map of the track
    num_players: int


class State(NamedTuple):
    circuit: Circuit
    players: List[Player]
    agent: Player


def read_map() -> Circuit:
    H, W, num_players = map(int, sys.stdin.readline().split())
    track = []
    for _ in range(H):
        row = list(map(int, sys.stdin.readline().split()))
        track.append(row)
    track = np.array(track)
    return Circuit(track, num_players)


def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def a_star_search(grid, start, goal):
    neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]  # Including diagonals
    close_set: Set = set()
    came_from: Dict = {}
    gscore: Dict = {start: 0}
    fscore: Dict = {start: heuristic(start, goal)}
    oheap = []
    heappush(oheap, (fscore[start], start))

    while oheap:
        current = heappop(oheap)[1]

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]

        close_set.add(current)
        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j
            if 0 <= neighbor[0] < grid.shape[0] and 0 <= neighbor[1] < grid.shape[1] and grid[
                neighbor[0], neighbor[1]] != -1:
                tentative_g_score = gscore[current] + 1
                if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, float('inf')):
                    continue
                if tentative_g_score < gscore.get(neighbor, float('inf')) or neighbor not in [i[1] for i in oheap]:
                    came_from[neighbor] = current
                    gscore[neighbor] = tentative_g_score
                    fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    heappush(oheap, (fscore[neighbor], neighbor))
    return []


def calculate_move(path: List[Tuple[int, int]], state: State) -> Tuple[int, int]:
    current_position = (state.agent.x, state.agent.y)
    current_velocity = (state.agent.vel_x, state.agent.vel_y)

    # Számítsuk ki a tervezett érkezési helyet a jelenlegi sebességgel
    projected_position = (
        current_position[0] + current_velocity[0],
        current_position[1] + current_velocity[1]
    )

    # Nézzük meg a projected position szomszédait
    neighbors = [
        (projected_position[0] + dx, projected_position[1] + dy)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    ]

    # Ha a projected position eleme a path-nak vagy annak szomszédjai közül bármelyik
    if projected_position in path or any(neighbor in path for neighbor in neighbors):
        closest_point = max(
            (point for point in neighbors if point in path),
            key=lambda p: path.index(p),
            default=None
        )

        if closest_point:
            # Gyorsítás vagy lassítás a path-hoz való igazodás érdekében
            desired_velocity_change = (
                closest_point[0] - current_position[0],
                closest_point[1] - current_position[1]
            )
            acceleration_x = max(min(desired_velocity_change[0], 1), -1)
            acceleration_y = max(min(desired_velocity_change[1], 1), -1)
            return (acceleration_x, acceleration_y)

    # Ha a projected position és annak szomszédjai sem elemei a path-nek
    if all(neighbor not in path for neighbor in neighbors):
        # Lassítás a letérés megelőzése érdekében
        acceleration_x = -1 if current_velocity[0] > 0 else (1 if current_velocity[0] < 0 else 0)
        acceleration_y = -1 if current_velocity[1] > 0 else (1 if current_velocity[1] < 0 else 0)

        return (acceleration_x, acceleration_y)

    return (0, 0)  # Alapértelmezés szerint lassítás, ha nincs szomszédos path-mező


def main():
    
    circuit = read_map()
    start_positions = np.argwhere(circuit.track == 1)
    goal_positions = np.argwhere(circuit.track == 100)

    if not start_positions.any() or not goal_positions.any():
        sys.stderr.write("No start or goal positions found.\n")
        return

    start_pos = tuple(start_positions[0])
    goal_pos = tuple(goal_positions[0])

    path = a_star_search(circuit.track, start_pos, goal_pos)

    state = State(circuit, [], Player(*start_pos, 0, 0))  # Initialize agent at start position with zero velocity

    while True:
        line = sys.stdin.readline().strip()
        if line == '~~~END~~~':
            break
        if len(line.split()) == 4:
            posx, posy, velx, vely = map(int, line.split())
            path = a_star_search(circuit.track, (posx, posy), goal_pos)
            state = state._replace(agent=Player(posx, posy, velx, vely))
            delta = calculate_move(path, state)
            sys.stdout.write(f'{delta[0]} {delta[1]}\n')
            sys.stdout.flush()

if __name__ == "__main__":
    print('READY', flush=True)
    main()