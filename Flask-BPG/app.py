from flask import Flask, request, jsonify, render_template
from termcolor import colored as c
import random

app = Flask(__name__)

#if input("Do you want a custom grid?(y/n) ") == "y" or "Y":
rows = 10 #int(input("How many rows? "))
cols = 10 #int(input("How many coloumns? "))
num_mines = 10 #int(input("How many mines? "))
#else:
    #rows = 10
    #cols = 10
    #num_mines = 10

grid = []
revealed = set()

# Create game board with mines and numbers
def generate_grid():
    grid = [[0 for _ in range(cols)] for _ in range(rows)]
    
    mine_pos = set()
    while len(mine_pos) < num_mines:
        r = random.randint(0, rows - 1)
        c = random.randint(0, cols - 1)
        if (r, c) not in mine_pos:
            mine_pos.add((r, c))
            grid[r][c] = -1

    for r, c in mine_pos:
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0: 
                    continue
                nr, nc = r + dr, c + dc
                if (0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != -1):
                    grid[nr][nc] += 1
           
    return grid

def get_neighbours(r, c):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                yield nr, nc

def flood_fill(r, c):
    to_reveal = set()
    stack = [(r, c)]

    while stack:
        r, c = stack.pop()
        if (r, c) in to_reveal:
            continue
        to_reveal.add((r, c))
        if grid[r][c] == 0:
            for nr, nc in get_neighbours(r, c):
                if (nr, nc) not in to_reveal and grid[nr][nc] != -1:
                    stack.append((nr, nc))
    return to_reveal

@app.route('/')
def minesweeper():
    return render_template('minesweeper.html')

@app.route('/reveal')
def reveal():
    r = int(request.args.get('row'))
    c = int(request.args.get('col'))
    if grid[r][c] == 0:
        cells = flood_fill(r, c)
    else: 
        cells = {(r, c)}

    data = [{'row': row, 'col': col, 'value': grid[row][col] if grid[row][col] != -1 else '-1'} for row, col in cells]
    return jsonify(data)

#TESTING PURPOSES
grid = generate_grid()
for row in grid:
    print(" ".join(str(cell) if cell != -1 else c("M", "red") for cell in row))

if __name__ == '__main__':
    app.run(debug=True)

