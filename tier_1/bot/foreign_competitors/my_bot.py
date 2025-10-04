import sys
from heapq import heappush, heappop

import numpy as np
from typing import Optional, NamedTuple, Set, Dict, List, Tuple


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
    players: list[Player]
    agent: Player

def read_map() -> Circuit:
    H, W, num_players = map(int, input().split())
    track = []
    for r_ind in range(H):
        row = list(map(int, input().split()))
        track.append(row)
    track = np.array(track)
    return Circuit(track, num_players)

def read_observation(old_state: State) -> Optional[State]:
    line = input()
    if line == '~~~END~~~':
        return None
    posx, posy, velx, vely = map(int, line.split())
    agent = Player(posx, posy, velx, vely)
    players = []
    for _ in range(old_state.circuit.num_players):
        pposx, pposy = map(int, input().split())
        players.append(Player(pposx, pposy, 0, 0))
    return old_state._replace(players=players, agent=agent)

def collision_det(track, pos: tuple[int, int], players, neighbor):
    positions = {tuple(pos) for player in players}
    return (
            0 <= neighbor[0] < track.shape[0] and
            0 <= neighbor[1] < track.shape[1] and
            track[neighbor[0], neighbor[1]] != -1 and
            neighbor not in positions and
            tuple(pos) not in positions
    )

def heuristic(x, y):
    return max(abs(x[0]-y[0]), abs(x[1]-y[1]))
    #return abs(x[0]-y[0]) + abs(x[1]-y[1])
    #return np.linalg.norm(np.array(x) - np.array(y))


def astar(state: State, players, start, goals):
    track = state.circuit.track
    closedSet: Set = set()
    came_from: Dict = {}
    g_score: Dict = {tuple(start): 0}
    closestGoal = min(goals, key=lambda x: heuristic (start, x))
    f_score: Dict = {tuple(start): heuristic(start, closestGoal)}
    heap = []
    heappush(heap, (f_score[tuple(start)], start))
    neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]  # Including diagonals

    while heap:
        current = heappop(heap)[1]

        if (np.array(current) == goals).all(1).any():
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            return path[::-1]

        closedSet.add(tuple(current))
        for dx, dy in neighbors:
            neighbor = (current[0] + dx, current[1] + dy)
            if not collision_det(track, current, players, neighbor) or neighbor in closedSet:
                continue
            elif neighbor not in came_from or neighbor not in [i[1] for i in heap]:
                came_from[neighbor] = current
                g_score[neighbor] = g_score[current] + 1
                closestGoal = min(goals, key=lambda x: heuristic(neighbor, x))
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, closestGoal)
                heappush(heap, (f_score[neighbor], neighbor))
    return None

def calculate_move(path: List[Tuple[int, int]], state: State) -> tuple[int, int]:
    current_position = (state.agent.x, state.agent.y)
    current_velocity = (state.agent.vel_x, state.agent.vel_y)
    if not path or current_position == path[-1]:
        return 0, 0  # No movement if we are at the goal or no path

    # Desired position in the next step
    target_position = path[0]

    # If the target position is reached, remove it from the path
    if target_position == current_position:
        path.pop(0)
        if not path:
            return 0, 0  # Stop if there are no more targets
        target_position = path[0]  # New target position

    # Calculate the necessary acceleration to reach the target position
    desired_velocity_change = (target_position[0] - (current_position[0] + current_velocity[0]),
                               target_position[1] - (current_position[1] + current_velocity[1]))

    # Limit acceleration between -1 and 1
    acceleration_x = max(min(desired_velocity_change[0], 1), -1)
    acceleration_y = max(min(desired_velocity_change[1], 1), -1)

    return acceleration_x, acceleration_y

def main():
    print('READY', flush=True)
    circuit = read_map()
    state: Optional[State] = State(circuit, [], None)

    start_positions = np.argwhere(circuit.track == 1)
    goal_positions = np.argwhere(circuit.track == 100)

    if not start_positions.any() or not goal_positions.any():
        sys.stderr.write("No start or goal positions found.\n")
        return

    state = read_observation(state)  # Initialize agent at start position with zero velocity
    start = state.agent.pos
    path = astar(state, state.players, start, goal_positions)


    while True:
        line = sys.stdin.readline().strip()
        if line == '~~~END~~~':
            break
        if len(line.split()) == 4:
            posx, posy, velx, vely = map(int, line.split())
            state = state._replace(agent=Player(posx, posy, velx, vely))
            delta = calculate_move(path, state)
            sys.stdout.write(f'{delta[0]} {delta[1]}\n')
            sys.stdout.flush()

if __name__ == "__main__":
    main()
