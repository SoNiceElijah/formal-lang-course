from pyformlang.cfg import CFG, Variable, Terminal


class TaskCFG(CFG):

    _weak_normal_from = None

    def to_weak_normal_form(self):
        """
        Преобразует грамматику к ОНФХ
        """

        if self._weak_normal_from is not None:
            return self._weak_normal_from

        x = self.eliminate_unit_productions().remove_useless_symbols()
        new_productions = x._get_productions_with_only_single_terminals()
        new_productions = x._decompose_productions(new_productions)

        cfg = TaskCFG(start_symbol=self._start_symbol, productions=set(new_productions))
        self._weak_normal_from = cfg
        return cfg

    @staticmethod
    def from_text(text: str, start_symbol: Variable = None):
        """
        Считывает грамматку из строки `text`. `start_symbol` - стартовый символ.
        По умолчанию S.
        """
        if start_symbol is None:

            start_symbol = Variable("S")
        cfg = CFG.from_text(text, start_symbol)
        return TaskCFG(start_symbol=cfg.start_symbol, productions=cfg.productions)

    @staticmethod
    def from_file(path: str, start_symbol: Variable = None):
        """
        Считывает грамматку из файла, по пути `path`. `start_symbol` - стартовый символ.
        По умолчанию S.
        """
        if start_symbol is None:
            start_symbol = Variable("S")
        with open(path) as file:
            return TaskCFG.from_text(
                "\n".join(file.readlines()), start_symbol=start_symbol
            )
