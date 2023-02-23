from __future__ import annotations

import ast
from functools import partial
from typing import Any, Generic, TypeVar

__all__ = (
    "Node",
    "Literals",
    "Variables",
    "Expressions",
    "Subscripting",
    "Comprehensions",
    "Controlflow",
    "Objects",
    "Module",
)

NodeT = TypeVar("NodeT")


class Node(Generic[NodeT]):
    ast: type[NodeT]
    data: dict[str, Any]

    lineno: int
    end_lineno: int

    col_offset: int
    end_col_offset: int

    def __init__(self, **data: Any) -> None:
        meta = data.pop("meta")
        self.lineno = meta.line
        self.end_lineno = meta.end_line

        self.col_offset = meta.column
        self.end_col_offset = meta.end_column

        self.data = data
        self.ast = data.pop("ast")

    def __class_getitem__(cls: type[Node[Any]], ast: str | NodeT) -> partial[Node[NodeT]]:
        if isinstance(ast, str):
            return cls  # pyright: ignore

        return partial(cls, ast=ast)

    def build(self) -> NodeT:
        parsed: dict[str, ast.AST | int] = {}

        def recurse(value: Node[Any] | list[Node[Any]]) -> Any:
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
    Constant = Node[ast.Constant]
    List = Node[ast.List]
    Tuple = Node[ast.Tuple]
    Set = Node[ast.Set]
    Dict = Node[ast.Dict]


class Variables:
    Name = Node[ast.Name]
    Starred = Node[ast.Starred]


class Expressions:
    Expr = Node[ast.Expr]

    UnaryOp = Node[ast.UnaryOp]
    BinOp = Node[ast.BinOp]
    Compare = Node[ast.Compare]

    Call = Node[ast.Call]
    Keyword = Node[ast.keyword]

    IfExp = Node[ast.IfExp]

    Attribute = Node[ast.Attribute]
    NamedExpr = Node[ast.NamedExpr]


class Subscripting:
    Subscript = Node[ast.Subscript]
    Slice = Node[ast.Slice]


class Comprehensions:
    ListComp = Node[ast.ListComp]
    SetComp = Node[ast.SetComp]
    GeneratorExp = Node[ast.GeneratorExp]
    DictComp = Node[ast.DictComp]
    Comphrehension = Node[ast.comprehension]


class Statements:
    Assign = Node[ast.Assign]
    AnnAssign = Node[ast.AnnAssign]
    AugAssign = Node[ast.AugAssign]

    Raise = Node[ast.Raise]
    Assert = Node[ast.Assert]
    Delete = Node[ast.Delete]
    Pass = Node[ast.Pass]

    Import = Node[ast.Import]
    ImprotFrom = Node[ast.ImportFrom]

    Alias = Node[ast.alias]


class Controlflow:
    If = Node[ast.If]
    For = Node[ast.For]
    While = Node[ast.While]

    Break = Node[ast.Break]
    Continue = Node[ast.Continue]

    Try = Node[ast.Try]
    ExceptHandler = Node[ast.ExceptHandler]

    With = Node[ast.With]
    WithItem = Node[ast.withitem]


class Objects:
    Functiondef = Node[ast.FunctionDef]
    Lambda = Node[ast.Lambda]

    Arguments = Node[ast.arguments]
    Arg = Node[ast.arg]

    Return = Node[ast.Return]
    Yield = Node[ast.Yield]
    YieldFrom = Node[ast.YieldFrom]

    Global = Node[ast.Global]
    Nonlocal = Node[ast.Nonlocal]

    ClassDef = Node[ast.ClassDef]

    AsyncFunctionDef = Node[ast.AsyncFunctionDef]
    Await = Node[ast.Await]

    AsyncFor = Node[ast.AsyncFor]
    AsyncWith = Node[ast.AsyncWith]


Module = Node[ast.Module]
