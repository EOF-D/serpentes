from __future__ import annotations

import ast
import typing
from functools import partial

__all__ = (
    "define",
    "Literals",
    "Variables",
    "Expressions",
    "Subscripting",
    "Comprehensions",
    "Controlflow",
    "Objects",
    "Module",
)

NodeT = typing.TypeVar("NodeT")


def define(node: NodeT) -> partial[Node[NodeT]]:
    return partial(Node, ast=node)


class Node(typing.Generic[NodeT]):
    ast: type[NodeT]
    data: dict[str, typing.Any]

    lineno: int
    end_lineno: int

    col_offset: int
    end_col_offset: int

    def __init__(self, **data: typing.Any) -> None:
        meta = data.pop("meta")
        self.lineno = meta.line
        self.end_lineno = meta.end_line

        self.col_offset = meta.column
        self.end_col_offset = meta.end_column

        self.data = data
        self.ast = data.pop("ast")

    def __repr__(self) -> str:
        return f"<Node={self.ast.__name__} id={id(self)}>"

    def build(self) -> NodeT:
        parsed: dict[str, ast.AST | int] = {}

        def recurse(value: Node[typing.Any] | list[Node[typing.Any]]) -> typing.Any:
            if isinstance(value, Node):
                return value.build()

            elif isinstance(value, list):  # pyright: ignore
                for index, node in enumerate(value):
                    value[index] = recurse(node)

                return value

            return value

        for name, value in self.data.items():
            parsed[name] = recurse(value)

        parsed.update(
            {
                "lineno": self.lineno,
                "end_lineno": self.end_lineno,
                "col_offset": self.col_offset,
                "end_col_offset": self.end_col_offset,
            }
        )

        return self.ast(**parsed)


class Literals:
    Constant = define(ast.Constant)
    List = define(ast.List)
    Tuple = define(ast.Tuple)
    Set = define(ast.Set)
    Dict = define(ast.Dict)


class Variables:
    Name = define(ast.Name)
    Starred = define(ast.Starred)


class Expressions:
    Expr = define(ast.Expr)

    UnaryOp = define(ast.UnaryOp)
    BinOp = define(ast.BinOp)
    Compare = define(ast.Compare)

    Call = define(ast.Call)
    Keyword = define(ast.keyword)

    IfExp = define(ast.IfExp)

    Attribute = define(ast.Attribute)
    NamedExpr = define(ast.NamedExpr)


class Subscripting:
    Subscript = define(ast.Subscript)
    Slice = define(ast.Slice)


class Comprehensions:
    ListComp = define(ast.ListComp)
    SetComp = define(ast.SetComp)
    GeneratorExp = define(ast.GeneratorExp)
    DictComp = define(ast.DictComp)
    Comphrehension = define(ast.comprehension)


class Statements:
    Assign = define(ast.Assign)
    AnnAssign = define(ast.AnnAssign)
    AugAssign = define(ast.AugAssign)

    Raise = define(ast.Raise)
    Assert = define(ast.Assert)
    Delete = define(ast.Delete)
    Pass = define(ast.Pass)

    Import = define(ast.Import)
    ImprotFrom = define(ast.ImportFrom)

    Alias = define(ast.alias)


class Controlflow:
    If = define(ast.If)
    For = define(ast.For)
    While = define(ast.While)

    Break = define(ast.Break)
    Continue = define(ast.Continue)

    Try = define(ast.Try)
    ExceptHandler = define(ast.ExceptHandler)

    With = define(ast.With)
    WithItem = define(ast.withitem)


class Objects:
    Functiondef = define(ast.FunctionDef)
    Lambda = define(ast.Lambda)

    Arguments = define(ast.arguments)
    Arg = define(ast.arg)

    Return = define(ast.Return)
    Yield = define(ast.Yield)
    YieldFrom = define(ast.YieldFrom)

    Global = define(ast.Global)
    Nonlocal = define(ast.Nonlocal)

    ClassDef = define(ast.ClassDef)

    AsyncFunctionDef = define(ast.AsyncFunctionDef)
    Await = define(ast.Await)

    AsyncFor = define(ast.AsyncFor)
    AsyncWith = define(ast.AsyncWith)


Module = define(ast.Module)
