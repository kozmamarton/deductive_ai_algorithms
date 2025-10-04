import numpy as np

from typing import Optional, NamedTuple, Set, Dict
from queue import PriorityQueue

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

def collision_det(track, pos, players):
    positions = {tuple(player.pos) for player in players}
    return (
        0 <= pos[0] < track.shape[0] and
        0 <= pos[1] < track.shape[1] and
        track[pos[0], pos[1]] >= 0 and
        pos not in positions
    )

def heuristic(x, y):
    return max(abs(x[0]-y[0]), abs(x[1]-y[1]))
    #return abs(x[0]-y[0]) + abs(x[1]-y[1])
    #return np.linalg.norm(np.array(x) - np.array(y))

# Itt csak az aktuális pozíciómtól 1 távolságra látok és ahhoz viszonyítva találom ki az utat
# Emiatt könnyen neki mehet a falnak
# Vagy le kell korlátoznom a sebességet 1-re, vagy nézni kell, hogy hová mutat az irányzék
# (vagy mindkettő)
# Annyi változás történt, hogy
#   1. Típusossá tettem amit tudtam és ami magic-number volt azt kiemeltem fv elejére ( mert <3 C++ )
#   2. A folytonos minimumkeresés kiküszöbölésére prioritásos sor lett az openSet
#       és mivel a proritásos sorban nem lehet ellenőrizni, hogy mi van benne (vagy megviccelt a python)
#       ezért lett hozzá a segéd hash (set)
#   3. Átneveztem ezt-azt, hogy könnyebben felfogjam mi történik és hogy ne sírjon a fordítóm
#   4. Bekerült egy lokális változó, a g_score ellenörzésére,
#       hogy amerre nézek azt már felfedeztem-e jobb úton (ilyesmi valamiért nem volt a példakódban)
def astar(state: State, players: list[Player], start: tuple, goals: np.ndarray):
    track = state.circuit.track
    open_set = PriorityQueue()
    closed_set: Set = set()
    came_from: Dict = {}
    closest_goal = min(goals, key=lambda x: heuristic(start, x))
    g_score: Dict = {start: 0}
    f_score: Dict = {start: heuristic(start, closest_goal)}

    open_set.put((f_score[start], start))
    neighbors = [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    open_set_hash = {start}

    while not open_set.empty():
        current = open_set.get()[1]
        open_set_hash.remove(current)

        if (np.array(current) == goals).all(1).any():
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            return path[::-1]

        closed_set.add(current)
        for dx, dy in neighbors:
            neighbor = (current[0] + dx, current[1] + dy)

            if collision_det(track, neighbor, players):
                temp_g_score = g_score[current] + 1

                if neighbor in closed_set and temp_g_score >= g_score.get(neighbor, float('inf')):
                    continue
                if temp_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = temp_g_score
                    closest_goal = min(goals, key=lambda x: heuristic(neighbor, x))
                    f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, closest_goal)
                    if neighbor not in open_set_hash:
                        open_set.put((f_score[neighbor], neighbor))
                        open_set_hash.add(neighbor)

    return None

def calculate_move(state: State) -> tuple[int, int]:
    track = state.circuit.track
    start = tuple(state.agent.pos)
    goals = np.argwhere(track == 100)

    path = astar(state, state.players, start, goals)
    # Ez elég huncut, mert hiába tudod hogyan jutsz el a célba, ha a sebesség miatt nekimész a falnak
    if path:
        next_move = path[1]
        delta_x = next_move[0] - (start[0] + state.agent.vel_x)
        delta_y = next_move[1] - (start[1] + state.agent.vel_y)
        x_vel = max(min(delta_x, 1), -1)
        y_vel = max(min(delta_y, 1), -1)
        return x_vel, y_vel
    else:
        return 0, 0

def main():
    print('READY', flush=True)
    circuit = read_map()
    state: Optional[State] = State(circuit, [], None)
    while True:
        assert state is not None
        state = read_observation(state)
        if state is None:
            return
        delta = calculate_move(state)
        print(f'{delta[0]} {delta[1]}')

if __name__ == "__main__":
    main()
