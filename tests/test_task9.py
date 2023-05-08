from project.task6 import TaskCFG
from project.task9 import make_query, matrix_algo
from networkx import MultiDiGraph


def test_can_do_simple_hellings_algo():

    g = MultiDiGraph()

    g.add_node(0)
    g.add_node(1)
    g.add_node(2)
    g.add_node(3)

    g.add_edge(0, 1, label="a")
    g.add_edge(1, 2, label="b")
    g.add_edge(2, 3, label="c")

    grammar = "S -> A D\nD -> B C\nA -> a\nB -> b\nC -> c"
    cfg = TaskCFG.from_text(grammar)

    actual = matrix_algo(cfg, g)
    expected = {(0, "S", 3), (1, "D", 3), (0, "A", 1), (1, "B", 2), (2, "C", 3)}

    assert actual == expected


def test_can_do_simple_query():

    g = MultiDiGraph()

    g.add_node(0)
    g.add_node(1)
    g.add_node(2)
    g.add_node(3)
    g.add_node(4)
    g.add_node(5)
    g.add_node(6)

    g.add_edge(0, 1, label="x")
    g.add_edge(1, 2, label="p")
    g.add_edge(2, 3, label="x")
    g.add_edge(3, 4, label="p")
    g.add_edge(4, 5, label="x")
    g.add_edge(5, 6, label="p")

    grammar = "S -> X | X E\nX -> x\nE -> P S\nP -> p\n"
    cfg = TaskCFG.from_text(grammar).to_weak_normal_form()

    actual = make_query(g, [0], [3, 5, 6], cfg, "S")

    assert actual == {(0, 3), (0, 5)}
