import random

ROWS = 10
COLS = 10
MINES = 10

class Minesweeper:
    def __init__(self, rows=10, cols=10, mines=10):
        self.rows = rows
        self.cols = cols
        self.mines = mines

        self.mgrid = []
        self.mrevealed = set()
        self.mfirst_click_done = False

    def generate_grid(self, first_r, first_c):
        while True:
            temp_grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
            mine_positions = set()
            forbidden = set((first_r + dr, first_c + dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1)
                            if 0 <= first_r + dr < ROWS and 0 <= first_c + dc < COLS)
            while len(mine_positions) < MINES:
                r = random.randint(0, ROWS - 1)
                c = random.randint(0, COLS - 1)
                if (r, c) not in mine_positions and (r, c) not in forbidden:
                    mine_positions.add((r, c))
            for r, c in mine_positions:
                temp_grid[r][c] = -1
            for r, c in mine_positions:
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < ROWS and 0 <= nc < COLS and temp_grid[nr][nc] != -1:
                            temp_grid[nr][nc] += 1
            if temp_grid[first_r][first_c] == 0:
                return temp_grid

    def get_neighbours(self, r, c):
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < ROWS and 0 <= nc < COLS:
                    yield nr, nc

    def flood_fill(self, r, c):
        to_reveal = set()
        stack = [(r, c)]
        while stack:
            r, c = stack.pop()
            if (r, c) in to_reveal:
                continue
            to_reveal.add((r, c))
            if self.mgrid[r][c] == 0:
                for nr, nc in self.get_neighbours(r, c):
                    if (nr, nc) not in to_reveal and self.grid[nr][nc] != -1:
                        stack.append((nr, nc))
        return to_reveal

    def reveal_cell(self, r, c):
        if not self.first_click_done:
            self.mgrid = self.generate_grid(r, c)
            self.mfirst_click_done = True

        if (r, c) in self.mrevealed:
            return [], False

        if self.grid[r][c] == 0:
            cells = self.flood_fill(r, c)
        else:
            cells = {(r, c)}

        self.mrevealed.update(cells)
        result = []

        for row, col in cells:
            value = self.grid[row][col]
            result.append({'row': row, 'col': col, 'value': value if value != -1 else "-1"})

        if self.mgrid[r][c] == -1:
            all_mines = [
                {'row': row, 'col': col, 'value': "-1"}
                for row in range(ROWS)
                for col in range(COLS)
                if self.mgrid[row][col] == -1
            ]
            return all_mines + result, True
        return result, False

    def reset_game(self):
        self.mgrid = []
        self.mrevealed = set()
        self.mfirst_click_done = False

