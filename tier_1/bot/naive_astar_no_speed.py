import numpy as np
from typing import Optional, NamedTuple

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

def valid_move(track, pos, players):
    positions = {tuple(player.pos) for player in players}
    return (
        0 <= pos[0] < track.shape[0] and
        0 <= pos[1] < track.shape[1] and
        track[pos[0], pos[1]] >= 0 and
        pos not in positions
    )

def heuristic(x, y):
    return np.linalg.norm(np.array(x) - np.array(y))

def astar(track, players, start, goals):
    openSet = {start}
    closedSet = set()
    parent = {}
    g_score = {start: 0}
    closestGoal = min(goals, key=lambda x: heuristic (start, x))
    f_score = {start: heuristic(start, closestGoal)}

    while openSet:
        current = min(openSet, key=lambda x: f_score[x])
        if (np.array(current) == goals).all(1).any():
            path = [current]
            while current in parent:
                current = parent[current]
                path.append(current)
            return path[::-1]

        openSet.remove(current)
        closedSet.add(current)
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            child = (current[0] + dx, current[1] + dy)
            if not valid_move(track, child, players) or child in closedSet:
                continue
            if child not in openSet:
                openSet.add(child)
                parent[child] = current
                g_score[child] = g_score[current] + 1
                closestGoal = min(goals, key=lambda x: heuristic(child, x))
                f_score[child] = g_score[child] + heuristic(child, closestGoal)
    return None

def calculate_move(state: State) -> tuple[int, int]:
    track = state.circuit.track
    start = tuple(state.agent.pos)
    goals = np.argwhere(track == 100)

    path = astar(track, state.players, start, goals)
    if path:
        next_move = path[1]
        delta_x = next_move[0] - start[0]
        delta_y = next_move[1] - start[1]
        return delta_x, delta_y
    else:
        return 0, 0

def main():
    print('READY',flush=True)
    circuit = read_map()
    state: Optional[State] = State(circuit, [], None)
    while True:
        assert state is not None
        state = read_observation(state)
        if state is None:
            return
        delta = calculate_move(state)
        print(f'{delta[0]} {delta[1]}', flush=True)

if __name__ == "__main__":
    main()
