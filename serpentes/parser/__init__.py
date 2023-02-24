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


@v_args(inline=True, meta=True)
class SrpTransformer(Transformer):
    TOKEN_TYPE: dict[str, str] = {}

    def parse_literals(self, meta: Meta, item: Token | Tree[Token]) -> Node[ast.Constant]:
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

    def string(self, meta: Meta, token: Token) -> Node[ast.Constant]:
        return Literals.Constant(value=token.value, meta=meta)
