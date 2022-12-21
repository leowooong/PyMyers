from pymyers import MyersBase, MyersRealTime, MyersTree, Diff, Matches, Inserts, Deletes


def test_case1():
    a = "ABCABBA"
    b = "CBABAC"
    matches = [(2, 0), (3, 2), (4, 3), (6, 4)]
    deletes = [0, 1, 5]
    inserts = [1, 5]
    diff = Diff(matches, deletes, inserts)

    diff_base = MyersBase(a, b).diff()
    assert diff_base == diff
    diff_tree = MyersTree(a, b).diff()
    assert diff_tree == diff
    diff_rt = MyersRealTime(a, b).diff()
    assert diff_rt == diff


def test_case2():
    a = "ABCABBA"
    b = "ABCABBA"
    matches = [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)]
    deletes = []
    inserts = []
    diff = Diff(matches, deletes, inserts)

    diff_base = MyersBase(a, b).diff()
    assert diff_base == diff
    diff_tree = MyersTree(a, b).diff()
    assert diff_tree == diff
    diff_rt = MyersRealTime(a, b).diff()
    assert diff_rt == diff


def test_case3():
    a = "ABCABBA"
    b = ""
    matches = []
    deletes = [0, 1, 2, 3, 4, 5, 6]
    inserts = []
    diff = Diff(matches, deletes, inserts)

    diff_base = MyersBase(a, b).diff()
    assert diff_base == diff
    diff_tree = MyersTree(a, b).diff()
    assert diff_tree == diff
    diff_rt = MyersRealTime(a, b).diff()
    assert diff_rt == diff


def test_case4():
    a = ""
    b = "ABCABBA"
    matches = []
    deletes = []
    inserts = [0, 1, 2, 3, 4, 5, 6]
    diff = Diff(matches, deletes, inserts)

    diff_base = MyersBase(a, b).diff()
    assert diff_base == diff
    diff_tree = MyersTree(a, b).diff()
    assert diff_tree == diff
    diff_rt = MyersRealTime(a, b).diff()
    assert diff_rt == diff


def test_case5():
    a = "ABCABBA"
    b = "0123456789"
    matches = []
    deletes = [0, 1, 2, 3, 4, 5, 6]
    inserts = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    diff = Diff(matches, deletes, inserts)

    diff_base = MyersBase(a, b).diff()
    assert diff_base == diff
    diff_tree = MyersTree(a, b).diff()
    assert diff_tree == diff
    diff_rt = MyersRealTime(a, b).diff()
    assert diff_rt == diff


def test_case6():
    a = [0, 1, 2, 3, 4, 5, 6, 7]
    b = "032145"
    cmp = lambda a, b: a == int(b)
    matches = [(0, 0), (3, 1), (4, 4), (5, 5)]
    deletes = [1, 2, 6, 7]
    inserts = [2, 3]
    diff = Diff(matches, deletes, inserts)

    diff_base = MyersBase(a, b, cmp=cmp).diff()
    assert diff_base == diff
    diff_tree = MyersTree(a, b, cmp=cmp).diff()
    assert diff_tree == diff
    diff_rt = MyersRealTime(a, b, cmp=cmp).diff()
    assert diff_rt == diff


def test_case7():
    a = "0123456789"
    b0 = ""
    b1 = "0"
    b2 = "34"
    b3 = "687"
    b4 = "890"
    b = [b0, b1, b2, b3, b4]

    myers = MyersRealTime(a, b[0])
    for bi in b[1:]:
        print(myers.update(bi))


def test_case8():
    from pymyers import Debug
    log_folder = "tests/log-myers-2022-12-21-18:19:11"
    a, *b = Debug.read(log_folder)

    myers = MyersRealTime(a, b[0])
    for bi in b[1:]:
        print(myers.update(bi))


if __name__ == "__main__":
    test_case8()
