from pyformlang.regular_expression import Regex
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton


def build_from_regex(re):
    """
    Функция строит минимального ДКА по заданному регулярному выражению `re` (`re` в строковом формате).
    """
    return Regex(re).to_epsilon_nfa().minimize()


def build_from_graph(graph, start_states=None, final_states=None):
    """
    Функция строит недетерминированный конечный автомат по графу
    в формате `MultiDiGraph`. Принимает массив стартовых `start_states` вершин
    и массив конечных `final_states` вершин
    """
    if start_states is None:
        start_states = graph.nodes

    if final_states is None:
        final_states = graph.nodes

    nfa = NondeterministicFiniteAutomaton()

    for a, b, w in graph.edges(data=True):
        nfa.add_transition(a, w["label"], b)

    for state in start_states:
        nfa.add_start_state(state)

    for state in final_states:
        nfa.add_final_state(state)

    return nfa
