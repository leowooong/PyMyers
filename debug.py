import turtle
from typing import List, Callable, SupportsIndex, Tuple

Coords = Tuple[int, int]


class Debug:
    def __init__(self,
                 a: SupportsIndex,
                 b: SupportsIndex,
                 plot: bool = True,
                 animation: bool = True,
                 plot_size: int = 50):
        self.a = a
        self.b = b
        self.plot = plot
        self.animation = animation
        self.plot_size = plot_size

        self.n = len(a)
        self.m = len(b)
        if self.plot:
            turtle.tracer(False)
            self._draw_background()
            turtle.tracer(self.animation)

    def forward(self, start: Coords, end: Coords):
        if self.plot:
            self._pen3()
            self._draw_line(start, end)

    def backward(self, start: Coords, end: Coords):
        if self.plot:
            self._pen4()
            self._draw_line(start, end)

    def update(self, b):
        self.b = self.b + b
        self.prev_m = self.m
        self.m = len(self.b)
        if self.plot:
            turtle.tracer(False)
            self._update_background()
            turtle.tracer(self.animation)

    def done(self):
        if self.plot:
            turtle.done()

    def _update_background(self):
        # set cavas size coordinates loaction/direction
        width = self.n*self.plot_size + 2*self.plot_size
        height = self.m*self.plot_size + 2*self.plot_size
        turtle.setup(width, height, startx=-1, starty=0)   # window size and position
        turtle.screensize(canvwidth=width, canvheight=height, bg='light blue')  # canvas size
        # Note: setworldcoordinates will invoke screensize agian, commet the line in turtle.py may give better plot
        turtle.setworldcoordinates(-1, self.m + 1, self.n + 1, -1)

        # set pen
        self.pen = turtle.Pen()
        self.pen.hideturtle()
        self.pen.speed(0)

        # draw grid with _pen1
        self._pen1()
        for i in range(self.n+1):
            self._draw_line([i, self.prev_m], [i, self.m])
        for i in range(self.prev_m+1, self.m+1):
            self._draw_line([0, i], [self.n, i])

        # draw texts with _pen1
        text_font_size = self.plot_size // 5 + 5
        coords_font_size = self.plot_size // 5

        for i, c in enumerate(self.b):
            self._draw_text([-0.1, i+0.6], c, text_font_size)
        for i in range(self.m + 1):
            self._draw_text([-0.1, i], str(i), coords_font_size)

        # draw diagonals with _pen2
        self._pen2()
        for i, ca in enumerate(self.a):
            for j, cb in enumerate(self.b):
                if j < self.prev_m:
                    continue
                if ca == cb:
                    self._draw_line([i, j], [i+1, j+1])

    def _draw_background(self):
        turtle.title('myers debug')

        # set cavas size coordinates loaction/direction
        width = self.n*self.plot_size + 2*self.plot_size
        height = self.m*self.plot_size + 2*self.plot_size
        turtle.setup(width, height, startx=-1, starty=0)   # window size and position
        turtle.screensize(canvwidth=width, canvheight=height, bg='light blue')  # canvas size
        # Note: setworldcoordinates will invoke screensize agian, commet the line in turtle.py may give better plot
        turtle.setworldcoordinates(-1, self.m + 1, self.n + 1, -1)

        # set pen
        self.pen = turtle.Pen()
        self.pen.hideturtle()
        self.pen.speed(0)

        # draw grid with _pen1
        self._pen1()
        for i in range(self.n + 1):
            self._draw_line([i, 0], [i, self.m])
        for i in range(self.m + 1):
            self._draw_line([0, i], [self.n, i])

        # draw texts with _pen1
        text_font_size = self.plot_size // 5 + 5
        coords_font_size = self.plot_size // 5
        for i, c in enumerate(self.a):
            self._draw_text([i+0.5, 0], c, text_font_size)
        for i in range(self.n + 1):
            self._draw_text([i, 0], str(i), coords_font_size)

        for i, c in enumerate(self.b):
            self._draw_text([-0.1, i+0.6], c, text_font_size)
        for i in range(self.m + 1):
            self._draw_text([-0.1, i], str(i), coords_font_size)

        # draw diagonals with _pen2
        self._pen2()
        for i, ca in enumerate(self.a):
            for j, cb in enumerate(self.b):
                if ca == cb:
                    self._draw_line([i, j], [i+1, j+1])

    def _draw_line(self, start: Coords, end: Coords):
        self.pen.penup()
        self.pen.goto(start)
        self.pen.pendown()
        self.pen.goto(end)
        turtle.update()

    def _draw_text(self, pos: Coords, text: str, font_size=16):
        self.pen.penup()
        self.pen.goto(pos)
        self.pen.pendown()
        self.pen.write(text, align='center', font=("Arial", font_size, "normal"))
        turtle.update()

    def _pen1(self):
        self.pen.color('blue')
        self.pen.pensize(2)

    def _pen2(self):
        self.pen.color('green')
        self.pen.pensize(1)

    def _pen3(self):
        self.pen.color('red')
        self.pen.pensize(3)

    def _pen4(self):
        self.pen.color('black')
        self.pen.pensize(4)
