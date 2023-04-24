from typing import List
from networkx import MultiDiGraph
from project.task6 import TaskCFG
from project.task8 import HellingsAlgoBuilder, make_query as hq
from project.task9 import MatrixAlgoBuilder, make_query as mq


class QueryBuilder:
    """
    Позволяет сделать запрос, используя алгоритм Хеллингса,
    или матричный алгоритм
    """

    def use_hellings():
        return HellingsAlgoBuilder()

    def use_matrix():
        return MatrixAlgoBuilder()

    @staticmethod
    def query(
        algo_name: str,
        graph: MultiDiGraph,
        starts: List,
        finals: List,
        grammar: TaskCFG,
        nonterminal: str,
    ):
        """
        Запрос, используя один из алгоритмов:
        algo_name = `hellings` | `matrix`
        """

        if algo_name == "hellings":
            return hq(graph, starts, finals, nonterminal)
        if algo_name == "matrix":
            return mq(graph, starts, finals, nonterminal)
        raise RuntimeError(f"{algo_name} <- uknown algorithm")
