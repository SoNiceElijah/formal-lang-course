from typing import List
from pyformlang.cfg import Variable
from project.task6 import TaskCFG
from project.graph import create_graph_from_name
from networkx import MultiDiGraph
import cfpq_data


def hellings_algo(grammar: TaskCFG, graph: MultiDiGraph):
    """
    Выполняет алгоритм Хеллингса
    """

    grammar = grammar.to_weak_normal_form()
    edges = set()

    for production in grammar.productions:
        if len(production.body) == 0:  # eps
            for n in graph.nodes:
                edges.add((n, production.head.to_text(), n))
        if len(production.body) == 1:  # terminal
            for u, v, e in graph.edges.data(data=True):
                if e["label"] == production.body[0].to_text():
                    edges.add((u, production.head.to_text(), v))

    def find_non_terminal(l, r):
        for p in grammar.productions:
            if (
                len(p.body) == 2
                and p.body[0] == Variable(l)
                and p.body[1] == Variable(r)
            ):
                return p.head.to_text()
        return None

    queue = list(edges)
    while len(queue) > 0:
        s1, left, t1 = queue.pop(0)

        should_add = set()
        for s2, right, t2 in edges:
            if t1 == s2:
                l = find_non_terminal(left, right)
                if l is not None:
                    tripple = (s1, l, t2)
                    if tripple not in edges:
                        queue.append(tripple)
                        should_add.add(tripple)
            if t2 == s1:
                l = find_non_terminal(right, left)
                if l is not None:
                    tripple = (s2, l, t1)
                    if tripple not in edges:
                        queue.append(tripple)
                        should_add.add(tripple)

        for e in should_add:
            edges.add(e)

    return edges


class HellingsAlgoBuilder:
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

        return lambda: hellings_algo(self._grammar, self._graph)


def make_query(
    graph: MultiDiGraph, starts: List, finals: List, grammar: TaskCFG, nonterminal: str
):
    """
    Функция решает задачу достижимости для заданного набора стартовых и финальных вершин, и заданного нетерминала.
    """

    tripples = hellings_algo(grammar, graph)

    answer = set()
    for s, l, t in tripples:
        if s in starts and t in finals and l == nonterminal:
            answer.add((s, t))

    return answer
