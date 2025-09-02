import random  
from termcolor import colored as c 

def generate_grid(rows, cols):
    grid = [[0 for _ in range(cols)] for _ in range(rows)]
    a = random.randint(0, 4)
    b = random.randint(0, 4)
    grid[a][b] = 1
    return grid

grid = generate_grid(5, 5)
for row in grid:
    print(" ".join(str(cell) if cell != 1 else c("1", "red") for cell in row))

