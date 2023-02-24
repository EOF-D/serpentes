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

Containers: typing.TypeAlias = (
    Node[ast.List] | Node[type[ast.Tuple]] | Node[type[ast.Set]] | Node[type[ast.Dict]]
)


def isnode(item: typing.Any) -> bool:
    return isinstance(item, Node)


@v_args(inline=True, meta=True)
class SrpTransformer(Transformer):
    def parse_container(self, meta: Meta, items: Tree) -> Containers:
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

        return types[items.data](meta=meta, elts=elements, ctx=ast.Load())

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

        raise RuntimeError("Unknown type.")

    const_none = parse_literals
    const_number = parse_literals
    const_false = parse_literals
    const_true = parse_literals

    def const_string(self, _: Meta, string: Node[type[ast.Constant]]):
        return string

    def string(self, meta: Meta, token: Token) -> Node[type[ast.Constant]]:
        return Literals.Constant(value=token.value, meta=meta)
