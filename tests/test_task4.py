from project.task4 import make_query
from networkx import MultiDiGraph


def test_simple_query():

    regex = "a b c | a b | a"

    g = MultiDiGraph()

    g.add_node(0)
    g.add_node(1)
    g.add_node(2)
    g.add_node(3)
    g.add_node(4)

    g.add_edge(0, 1, label="a")
    g.add_edge(1, 2, label="b")
    g.add_edge(2, 3, label="c")
    g.add_edge(0, 4, label="d")

    assert len(make_query(g, [0], [3], regex, each=False)) == 1
    assert len(make_query(g, [0], [2, 3], regex, each=False)) == 2
    assert len(make_query(g, [0], [1, 2, 3], regex, each=False)) == 3


def test_simple_query_with_vals():

    regex = "a b c | a b | a"

    g = MultiDiGraph()

    g.add_node(0)
    g.add_node(1)
    g.add_node(2)
    g.add_node(3)
    g.add_node(4)

    g.add_edge(0, 1, label="a")
    g.add_edge(1, 2, label="b")
    g.add_edge(2, 3, label="c")
    g.add_edge(0, 4, label="d")

    expected = set()

    expected.add(3)
    assert make_query(g, [0], [3], regex, each=False) == expected

    expected.add(2)
    assert make_query(g, [0], [2, 3], regex, each=False) == expected

    expected.add(1)
    assert make_query(g, [0], [1, 2, 3], regex, each=False) == expected


def test_simple_query_with_vals_each():

    regex = "a b c | a b | a | c"

    g = MultiDiGraph()

    g.add_node(0)
    g.add_node(1)
    g.add_node(2)
    g.add_node(3)
    g.add_node(4)

    g.add_edge(0, 1, label="a")
    g.add_edge(1, 2, label="b")
    g.add_edge(2, 3, label="c")
    g.add_edge(0, 4, label="d")

    assert make_query(g, [0], [1, 2, 3], regex, each=True) == [{1, 2, 3}]
    assert make_query(g, [0, 2], [1, 2, 3], regex, each=True) == [{1, 2, 3}, {2, 3}]
