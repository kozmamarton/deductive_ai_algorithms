import argparse
import pygame
from judge import replay

from typing import Optional, ClassVar, NamedTuple

class Screen:
    MARGIN = 10
    DEFAULT_TRACK_CELL_SIZE = 12
    DEFAULT_GRID_LINE_WIDTH = 1
    THIN_WALL_WIDTH = 3

    class TrackColours(NamedTuple):
        wall: pygame.Color = pygame.Color('red')
        thin_wall: pygame.Color = pygame.Color('darkred')
        road: pygame.Color = pygame.Color('lightgreen')
        player_contour: pygame.Color = pygame.Color(50, 50, 50, 100)
        grid: pygame.Color = pygame.Color('gray')
        goal_cells: tuple[pygame.Color, pygame.Color] = (pygame.Color('black'),
                                                         pygame.Color('white'))

    TRACK_COLOURS = TrackColours()
    # from Matplotlib's tab10
    PLAYER_COLOURS: ClassVar[list[pygame.Color]] = [
        pygame.Color(c) for c in
        [[31, 119, 180], [255, 127, 14], [44, 160, 44], [214, 39, 40],
         [148, 103, 189], [140, 86, 75], [227, 119, 194], [127, 127, 127],
         [188, 189, 34], [23, 190, 207], [250, 128, 114], [255, 140, 0],
         [175, 238, 238], [0, 191, 255], [186, 85, 211], [255, 0, 255],
         [192, 192, 192], [178, 34, 34], [210, 105, 30], [255, 215, 0],
         [107, 142, 35], [184, 134, 11], [0, 250, 154], [47, 79, 79],
         [139, 0, 139], [220, 20, 60], [255, 127, 80], [0, 0, 128],
         [65, 105, 225], [255, 105, 180], [255, 239, 213]]
    ]
    INACTIVE_PLAYER_ALPHA = 160
    FONT_SIZE = 30
    FONT_COLOUR = pygame.Color(255, 255, 255)
    BACKGROUND_COLOUR = pygame.Color('black')

    def __init__(self, env_info: replay.EnvInfo, cell_size: int):
        track_width = len(env_info.track[0])
        track_height = len(env_info.track)
        self.track_cell_size = cell_size
        self.trace_width = self.track_cell_size // 8 + 1
        self.grid_line_width = self.DEFAULT_GRID_LINE_WIDTH
        width = track_width * self.track_cell_size + 2 * self.MARGIN
        height = (
            4 * self.MARGIN  #
            + track_height * self.track_cell_size  # track
            + 2 * self.FONT_SIZE  # status lines
        )
        self.screen = pygame.display.set_mode((width, height),
                                              flags=pygame.RESIZABLE)
        self.font = pygame.font.SysFont('', self.FONT_SIZE)
        self.track_height = track_height * self.track_cell_size
        if env_info.player_names:
            self.player_names = env_info.player_names
        else:
            self.player_names = [str(i) for i in range(env_info.num_players)]
        self._draw_track_first(env_info)

    def _cell_pos(self, r: int, c: int) -> tuple[int, int]:
        y = self.MARGIN + self.track_cell_size * r
        x = self.MARGIN + self.track_cell_size * c
        return y, x

    def draw_track(self) -> None:
        self.screen.blit(self.track_surface, (self.MARGIN, self.MARGIN))

    def _draw_track_first(self, env_info: replay.EnvInfo) -> None:
        width = (len(env_info.track[0])
                 - 1) * self.track_cell_size + self.grid_line_width
        height = (len(env_info.track)
                  - 1) * self.track_cell_size + self.grid_line_width
        self.track_surface = pygame.Surface((width, height))
        grid_surface = pygame.Surface((width, height)).convert_alpha()
        grid_surface.fill((0, 0, 0, 0))

        c = env_info.track
        for i, row in enumerate(env_info.track):  # row_ind
            for j, cell in enumerate(row):  # col_ind
                # draw a rectangle if not in the last row or column
                if i + 1 < len(env_info.track) and j + 1 < len(
                        env_info.track[0]):
                    cell_color = self.TRACK_COLOURS.wall if c[i][j] < 0 and c[
                        i + 1][j] < 0 and c[i][j + 1] < 0 and c[i + 1][
                            j + 1] < 0 else self.TRACK_COLOURS.road
                    pygame.draw.rect(
                        self.track_surface, cell_color,
                        pygame.Rect(j * self.track_cell_size,
                                    i * self.track_cell_size,
                                    self.track_cell_size, self.track_cell_size))
                # draw separating lines
                x = j * self.track_cell_size
                y = i * self.track_cell_size
                if i > 0 and c[i][j] < 0 and c[i - 1][j] < 0:  # pylint: disable=chained-comparison
                    border_color = self.TRACK_COLOURS.thin_wall
                    border_width = self.THIN_WALL_WIDTH * self.grid_line_width
                else:
                    border_color = self.TRACK_COLOURS.grid
                    border_width = self.grid_line_width
                pygame.draw.line(
                    self.track_surface,
                    border_color, (x, y), (x, y - self.track_cell_size),
                    width=border_width)
                if j > 0 and c[i][j] < 0 and c[i][j - 1] < 0:  # pylint: disable=chained-comparison
                    border_color = self.TRACK_COLOURS.thin_wall
                    border_width = self.THIN_WALL_WIDTH * self.grid_line_width
                else:
                    border_color = self.TRACK_COLOURS.grid
                    border_width = self.grid_line_width
                pygame.draw.line(
                    self.track_surface,
                    border_color, (x, y), (x - self.track_cell_size, y),
                    width=border_width)
                # draw goal field
                if c[i][j] == 100:
                    pygame.draw.rect(
                        grid_surface, self.TRACK_COLOURS.goal_cells[(i+j) % 2],
                        pygame.Rect((j-0.5) * self.track_cell_size,
                                    (i-0.5) * self.track_cell_size,
                                    self.track_cell_size, self.track_cell_size))

        self.track_surface.blit(grid_surface, (0, 0))

    def draw_players(self, state: replay.State):
        for i, p in enumerate(state.players):
            y, x = self._cell_pos(p.x, p.y)
            y += 1
            x += 1
            pygame.draw.circle(self.screen, self.PLAYER_COLOURS[i], (x, y),
                               self.track_cell_size / 3 + 1)
            pygame.draw.circle(
                self.screen,
                self.TRACK_COLOURS.player_contour, (x, y),
                self.track_cell_size / 3 + 1,
                width=1)

    def draw_forward_arrows(self, state: replay.State):
        buffer = pygame.Surface(
            (self.track_surface.get_width(),
             self.track_surface.get_height())).convert_alpha()
        buffer.fill((0, 0, 0, 0))
        for i, p in enumerate(state.players):
            y, x = self._cell_pos(p.x, p.y)
            y2, x2 = self._cell_pos(p.x + p.vel_x, p.y + p.vel_y)
            inactive_player_colour = pygame.Color(self.PLAYER_COLOURS[i])
            inactive_player_colour.a = self.INACTIVE_PLAYER_ALPHA
            pygame.draw.line(
                buffer,
                inactive_player_colour, (x, y), (x2, y2),
                width=self.trace_width)
            for yy in range(p.y + p.vel_y - 1, p.y + p.vel_y + 2):  # [-1,0;1]
                for xx in range(p.x + p.vel_x - 1,
                                p.x + p.vel_x + 2):  # [-1,0;1]
                    y, x = self._cell_pos(xx, yy)
                    pygame.draw.circle(buffer, inactive_player_colour, (x, y),
                                       self.track_cell_size / 4 + 1)
        self.screen.blit(buffer, (0, 0))

    def draw_backward_arrows(self, last_state: replay.State,
                             state: replay.State) -> None:
        buffer = pygame.Surface(
            (self.track_surface.get_width(),
             self.track_surface.get_height())).convert_alpha()
        buffer.fill((0, 0, 0, 0))
        for i, (p_old,
                p_now) in enumerate(zip(last_state.players, state.players)):
            if p_old == p_now:
                continue
            y, x = self._cell_pos(p_old.x, p_old.y)
            y2, x2 = self._cell_pos(p_now.x, p_now.y)
            pygame.draw.line(
                buffer,
                self.PLAYER_COLOURS[i], (x, y), (x2, y2),
                width=self.trace_width)
            # draw x to the starting point of the arrow
            r = self.track_cell_size // 4
            pygame.draw.line(
                buffer,
                self.PLAYER_COLOURS[i], (x - r, y - r), (x + r, y + r),
                width=self.trace_width)
            pygame.draw.line(
                buffer,
                self.PLAYER_COLOURS[i], (x - r, y + r), (x + r, y - r),
                width=self.trace_width)
        self.screen.blit(buffer, (0, 0))

    def print_info(self, t: int | str, last_step: Optional[replay.PlayerStep]):
        line = self.font.render(f'Turn: {t}', True, self.FONT_COLOUR, self.BACKGROUND_COLOUR)
        y = 2 * self.MARGIN + self.track_height
        self.screen.blit(line, (self.MARGIN, y))
        if last_step is not None:
            y += self.MARGIN + self.FONT_SIZE
            if last_step.status:
                step_text = last_step.status
            elif not last_step.success:
                step_text = 'Invalid move.'
            else:
                step_text = (
                    f'last move: dx: {last_step.dx} dy: {last_step.dy}')
            player_legend = self.font.render(
                f'Player {self.player_names[last_step.player_ind]}: ', True,
                self.PLAYER_COLOURS[last_step.player_ind], self.BACKGROUND_COLOUR)
            status_line = self.font.render(f'{step_text}', True,
                                           self.FONT_COLOUR, self.BACKGROUND_COLOUR)
            self.screen.blit(player_legend, (self.MARGIN, y))
            self.screen.blit(status_line,
                             (self.MARGIN + player_legend.get_width(), y))

    def draw_all(self,
                 state: replay.State,
                 last_state: Optional[replay.State],
                 last_step: Optional[replay.PlayerStep],
                 max_t: Optional[str | int] = None) -> None:
        self.screen.fill(self.BACKGROUND_COLOUR)
        self.draw_track()
        self.draw_players(state)
        self.draw_forward_arrows(state)
        if last_state is not None:
            self.draw_backward_arrows(last_state, state)
        if max_t:
            turn = f'{state.turn} / {max_t}'
        else:
            turn = str(state.turn)
        self.print_info(turn, last_step)

def app(history: replay.Replay, cell_size: int):
    pygame.init()
    pygame.display.set_caption('Grid race')
    screen = Screen(history.env_info, cell_size)
    clock = pygame.time.Clock()
    running = True
    t = 0
    playdir = 0
    repeat = 0
    last_step = None
    max_turns = max(history.states, key=lambda s: s.turn).turn
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    playdir = 1
                elif event.key == pygame.K_LEFT:
                    playdir = -1
            elif event.type == pygame.KEYUP:
                playdir = 0
                repeat = 0
        if playdir != 0:
            repeat += 1
        if playdir == 1 and (repeat == 1
                             or repeat > 10) and t < len(history.states) - 1:
            t += 1
        if playdir == -1 and (repeat == 1 or repeat > 10) and t > 0:
            t -= 1
        if t > 0:
            last_step = history.steps[t - 1]
            last_state = history.states[t - 1]
        else:
            last_step = None
            last_state = None

        screen.draw_all(history.states[t], last_state, last_step, max_turns)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'replay_file',
        type=str,
        help='Path to the replay file (output by the judge program).')
    parser.add_argument(
        '--cell_size',
        type=int,
        default=Screen.DEFAULT_TRACK_CELL_SIZE,
        help='Size (in pixels) of the cells in the visualisation.')
    return parser.parse_args()

def main():
    args = parse_args()
    history = replay.deserialise(args.replay_file, allow_extra_keys=True)
    assert history.version >= 1, (
        f'Replay file version ({history.version}) is too old.')
    app(history, args.cell_size)

if __name__ == "__main__":
    main()
