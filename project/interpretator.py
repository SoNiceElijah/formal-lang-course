from typing import List, TextIO
from antlr4 import *
import sys

from pyformlang.finite_automaton import Epsilon
import networkx

from project.antlr_parser.FormLangVisitor import FormLangVisitor
from project.antlr_parser.FormLangParser import FormLangParser
from project.antlr_parser.FormLangLexer import FormLangLexer

from project.graph import create_graph_from_name
from project.task2 import build_from_graph, build_from_regex
from project.task3 import intersect
from project.task4 import find_reachable_fa


class TypeBox:
    def __init__(self, type: str, subtype=None):
        self.__type = type
        self.__sub = subtype

    def pure_type(self):
        return self.__type

    def type(self):
        if self.__sub is not None:
            return self.__type + f"[{self.__sub.type()}]"
        return self.__type

    def subtype(self):
        return self.__sub

    def __str__(self):
        return self.type()

    def __repr__(self):
        return self.type()

    #############################################################

    def is_string(self):
        return self.__type == "string"

    def is_number(self):
        return self.__type == "number"

    def is_boolean(self):
        return self.__type == "boolean"

    def is_set(self):
        return self.__type == "set"

    def is_fa(self):
        return self.__type == "FA"

    def is_rsm(self):
        return self.__type == "RSM"

    def is_node(self):
        return self.__type == "node"

    def is_edge(self):
        return self.__type == "edge"

    def is_lambda(self):
        return self.__type == "lambda"

    def is_never(self):
        return self.__type == "never"

    def is_unit(self):
        return self.__type == "unit"

    def is_node_pair(self):
        return self.__type == "node_pair"

    def one_of(self, *types):
        for t in types:
            if self.is_same(t):
                return True
        return False

    def is_same(self, other):
        return isinstance(other, TypeBox) and (
            other.type() == "any"
            or self.__type == "any"
            or other.pure_type() == self.__type
        )

    def is_same_deep(self, other):
        return self.is_same(other) and (
            (self.__sub is None and other.subtype() is None)
            or self.__sub.is_same_deep(other.subtype())
        )

    #############################################################

    @staticmethod
    def string():
        return TypeBox("string")

    @staticmethod
    def number():
        return TypeBox("number")

    @staticmethod
    def boolean():
        return TypeBox("boolean")

    @staticmethod
    def set(sub):
        return TypeBox("set", sub)

    @staticmethod
    def fa():
        return TypeBox("fa")

    @staticmethod
    def rsm():
        return TypeBox("rsm")

    @staticmethod
    def lmb():
        return TypeBox("lambda")

    @staticmethod
    def node():
        return TypeBox("node")

    @staticmethod
    def edge():
        return TypeBox("edge")

    @staticmethod
    def node_pair():
        return TypeBox("node_pair")

    @staticmethod
    def never():
        return TypeBox("never")

    @staticmethod
    def unit():
        return TypeBox("unit")

    @staticmethod
    def any():
        return TypeBox("any")

    @staticmethod
    def any_set():
        return TypeBox.set(TypeBox.any())


class ValBox:
    def __init__(self, type: TypeBox, val) -> None:
        self.__type = type
        self.__val = val

    def val(self):
        return self.__val

    def type(self):
        return self.__type

    def __str__(self):
        return str(self.__val)

    def __repr__(self):
        return f"[ val : {repr(self.__val)}, type : {repr(self.__type)} ]"

    ##################################################################

    def is_string(self):
        return self.__type.is_string()

    def is_number(self):
        return self.__type.is_number()

    def is_boolean(self):
        return self.__type.is_boolean()

    def is_set(self):
        return self.__type.is_set()

    def is_fa(self):
        return self.__type.is_fa()

    def is_rsm(self):
        return self.__type.is_rsm()

    def is_node(self):
        return self.__type.is_node()

    def is_edge(self):
        return self.__type.is_edge()

    def is_never(self):
        return self.__type.is_never()

    def is_unit(self):
        return self.__type.is_unit()

    def is_lambda(self):
        return self.__type.is_lambda()

    def is_type(self, type: TypeBox):
        return self.__type.is_same(type)

    ##################################################################

    @staticmethod
    def string(val):
        return ValBox(TypeBox.string(), val)

    @staticmethod
    def number(val):
        return ValBox(TypeBox.number(), val)

    @staticmethod
    def boolean(val):
        return ValBox(TypeBox.boolean(), val)

    @staticmethod
    def set(sub, val):
        return ValBox(TypeBox.set(sub), val)

    @staticmethod
    def fa(val):
        return ValBox(TypeBox.fa(), val)

    @staticmethod
    def rsm(val):
        return ValBox(TypeBox.rsm(), val)

    @staticmethod
    def node(val):
        return ValBox(TypeBox.node(), val)

    @staticmethod
    def edge(val):
        return ValBox(TypeBox.edge(), val)

    @staticmethod
    def lmb(val):
        return ValBox(TypeBox.lmb(), val)

    @staticmethod
    def undefined():
        return ValBox(TypeBox.never(), None)

    @staticmethod
    def unit():
        return ValBox(TypeBox.unit(), "unit")


class Interpretator(FormLangVisitor):
    def __init__(self, stdout: TextIO = None):
        self.__context = {}
        self.__stdout = stdout if stdout is not None else sys.stdout
        self.__stop = False
        self.__error = None

    def __fail(self, msg):
        self.__stop = True
        self.__error = msg
        return ValBox.undefined()

    def __run(self, ctx, childrens, action):
        items = []
        for idx, tps in childrens:
            res = self.visit(ctx.getChild(idx))
            if self.__stop:
                return res
            if not (res.is_type(tps) or res.type().one_of(*tps)):
                return self.__fail(
                    f"{res.type().type()} != {', '.join(map(lambda x : x.type(), tps))}"
                )
            items.append(res)
        return action(items)

    def getContext(self):
        return self.__context

    #####################################################################

    def visitProg(self, ctx):
        for x in ctx.stmt():
            self.visit(x)
            if self.__stop:
                return self.__error
        return ValBox.unit()

    #####################################################################

    def visitStmt(self, ctx):
        return self.visit(ctx.getChild(0))

    #####################################################################

    def visitAssignment(self, ctx):
        var = ctx.getChild(0).getText()
        right = self.visit(ctx.getChild(2))
        if self.__stop:
            return right
        self.__context[var] = right
        return ValBox.unit()

    #####################################################################

    def printAction(self, args):
        self.__stdout.write(str(args[0]))
        return ValBox.unit()

    def visitPrint(self, ctx):
        return self.__run(
            ctx,
            [[1, [TypeBox.string(), TypeBox.number(), TypeBox.any_set()]]],
            self.printAction,
        )

    #####################################################################

    def visitNumber(self, ctx):
        return ValBox.number(int(ctx.getText()))

    #####################################################################

    def visitString(self, ctx):
        return ValBox.string(ctx.getText()[1:-1])

    #####################################################################

    def visitVar(self, ctx):
        name = ctx.getText()
        if name not in self.__context:
            return self.__fail(f"Can not find var with name: '{name}'!")
        return self.__context[name]

    #####################################################################

    def visitRange(self, ctx):
        start = int(ctx.getChild(1).getText())
        finish = int(ctx.getChild(3).getText())

        s = set()
        for x in range(start, finish):
            s.add(x)

        return ValBox.set(TypeBox.number(), s)

    #####################################################################

    def visitSet(self, ctx):
        item = self.visit(ctx.getChild(1))
        if self.__stop:
            return item
        if not item.type().one_of(TypeBox.string(), TypeBox.number()):
            return self.__fail(f"Can not make set of item '{item.type().type()}'")

        s = set()
        s.add(item.val())

        i = 0
        for x in range(3, ctx.getChildCount()):
            if i % 2 == 0:
                ch = self.visit(ctx.getChild(x))
                if self.__stop:
                    return ch
                if not item.type().is_same(ch.type()):
                    return self.__fail(
                        f"Can not add item of type '{ch.type().type()}' in set['{item.type().type()}']"
                    )

                s.add(ch.val())

            i += 1

        return ValBox.set(item.type(), s)

    #####################################################################

    def visitLambda(self, ctx):
        var = ctx.getChild(1).getText()
        body = ctx.getChild(3)

        def func(x, t):
            oldVar = None
            if var in self.__context:
                oldVar = self.__context[var]
            self.__context[var] = ValBox(t, x)
            res = self.visit(body)
            if oldVar is not None:
                self.__context[var] = oldVar
            else:
                self.__context.pop(var)
            return res

        return ValBox.lmb(func)

    #####################################################################

    def visitGetExpr(self, ctx):

        command = ctx.getChild(2).getText()

        def action(args):
            automaton = args[0].val()

            if command == "starts":
                return ValBox.set(TypeBox.node(), automaton.start_states)
            if command == "finals":
                return ValBox.set(TypeBox.node(), automaton.final_states)
            if command == "vertices":
                return ValBox.set(TypeBox.node(), automaton.states)
            if command == "edges":

                edges = []

                for f, e, t in automaton:
                    edge = (f, e, t)
                    edges.append(edge)

                return ValBox.set(TypeBox.edge(), edges)
            if command == "lables":
                return ValBox.set(TypeBox.string(), automaton.symbols)
            if command == "reachable":
                return ValBox.set(TypeBox.node_pair(), find_reachable_fa(automaton))

        return self.__run(ctx, [[0, [TypeBox.fa()]]], action)

    def visitOpExpr(self, ctx):

        op = ctx.getChild(1).getText()

        if op in ["||>", "||:"]:

            def action(args):

                verts = args[0].val()
                automaton = args[1].val()

                for v in verts:
                    if op == "||>":
                        automaton.add_start_state(v)
                    if op == "||:":
                        automaton.add_final_state(v)

                return ValBox.fa(automaton)

            return self.__run(
                ctx, [[0, [TypeBox.any_set()]], [2, [TypeBox.fa()]]], action
            )

        if op in ["|>", "|:"]:

            def action(args):
                vert = args[0].val()
                automaton = args[1].val()

                if op == "|>":
                    automaton.add_start_state(vert)
                if op == "|:":
                    automaton.add_final_state(vert)

                return ValBox.fa(automaton)

            return self.__run(
                ctx,
                [[0, [TypeBox.string(), TypeBox.number()]], [2, [TypeBox.fa()]]],
                action,
            )

        if op in ["&", ".", "|"]:

            def action(args):

                left = args[0].val()
                right = args[1].val()

                if op == "&":
                    return ValBox.fa(intersect(left, right))
                if op == "|":
                    return ValBox.fa(left.union(right))
                if op == ".":
                    return ValBox.fa(left.concatenate(right))

            return self.__run(ctx, [[0, [TypeBox.fa()]], [2, [TypeBox.fa()]]], action)

        if op == "in":

            def action(args):

                v = args[0].val()
                s = args[1].val()

                return ValBox.boolean(v in s)

            return self.__run(
                ctx, [[0, TypeBox.any()], [2, [TypeBox.any_set()]]], action
            )

    def visitFuncExpr(self, ctx):

        func = ctx.getChild(1).getText()

        def action(args):
            s = args[0].val()
            f = args[1].val()

            if func == "map":
                r = set()
                for v in s:
                    res = f(v, args[0].type().subtype())
                    if self.__stop:
                        return res
                    r.add(res.val())
                return ValBox.set(res.type(), r)
            if func == "filter":
                r = set()
                for v in s:
                    res = f(v, args[0].type().subtype())
                    if self.__stop:
                        return res
                    if not res.is_boolean():
                        return self.__fail(
                            f"Filter function returned '{res.type().type()}', expected 'boolean'!"
                        )
                    if res.val():
                        r.add(v)
                return ValBox.set(args[0].type().subtype(), r)

        return self.__run(ctx, [[0, [TypeBox.any_set()]], [2, [TypeBox.lmb()]]], action)

    def visitAstExpr(self, ctx):
        def action(args):
            auto = args[0].val()
            for x in auto.start_states:
                for y in auto.final_states:
                    auto.add_transition(x, Epsilon(), y)

            return ValBox.fa(auto)

        return self.__run(ctx, [[0, [TypeBox.fa()]]], action)

    def visitAccessExpr(self, ctx):

        prop = ctx.getChild(2).getText()[1:-1]

        def action(args):

            obj = args[0].val()

            if prop == "str":
                return ValBox.string(str(obj))

            if args[0].is_edge():
                if prop == "from":
                    return ValBox.string(obj[0])
                if prop == "to":
                    return ValBox.string(obj[2])
                if prop == "label":
                    return ValBox.string(obj[1])

            if args[0].type().is_node_pair():
                if prop == "from":
                    return ValBox.string(obj[0])
                if prop == "to":
                    return ValBox.string(obj[1])

            if not (isinstance(obj, dict) and prop in obj) or (hasattr(obj, prop)):
                return self.__fail(
                    f"Can not get property '{prop}' from '{args[0].type().type()}'"
                )
            return ValBox.string(obj[prop])

        return self.__run(ctx, [[0, TypeBox.any()]], action)

    def visitLoadExpr(self, ctx):
        path = ctx.getChild(1).getText()[1:-1]
        tokens = path.split("://")

        if len(tokens) != 2:
            return self.__fail(f"Use load protocol, example: 'name://ws'")

        protocol, url = tokens
        if protocol == "name":
            return ValBox.fa(build_from_graph(create_graph_from_name(url), [], []))

        if protocol == "dot":
            return ValBox.fa(build_from_graph(networkx.nx_pydot.read_dot(url)))

        if protocol == "regex":
            return ValBox.fa(build_from_regex(url))

        return self.__fail(f"Uknown load protocol: '{protocol}'")

    def visitExpr(self, ctx):
        if ctx.getChildCount() == 1:
            return self.visit(ctx.getChild(0))

        if ctx.getChildCount() == 3:
            if ctx.getChild(0).getText() == "(":
                return self.visit(ctx.getChild(1))
            op = ctx.getChild(1).getText()
            if op == "get":
                return self.visitGetExpr(ctx)
            elif op in ["map", "filter"]:
                return self.visitFuncExpr(ctx)
            else:
                return self.visitOpExpr(ctx)

        if ctx.getChildCount() == 2:
            if ctx.getChild(0).getText() == "load":
                return self.visitLoadExpr(ctx)
            return self.visitAstExpr(ctx)

        if ctx.getChildCount() == 4:
            return self.visitAccessExpr(ctx)


def interpret(s: str, stream: TextIO = None):

    lexems = FormLangLexer(InputStream(s))
    parser = FormLangParser(CommonTokenStream(lexems))

    tree = parser.prog()
    visitor = Interpretator(stream)

    error = visitor.visit(tree)
    if isinstance(error, str):
        return error
    return None
