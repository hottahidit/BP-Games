import random
from termcolor import colored as c

def generate_grid(rows, cols, num_mines):
    grid = [[0 for v in range(cols)] for t in range(rows)]

    mine_positions = set()
    while len(mine_positions) < num_mines:
        r = random.randint(0, rows - 1)
        c = random.randint(0, cols - 1)
        if (r, c) not in mine_positions:
            mine_positions.add((r, c))
            grid[r][c] = -1  

    for r, c in mine_positions:
        for deltar in (-1, 0, 1):
            for deltac in (-1, 0, 1):
                nr, nc = r + deltar, c + deltac
                if (0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != -1):
                    grid[nr][nc] += 1

    return grid

grid = generate_grid(18, 18, 40)

for row in grid:
    print(" ".join(str(cell) if cell != -1 else c("M", "red") for cell in row))
