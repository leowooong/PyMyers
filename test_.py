from myers import MyersBase, MyersTree, MyersRealTime
import pytest

a1 = 'ABCABBA'
b1 = 'CBABAC'

a2 = '金庸小说人物风清扬是一个英俊、纯洁、忠诚、勇敢、聪明的青年。他是一个武林高手，也是一个自给自足的游侠。他忠于自己的信念，不畏权势，敢于挑战邪恶势力。他的智慧、勇气和善良吸引着众多追随者，成为武林中的一代宗师。'
b2 = '风清扬是一位金庸小说中的人物，他英俊、纯洁、忠诚和勇敢。他是一名武林高手，'
# '也是一名自给自足的游侠。他忠于自己的信念，不畏权势，敢于挑战邪恶势力。他的智慧、勇气和善良吸引了许多人追随他，成为武林中的一代宗师。'


# noplot
def test_myers_short_noplot():
    fn = MyersBase(a1, b1, plot=False)
    fn.diff()


def test_myerstree_short_noplot():
    fn = MyersTree(a1, b1, plot=False)
    fn.diff()


# plot
def test_myers_short_plot():
    fn = MyersBase(a1, b1, plot=True, plot_size=50)
    print(fn.diff())


def test_myers_long_plot():
    fn = MyersTree(a2, b2, plot=True, animation=False, plot_size=20)
    print(fn.diff())


def test_myerstree_short_plot():
    fn = MyersTree(a1, b1, plot=True, plot_size=50)
    fn.diff()


def test_myerstree_long_plot():
    fn = MyersTree(a2, b2, plot=True, animation=False, plot_size=20)
    print(fn.diff())

def test_myersrealtime_short_plot():
    fn = MyersRealTime(a1, b1, plot=True, plot_size=80)
    matches, deletes, inserts = fn.diff()
    print(matches, [(a1[c[0]], b1[c[1]]) for c in matches])
    print(deletes, [a1[c] for c in deletes])
    print(inserts, [b1[c] for c in inserts])

if __name__ == '__main__':
    # test_myers_short_noplot()
    # test_myers_short_plot()
    # test_myers_long_plot()
    # test_myerstree_short_plot()
    test_myerstree_long_plot()
    # test_myersrealtime_short_plot()
