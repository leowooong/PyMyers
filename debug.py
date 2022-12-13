import turtle
from typing import List, Callable, SupportsIndex


class Debug:
    def __init__(self, a: SupportsIndex, b: SupportsIndex, size: int = 80, plot: bool = True):
        self.a = a
        self.b = b
        self.size = size
        self.plot = plot

        self.n = len(a)
        self.m = len(b)
        self.trace = []
        if self.plot:
            self.base_plot()

    def done(self):
        self.trace = self.trace[::-1]
        for i in self.trace:
            print('{} ==> {}'.format(*i))

        if self.plot:
            turtle.done()

    def forward(self, start, end):
        if self.plot:
            self.pen3()
            self.draw_line(start, end)

    def backward(self, start, end):
        self.trace.append([end, start])
        if self.plot:
            self.pen4()
            self.draw_line(start, end)

    def base_plot(self):
        turtle.title('myers debug')

        # set cavas size coordinates loaction/direction
        width = self.n*self.size + 2*self.size
        height = self.m*self.size + 2*self.size
        turtle.setup(width, height)   # window size
        turtle.screensize(canvwidth=width, canvheight=height, bg='light blue')  # canvas size
        # Note: setworldcoordinates will invoke screensize agian, commet the line in turtle.py may give better plot
        turtle.setworldcoordinates(-1, self.m + 1, self.n + 1, -1)

        # set pen
        turtle.tracer(False)  # set to True for animation
        self.pen = turtle.Pen()
        self.pen.hideturtle()
        self.pen.speed(0)

        # draw grid with pen1
        self.pen1()
        for i in range(self.n + 1):
            self.draw_line([i, 0], [i, self.m])
        for i in range(self.m + 1):
            self.draw_line([0, i], [self.n, i])

        # draw texts with pen1
        text_font_size = self.size // 5 + 5
        coords_font_size = self.size // 5
        for i, c in enumerate(self.a):
            self.draw_text([i+0.5, 0], c, text_font_size)
        for i in range(self.n + 1):
            self.draw_text([i, 0], str(i), coords_font_size)

        for i, c in enumerate(self.b):
            self.draw_text([-0.1, i+0.6], c, text_font_size)
        for i in range(self.m + 1):
            self.draw_text([-0.1, i], str(i), coords_font_size)

        # draw diagonals with pen2
        self.pen2()
        for i, ca in enumerate(self.a):
            for j, cb in enumerate(self.b):
                if ca == cb:
                    self.draw_line([i, j], [i+1, j+1])

    def draw_line(self, start, end):
        self.pen.penup()
        self.pen.goto(start)
        self.pen.pendown()
        self.pen.goto(end)
        turtle.update()

    def draw_text(self, pos, text, font_size=16):
        self.pen.penup()
        self.pen.goto(pos)
        self.pen.pendown()
        self.pen.write(text, align='center', font=("Arial", font_size, "normal"))
        turtle.update()

    def pen1(self):
        self.pen.color('blue')
        self.pen.pensize(2)

    def pen2(self):
        self.pen.color('green')
        self.pen.pensize(1)

    def pen3(self):
        self.pen.color('red')
        self.pen.pensize(3)

    def pen4(self):
        self.pen.color('black')
        self.pen.pensize(4)
