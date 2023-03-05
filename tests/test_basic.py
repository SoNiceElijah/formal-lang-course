import project.graph as g
import tempfile
import pydot


def test_can_get_info_by_name_wc():
    info = g.get_graph_info_from_name("wc")
    assert info == (332, 269, ["d", "a"])


def test_can_get_info_by_name_ls():
    info = g.get_graph_info_from_name("ls")
    assert info == (1687, 1453, ["d", "a"])


def test_can_create_2_cycle_graph_and_save():
    with tempfile.NamedTemporaryFile(delete=True) as f:
        g.create_2_cycle_graph_and_save(2, 3, ["x", "y"], f.name)
        x = pydot.graph_from_dot_file(f.name)
        assert x is not None
