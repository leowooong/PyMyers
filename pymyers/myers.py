from collections import namedtuple
from dataclasses import dataclass
from typing import Any, Callable, List, Optional, Sequence

from pymyers.debug import Coord, Debug

Matches = List[Coord]  # list of (a_coord, b_coord)
Deletes = List[int]  # list of a_coord
Inserts = List[int]  # list of b_coord
Diff = namedtuple("Diff", ["matches", "deletes", "inserts"])


class MyersBase:
    def __init__(
        self,
        a: Sequence,
        b: Sequence,
        eq: Optional[Callable[[Any, Any], bool]] = None,
        plot: bool = False,
        animation: bool = False,
        plot_size: int = 50,
        log_path: str = "",
    ):
        """myerse base

        Args:
            a (Sequence): a reference str/list/...
            b (Sequence): str/list/... that is expected to be compared with a
            eq (Optional[Callable[[Any, Any], bool]]): eq fn which should resolve a==b. Defaults to None.
            plot (bool, optional): whether plot debug figure. Defaults to False.
            animation (bool, optional): draw debug figure slowly or instantly. Defaults to True.
            plot_size (int, optional): debug figure size. Defaults to 50.
            log_path (str, optional): log_path to save a, b. Defaults to '', no data will be saved.
        """
        self.a = a
        self.b = b
        self.eq = eq if eq else lambda a, b: a == b
        self.plot = plot
        self.animation = animation
        self.plot_size = plot_size
        self.log_path = log_path
        self.debug = Debug(a, b, eq=self.eq, plot=plot, animation=animation, plot_size=plot_size, log_path=log_path)

    def shortest_edit(self) -> List[List[int]]:  # type: ignore [return]
        n, m = len(self.a), len(self.b)
        maxd = n + m
        v = [0] * (maxd * 2 + 1)  # store x value indexed by k
        trace = []
        for d in range(maxd + 1):  # maxd included
            trace.append(v.copy())
            for k in range(-d, d + 1, 2):
                # moving downward
                if k == -d or (k != d and v[k - 1] < v[k + 1]):
                    x = v[k + 1]
                    self.debug.forward(Coord(x, x - k - 1), Coord(x, x - k))
                # moving rightward
                else:
                    x = v[k - 1] + 1
                    self.debug.forward(Coord(x - 1, x - k), Coord(x, x - k))
                y = x - k
                # moving diagonally
                while x < n and y < m and self.eq(self.a[x], self.b[y]):
                    x, y = x + 1, y + 1
                    self.debug.forward(Coord(x - 1, y - 1), Coord(x, y))
                v[k] = x
                # end
                if x >= n and y >= m:
                    return trace

    def backtrace(self, forward_trace: List[List[int]]) -> List[Coord]:
        x, y = len(self.a), len(self.b)
        backward_trace = []
        for d in range(len(forward_trace))[::-1]:
            v = forward_trace[d]
            k = x - y
            # moving downward
            if k == -d or (k != d and v[k - 1] < v[k + 1]):
                prev_k = k + 1
            # moving rightward
            else:
                prev_k = k - 1
            prev_x = v[prev_k]
            prev_y = prev_x - prev_k

            # moving diagonally
            while x > prev_x and y > prev_y:
                self.debug.backward(Coord(x, y), Coord(x - 1, y - 1))
                backward_trace.append(Coord(x, y))
                x, y = x - 1, y - 1
            self.debug.backward(Coord(x, y), Coord(prev_x, prev_y))
            backward_trace.append(Coord(x, y))
            x, y = prev_x, prev_y
        return [Coord(0, -1)] + backward_trace[::-1]  # add virtual root

    @staticmethod
    def resolve_trace(trace: List[Coord]) -> Diff:
        """resolve trace to 3 lists of int(a_coord/b_coord)

        Args:
            trace (List[Coord]): trace of a list of Coord, the return value of diff

        Returns:
            Diff: namedtuple('Diff', ['matches', 'deletes', 'inserts']), corresponding to indexes of (a, b), indexes of a, indexes of b respectively
        """
        matches: Matches = []
        deletes: Deletes = []
        inserts: Inserts = []
        for i, c in enumerate(trace[:-1]):
            if c.x + 1 == trace[i + 1].x and c.y + 1 == trace[i + 1].y:
                matches.append(c)
            elif c.x + 1 == trace[i + 1].x:
                deletes.append(c.x)
            else:
                inserts.append(c.y)
        if len(inserts) and inserts[0] == -1:
            inserts = inserts[1:]  # remove virtual root
        return Diff(matches, deletes, inserts)

    def diff(self) -> Diff:
        """calculate diff between a, b

        Returns:
            Diff: namedtuple('Diff', ['matches', 'deletes', 'inserts']), corresponding to indexes of (a, b), indexes of a, indexes of b respectively
        """
        forward_trace = self.shortest_edit()
        backward_trace = self.backtrace(forward_trace)
        self.debug.done()
        return self.resolve_trace(backward_trace)


@dataclass
class TreeNode:
    x: int
    y: int

    @property
    def k(self) -> int:
        return self.x - self.y

    @property
    def coord(self) -> Coord:
        return Coord(self.x, self.y)

    right_ch: Optional["TreeNode"] = None  # rightward child
    down_ch: Optional["TreeNode"] = None  # downward child
    diag_ch: Optional["TreeNode"] = None  # diagonal child
    p: Optional["TreeNode"] = None  # parent

    def downward(self) -> "TreeNode":
        if self.down_ch:
            return self.down_ch
        node = TreeNode(self.x, self.y + 1, p=self)
        self.down_ch = node
        return node

    def rightward(self) -> "TreeNode":
        if self.right_ch:
            return self.right_ch
        node = TreeNode(self.x + 1, self.y, p=self)
        self.right_ch = node
        return node

    def diagonal(self) -> "TreeNode":
        if self.diag_ch:
            return self.diag_ch
        node = TreeNode(self.x + 1, self.y + 1, p=self)
        self.diag_ch = node
        return node

    def diagonal_with(self, other: "TreeNode") -> bool:
        return self.coord == other.coord + Coord(1, 1) or self.coord + Coord(1, 1) == other.coord

    def __gt__(self, other: "TreeNode") -> bool:
        return self.x + self.y > other.x + other.y

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TreeNode):
            return NotImplemented
        return self.coord == other.coord


class Tree:
    def __init__(self, leave_size: int = 3):
        self.root: TreeNode = TreeNode(0, -1)  # virtual root
        self.end_node: TreeNode = self.root
        self.farest_node: TreeNode = self.root

        self._leaves: List[Optional[TreeNode]] = [None] * leave_size
        self._leaves[1] = self.root  # set virtual root
        self.commit()

        self._trace: List[TreeNode] = [self.root]
        self._latest_trace: List[TreeNode] = []
        self._tmp_trace: List[TreeNode] = []

    @property
    def leaves(self):
        return self._leaves

    @property
    def trace(self) -> List[Coord]:
        return [n.coord for n in self._trace]

    @property
    def latest_trace(self) -> List[Coord]:
        return [n.coord for n in self._latest_trace]

    def add(self, node: TreeNode) -> None:
        self._leaves[node.k] = node
        self.farest_node = max(self.farest_node, node)

    def expand(self, d: int) -> None:
        if len(self._leaves) < d * 2 + 1:
            self._leaves += [None] * 2 * d
            self._leaves[-d:] = self._leaves[-d - 2 * d : -2 * d]

    def on_trace(self, node: TreeNode) -> bool:
        self._tmp_trace.append(node)
        try:
            index = self._trace.index(node)  # TODO: O(n) time time complexity
            self._trace = self._trace[:index] + self._tmp_trace[::-1]
            self._latest_trace = self._tmp_trace[::-1]
            self._tmp_trace = []
            return True
        except ValueError:
            return False

    def commit(self):
        self._leaves_backup = self._leaves[:]
        self._commited = True

    def checkout(self):
        self._leaves = self._leaves_backup[:]
        self.farest_node = self.root
        self._commited = False

    @property
    def commited(self):
        return self._commited

    def truncate(self, depth: int) -> Coord:
        node = self.end_node
        d = 0
        while node.p:
            if not node.diagonal_with(node.p):
                d += 1
            if d >= depth and node.diagonal_with(node.p):
                node = node.p
                break
            node = node.p  # type: ignore [assignment]

        if node == self.root:
            node = self.root.down_ch  # type: ignore [assignment]
        return node.coord


class MyersTree(MyersBase):
    def __init__(
        self,
        a: Sequence,
        b: Sequence,
        eq: Optional[Callable[[Any, Any], bool]] = None,
        plot: bool = False,
        animation: bool = False,
        plot_size: int = 50,
        log_path: str = "",
    ):
        """myerse using tree data structure support, less memory consumption, better readerable

        Args:
            a (Sequence): a reference str/list/...
            b (Sequence): str/list/... that is expected to be compared with a
            eq (Optional[Callable[[Any, Any], bool]]): eq fn which should resolve a==b. Defaults to None.
            plot (bool, optional): whether plot debug figure. Defaults to False.
            animation (bool, optional): draw debug figure slowly or instantly. Defaults to True.
            plot_size (int, optional): debug figure size. Defaults to 50.
            log_path (str, optional): log_path to save a, b. Defaults to '', no data will be saved.
        """
        super().__init__(a, b, eq, plot, animation, plot_size, log_path)
        self.tree = Tree()

    def shortest_edit(self):
        n, m = len(self.a), len(self.b)
        maxd = n + m
        for d in range(maxd + 1):  # maxd included
            self.tree.expand(d)
            for k in range(-d, d + 1, 2):
                # moving downward
                if k == -d or (k != d and self.tree.leaves[k - 1].x < self.tree.leaves[k + 1].x):
                    node = self.tree.leaves[k + 1].downward()
                    self.tree.add(node)
                    self.debug.forward(node.p.coord, node.coord)
                # moving rightward
                else:
                    node = self.tree.leaves[k - 1].rightward()
                    self.tree.add(node)
                    self.debug.forward(node.p.coord, node.coord)
                # moving diagonally
                while node.x < n and node.y < m and self.eq(self.a[node.x], self.b[node.y]):
                    node = self.tree.leaves[k].diagonal()
                    self.tree.add(node)
                    self.debug.forward(node.p.coord, node.coord)
                # end
                if node.x >= n and node.y >= m:
                    self.tree.end_node = node
                    return

    def backtrace(self):
        end_node = self.tree.end_node
        while not self.tree.on_trace(end_node):  # tree.root is on trace
            self.debug.backward(end_node.coord, end_node.p.coord)
            end_node = end_node.p

    def diff(self) -> Diff:
        """calculate diff between a, b

        Returns:
            Diff: namedtuple('Diff', ['matches', 'deletes', 'inserts']), corresponding to indexes of (a, b), indexes of a, indexes of b respectively
        """
        self.shortest_edit()
        self.backtrace()
        self.debug.done()
        return self.resolve_trace(self.tree.trace)


class MyersRealTime(MyersTree):
    def __init__(
        self,
        a: Sequence,
        b: Sequence,
        eq: Optional[Callable[[Any, Any], bool]] = None,
        plot: bool = False,
        animation: bool = False,
        plot_size: int = 50,
        log_path: str = "",
        max_depth: int = 50,
        truncate_depth: Optional[int] = None,
    ):
        """myerse with realtime support

        Args:
            a (Sequence): a reference str/list/...
            b (Sequence): str/list/... that is expected to be compared with a, b can be empty.
            eq (Optional[Callable[[Any, Any], bool]]): eq fn which should resolve a==b. Defaults to None.
            plot (bool, optional): whether plot debug figure. Defaults to False.
            animation (bool, optional): draw debug figure slowly or instantly. Defaults to True.
            plot_size (int, optional): debug figure size. Defaults to 50.
            log_path (str, optional): log_path to save a, b. Defaults to '', no data will be saved.
            max_depth (int): max depth of trace
            truncate_depth (int): min depth backtraced from end_node after trace exceeds max_depth,
                                  coords not backtraced will be deleted,
                                  the bigger truncate_depth the more coords will be reserved,
                                  truncate_depth should not be bigger than max_depth,
                                  if unspecified, defaults to truncate_depth // 3.

        """
        super().__init__(a, b, eq, plot, animation, plot_size, log_path)
        self.current_d = 0
        self.break_d = 0
        self.start_coord = Coord(0, 0)

        self.max_depth = max_depth
        self.truncate_depth = truncate_depth if truncate_depth else max_depth // 3

    def update(self, b: Sequence) -> Diff:
        """add new b and get new diffs

        Args:
            b (Sequence): b to be appended to current b

        Returns:
            Diff: namedtuple('Diff', ['matches', 'deletes', 'inserts']), corresponding to indexes of (a, b), indexes of a, indexes of b respectively
        """
        self.truncate()
        if not len(b):
            return self.resolve_trace([])

        self.b = self.b + b  # type: ignore [operator]
        self.debug.update(b)
        self.tree.checkout()
        self.realtime_shortest_edit()
        self.backtrace()
        trace = [c + self.start_coord for c in self.tree.latest_trace]
        return self.resolve_trace(trace)

    def truncate(self):
        if self.current_d >= self.max_depth:  # self.break_d - self.current_d == -9:  # TODO: value?
            self.current_d = 0
            self.break_d = 0
            truncate_coord = self.tree.truncate(self.truncate_depth)
            self.a = self.a[truncate_coord.x :]
            self.b = self.b[truncate_coord.y :]
            self.start_coord += truncate_coord
            self.tree = Tree()
            self.debug = Debug(
                self.a,
                self.b,
                eq=self.eq,
                plot=self.plot,
                animation=self.animation,
                plot_size=self.plot_size,
                log_path=self.log_path,
                start_coord=self.start_coord,
            )

    def realtime_shortest_edit(self):
        n, m = len(self.a), len(self.b)
        maxd = n + m
        for d in range(self.current_d, maxd + 1):  # maxd included
            self.tree.expand(d)
            for k in range(-d, d + 1, 2):
                # moving downward
                if k == -d or (k != d and self.tree.leaves[k - 1].x < self.tree.leaves[k + 1].x):
                    node = self.tree.leaves[k + 1].downward()
                    self.tree.add(node)
                    self.debug.forward(node.p.coord, node.coord)
                # moving rightward
                else:
                    node = self.tree.leaves[k - 1].rightward()
                    self.tree.add(node)
                    self.debug.forward(node.p.coord, node.coord)
                # moving diagonally
                while node.x < n and node.y < m and self.eq(self.a[node.x], self.b[node.y]):
                    node = self.tree.leaves[k].diagonal()
                    self.tree.add(node)
                    self.debug.forward(node.p.coord, node.coord)
                # saving status
                if not self.tree.commited and node.y == m:
                    self.tree.commit()
                    self.current_d = d
            # end
            if self.tree.farest_node.y >= m:
                self.tree.end_node = self.tree.farest_node
                self.break_d = d
                break
