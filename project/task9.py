from typing import Dict, List
from project.graph import create_graph_from_name
from project.task6 import TaskCFG
from networkx import MultiDiGraph
from scipy.sparse import dok_matrix
import numpy as np
import cfpq_data


def matrix_algo(grammar: TaskCFG, graph: MultiDiGraph):

    grammar = grammar.to_weak_normal_form()

    n = len(graph.nodes)

    mapper = {}
    unmapper = {}

    for i, v in enumerate(graph.nodes):
        mapper[v] = i
        unmapper[i] = v

    ms = {}
    for g in grammar.productions:
        m = dok_matrix((n, n), dtype=np.bool_)

        if len(g.body) == 0:
            for i in range(n):
                m[i, i] = True
        elif len(g.body) == 1:
            for u, v, e in graph.edges.data(data=True):
                if e["label"] == g.body[0].to_text():
                    m[mapper[u], mapper[v]] = True

        key = g.head.to_text()
        if key in ms:
            ms[key] += m
        else:
            ms[key] = m

    changed = True
    while changed:
        changed = False

        for g in grammar.productions:

            c = g.head.to_text()
            prev_ones = ms[c].count_nonzero()

            if len(g.body) == 2:

                left = g.body[0].to_text()
                right = g.body[1].to_text()

                ms[c] += ms[left] @ ms[right]

                if prev_ones != ms[c].count_nonzero():
                    changed = True

    answer = set()
    for key, val in ms.items():
        xs, ys = val.nonzero()
        for i, j in zip(xs, ys):
            answer.add((unmapper[i], key, unmapper[j]))

    return answer


class MatrixAlgoBuilder:
    """
    Собирает алгоритм с заданной грамматикой и графом
    """

    def __init__(self, grammar: TaskCFG = None, graph: MultiDiGraph = None) -> None:
        self._grammar = grammar
        self._graph = graph

    def load_graph_from_name(self, name: str):
        self._graph = create_graph_from_name(name)
        return self

    def load_graph_from_file(self, path: str):
        self._graph = cfpq_data.graph_from_csv(path)
        return self

    def load_grammar_from_text(self, text: str):
        self._grammar = TaskCFG.from_text(text)
        return self

    def load_grammar_from_file(self, path: str):
        self._grammar = TaskCFG.from_file(path)
        return self

    def build(self):
        """
        Возвращает функцию для запуска алгоритма, с заданными параметрами
        """
        if self._grammar is None:
            raise RuntimeError("grammar was not specified!")
        if self._graph is None:
            raise RuntimeError("graph is not specified!")

        return lambda: matrix_algo(self._grammar, self._graph)

    def run(self, starts: List, finals: List, nonterminal: str):

        tripples = self.build()()

        answer = set()
        for s, l, t in tripples:
            if s in starts and t in finals and l == nonterminal:
                answer.add((s, t))

        return answer


def make_query(
    graph: MultiDiGraph, starts: List, finals: List, grammar: TaskCFG, nonterminal: str
):
    """
    Функция решает задачу достижимости для заданного набора стартовых и финальных вершин, и заданного нетерминала.
    """

    tripples = matrix_algo(grammar, graph)

    answer = set()
    for s, l, t in tripples:
        if s in starts and t in finals and l == nonterminal:
            answer.add((s, t))

    return answer
