from project.task7 import TaskECFG, TaskRFA
from pyformlang.regular_expression import Regex
from pyformlang.cfg import CFG
import tempfile


def test_can_simple_read_ecfg():

    ecfg = TaskECFG.from_text("S -> A b\n      A -> a")

    assert [x for x, _ in ecfg.productions.items()] == ["S", "A"]
    assert (
        ecfg.productions["S"]
        .to_epsilon_nfa()
        .is_equivalent_to(Regex("A b").to_epsilon_nfa())
    )
    assert (
        ecfg.productions["A"]
        .to_epsilon_nfa()
        .is_equivalent_to(Regex("a").to_epsilon_nfa())
    )


def test_can_read_one_line_ecfg():

    ecfg = TaskECFG.from_text("S -> a | b | c*")

    assert [x for x, _ in ecfg.productions.items()] == ["S"]
    assert (
        ecfg.productions["S"]
        .to_epsilon_nfa()
        .is_equivalent_to(Regex("a | b | c*").to_epsilon_nfa())
    )


def test_can_read_two_line_ecfg():

    ecfg = TaskECFG.from_text("S -> a | b | c*\nS -> d | e")

    assert [x for x, _ in ecfg.productions.items()] == ["S"]
    assert (
        ecfg.productions["S"]
        .to_epsilon_nfa()
        .is_equivalent_to(Regex("a | b | c* | d | e ").to_epsilon_nfa())
    )


def test_can_read_from_file_ecfg():

    grammar = "S -> a | b | c*"

    with tempfile.NamedTemporaryFile(delete=True) as f:
        f.write(grammar.encode())
        f.flush()

        ecfg = TaskECFG.from_file(f.name)

        assert [x for x, _ in ecfg.productions.items()] == ["S"]
        assert (
            ecfg.productions["S"]
            .to_epsilon_nfa()
            .is_equivalent_to(Regex("a | b | c*").to_epsilon_nfa())
        )


def test_can_read_from_cfg_ecfg():

    grammar = "S -> A B\nA -> a\nB -> b"
    ecfg = TaskECFG.from_cfg(CFG.from_text(grammar))

    assert set([x for x, _ in ecfg.productions.items()]) == set(["S", "A", "B"])
    assert (
        ecfg.productions["S"]
        .to_epsilon_nfa()
        .is_equivalent_to(Regex("A B").to_epsilon_nfa())
    )
    assert (
        ecfg.productions["A"]
        .to_epsilon_nfa()
        .is_equivalent_to(Regex("a").to_epsilon_nfa())
    )
    assert (
        ecfg.productions["B"]
        .to_epsilon_nfa()
        .is_equivalent_to(Regex("b").to_epsilon_nfa())
    )


def can_build_recursive_automaton_from_ecfg():

    ecfg = TaskECFG.from_text("S -> A | B | c*\nS -> d\nA -> a\nB -> b")

    rfa = TaskRFA.from_ecfg(ecfg)

    assert rfa.automatus["S"].is_equivalent_to(Regex("A | B | c* | d").to_epsilon_nfa())
    assert rfa.automatus["A"].is_equivalent_to(Regex("a").to_epsilon_nfa())
    assert rfa.automatus["B"].is_equivalent_to(Regex("b").to_epsilon_nfa())
