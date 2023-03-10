from __future__ import annotations

import ast
import typing

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

CompOp: typing.TypeAlias = (
    ast.Eq
    | ast.NotEq
    | ast.Lt
    | ast.LtE
    | ast.Gt
    | ast.GtE
    | ast.Is
    | ast.IsNot
    | ast.In
    | ast.NotIn
)

CompExpr: typing.TypeAlias = tuple[Node[typing.Any], list[Node[type[ast.comprehension]]]]
DictComp: typing.TypeAlias = tuple[
    tuple[Node[typing.Any], ...], list[Node[type[ast.comprehension]]]
]

COMP_OPERATORS: dict[str, CompOp] = {
    "==": ast.Eq(),
    "!=": ast.NotEq(),
    "<": ast.Lt(),
    "<=": ast.LtE(),
    ">": ast.Gt(),
    ">=": ast.GtE(),
    "is": ast.Is(),
    "is not": ast.IsNot(),
    "in": ast.In(),
    "not in": ast.NotIn(),
}


def isnode(item: typing.Any) -> bool:
    return isinstance(item, Node)


@v_args(inline=True, meta=True)
class SrpTransformer(Transformer):
    def module(self, _: Meta, *items: Node[typing.Any]) -> Module:
        return Module(body=items, type_ignores=[])

    def expr_statement(self, meta: Meta, expr: Node[typing.Any]) -> Node[type[ast.Expr]]:
        return Expressions.Expr(meta=meta, value=expr)

    def list_comp(self, meta: Meta, comp: CompExpr) -> Node[type[ast.ListComp]]:
        return Comprehensions.ListComp(meta=meta, elt=comp[0], generators=comp[1])

    def gen_expr(self, meta: Meta, comp: CompExpr) -> Node[type[ast.GeneratorExp]]:
        return Comprehensions.GeneratorExp(meta=meta, elt=comp[0], generators=comp[1])

    def set_expr(self, meta: Meta, comp: CompExpr) -> Node[type[ast.SetComp]]:
        return Comprehensions.SetComp(meta=meta, elt=comp[0], generators=comp[1])

    def dict_expr(self, meta: Meta, comp: DictComp):
        return Comprehensions.DictComp(
            meta=meta, key=comp[0][0], value=comp[0][1], generators=comp[1]
        )

    def comp_expr(
        self,
        _: Meta,
        elts: Node[typing.Any],
        generators: list[Node[type[ast.comprehension]]],
    ) -> CompExpr:
        return elts, generators

    def comp_if(self, _: Meta, test: Node[typing.Any]) -> Node[typing.Any]:
        return test

    def comp_for(
        self,
        meta: Meta,
        target: Node[typing.Any],
        iterator: Node[typing.Any],
        ifs: Node[typing.Any],
    ) -> list[Node[type[ast.comprehension]]]:
        if ctx := target.data.get("ctx"):
            if not isinstance(ctx, ast.Store):
                target.data["ctx"] = ast.Store()

        if "elts" in target.ast._fields:
            for item in target.data["elts"]:
                if item.ast is ast.Name:
                    item.data["ctx"] = ast.Store()

                elif item.ast is ast.Attribute:
                    item.data["value"].data["ctx"] = ast.Store()
                    item.data["ctx"] = ast.Store()

        return [
            Comprehensions.Comphrehension(
                meta=meta,
                target=target,
                iter=iterator,
                ifs=[ifs] if ifs is not None else [],
                is_async=0,
            )
        ]

    def subscript(
        self,
        meta: Meta,
        target: Node[typing.Any],
        slice: Node[typing.Any],
        ctx: Context = ast.Load(),
    ) -> Node[type[ast.Subscript]]:
        return Subscripting.Subscript(meta=meta, value=target, slice=slice, ctx=ctx)

    def slice(self, meta: Meta, *items: Node[typing.Any]):
        lower, upper, step = items

        if lower is not None and step is None and upper is None:
            return lower

        return Subscripting.Slice(meta=meta, lower=lower, upper=upper, step=step)

    def assign_expr(
        self,
        meta: Meta,
        target: Node[type[ast.Name | ast.Attribute]],
        value: Node[typing.Any],
    ) -> Node[type[ast.NamedExpr]]:
        if ctx := target.data.get("ctx"):
            if not isinstance(ctx, ast.Store):
                target.data["ctx"] = ast.Store()

        return Expressions.NamedExpr(meta=meta, target=target, value=value)

    def if_expr(self, meta: Meta, *items: Node[typing.Any]) -> Node[type[ast.IfExp]]:
        return Expressions.IfExp(meta=meta, test=items[1], body=items[0], orelse=items[2])

    def sum_atom(self, _: Meta, atom: Node[type[ast.BinOp]]) -> Node[type[ast.BinOp]]:
        return atom

    def call_expr(
        self,
        meta: Meta,
        func: Node[type[ast.Name | ast.Attribute]],
        arguments: Node[typing.Any] | list[Node[typing.Any]],
    ) -> Node[type[ast.Call]]:
        keywords: list[Node[ast.keyword]] = []
        passed: list[Node[typing.Any]] = []

        if isinstance(arguments, list):
            for argument in arguments:
                if argument.ast is ast.keyword:
                    keywords.append(argument)

                else:
                    passed.append(argument)

        if not isinstance(arguments, list):
            if arguments is None:
                pass

            elif arguments.ast is not ast.keyword:
                passed = [arguments]

            elif arguments.ast is ast.keyword:
                keywords = [arguments]

        return Expressions.Call(meta=meta, func=func, args=passed, keywords=keywords)

    def call_kwargs(self, meta: Meta, items: Node[typing.Any]) -> Node[type[ast.keyword]]:
        return Expressions.Keyword(meta=meta, arg=None, value=items)

    def arguments(self, _: Meta, *items: Node[typing.Any]) -> list[Node[typing.Any]]:
        return list(items)

    def argument(self, _: Meta, item: Node[typing.Any]) -> Node[typing.Any]:
        return item

    def keyword(self, meta: Meta, *argument: Node[typing.Any]) -> Node[typing.Any]:
        return Expressions.Keyword(
            meta=meta, arg=argument[0].data["id"], value=argument[1]
        )

    def attr(
        self, meta: Meta, first: Node[type[ast.Name]], *items, ctx: Context = ast.Load()
    ) -> Node[type[ast.Attribute]]:
        listed = list(items)

        def parse(
            attr: Node[type[ast.Name] | type[ast.Attribute]],
        ) -> str | Node[type[ast.Attribute]]:
            if id := attr.data.get("id"):
                return id

            elif attribute := attr.data.get("attr"):
                return attribute

            raise ValueError("Unknown type.")

        attribute = Expressions.Attribute(
            meta=meta, value=first, attr=parse(listed.pop(0)), ctx=ctx
        )

        for other in listed:
            attribute = Expressions.Attribute(
                meta=meta, value=attribute, attr=parse(other), ctx=ctx
            )

        return attribute

    def comp_oper(
        self, meta: Meta, *items: Node[typing.Any] | CompOp
    ) -> Node[type[ast.Compare]]:
        listed = list(items)
        left = listed.pop(0)

        operators: list[CompOp] = []
        comparators: list[Node[typing.Any]] = []

        for potential in listed:
            if isinstance(potential, Node):
                comparators.append(potential)
                continue

            operators.append(potential)

        return Expressions.Compare(
            meta=meta, left=left, ops=operators, comparators=comparators
        )

    def comp_op(self, _: Meta, token: Token) -> CompOp:
        return COMP_OPERATORS[token.value]

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
            case "exp":
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
        self, meta: Meta, expr: Node[typing.Any], ctx: Context = ast.Load()
    ) -> Node[type[ast.Starred]]:
        return Variables.Starred(meta=meta, value=expr, ctx=ctx)

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

    def const_string(
        self, _: Meta, string: Node[type[ast.Constant]]
    ) -> Node[type[ast.Constant]]:
        return string

    def string(self, meta: Meta, token: Token) -> Node[type[ast.Constant]]:
        return Literals.Constant(value=token.value.replace('"', ""), meta=meta)
