from project.task2 import build_from_regex
from project.task3 import intersect, make_query
from networkx import MultiDiGraph


def test_simple_instersect():
    a = build_from_regex("a b")
    b = build_from_regex("b c")

    expected = a.get_intersection(b)
    actual = intersect(a, b)

    assert expected.is_equivalent_to(actual)


def test_another_simple_instersect():
    a = build_from_regex("b*")
    b = build_from_regex("b | c")

    expected = a.get_intersection(b)
    actual = intersect(a, b)

    assert expected.is_equivalent_to(actual)


def test_another_2_simple_instersect():
    a = build_from_regex("a a a | b b | c | d*")
    b = build_from_regex("a b c | d*")

    expected = a.get_intersection(b)
    actual = intersect(a, b)

    assert expected.is_equivalent_to(actual)


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

    assert len(make_query(g, [0], [3], regex)) == 1
    assert len(make_query(g, [0], [2, 3], regex)) == 2
    assert len(make_query(g, [0], [1, 2, 3], regex)) == 3


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

    expected.add((0, 3))
    assert make_query(g, [0], [3], regex) == expected

    expected.add((0, 2))
    assert make_query(g, [0], [2, 3], regex) == expected

    expected.add((0, 1))
    assert make_query(g, [0], [1, 2, 3], regex) == expected
