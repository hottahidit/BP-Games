import random
import time

WIDTH = 10
HEIGHT = 10

class BrickBreakerGame:
    def __init__(self):
        self.width = WIDTH
        self.height = HEIGHT
        self.lives = 3
        self.reset()

    def reset(self):
        self.bricks = [[1 for _ in range(self.width)] for _ in range(3)]
        self.paddle_pos = self.width // 2
        self.ball_pos = [self.height - 2, self.paddle_pos]
        self.ball_dir = [0, 0]
        self.balls = [self.ball_pos[:]]
        self.running = False
        self.level = 1
        self.speed = 0.5
        self.last_move_time = time.time()

    def start(self):
        if not self.running:
            direction = random.choice([-1, 1])
            self.ball_dir = [-1, direction]
            self.running = True
            self.last_move_time = time.time()

    def move_paddle(self, direction):
        if direction == "left" and self.paddle_pos > 0:
            self.paddle_pos -= 1
        elif direction == "right" and self.paddle_pos < self.width - 1:
            self.paddle_pos += 1
        if not self.running:
            self.ball_pos[1] = self.paddle_pos

    def update(self):
        if not self.running or time.time() - self.last_move_time < self.speed:
            return
        self.last_move_time = time.time()
        new_r = self.ball_pos[0] + self.ball_dir[0]
        new_c = self.ball_pos[1] + self.ball_dir[1]

        if new_c < 0 or new_c >= self.width:
            self.ball_dir[1] *= -1
            new_c = self.ball_pos[1] + self.ball_dir[1]

        if new_r < len(self.bricks):
            if self.bricks[new_r][new_c] > 0:
                self.bricks[new_r][new_c] -= 1
                self.ball_dir[0] *= -1
                new_r = self.ball_pos[0] + self.ball_dir[0]

        elif new_r == self.height - 1:
            if new_c == self.paddle_pos:
                offset = new_c - self.paddle_pos
                self.ball_dir[0] = -1
                self.ball_dir[1] = offset
            else:
                self.lives -= 1
                self.running = False
                if self.lives > 0:
                    self.ball_pos = [self.height - 2, self.paddle_pos]
                    self.ball_dir = [0, 0]
                    self.last_move_time = time.time()
                else:
                    self.reset()
                return

        if new_r < 0:
            self.ball_dir[0] *= -1
            new_r = self.ball_pos[0] + self.ball_dir[0]

        self.ball_pos = [new_r, new_c]

    def get_state(self):
        grid = [[" " for _ in range(self.width)] for _ in range(self.height)]
        for r in range(len(self.bricks)):
            for c in range(self.width):
                if self.bricks[r][c] > 0:
                    grid[r][c] = "#"
        grid[self.height - 1][self.paddle_pos] = "="
        grid[self.ball_pos[0]][self.ball_pos[1]] = "o"
        return "\n".join("".join(row) for row in grid)

