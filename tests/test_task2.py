from project.task2 import build_from_graph, build_from_regex
from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    NondeterministicFiniteAutomaton,
)
from networkx import MultiDiGraph


def test_can_build_from_regex_1():
    x = build_from_regex("a|b")

    expected = DeterministicFiniteAutomaton()

    expected.add_transition(0, "a", 1)
    expected.add_transition(0, "b", 1)
    expected.add_start_state(0)
    expected.add_final_state(1)

    assert expected.is_equivalent_to(x)


def test_can_build_from_regex_2():
    x = build_from_regex("a*")

    expected = DeterministicFiniteAutomaton()

    expected.add_transition(0, "a", 0)
    expected.add_start_state(0)
    expected.add_final_state(0)

    assert expected.is_equivalent_to(x)


def test_can_build_from_regex_3():
    x = build_from_regex("a b c")

    expected = DeterministicFiniteAutomaton()

    expected.add_transition(0, "a", 1)
    expected.add_transition(1, "b", 2)
    expected.add_transition(2, "c", 3)
    expected.add_start_state(0)
    expected.add_final_state(3)

    assert expected.is_equivalent_to(x)


def test_can_build_from_graph_1():

    g = MultiDiGraph()

    g.add_node(0)
    g.add_node(1)
    g.add_node(2)
    g.add_node(3)

    g.add_edge(0, 1, label="a")
    g.add_edge(1, 2, label="b")
    g.add_edge(2, 3, label="c")

    x = build_from_graph(g, start_states=[0], final_states=[3])

    expected = NondeterministicFiniteAutomaton()

    expected.add_transition(0, "a", 1)
    expected.add_transition(1, "b", 2)
    expected.add_transition(2, "c", 3)
    expected.add_start_state(0)
    expected.add_final_state(3)

    assert expected.is_equivalent_to(x)
