from antlr4 import *
import pydot

from project.antlr_parser.FormLangVisitor import FormLangVisitor
from project.antlr_parser.FormLangParser import FormLangParser
from project.antlr_parser.FormLangLexer import FormLangLexer


class DotFormLangVisitor(FormLangVisitor):
    def __init__(self):
        super().__init__()
        self.__graph = pydot.Dot("FormLangRes", graph_type="graph")
        self.__node_idx = 0

    def __getNewNode(self, label):
        idx = self.__node_idx
        self.__node_idx += 1
        name = f"a{idx}"
        n = pydot.Node(name, label=label)
        self.__graph.add_node(n)
        return name

    def __connect(self, a, b):
        self.__graph.add_edge(pydot.Edge(a, b))

    def __run(self, ctx, label, *childs):
        n = self.__getNewNode(label)
        for ch in childs:
            item = ctx.getChild(ch)
            x = self.visit(item)
            self.__connect(n, x)
        return n

    def result(self) -> pydot.Dot:
        return self.__graph

    def visitProg(self, ctx):
        n = self.__getNewNode("program")
        for e in ctx.stmt():
            x = self.visit(e)
            self.__connect(n, x)
        return n

    def visitStmt(self, ctx):
        return self.__run(ctx, "statement", 0)

    def visitAssignment(self, ctx):
        return self.__run(ctx, "assignment", 0, 2)

    def visitPrint(self, ctx):
        return self.__run(ctx, "show", 1)

    def visitNumber(self, ctx):
        return self.__getNewNode(f"val [number={ctx.getText()}]")

    def visitString(self, ctx):
        return self.__getNewNode(f"val [string={ctx.getText()}]")

    def visitSet(self, ctx):
        n = self.__getNewNode("val [set -> ]")
        i = 0
        for c in ctx.getChildren():
            if i % 2 == 1:
                x = self.visit(c)
                self.__connect(n, x)
            i += 1
        return n

    def visitTuple(self, ctx):
        n = self.__getNewNode("val [tuple -> ]")
        i = 0
        for c in ctx.getChildren():
            if i % 2 == 1:
                x = self.visit(c)
                self.__connect(n, x)
            i += 1
        return n

    def visitRange(self, ctx):
        return self.__getNewNode(f"val [range {ctx.getChild(1)} ... {ctx.getChild(3)}]")

    def visitVar(self, ctx):
        return self.__getNewNode(f"var [{ctx.getText()}]")

    def visitLambda(self, ctx):
        return self.__run(ctx, f"lambda \\{ctx.getChild(1).getText()}", 3)

    def visitExpr(self, ctx):
        if ctx.getChildCount() == 1:
            return self.__run(ctx, "expression", 0)
        if ctx.getChildCount() == 3:
            if ctx.getChild(0).getText() == "(":
                return self.visit(ctx.getChild(1))
            op = ctx.getChild(1).getText()
            if op == "get":
                return self.__run(
                    ctx, f"get expression [{ctx.getChild(2).getText()}]", 0
                )
            else:
                return self.__run(
                    ctx, f"bin expression [{ctx.getChild(1).getText()}]", 0, 2
                )
        if ctx.getChildCount() == 2:
            if ctx.getChild(0).getText() == "load":
                return self.__getNewNode(f"load [{ctx.getChild(1).getText()}]")
            if ctx.getChild(1).getText() == "*":
                return self.__run(ctx, "ast", 0)
        if ctx.getChildCount() == 4:
            return self.__getNewNode(f"Access [{ctx.getChild(2).getText()}]")


def containsString(s: str):
    """
    Проверяет, принадлежит ли строка заданной грамматике, или нет
    """

    lexems = FormLangLexer(InputStream(s))
    lexems.removeErrorListeners()

    parser = FormLangParser(CommonTokenStream(lexems))
    parser.removeErrorListeners()

    parser.prog()
    return parser.getNumberOfSyntaxErrors() == 0


def generateDot(s: str):
    """
    Генерирует DOT файл с описанием дерева разбора для данного входа
    """

    lexems = FormLangLexer(InputStream(s))
    parser = FormLangParser(CommonTokenStream(lexems))

    tree = parser.prog()

    visitor = DotFormLangVisitor()
    visitor.visit(tree)

    dot = visitor.result()

    return dot.to_string()
