from typing import List, Callable, Optional, SupportsIndex, Union, Tuple
from debug import Debug, Coords
from dataclasses import dataclass


class Myers:
    def __init__(self,
                 a: SupportsIndex,
                 b: SupportsIndex,
                 cmp: Callable = None,
                 plot: bool = False,
                 animation: bool = True,
                 plot_size: int = 50):
        self.a = a
        self.b = b
        self.cmp = cmp
        self.plot = plot
        self.animation = animation
        self.plot_size = plot_size
        self.debug = Debug(a, b, plot=plot, animation=animation, plot_size=plot_size)

    def shortest_edit(self):
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

    def backtrace(self, trace):
        x, y = len(self.a), len(self.b)
        for d in range(len(trace))[::-1]:
            v = trace[d]
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
                x, y = x - 1, y - 1
            self.debug.backward([x, y], [prev_x, prev_y])
            x, y = prev_x, prev_y

    def diff(self) -> List[Coords]:
        self.backtrace(self.shortest_edit())
        self.debug.done()
        return self.debug.trace


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
        self.leaves: List[TreeNode] = [None] * leave_size
        # self.trace: List[TreeNode] = []
        self.leaves[1] = root  # set virtual root

    def append(self, node: TreeNode):
        self.leaves[node.k] = node

    def expand_leaves(self, d: int):
        if len(self.leaves) < d * 2 + 1:
            self.leaves += [None] * 2 * d
            self.leaves[-d:] = self.leaves[-d-2*d: -2*d]


class MyersTree(Myers):
    def __init__(self,
                 a: SupportsIndex,
                 b: SupportsIndex,
                 cmp: Callable = None,
                 plot: bool = False,
                 animation: bool = True,
                 plot_size: int = 50):
        super().__init__(a, b, cmp, plot, animation, plot_size)

    def shortest_edit(self):
        n, m = len(self.a), len(self.b)
        maxd = n + m
        root = TreeNode(0, -1)  # virtual root
        tree = Tree(root, maxd * 2 + 1)
        for d in range(maxd + 1):  # maxd included
            for k in range(-d, d + 1, 2):
                # moving downward
                if k == -d or (k != d and tree.leaves[k - 1].x < tree.leaves[k + 1].x):
                    node = tree.leaves[k + 1].downward()
                    tree.append(node)
                    self.debug.forward(node.p.coords, node.coords)
                # moving rightward
                else:
                    node = tree.leaves[k - 1].rightward()
                    tree.append(node)
                    self.debug.forward(node.p.coords, node.coords)
                # moving diagonally
                while node.x < n and node.y < m and self.a[node.x] == self.b[node.y]:
                    node = tree.leaves[k].diagonal()
                    tree.append(node)
                    self.debug.forward(node.p.coords, node.coords)
                # end
                if node.x >= n and node.y >= m:
                    tree.end_node = node
                    return tree

    def backtrace(self, tree: Tree):
        end_node = tree.end_node
        while end_node != tree.root:
            self.debug.backward(end_node.coords, end_node.p.coords)
            end_node = end_node.p


class MyersRealTime(MyersTree):
    def __init__(self,
                 a: SupportsIndex,
                 b: SupportsIndex,
                 cmp: Callable = None,
                 plot: bool = False,
                 animation: bool = True,
                 plot_size: int = 50):
        super().__init__(a, b, cmp, plot, animation, plot_size)
        root = TreeNode(0, -1)  # virtual root
        self.tree = Tree(root, 3)
        self.current_d = 0

    def update(self, b) -> TreeNode:
        self.b = self.b + b
        self.debug = Debug(self.a, self.b, plot=self.plot, animation=self.animation, plot_size=self.plot_size)
        self.shortest_edit()
        # self.backtrace()
        return self.tree.end_node
        # self.tree.trim() # TODO

    def shortest_edit(self):
        n, m = len(self.a), len(self.b)
        maxd = n + m
        for d in range(self.current_d, maxd + 1):  # maxd included
            self.tree.expand_leaves(d)
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
                if node.y >= m:
                    self.tree.end_node = node
                    # in next update, d-loop start from d again, the dth tree.leaves will be replaced
                    # tree is thus kept tidy
                    self.current_d = d
                    return

    def backtrace(self):
        end_node = self.tree.end_node
        while end_node != self.tree.root:
            self.debug.backward(end_node.coords, end_node.p.coords)
            end_node = end_node.p


if __name__ == '__main__':
    a = 'abcdefgqbcdefg'
    b1 = 'abvcd'
    b2 = 'saqbckle'
    b3 = 'efglk'

    fn = MyersRealTime(a, '', plot=True, plot_size=30)
    fn.update(b1)
    fn.update(b2)
    fn.update(b3)
    fn.debug.done()
