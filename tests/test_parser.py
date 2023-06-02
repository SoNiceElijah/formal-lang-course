from project.parser import containsString, generateDot
import pydot


def test_simple_vals():

    assert containsString("x is 3;")
    assert containsString('x is "string";')
    assert containsString("x is 3.14;")


def test_complicated_vals():

    assert containsString("x is {1, 2, 3, 4, 5};")
    assert containsString('x is {"a", "b", "c"};')
    assert containsString('x is ("a", 3);')
    assert containsString("x is {1 .. 5};")


def test_not_accepts_simple_vals():

    assert not containsString("x is 3.1.4;")
    assert not containsString("x is ();")


def test_accepts_lambdas():

    assert containsString("f is / x -> x /;")
    assert containsString("f is / x -> 3 |> x /;")
    assert containsString("f is / x -> x filter / y -> y in x / /;")


def test_not_accepts_lambdas():

    assert not containsString("f is (x) => x;")
    assert not containsString("f is (x) -> x;")
    assert not containsString("f is \\x -> x;")
    assert not containsString("f is [](x) { return x; };")
    assert not containsString("f is lambda x : x;")


def test_works_with_operators():

    assert containsString("f is { 3 } ||> x;")
    assert containsString("f is { 3 } ||: x;")
    assert containsString("f is 3 |> x;")
    assert containsString("f is 3 |: x;")

    assert containsString("f is x & y;")
    assert containsString("f is x . y;")
    assert containsString("f is x | y;")
    assert containsString("f is x smb y;")
    assert containsString("f is x in y;")


def test_not_works_with_operators():

    assert not containsString("f is 2 + 3;")
    assert not containsString("f is 2 - 3;")
    assert not containsString("f is 2 * 3;")
    assert not containsString("f is 2 / 3;")
    assert not containsString("f is 2 ^ 3;")


def test_can_load_n_show():

    assert containsString('f is load "graph"; show f;')


def test_can_use_get():

    assert containsString("x is g get starts;")
    assert containsString("x is g get finals;")
    assert containsString("x is g get reachable;")
    assert containsString("x is g get vertices;")
    assert containsString("x is g get edges;")
    assert containsString("x is g get lables;")


def test_can_not_use_get():

    assert not containsString("x is g get me some money;")
    assert not containsString("x is g get 3;")
    assert not containsString('x is g get "wefewf";')
    assert not containsString("x is g get;")


def test_can_map_n_filter():

    assert containsString("x is g map / e -> { e } /;")
    assert containsString("x is g filter / e -> e in (g get starts) /;")


def test_can_not_map_n_filter():

    assert not containsString("x is g map 5;")
    assert not containsString("x is g filter { 1 };")


def test_can_get_field():

    assert containsString('x is a["name"];')
    assert containsString("x is a[0];")


def test_can_not_get_field():

    assert not containsString("x is a[{ 2 }];")
    assert not containsString("x is a[g];")


expected_dot = """
graph FormLangRes {
a0 [label=program];
a1 [label=statement];
a2 [label=assignment];
a3 [label="var [x]"];
a2 -- a3;
a4 [label="bin expression [filter]"];
a5 [label="bin expression [map]"];
a6 [label=expression];
a7 [label="var [g]"];
a6 -- a7;
a5 -- a6;
a8 [label=lambda];
a9 [label="var [x]"];
a8 -- a9;
a10 [label=expression];
a11 [label="val [set -> ]"];
a12 [label=expression];
a13 [label="var [x]"];
a12 -- a13;
a11 -- a12;
a10 -- a11;
a8 -- a10;
a5 -- a8;
a4 -- a5;
a14 [label=lambda];
a15 [label="var [x]"];
a14 -- a15;
a16 [label="bin expression [in]"];
a17 [label=expression];
a18 [label="var [x]"];
a17 -- a18;
a16 -- a17;
a19 [label=expression];
a20 [label="var [a]"];
a19 -- a20;
a16 -- a19;
a14 -- a16;
a4 -- a14;
a2 -- a4;
a1 -- a2;
a0 -- a1;
}
"""


def test_can_gen_dot():

    assert expected_dot == "\n" + generateDot(
        "x is g map / x -> { x }/ filter / x -> x in a/;"
    )
