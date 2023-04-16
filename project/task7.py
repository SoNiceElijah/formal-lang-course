from pyformlang.cfg import CFG, Variable, Terminal
from pyformlang.regular_expression import Regex
from pyformlang.finite_automaton import EpsilonNFA
from typing import Dict, Callable


class TaskECFG:
    """
    Представление для ECFG
    """

    @staticmethod
    def from_text(text: str):
        """
        Создает ECFG из текста
        """

        productions = {}

        lines = text.splitlines()
        lines = list(filter(lambda x: len(x) > 0, map(lambda x: x.strip(), lines)))

        for line in lines:
            tokens = line.split("->")

            name = tokens[0].strip()
            body = tokens[1].strip()

            if name in productions:
                productions[name] = productions[name].union(Regex(body))
            else:
                productions[name] = Regex(body)

        return TaskECFG(productions=productions)

    @staticmethod
    def from_file(path: str):
        """
        Создает ECFG из файла по пути path
        """
        with open(path) as f:
            return TaskECFG.from_text("\n".join(f.readlines()))

    @staticmethod
    def from_cfg(cfg: CFG):
        """
        Создает ECFG из CFG
        """
        return TaskECFG.from_text(cfg.to_text())

    def __init__(
        self, /, productions: Dict[str, Regex] = None, start_symbol: str = None
    ):
        self._productions = productions if productions is not None else {}
        self._start_symbol = "S" if start_symbol is None else start_symbol

    @property
    def productions(self):
        return self._productions


class TaskRFA:
    """
    Представление для recursive finite automaton
    """

    @staticmethod
    def from_ecfg(ecfg: TaskECFG):
        """
        Создает RFA из ECFG
        """
        a = {}
        for v, r in ecfg.productions.items():
            a[v] = r.to_epsilon_nfa()
        return TaskRFA(a)

    @staticmethod
    def from_text(text: str):
        """
        Создает RFA из текста
        """
        return TaskRFA.from_ecfg(TaskECFG.from_text(text))

    @staticmethod
    def from_file(path: str):
        """
        Создает RFA из файла
        """
        return TaskRFA.from_ecfg(TaskECFG.from_file(path))

    @staticmethod
    def from_procedure(func: Callable[[], TaskECFG]):
        """
        Создает RFA из ECFG, который возвращает переданная процедура
        """
        return TaskRFA.from_ecfg(func())

    def __init__(self, automatus: Dict[str, EpsilonNFA]):
        self._automatus = automatus

    def minimize(self):
        a = {}
        for name, auto in self._automatus.items():
            a[name] = auto.minimize()
        return TaskRFA(a)

    @property
    def automatus(self):
        return self._automatus
