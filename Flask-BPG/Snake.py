import random
import time

TICK_BASE = 0.12
GRID_W = 20
GRID_H = 20

class SnakeGame:
    """
    The Snake Game main functions
    """

    def __init__(self):
        self.sgrid_w = GRID_W
        self.sgrid_h = GRID_H
        self.reset()

    def reset(self):
        cx = self.sgrid_w // 2
        cy = self.sgrid_h // 2
        self.ssnake = [(cx, cy), (cx-1, cy), (cx-2, cy)]
        self.dir = (1, 0)
        self.next_dir = self.dir
        self.spawn_food()
        self.sscore = 0
        self.salive = True
        self.speed_multiplier = 0.97
        self.tick_delay = TICK_BASE
        self.last_tick = time.time()

    def spawn_food(self):
        empty = {(x,y) for x in range(self.sgrid_w) for y in range(self.sgrid_h)} - set(self.ssnake)
        self.sfood = random.choice(list(empty)) if empty else None

    def change_dir(self, dx, dy):
        if (dx == -self.dir[0] and dy == -self.dir[1]):
            return
        self.next_dir = (dx, dy)

    def tick(self):
        if not self.salive:
            return
        now = time.time()
        if now - self.last_tick < self.tick_delay:
            return
        self.last_tick = now

        self.dir = self.next_dir
        head = self.ssnake[0]
        new_head = ((head[0] + self.dir[0]) % self.sgrid_w, (head[1] + self.dir[1]) % self.sgrid_h)
        if new_head in self.ssnake:
            self.salive = False
            return
        self.ssnake.insert(0, new_head)
        if self.sfood and new_head == self.sfood:
            self.sscore += 1
            #self.speed_multiplier *= 0.5
            self.tick_delay = max(0.03, TICK_BASE * self.speed_multiplier)
            self.spawn_food()
        else:
            self.ssnake.pop()

    def serialize(self):
        return {
            'snake': self.ssnake,
            'food': self.sfood,
            'score': self.sscore,
            'alive': self.salive,
            'grid': (self.sgrid_w, self.sgrid_h)
        }

