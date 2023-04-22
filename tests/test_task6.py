from project.task6 import TaskCFG
from pyformlang.cfg import Production, Variable, Terminal
import tempfile


def test_read_from_file():

    grammar = "S -> A B\nA -> a\nB -> b"

    with tempfile.NamedTemporaryFile(delete=True) as f:
        f.write(grammar.encode())
        f.flush()

        cfg = TaskCFG.from_file(f.name)

        assert cfg.contains("ab")
        assert not cfg.contains("a")
        assert not cfg.contains("fsf")


def test_convert_to_wcnf():

    grammar = "S -> A B C\nA -> a\nB -> b\nD -> D\nE -> e\n C -> c | c | c"
    cfg = TaskCFG.from_text(grammar)
    x = cfg.to_weak_normal_form()

    c = Production(Variable("C"), [Terminal("c")])
    b = Production(Variable("B"), [Terminal("b")])
    a = Production(Variable("A"), [Terminal("a")])
    s = Production(Variable("S"), [Variable("A"), Variable("C#CNF#1")])
    ccnf1 = Production(Variable("C#CNF#1"), [Variable("B"), Variable("C")])

    assert x.start_symbol == Variable("S")
    assert a in x.productions
    assert b in x.productions
    assert c in x.productions
    assert s in x.productions
    assert ccnf1 in x.productions

    assert len(x.productions) == 5
