from typing import List, Callable, Optional, SupportsIndex, Union
from debug import Debug
from dataclasses import dataclass


class Myers:
    def __init__(self, a: SupportsIndex,
                 b: SupportsIndex,
                 cmp: Callable = None,
                 plot: bool = False,
                 plot_size: int = 50):
        self.a = a
        self.b = b
        self.cmp = cmp
        self.debug = Debug(a, b, size=plot_size, plot=plot)

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

    def diff(self):
        self.backtrace(self.shortest_edit())
        self.debug.done()


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

    rc: Optional['TreeNode'] = None  # downward child
    doc: Optional['TreeNode'] = None  # rightward child
    dic: Optional['TreeNode'] = None  # diagonal child
    p: Optional['TreeNode'] = None  # parent

    def downward(self) -> 'TreeNode':
        node = TreeNode(self.x, self.y + 1, p=self)
        self.doc = node
        return node

    def rightward(self) -> 'TreeNode':
        node = TreeNode(self.x + 1, self.y, p=self)
        self.rc = node
        return node

    def diagonal(self) -> 'TreeNode':
        node = TreeNode(self.x + 1, self.y + 1, p=self)
        self.dic = node
        return node


class Tree:
    def __init__(self, root: TreeNode, max_num_leaves: int):
        self.root: TreeNode = root
        self.end_node: TreeNode = root
        self.leaves: List[TreeNode] = [None] * max_num_leaves
        # self.trace: List[TreeNode] = []
        self.leaves[1] = root  # set virtual root

    def append(self, node: TreeNode):
        self.leaves[node.k] = node


class MyersTree(Myers):
    def __init__(self, a: SupportsIndex,
                 b: SupportsIndex,
                 cmp: Callable = None,
                 plot: bool = False,
                 plot_size: int = 50):
        super().__init__(a, b, cmp, plot, plot_size)

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


class RealTimeMyers:
    pass


if __name__ == '__main__':
    a = 'ABCABBA'
    b = 'CBABAC'
    m = MyersTree(a, b, plot=True, plot_size=50)
    m.diff()
