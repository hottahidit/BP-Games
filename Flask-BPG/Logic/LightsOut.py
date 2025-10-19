import random

class LightsOutGame:
    def __init__(self, rows=5, cols=5):
        self.rows = rows
        self.cols = cols
        self.grid = [[1 for _ in range(cols)] for _ in range(rows)]  # All ON

    def reset_game(self, rows=None, cols=None):
        if rows:
            self.rows = rows
        if cols:
            self.cols = cols
        self.grid = [[1 for _ in range(self.cols)] for _ in range(self.rows)]

    def toggle(self, r, c):
        for dr, dc in [(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                self.grid[nr][nc] ^= 1  

    def get_state(self):
        return {
            "rows": self.rows,
            "cols": self.cols,
            "grid": self.grid,
            "win": all(cell == 0 for row in self.grid for cell in row)
        }

