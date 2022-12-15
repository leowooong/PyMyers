from typing import List, Callable, Optional, SupportsIndex, Union, Tuple
from debug import Debug, Coords
from dataclasses import dataclass

Matches = List[Coords]  # list of (a_coord, b_coord)
Deletes = List[int]  # list of a_coord
Inserts = List[int]  # list of b_coord


class MyersBase:
    def __init__(self,
                 a: SupportsIndex,
                 b: SupportsIndex,
                 cmp: Callable = None,
                 plot: bool = False,
                 animation: bool = False,
                 plot_size: int = 50):
        """myerse base

        Args:
            a (SupportsIndex): a reference str/list/...
            b (SupportsIndex): str/list/... that is expected to be compared with a
            cmp (Callable, optional): cmp fn which should resolve a==b. Defaults to None.
            plot (bool, optional): whether plot debug figure. Defaults to False.
            animation (bool, optional): draw debug figure slowly or instantly. Defaults to True.
            plot_size (int, optional): debug figure size. Defaults to 50.
        """
        self.a = a
        self.b = b
        self.cmp = cmp
        self.debug = Debug(a, b, plot=plot, animation=animation, plot_size=plot_size)

    def shortest_edit(self) -> List[List[int]]:
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
                    self.debug.forward([x, x-k-1], [x, x-k])
                # moving rightward
                else:
                    x = v[k - 1] + 1
                    self.debug.forward([x-1, x-k], [x, x-k])
                y = x - k
                # moving diagonally
                while x < n and y < m and self.a[x] == self.b[y]:
                    x, y = x + 1, y + 1
                    self.debug.forward([x-1, y-1], [x, y])
                v[k] = x
                # end
                if x >= n and y >= m:
                    return trace

    def backtrace(self, forward_trace) -> List[Coords]:
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
                self.debug.backward([x, y], [x-1, y-1])
                forward_trace.append([x, y])
                x, y = x - 1, y - 1
            self.debug.backward([x, y], [prev_x, prev_y])
            backward_trace.append([x, y])
            x, y = prev_x, prev_y
        return [0, -1] + backward_trace[::-1]   # add virtual root

    @staticmethod
    def resolve_trace(trace: List[Coords]) -> Tuple[Matches, Deletes, Inserts]:
        """resolve trace to 3 lists of int(a_coord/b_coord)

        Args:
            trace (List[Coords]): trace of a list of Coords, the return value of diff

        Returns:
            Tuple[Matches, Deletes, Inserts]: matche indexes of (a, b), delete indexes of a, insert indexes of b
        """
        matches = []
        deletes = []
        inserts = []
        for i, c in enumerate(trace[:-1]):
            if c[0]+1 == trace[i+1][0] and c[1]+1 == trace[i + 1][1]:
                matches.append(c)
            elif c[0]+1 == trace[i+1][0]:
                deletes.append(c[0])
            else:
                inserts.append(c[1])
        return matches, deletes, inserts[1:]  # remove virtual root

    def diff(self) -> Tuple[Matches, Deletes, Inserts]:
        """calculate diff between a, b

        Returns:
            Tuple[Matches, Deletes, Inserts]: matche indexes of (a, b), delete indexes of a, insert indexes of b
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
    def k(self):
        return self.x - self.y

    @property
    def coords(self):
        return [self.x, self.y]

    right_ch: Optional['TreeNode'] = None  # rightward child
    down_ch: Optional['TreeNode'] = None  # downward child
    diag_ch: Optional['TreeNode'] = None  # diagonal child
    p: Optional['TreeNode'] = None  # parent

    def downward(self) -> 'TreeNode':
        node = TreeNode(self.x, self.y + 1, p=self)
        self.down_ch = node
        return node

    def rightward(self) -> 'TreeNode':
        node = TreeNode(self.x + 1, self.y, p=self)
        self.right_ch = node
        return node

    def diagonal(self) -> 'TreeNode':
        node = TreeNode(self.x + 1, self.y + 1, p=self)
        self.diag_ch = node
        return node


class Tree:
    def __init__(self, root: TreeNode, leave_size: int):
        self.root: TreeNode = root
        self.end_node: TreeNode = root

        self._leaves: List[TreeNode] = [None] * leave_size
        self._leaves[1] = root  # set virtual root

        self._trace: List[TreeNode] = [root]
        self._update_trace: List[TreeNode] = []
        self._tmp_trace: List[TreeNode] = []

    @property
    def leaves(self):
        return self._leaves

    @property
    def trace(self) -> List[Coords]:
        return [n.coords for n in self._trace]

    @property
    def update_trace(self) -> List[Coords]:
        return [n.coords for n in self._update_trace]

    def append(self, node: TreeNode) -> None:
        self._leaves[node.k] = node

    def expand(self, d: int) -> None:
        if len(self._leaves) < d * 2 + 1:
            self._leaves += [None] * 2 * d
            self._leaves[-d:] = self._leaves[-d-2*d: -2*d]

    def on_trace(self, node: TreeNode) -> bool:
        self._tmp_trace.append(node)
        try:
            index = self._trace.index(node)
            self._trace = self._trace[:index] + self._tmp_trace[::-1]
            self._update_trace = self._tmp_trace[::-1]
            self._tmp_trace = []
            return True
        except ValueError:
            return False


class MyersTree(MyersBase):
    def __init__(self,
                 a: SupportsIndex,
                 b: SupportsIndex,
                 cmp: Callable = None,
                 plot: bool = False,
                 animation: bool = False,
                 plot_size: int = 50):
        """myerse using tree data structure support, less memory consumption, better readerable

        Args:
            a (SupportsIndex): a reference str/list/...
            b (SupportsIndex): str/list/... that is expected to be compared with a
            cmp (Callable, optional): cmp fn which should resolve a==b. Defaults to None.
            plot (bool, optional): whether plot debug figure. Defaults to False.
            animation (bool, optional): draw debug figure slowly or instantly. Defaults to True.
            plot_size (int, optional): debug figure size. Defaults to 50.
        """
        super().__init__(a, b, cmp, plot, animation, plot_size)
        root = TreeNode(0, -1)  # virtual root
        self.tree = Tree(root, 3)

    def shortest_edit(self):
        n, m = len(self.a), len(self.b)
        maxd = n + m
        for d in range(maxd + 1):  # maxd included
            self.tree.expand(d)
            for k in range(-d, d + 1, 2):
                # moving downward
                if k == -d or (k != d and self.tree.leaves[k - 1].x < self.tree.leaves[k + 1].x):
                    node = self.tree.leaves[k + 1].downward()
                    self.tree.append(node)
                    self.debug.forward(node.p.coords, node.coords)
                # moving rightward
                else:
                    node = self.tree.leaves[k - 1].rightward()
                    self.tree.append(node)
                    self.debug.forward(node.p.coords, node.coords)
                # moving diagonally
                while node.x < n and node.y < m and self.a[node.x] == self.b[node.y]:
                    node = self.tree.leaves[k].diagonal()
                    self.tree.append(node)
                    self.debug.forward(node.p.coords, node.coords)
                # end
                if node.x >= n and node.y >= m:
                    self.tree.end_node = node
                    return self.tree

    def backtrace(self):
        end_node = self.tree.end_node
        while not self.tree.on_trace(end_node):  # tree.root is on trace
            self.debug.backward(end_node.coords, end_node.p.coords)
            end_node = end_node.p

    def diff(self) -> Tuple[Matches, Deletes, Inserts]:
        """calculate diff between a, b

        Returns:
            Tuple[Matches, Deletes, Inserts]: matche indexes of (a, b), delete indexes of a, insert indexes of b
        """
        self.shortest_edit()
        self.backtrace()
        self.debug.done()
        return self.resolve_trace(self.tree.trace)


class MyersRealTime(MyersTree):
    def __init__(self,
                 a: SupportsIndex,
                 b: SupportsIndex,
                 cmp: Callable = None,
                 plot: bool = False,
                 animation: bool = False,
                 plot_size: int = 50):
        """myerse with realtime support

        Args:
            a (SupportsIndex): a reference str/list/...
            b (SupportsIndex): str/list/... that is expected to be compared with a, b can be empty.
            cmp (Callable, optional): cmp fn which should resolve a==b. Defaults to None.
            plot (bool, optional): whether plot debug figure. Defaults to False.
            animation (bool, optional): draw debug figure slowly or instantly. Defaults to True.
            plot_size (int, optional): debug figure size. Defaults to 50.
        """
        super().__init__(a, b, cmp, plot, animation, plot_size)
        self.current_d = 0

    def update(self, b: SupportsIndex) -> Tuple[Matches, Deletes, Inserts]:
        """append new b and get new diffs

        Args:
            b (SupportsIndex): b to be appended to current b

        Returns:
            Tuple[Matches, Deletes, Inserts]: matche indexes of (a, b), delete indexes of a, insert indexes of b
        """
        self.b = self.b + b
        self.debug.update(b)
        self.realtime_shortest_edit()
        self.backtrace()
        return self.resolve_trace(self.tree.update_trace)
        # self.tree.trim() # TODO

    def realtime_shortest_edit(self):
        n, m = len(self.a), len(self.b)
        maxd = n + m
        for d in range(self.current_d, maxd + 1):  # maxd included
            self.tree.expand(d)
            for k in range(-d, d + 1, 2):
                # moving downward
                if k == -d or (k != d and self.tree.leaves[k - 1].x < self.tree.leaves[k + 1].x):
                    node = self.tree.leaves[k + 1].downward()
                    self.tree.append(node)
                    self.debug.forward(node.p.coords, node.coords)
                # moving rightward
                else:
                    node = self.tree.leaves[k - 1].rightward()
                    self.tree.append(node)
                    self.debug.forward(node.p.coords, node.coords)
                # moving diagonally
                while node.x < n and node.y < m and self.a[node.x] == self.b[node.y]:
                    node = self.tree.leaves[k].diagonal()
                    self.tree.append(node)
                    self.debug.forward(node.p.coords, node.coords)
                # end
                if node.y >= m:  # TODO: break too early, there may be a better path in dth-loop
                    self.tree.end_node = node
                    # in next update, d-loop start from d again, the dth tree.leaves will be updated
                    # tree is thus kept tidy
                    self.current_d = d
                    return


if __name__ == '__main__':
    a = 'abcdefgqbcdefglkjhiofawsjnfdlkdlifjgo'
    b1 = 'abvcd'
    b2 = 'efognngqbb'
    b3 = 'cdlgkn'
    b4 = 'lsjdfoasidfajmljsjdfl'

    fn = MyersRealTime(a, '', plot=True, animation=False, plot_size=50)
    print(fn.update(b1))
    print(fn.update(b2))
    print(fn.update(b3))
    print(fn.update(b4))
    fn.debug.done()
