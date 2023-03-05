from pyformlang.regular_expression import Regex
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton


def build_from_regex(re):
    return Regex(re).to_epsilon_nfa().minimize()


def build_from_graph(graph, start_states=None, final_states=None):

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
