from pyformlang.finite_automaton import EpsilonNFA
from scipy.sparse import dok_matrix, block_diag, identity, hstack
import numpy as np
from project.task2 import build_from_regex, build_from_graph
from typing import Union, List
from networkx import MultiDiGraph


def find_reachable(
    graph: MultiDiGraph, starts: List, re: str, *, each=True
) -> Union[set, List[set]]:
    """
    Определяет достижимые из `starts` вершины согласно регулярным ограничениям `re`
    В зависимости от `each` возвращает достижимость из каждой вершины отдельно,
    или одно множество достижимых вершин
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
            [mapper[x] for x in automatus.states],
        )

    res = []
    for st in [starts] if not each else [[s] for s in starts]:

        a = build_from_regex(re)
        b = build_from_graph(graph, st)

        m_a, ss_a, fs_a = convert(a)
        m_b, ss_b, fs_b = convert(b)

        n_a = len(fs_a)
        ss_b = [n_a + i for i in ss_b]

        e_ab = set(m_a.keys()).intersection(set(m_b.keys()))
        m_ab = {e: block_diag((m_a[e], m_b[e]), format="dok") for e in e_ab}

        n1_ab = len(fs_a)
        n2_ab = len(fs_a) + len(fs_b)

        reachable = hstack(
            [
                identity(n1_ab, dtype=np.bool_, format="dok"),
                dok_matrix((n1_ab, n2_ab - n1_ab), dtype=np.bool_),
            ],
            format="dok",
        )
        for x in ss_a:
            for y in ss_b:
                reachable[x, y] = np.bool_(True)

        current = reachable
        zeros = None
        while zeros is None or reachable.count_nonzero() != zeros:
            succ = hstack(
                [
                    identity(n1_ab, dtype=np.bool_, format="dok"),
                    dok_matrix((n1_ab, n2_ab - n1_ab), dtype=np.bool_),
                ],
                format="dok",
            )
            for m in m_ab.values():
                n = current @ m
                for i in range(n_a):
                    for j in range(n_a):
                        if n[i, j]:
                            for x in range(n_a, n2_ab):
                                succ[j, x] += n[i, x]

            zeros = reachable.count_nonzero()
            reachable += succ

            current = succ

        fs = set()
        for i in fs_a:
            for j in fs_b:
                if reachable[i, n_a + j]:
                    fs.add(list(b.states)[j])
        res.append(fs)

    return res[0] if not each else res


def make_query(
    graph: MultiDiGraph, starts: List, finals: List, re: str, *, each=True
) -> Union[set, List[set]]:
    """
    Определяет достижимые из `starts` вершины `finals` согласно регулярным ограничениям `re`
    В зависимости от `each` возвращает достижимость из каждой вершины отдельно,
    или одно множество достижимых вершин
    """

    reachable = find_reachable(graph, starts, re, each=each)
    reachable = [reachable] if not each else reachable

    res = []
    for x in reachable:
        res.append({r for r in x if r in finals})

    return res[0] if not each else res
