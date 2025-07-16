#Python game logic for brick breaker
from termcolor import colored as c

class Brick:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True


class Paddle:
    def __init__(self, width, game_width):
        self.width = width
        self.x = (game_width - width) // 2


class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class BrickBreaker:
    def __init__(self, width=20, height=20, paddle_width=5):
        self.width = width
        self.height = height
        self.paddle = Paddle(paddle_width, width)
        self.ball = Ball(x=width // 2, y=height - 3)
        self.bricks = self.generate_bricks(rows=4, cols=width // 2)

    def generate_bricks(self, rows, cols):
        bricks = []
        for row in range(rows):
            for col in range(cols):
                brick_x = col * 2  
                brick_y = row
                bricks.append(Brick(brick_x, brick_y))
        return bricks

    def print_board(self):
        grid = [[" " for _ in range(self.width)] for _ in range(self.height)]

        for brick in self.bricks:
            if brick.alive:
                grid[brick.y][brick.x] = "#"

        for i in range(self.paddle.width):
            px = self.paddle.x + i
            if 0 <= px < self.width:
                grid[self.height - 2][px] = c("=", "white", attrs=["bold"])

        bx, by = int(self.ball.x), int(self.ball.y)
        if 0 <= bx < self.width and 0 <= by < self.height:
            grid[by][bx] = c("O", "red")

        for row in grid:
            print("".join(row))


if __name__ == "__main__":
    game = BrickBreaker()
    game.print_board()

