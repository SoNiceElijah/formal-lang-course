import cfpq_data
import networkx


def create_graph_from_name(name):
    return cfpq_data.graph_from_csv(cfpq_data.download(name))


def get_graph_info_from_name(name):
    g = create_graph_from_name(name)

    ns = g.number_of_nodes()
    es = g.number_of_edges()

    ls = cfpq_data.get_sorted_labels(g)

    return ns, es, ls


def create_2_cycle_graph(n1, n2, labels):
    return cfpq_data.labeled_two_cycles_graph(n1, n2, labels=labels)


def save_graph(gr, path):
    networkx.drawing.nx_pydot.write_dot(gr, path)


def create_2_cycle_graph_and_save(n1, n2, labels, path="default.dot"):
    save_graph(create_2_cycle_graph(n1, n2, labels), path)
