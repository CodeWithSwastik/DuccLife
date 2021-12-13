from render import Renderer
from io import BytesIO
import random


class Player:
    def __init__(self, acc, fuel, max_vel, intelligence=30):
        self.pos = -25
        self.vel = 1.45
        self.acc = acc
        self.fuel = fuel

        self.MAX_VEL = max_vel
        self.PILOT_INTEL = intelligence  # 0-100

        self.thrusting = False

    def update(self):
        self.pos += round(self.vel)

        if self.thrusting and self.fuel > 0 and self.vel < self.MAX_VEL:
            self.vel += self.acc
            self.fuel -= 1

        if self.thrusting:
            if random.uniform(0, 100) > self.PILOT_INTEL + 10:
                self.thrusting = False
        else:
            if random.uniform(0, 100) < self.PILOT_INTEL + 10:
                self.thrusting = True

        self.thrusting = self.fuel > 0 and self.vel < self.MAX_VEL and self.thrusting


class Game:
    FINISH = 850

    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2

        self.renderer = Renderer()

        self.winner = None

        self.tick = 0

    def update(self):
        self.player1.update()
        self.player2.update()
        if self.tick % 2 == 0:
            self.renderer.add_frame(self.player1, self.player2)
        self.tick += 1

    def run(self):
        while self.player1.pos < self.FINISH and self.player2.pos < self.FINISH:
            self.update()

        if self.player1.pos >= self.FINISH and self.player2.pos >= self.FINISH:
            self.winner = None
        else:
            self.winner = "White" if self.player1.pos >= self.FINISH else "Yellow"

        [self.update() for _ in range(10)]

        b = BytesIO()
        self.renderer.render(b)
        b.seek(0)
        return b
