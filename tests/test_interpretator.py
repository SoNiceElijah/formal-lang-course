import io
from project.interpretator import interpret


def run(text: str, nocomp=False):
    stream = io.StringIO()
    error = interpret(text, stream)
    assert error is None if not nocomp else isinstance(error, str)
    return stream.getvalue()


def test_simple():
    assert run("show 3;") == "3"
    assert run("show {1, 3};") == "{1, 3}"


def test_basic():
    run('x is load "name://wc"')
    assert run('x is load "name://wc"; show ({1, 2} ||> x) get starts;') == "{1, 2}"
    assert run('x is load "name://wc"; show ({1, 2} ||: x) get finals;') == "{1, 2}"

    q = run('x is load "name://wc"; show x get lables;')
    assert "a" in q
    assert "d" in q


def test_operators():

    run('a is load "regex://a b c"; b is load "regex://a"; x is a & b;')
    run('a is load "regex://a b c"; b is load "regex://a"; x is a | b;')
    run('a is load "regex://a b c"; b is load "regex://a"; x is a . b;')
    run('x is load "name://wc"; x is x*;')


def test_lambdas():

    assert (
        run("a is { 1 }; x is {1, 2, 3, 4, 5, 6} filter /x -> x in a/; show x;")
        == "{1}"
    )
    assert (
        run("a is { 1, 3 }; x is {1, 2, 3, 5} map /x -> x in a/; show x;")
        == "{False, True}"
    )


def test_ncomp():

    run('x is load "wc";', True)
    run('x is "abc"; show x get lables;', True)
    run('x is "abc"; y is 3; show x & y;', True)
