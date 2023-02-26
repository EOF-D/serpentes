from __future__ import annotations

import ast
import typing
from itertools import islice

from lark import Token, Transformer, Tree, v_args
from lark.tree import Meta

from ..nodes import (
    Comprehensions,
    Controlflow,
    Expressions,
    Literals,
    Module,
    Node,
    Objects,
    Subscripting,
    Variables,
)

Context: typing.TypeAlias = ast.Load | ast.Store | ast.Del
Containers: typing.TypeAlias = (
    Node[type[ast.List]]
    | Node[type[ast.Tuple]]
    | Node[type[ast.Set]]
    | Node[type[ast.Dict]]
)

BitOp: typing.TypeAlias = ast.LShift | ast.RShift | ast.BitOr | ast.BitXor | ast.BitAnd
UnaryOp: typing.TypeAlias = ast.UAdd | ast.USub | ast.Invert | ast.Not
MulOp: typing.TypeAlias = ast.Mult | ast.Div | ast.Mod | ast.Pow | ast.MatMult


def isnode(item: typing.Any) -> bool:
    return isinstance(item, Node)


@v_args(inline=True, meta=True)
class SrpTransformer(Transformer):
    def module(self, _: Meta, *items: Node[typing.Any]) -> Module:
        return Module(body=items, type_ignores=[])

    def expr_statement(self, meta: Meta, expr: Node[typing.Any]) -> Node[type[ast.Expr]]:
        return Expressions.Expr(meta=meta, value=expr)

    def bool_oper(self, meta: Meta, *operation) -> Node[type[ast.BoolOp]]:
        op = None
        items = list(operation)

        for item in operation:
            if isinstance(item, (ast.Or, ast.And)):
                op = item

        if op is None:
            raise ValueError("Unknown bool operator.")

        items.pop(items.index(op))
        return Expressions.BoolOp(meta=meta, op=op, values=items)

    def bool_op(self, _: Meta, token: Token) -> ast.Or | ast.And:
        return ast.Or() if token.value == "or" else ast.And()

    def product(
        self,
        meta: Meta,
        *operation: tuple[Node[typing.Any], MulOp | ast.Add | ast.Sub, Node[typing.Any]],
    ) -> Node[type[ast.BinOp]]:
        return Expressions.BinOp(
            meta=meta, left=operation[0], op=operation[1], right=operation[2]
        )

    sum = product

    def add_op(self, _: Meta, token: Token) -> ast.Add | ast.Sub:
        return ast.Add() if token.value == "+" else ast.Sub()

    def mul_op(self, _: Meta, token: Token) -> MulOp:
        match token.value:
            case "*":
                return ast.Mult()
            case "/":
                return ast.Div()
            case "%":
                return ast.Mod()
            case "**":
                return ast.Pow()
            case "@":
                return ast.MatMult()

            case _:
                raise ValueError("Unknown mult operator.")

    def bit_expr(
        self, meta: Meta, *operation: tuple[Node[typing.Any], BitOp, Node[typing.Any]]
    ) -> Node[type[ast.BinOp]]:
        return Expressions.BinOp(
            meta=meta, left=operation[0], op=operation[1], right=operation[2]
        )

    def bit_op(self, _: Meta, token: Token) -> BitOp:
        match token.value:
            case "<<":
                return ast.LShift()
            case ">>":
                return ast.RShift()
            case "|":
                return ast.BitOr()
            case "^":
                return ast.BitXor()
            case "&":
                return ast.BitAnd()

            case _:
                raise ValueError("Unknown bit operator.")

    def unary_expr(
        self, meta: Meta, op: UnaryOp, oper: Node[typing.Any]
    ) -> Node[type[ast.UnaryOp]]:
        return Expressions.UnaryOp(meta=meta, op=op, operand=oper)

    def unary_operator(self, _: Meta, token: Token) -> UnaryOp:
        match token.value:
            case "[+":
                return ast.UAdd()
            case "[-":
                return ast.USub()
            case "[~":
                return ast.Invert()
            case "[not":
                return ast.Not()

            case _:
                raise ValueError("Unknown unary operator.")

    unary_add = unary_operator
    unary_neg = unary_operator
    unary_invert = unary_operator
    unary_not = unary_operator

    def star_expr(
        self, meta: Meta, *expr: Node[typing.Any], ctx: Context = ast.Load()
    ) -> Node[type[ast.Starred]]:
        return Variables.Starred(meta=meta, value=expr[1], ctx=ctx)

    def name(
        self, meta: Meta, token: Token, ctx: Context = ast.Load()
    ) -> Node[type[ast.Name]]:
        return Variables.Name(meta=meta, id=token.value, ctx=ctx)

    def variable(self, _: Meta, item: Node[type[ast.Name]]) -> Node[type[ast.Name]]:
        return item

    def parse_container(
        self, meta: Meta, items: Tree, ctx: Context = ast.Load()
    ) -> Containers:
        if items.data == "dict":
            keys: list[Node[typing.Any]] = []
            values: list[Node[typing.Any]] = []

            for pair in typing.cast(list, items.children):
                keys.append(pair[0])
                values.append(pair[1])

            return Literals.Dict(meta=meta, keys=keys, values=values)

        types = {"list": Literals.List, "tuple": Literals.Tuple, "set": Literals.Set}

        elements: list[Node] = []
        for element in items.scan_values(isnode):
            elements.append(element)

        node = types[items.data]
        kwargs = {"ctx": ctx} if not node is Literals.Set else {}

        return node(meta=meta, elts=elements, **kwargs)

    def key_value(self, _: Meta, key, value) -> tuple[Node[typing.Any], Node[typing.Any]]:
        return key, value

    def expression(self, _: Meta, item):
        return item

    list_literal = parse_container
    tuple_literal = parse_container
    set_literal = parse_container
    dict_literal = parse_container

    def parse_literals(
        self, meta: Meta, item: Token | Tree[Token]
    ) -> Node[type[ast.Constant]]:
        values: dict[str, bool | None] = {"true": True, "false": False}

        if isinstance(item, Token):
            return Literals.Constant(
                value=values.get(item.value),
                meta=meta,
            )

        elif isinstance(item, Tree):
            token: Token = typing.cast(Token, item.children[0])

            bases = {
                "python__HEX_NUMBER": 16,
                "python__BIN_NUMBER": 2,
                "python__OCT_NUMBER": 8,
                "python__DEC_NUMBER": 10,
            }

            value = int()

            if base := bases.get(token.type):
                value = int(token.value, base)

            elif token.type == "python__FLOAT_NUMBER":
                value = int(float(token.value))

            return Literals.Constant(value=value, meta=meta)

        raise ValueError("Unknown type.")

    const_none = parse_literals
    const_number = parse_literals
    const_false = parse_literals
    const_true = parse_literals

    def const_string(self, _: Meta, string: Node[type[ast.Constant]]):
        return string

    def string(self, meta: Meta, token: Token) -> Node[type[ast.Constant]]:
        return Literals.Constant(value=token.value, meta=meta)
