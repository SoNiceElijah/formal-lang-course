from pyformlang.finite_automaton import EpsilonNFA
from scipy.sparse import dok_matrix, kron
import numpy as np
from collections import namedtuple
from project.task2 import build_from_regex, build_from_graph
from typing import Union, List
from networkx import MultiDiGraph

IntersectionResult = namedtuple(
    "IntersectionResult",
    ["matrix_dict", "start_states", "final_states", "states_restore"],
)


def intersect(
    a: EpsilonNFA, b: EpsilonNFA, *, shouldConvert: bool = True
) -> Union[EpsilonNFA, IntersectionResult]:
    """
    Строит пересечение 2х конечных автоматов `a` и `b`. Возвращает `EpsilonNFA` если
    `shouldConvert = true` и `IntersectionResult` иначе.
    """

    def convert(automatus: EpsilonNFA):
        mapper = {}
        n = 0
        for idx, state in enumerate(automatus.states):
            mapper[state] = idx
            n += 1
        edges_matrixes = {}
        for a, e, b in automatus:
            if e not in edges_matrixes:
                edges_matrixes[e] = dok_matrix((n, n), dtype=np.bool_)
            edges_matrixes[e][mapper[a], mapper[b]] = np.bool_(True)

        return (
            edges_matrixes,
            [mapper[x] for x in automatus.start_states],
            [mapper[x] for x in automatus.final_states],
        )

    def unconvert(mat, starts, finals):
        res = EpsilonNFA()

        for e, m in mat.items():
            res.add_transitions([(f, e, t) for (f, t) in zip(*m.nonzero())])

        for state in starts:
            res.add_start_state(state)
        for state in finals:
            res.add_final_state(state)

        return res

    m_a, ss_a, fs_a = convert(a)
    m_b, ss_b, fs_b = convert(b)

    e_ab = set(m_a.keys()).intersection(set(m_b.keys()))
    m_ab = {e: kron(m_a[e], m_b[e]) for e in e_ab}

    n = len(b.states)
    ss_ab = [i * n + j for i in ss_a for j in ss_b]
    fs_ab = [i * n + j for i in fs_a for j in fs_b]

    restore = lambda x: list(b.states)[x % n]
    return (
        unconvert(m_ab, ss_ab, fs_ab)
        if shouldConvert
        else IntersectionResult(m_ab, ss_ab, fs_ab, restore)
    )


def make_query(graph: MultiDiGraph, starts: List, finals: List, re: str) -> set:
    """
    По графу `graph` с заданными стартовыми `starts`
    и финальными `finals` вершинами и регулярному выражению `re`
    возвращает те пары вершин из заданных стартовых и финальных,
    которые связанны путём, формирующем слово из языка, задаваемого регулярным выражением
    """

    def find_closure(m):
        zeros = m.count_nonzero()
        while True:
            m += m @ m
            if zeros == m.count_nonzero():
                break
            zeros = m.count_nonzero()

        return m

    a = build_from_regex(re)
    b = build_from_graph(graph, starts, finals)

    mats, ss, fs, backtrack = intersect(a, b, shouldConvert=False)
    mat = find_closure(sum(mats.values()))

    answer = set()
    for x, y in zip(*mat.nonzero()):
        if x in ss and y in fs:
            answer.add((backtrack(x), backtrack(y)))

    return answer
