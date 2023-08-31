from easy_pil import Canvas, Editor, Font
import imageio as io
from copy import copy


class Renderer:
    WIDTH, HEIGHT = 800, 300
    duck1 = Editor("assets/duck-rocket1.png").resize((124, 90))
    duck2 = Editor("assets/duck-rocket2.png").resize((124, 90))
    duckoff1 = Editor("assets/duck-rocketoff1.png").resize((124, 90))
    duckoff2 = Editor("assets/duck-rocketoff2.png").resize((124, 90))
    poppins = Font.poppins(size=30)

    def __init__(self):
        self.background = Editor(Canvas((self.WIDTH, self.HEIGHT), color="#000000"))

        self.frames = []

    def add_frame(self, player1, player2):
        frame = copy(self.background)
        frame.paste(
            self.duck1 if player1.thrusting else self.duckoff1,
            (player1.pos, self.HEIGHT - 250),
        )
        frame.paste(
            self.duck2 if player2.thrusting else self.duckoff2,
            (player2.pos, self.HEIGHT - 150),
        )

        # frame.text(
        #     (10, 260),
        #     f"Velocity 1: {round(player1.vel)} km/h   "
        #     + f"Velocity 2: {round(player2.vel)} km/h",
        #     font=self.poppins,
        #     color="white",
        # )
        self.frames.append(io.imread(frame.image_bytes))

    def render(self, path, fps=60):
        io.mimsave(path, self.frames, duration=(1000 * (1 / fps)), format="GIF")
