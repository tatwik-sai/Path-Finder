import pygame   # Graphics
import math     # Computation
from search import Search   # To Solve


class PathFinder:
    """
    A path finder visualizer to visualize path finding algorithms.
    """
    def __init__(self, shape: tuple = (33, 65), size: int = 20, algorithm: str = 'bfs'):
        # Variables
        self.running = True
        self.shifting_start = False
        self.shifting_stop = False
        self.adding_obstacles = False
        self.removing_obstacles = False
        self.blocks = []

        # Solve Variables
        self.solve_speed = 5
        self.moved_after_solve = False
        self.solving = False
        self.solved = False
        self.algorithm = algorithm
        self.exploring = False
        self.turned = False
        self.constructing_path = False
        self.found_solution = False
        self.explored = []
        self.path = []

        # Sizes
        self.shape = shape
        self.block_size = size
        self.gap = 1
        self.width = shape[1] * self.block_size + (shape[1] + 1) * self.gap
        self.height = shape[0] * self.block_size + (shape[0] + 1) * self.gap

        # Display
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_icon(pygame.image.load('icon.png'))
        pygame.display.set_caption('Path Finder Visualiser' + str(shape))

        # Images
        self.start_img = pygame.transform.scale(pygame.image.load('start.png'), (self.block_size, self.block_size))
        self.goal_img = pygame.transform.scale(pygame.image.load('goal.png'), (self.block_size, self.block_size))

        # Colors
        self.bg_color = (0, 161, 157)
        self.block_color = (255, 255, 255)
        self.colors = {'free': self.block_color, 'start': self.block_color, 'goal': self.block_color,
                       'obstacle': (0, 0, 0), 'path': (64, 204, 49), 'explored': (255, 0, 0)}

        # Adding Blocks
        x, y = self.gap, self.gap
        for i in range(self.shape[0]):
            row_blocks = []
            for j in range(self.shape[1]):
                row_blocks.append([pygame.Rect((x, y), (self.block_size, self.block_size)), 'free'])
                x += self.block_size + self.gap
            self.blocks.append(row_blocks)
            x = self.gap
            y += self.block_size + self.gap

        # Start, Stop Initialization
        self.start_pos = (int(shape[0] / 2), int(shape[1] / 2))
        self.goal_pos = (self.start_pos[0], self.start_pos[1] + 1)
        self.blocks[self.start_pos[0]][self.start_pos[1]][1] = 'start'
        self.blocks[self.goal_pos[0]][self.goal_pos[1]][1] = 'goal'

    def draw(self):
        """
        Draws different types of blocks on to the screen.
        """
        self.screen.fill(self.bg_color)
        for row in self.blocks:
            for block in row:
                pygame.draw.rect(self.screen, self.colors[block[1]], block[0], border_radius=5)
                if block[1] == 'start':
                    rect = self.start_img.get_rect()
                    rect.x, rect.y = block[0].x, block[0].y
                    self.screen.blit(self.start_img, rect)
                elif block[1] == 'goal':
                    rect = self.goal_img.get_rect()
                    rect.x, rect.y = block[0].x, block[0].y
                    self.screen.blit(self.goal_img, rect)
        pygame.display.update()

    def handle_clicks(self, pos: tuple):
        """
        Handles mouse users mouse inputs.

        :param pos: The position of the mouse.
        """
        if self.solving or self.solved:
            self.reset()
        for row in range(self.shape[0]):
            for col in range(self.shape[1]):
                if self.blocks[row][col][0].collidepoint(pos):
                    if self.adding_obstacles and self.blocks[row][col][1] == 'free':
                        self.blocks[row][col][1] = 'obstacle'
                    elif self.removing_obstacles and self.blocks[row][col][1] == 'obstacle':
                        self.blocks[row][col][1] = 'free'
                    elif self.shifting_start and self.blocks[row][col][1] == 'free':
                        self.blocks[self.start_pos[0]][self.start_pos[1]][1] = 'free'
                        self.start_pos = (row, col)
                        self.blocks[row][col][1] = 'start'
                    elif self.shifting_stop and self.blocks[row][col][1] == 'free':
                        self.blocks[self.goal_pos[0]][self.goal_pos[1]][1] = 'free'
                        self.goal_pos = (row, col)
                        self.blocks[row][col][1] = 'goal'

    def next_states(self, state: tuple) -> list:
        """
        Returns the next possible states from the given state.

        :param state: The position of the block.
        :return: The next possible states from the given state.
        """
        row, col = state[0], state[1]
        surrounding_blocks = [(row + 1, col), (row - 1, col), (row, col + 1), (row, col - 1)]
        next_blocks = []
        for pos in surrounding_blocks:
            if pos[0] < 0 or pos[0] >= self.shape[0] or pos[1] < 0 or pos[1] >= self.shape[1]:
                pass
            else:
                if self.blocks[pos[0]][pos[1]][1] in ['free', 'goal']:
                    next_blocks.append(pos)
        return next_blocks

    def cost(self, state: tuple) -> float:
        """
        Returns the negative of the direct distance between goal and the given state.

        :param state: The position of the block.
        :return: The direct point to point distance.
        """
        return -1 * math.sqrt((state[0] - self.goal_pos[0]) ** 2 + (state[1] - self.goal_pos[1]) ** 2)

    def solve(self):
        """
        Solves the maze and updates the path and explored variables of the class.
        """
        try:
            search = Search(goal_test=lambda state: state == self.goal_pos, next_states=self.next_states)
            search.set_state(self.start_pos)
            self.path = search.search(algorithm=self.algorithm, verbose=False, show_time=False, heuristic=self.cost)
            self.explored = list(search.tree.tree.keys())[2:]
            self.explored = [(int(pos.split(',')[0][1:]), int(pos.split(',')[1][:-1])) for pos in self.explored]
            self.path = self.path[1:-1]
            self.exploring = True
            self.found_solution = True
        except StopIteration as error:
            self.found_solution = False
            print(error)

    def visualise_solve(self, speed=None):
        """
        Visualizes the path on to the pygame window.

        :param speed: The number of blocks to visualize on every call.
        """
        if speed is None:
            speed = self.solve_speed
        for _ in range(speed):
            if self.exploring:
                pos = self.explored.pop(0)
                if pos != self.goal_pos:
                    self.blocks[pos[0]][pos[1]][1] = 'explored'
                if len(self.explored) == 0:
                    self.exploring = False
            elif not self.turned:
                if len(self.path) > 0:
                    rotate_degree = 0
                    if self.path[0][0] < self.start_pos[0]:
                        rotate_degree = 90
                    elif self.path[0][0] > self.start_pos[0]:
                        rotate_degree = 270
                    elif self.path[0][1] < self.start_pos[1]:
                        rotate_degree = 180
                    self.start_img = pygame.transform.scale(pygame.image.load('start.png'), (self.block_size, self.block_size))
                    self.start_img = pygame.transform.rotate(self.start_img, rotate_degree)
                self.turned = True
                self.constructing_path = True
            elif self.constructing_path:
                if len(self.path) > 0:
                    pos = self.path.pop()
                    if pos != self.goal_pos:
                        self.blocks[pos[0]][pos[1]][1] = 'path'
                else:
                    self.turned = False
                    self.constructing_path = False
                    self.solving = False
                    self.solved = True
                    break

    def reset(self):
        """
        Resets the program but keeps start, stop, and obstacle blocks.
        """
        self.solved = False
        self.solving = False
        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                if self.blocks[i][j][1] in ['path', 'explored']:
                    self.blocks[i][j][1] = 'free'
        self.start_img = pygame.transform.scale(pygame.image.load('start.png'), (self.block_size, self.block_size))

    def main(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.blocks[self.start_pos[0]][self.start_pos[1]][0].collidepoint(pygame.mouse.get_pos()):
                            self.shifting_start = True
                        elif self.blocks[self.goal_pos[0]][self.goal_pos[1]][0].collidepoint(pygame.mouse.get_pos()):
                            self.shifting_stop = True
                        else:
                            self.adding_obstacles = True
                    elif event.button == 3:
                        self.removing_obstacles = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        if self.adding_obstacles:
                            self.adding_obstacles = False
                        elif self.shifting_start:
                            self.shifting_start = False
                        else:
                            self.shifting_stop = False
                    elif event.button == 3:
                        self.removing_obstacles = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not self.solving:
                        if not self.solved:
                            self.solve()
                            self.solving = True
                    elif event.key == pygame.K_RETURN:
                        self.reset()
                        self.solve()
                        self.visualise_solve(self.shape[0]*self.shape[1])
                    elif event.key == pygame.K_r:
                        self.__init__()
            if self.solving and self.found_solution:
                self.visualise_solve()
            if any([self.adding_obstacles, self.removing_obstacles, self.shifting_start, self.shifting_stop]):
                self.handle_clicks(pygame.mouse.get_pos())
            self.draw()


if __name__ == '__main__':
    print("""
Mouse Clicks:
    left: To draw obstacles and to shift start and goal positions on drag.
    right: To remove obstacles on drag.
Keys:
    space: To visualize the solving process slowly.
    enter: To visualize the solving process on one go.
    """)
    # PathFinder((22, 44), 30).main()
    PathFinder().main()
