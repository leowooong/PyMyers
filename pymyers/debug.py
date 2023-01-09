import datetime
import pickle
import shutil
import turtle
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, List, Optional, Sequence, Union


@dataclass
class Coord:
    x: int
    y: int

    def __iter__(self):
        yield self.x
        yield self.y

    def __add__(self, other: "Coord"):
        return Coord(self.x + other.x, self.y + other.y)

    def __eq__(self, other: object):
        if isinstance(other, Coord):
            return self.x == other.x and self.y == other.y
        if isinstance(other, Sequence):
            return self.x == other[0] and self.y == other[1]
        else:
            return NotImplemented


class Debug:
    def __init__(
        self,
        a: Sequence,
        b: Sequence,
        eq: Optional[Callable[[Any, Any], bool]] = None,
        plot: bool = True,
        animation: bool = True,
        plot_size: int = 50,
        log_path: Union[str, Path] = "",
        max_logs: int = 5,
        max_n: int = 100,
        max_m: int = 80,
        start_coord: Coord = Coord(0, 0),
    ):
        self.a = a[:max_n] if max_n else a
        self.b = b[:max_m] if max_m else b
        self.eq = eq if eq else lambda a, b: a == b
        self.plot = plot
        self.animation = animation
        self.plot_size = plot_size
        self.start_coord = start_coord

        # logging
        now = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
        if log_path:
            self.log_path = Path(log_path) / "log-myers-{}".format(now)
            self.log_path.mkdir(parents=True, exist_ok=True)
            sub_log_paths = sorted(Path(log_path).iterdir(), reverse=True)
            for p in sub_log_paths[max_logs:]:
                shutil.rmtree(p)
        else:
            self.log_path = ""  # type: ignore [assignment]
        self._write(self.a, "a0.pickle")
        self._write(self.b, "b0.pickle")
        self._update_num = 1

        self.n = len(self.a)
        self.m = len(self.b)
        if self.plot:
            self._clear()
            turtle.tracer(False)
            self._draw_background()
            turtle.tracer(self.animation)

        self.forward_color = "red"

    def forward(self, start: Coord, end: Coord):
        if self.plot:
            self._pen3()
            self._draw_line(start, end)

    def backward(self, start: Coord, end: Coord):
        if self.plot:
            self._pen4()
            self._draw_line(start, end)

    def update(self, b):
        self._write(b, "b{}.pickle".format(self._update_num))
        self._update_num += 1
        self.b = self.b + b
        self.prev_m = self.m
        self.m = len(self.b)
        if self.plot:
            turtle.tracer(False)
            self._update_background()
            turtle.tracer(self.animation)

        if self.forward_color == "red":
            self.forward_color = "yellow"
        elif self.forward_color == "yellow":
            self.forward_color = "green"
        elif self.forward_color == "green":
            self.forward_color = "red"

    def done(self):
        if self.plot:
            turtle.done()

    @staticmethod
    def read(folder: Union[str, Path]) -> List[Sequence]:
        """read from myers log folder

        Args:
            folder (_type_): foler with head log-myers-

        Returns:
            List[Sequence]: list in order [a0, b0, b1, b2 ...]
        """
        tmp = []
        # reading a
        with open(Path(folder) / "a0.pickle", "rb") as f:
            tmp.append(pickle.load(f))
        # reading b
        i = 0
        while True:
            b_file = Path(folder) / "b{}.pickle".format(i)
            if b_file.exists():
                with open(b_file, "rb") as f:
                    tmp.append(pickle.load(f))
                i += 1
            else:
                break
        return tmp

    def _clear(self):
        if self.plot:
            turtle.clearscreen()

    def _write(self, data, filename):
        if self.log_path:
            with open(self.log_path / filename, "wb") as f:
                pickle.dump(data, f)

    def _update_background(self):
        # set cavas size coordinates loaction/direction
        width = self.n * self.plot_size + 2 * self.plot_size
        height = self.m * self.plot_size + 2 * self.plot_size
        turtle.setup(width, height, startx=-1, starty=0)  # window size and position
        turtle.screensize(canvwidth=width, canvheight=height, bg="light blue")  # canvas size
        # Note: setworldcoordinates will invoke screensize agian, commet the line in turtle.py may give better plot
        turtle.setworldcoordinates(-1, self.m + 1, self.n + 1, -1)

        # set pen
        self.pen = turtle.Pen()
        self.pen.hideturtle()
        self.pen.speed(0)

        # draw grid with _pen1
        self._pen1()
        for i in range(self.n + 1):
            self._draw_line([i, self.prev_m], [i, self.m])
        for i in range(self.prev_m + 1, self.m + 1):
            self._draw_line([0, i], [self.n, i])

        # draw texts with _pen1
        text_font_size = self.plot_size // 5 + 5
        coords_font_size = self.plot_size // 5

        for i, c in enumerate(self.b):
            self._draw_text([-0.1, i + 0.6], c, text_font_size)
        for i in range(self.m + 1):
            c = str(i + self.start_coord.y)
            self._draw_text([-0.1, i], c, coords_font_size)

        # draw diagonals with _pen2
        self._pen2()
        for i, ca in enumerate(self.a):
            for j, cb in enumerate(self.b):
                if j < self.prev_m:
                    continue
                if self.eq(ca, cb):
                    self._draw_line([i, j], [i + 1, j + 1])

    def _draw_background(self):
        turtle.title("myers debug")

        # set cavas size coordinates loaction/direction
        width = self.n * self.plot_size + 2 * self.plot_size
        height = self.m * self.plot_size + 2 * self.plot_size
        turtle.setup(width, height, startx=-1, starty=0)  # window size and position
        turtle.screensize(canvwidth=width, canvheight=height, bg="light blue")  # canvas size
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
            self._draw_text([i + 0.5, 0], c, text_font_size)
        for i in range(self.n + 1):
            c = str(i + self.start_coord.x)
            self._draw_text([i, 0], c, coords_font_size)

        for i, c in enumerate(self.b):
            self._draw_text([-0.1, i + 0.6], c, text_font_size)
        for i in range(self.m + 1):
            c = str(i + self.start_coord.y)
            self._draw_text([-0.1, i], c, coords_font_size)

        # draw diagonals with _pen2
        self._pen2()
        for i, ca in enumerate(self.a):
            for j, cb in enumerate(self.b):
                if self.eq(ca, cb):
                    self._draw_line([i, j], [i + 1, j + 1])

    def _draw_line(self, start: Coord, end: Coord):
        self.pen.penup()
        self.pen.goto(start)
        self.pen.pendown()
        self.pen.goto(end)
        turtle.update()

    def _draw_text(self, pos: Coord, text: str, font_size=16):
        if type(text) != str:
            return
        self.pen.penup()
        self.pen.goto(pos)
        self.pen.pendown()
        self.pen.write(text, align="center", font=("Arial", font_size, "normal"))
        turtle.update()

    def _pen1(self):
        self.pen.color("blue")
        self.pen.pensize(2)

    def _pen2(self):
        self.pen.color("green")
        self.pen.pensize(1)

    def _pen3(self):
        self.pen.color(self.forward_color)
        self.pen.pensize(3)

    def _pen4(self):
        self.pen.color("black")
        self.pen.pensize(4)
