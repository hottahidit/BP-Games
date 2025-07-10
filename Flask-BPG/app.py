from flask import Flask, request, jsonify, render_template, redirect, url_for
from termcolor import colored as c
import random

app = Flask(__name__)

rows = 10
cols = 10
num_mines = 10

grid = []
revealed = set()
first_click_done = False

def generate_grid(first_r, first_c):
    while True:
        temp_grid = [[0 for _ in range(cols)] for _ in range(rows)]
        mine_positions = set()

        forbidden = set((first_r + dr, first_c + dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if 0 <= first_r + dr < rows and 0 <= first_c + dc < cols)

        while len(mine_positions) < num_mines:
            r = random.randint(0, rows - 1)
            c = random.randint(0, cols - 1)
            if (r, c) not in mine_positions and (r, c) not in forbidden:
                mine_positions.add((r, c))

        for r, c in mine_positions:
            temp_grid[r][c] = -1

        for r, c in mine_positions:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols and temp_grid[nr][nc] != -1:
                        temp_grid[nr][nc] += 1

        if temp_grid[first_r][first_c] == 0:
            return temp_grid

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


@app.route('/reset')
def reset():
    global grid, revealed, first_click_done
    grid = []
    revealed = set()
    first_click_done = False
    return redirect('/')


@app.route('/reveal')
def reveal():
    global grid, revealed, first_click_done

    r = int(request.args.get('row'))
    c = int(request.args.get('col'))

    if not first_click_done:
        grid.clear()
        grid.extend(generate_grid(r, c))
        first_click_done = True

    if (r, c) in revealed:
        return jsonify([])

    if grid[r][c] == 0:
        cells = flood_fill(r, c)
    else:
        cells = {(r, c)}

    revealed.update(cells)

    data = []
    for row, col in cells:
        value = grid[row][col]
        cell = {'row': row, 'col': col, 'value': value if value != -1 else "-1"}
        data.append(cell)

    if grid[r][c] == -1:
        all_mines = [
            {'row': row, 'col': col, 'value': "-1"}
            for row in range(rows)
            for col in range(cols)
            if grid[row][col] == -1
        ]
        return jsonify(all_mines + data + [{'game_over': True}])

    return jsonify(data)

#TESTING
for row in grid:
    print(" ".join(str(cell) if cell != -1 else c("M", "red") for cell in row))

if __name__ == '__main__':
    app.run(debug=True)

